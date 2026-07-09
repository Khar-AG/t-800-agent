#!/usr/bin/env python3
"""t800_plugin_audit.py — machine inventory of a Cursor plugin (v1.11).

Writes ONLY under --out. Never prunes. Never writes to T-800 KB.

Usage:
  python3 scripts/t800_plugin_audit.py --plugin-root <PATH> --out <DIR> \\
      [--strict-alwaysapply large]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ALWAYS_RE = re.compile(r"^alwaysApply:\s*true\b", re.M | re.I)
NAME_RE = re.compile(r"^name:\s*[\"']?([^\s\"'#]+)", re.M)
FRONT_NAME_RE = re.compile(r"^---\s*\n(.*?)\n---", re.S)
AGENT_REF_RE = re.compile(
    r"(?:Task\s*\(\s*|`)?([a-z][a-z0-9_-]*(?:-[a-z0-9_]+)*)(?:`|\s*\))?",
    re.I,
)
# Prefer explicit Task(...) and known agent-like tokens in chains
TASK_RE = re.compile(r"Task\s*\(\s*[`'\"]?([a-z][a-z0-9_-]+)[`'\"]?\s*\)", re.I)
BARE_AGENT_RE = re.compile(r"\b([a-z][a-z0-9]*(?:-[a-z0-9]+)+)\b")


def find_plugin_json(plugin_root: Path) -> Path | None:
    for rel in (".cursor-plugin/plugin.json", "plugin.json"):
        p = plugin_root / rel
        if p.is_file():
            return p
    return None


def list_md_stems(directory: Path, pattern: str = "*.md") -> list[str]:
    if not directory.is_dir():
        return []
    return sorted(p.stem for p in directory.glob(pattern) if p.is_file())


def list_skill_names(skills_dir: Path) -> list[str]:
    if not skills_dir.is_dir():
        return []
    names: list[str] = []
    for skill_md in sorted(skills_dir.glob("*/SKILL.md")):
        names.append(skill_md.parent.name)
    # also flat skills/*.md if any
    for p in sorted(skills_dir.glob("*.md")):
        if p.name.lower() != "readme.md":
            names.append(p.stem)
    return sorted(set(names))


def list_rule_files(rules_dir: Path) -> list[Path]:
    if not rules_dir.is_dir():
        return []
    out: list[Path] = []
    for p in sorted(rules_dir.rglob("*")):
        if p.is_file() and p.suffix.lower() in {".mdc", ".md"}:
            out.append(p)
    return out


def parse_always_apply(path: Path) -> bool:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    head = text[:2000]
    return bool(ALWAYS_RE.search(head))


def agent_id_from_file(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return path.stem
    m = FRONT_NAME_RE.match(text)
    if m:
        nm = NAME_RE.search(m.group(1))
        if nm:
            return nm.group(1).strip()
    return path.stem


def load_json(path: Path) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def collect_agent_refs_from_obj(obj: Any, into: set[str]) -> None:
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in {"agents", "primary_agents", "optional_agents", "required_agents", "chain"} and isinstance(
                v, list
            ):
                for item in v:
                    if isinstance(item, str) and re.match(r"^[a-z][a-z0-9_-]+$", item):
                        into.add(item)
                    elif isinstance(item, dict):
                        aid = item.get("id") or item.get("agent") or item.get("name")
                        if isinstance(aid, str):
                            into.add(aid)
            collect_agent_refs_from_obj(v, into)
    elif isinstance(obj, list):
        for item in obj:
            collect_agent_refs_from_obj(item, into)
    elif isinstance(obj, str):
        for m in TASK_RE.finditer(obj):
            into.add(m.group(1))


def collect_refs_from_markdown(text: str, known_agents: set[str]) -> set[str]:
    found: set[str] = set()
    for m in TASK_RE.finditer(text):
        found.add(m.group(1))
    for m in BARE_AGENT_RE.finditer(text):
        tok = m.group(1)
        if tok in known_agents:
            found.add(tok)
    return found


def inventory_hooks(plugin_root: Path) -> dict[str, Any]:
    hooks_path = plugin_root / "hooks.json"
    hooks_dir = plugin_root / "hooks"
    result: dict[str, Any] = {
        "hooks_json": hooks_path.is_file(),
        "hooks_dir": hooks_dir.is_dir(),
        "events": [],
        "script_files": [],
    }
    if hooks_path.is_file():
        data = load_json(hooks_path)
        if isinstance(data, dict):
            hooks = data.get("hooks", data)
            if isinstance(hooks, dict):
                result["events"] = sorted(hooks.keys())
            result["raw_keys"] = sorted(data.keys())
    if hooks_dir.is_dir():
        result["script_files"] = sorted(
            str(p.relative_to(plugin_root)) for p in hooks_dir.rglob("*") if p.is_file()
        )
    return result


def build_inventory(plugin_root: Path) -> dict[str, Any]:
    plugin_json_path = find_plugin_json(plugin_root)
    plugin_meta: dict[str, Any] = {"path": None, "ok": False}
    if plugin_json_path:
        meta = load_json(plugin_json_path)
        plugin_meta = {
            "path": str(plugin_json_path.relative_to(plugin_root)),
            "ok": isinstance(meta, dict),
            "name": (meta or {}).get("name") if isinstance(meta, dict) else None,
            "version": (meta or {}).get("version") if isinstance(meta, dict) else None,
            "displayName": (meta or {}).get("displayName") if isinstance(meta, dict) else None,
        }

    agents_dir = plugin_root / "agents"
    cursor_agents = plugin_root / ".cursor" / "agents"
    agent_files: list[Path] = []
    if agents_dir.is_dir():
        agent_files.extend(sorted(agents_dir.glob("*.md")))
    if cursor_agents.is_dir():
        for p in sorted(cursor_agents.glob("*.md")):
            if p.name not in {f.name for f in agent_files}:
                agent_files.append(p)

    agents: list[dict[str, str]] = []
    agent_ids: set[str] = set()
    for p in agent_files:
        aid = agent_id_from_file(p)
        agent_ids.add(aid)
        agents.append(
            {
                "id": aid,
                "file": str(p.relative_to(plugin_root)),
            }
        )

    commands_dir = plugin_root / "commands"
    if not commands_dir.is_dir():
        commands_dir = plugin_root / ".cursor" / "commands"
    command_names = list_md_stems(commands_dir) if commands_dir.is_dir() else []

    skills_dir = plugin_root / "skills"
    if not skills_dir.is_dir():
        skills_dir = plugin_root / ".cursor" / "skills"
    skill_names = list_skill_names(skills_dir) if skills_dir.is_dir() else []

    rules_dir = plugin_root / "rules"
    if not rules_dir.is_dir():
        rules_dir = plugin_root / ".cursor" / "rules"
    rule_files = list_rule_files(rules_dir) if rules_dir.is_dir() else []
    rules_detail: list[dict[str, Any]] = []
    always_count = 0
    for rp in rule_files:
        always = parse_always_apply(rp)
        if always:
            always_count += 1
        try:
            chars = len(rp.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            chars = 0
        rules_detail.append(
            {
                "name": rp.stem,
                "file": str(rp.relative_to(plugin_root)),
                "always_apply": always,
                "chars": chars,
            }
        )

    # command-chains
    chains_path = plugin_root / "shared" / "command-chains.json"
    chain_commands: list[str] = []
    refs_from_chains: set[str] = set()
    chains_present = chains_path.is_file()
    if chains_present:
        chains_data = load_json(chains_path)
        if isinstance(chains_data, dict):
            cmds = chains_data.get("commands", {})
            if isinstance(cmds, dict):
                chain_commands = sorted(cmds.keys())
                collect_agent_refs_from_obj(cmds, refs_from_chains)
            collect_agent_refs_from_obj(chains_data, refs_from_chains)

    # registry cross-check + call graph (leads → leaf)
    registry_candidates = [
        plugin_root / "registry" / "agents-registry.json",
        plugin_root / "agents-registry.json",
    ]
    registry_path: Path | None = None
    registry_ids: set[str] = set()
    registry_edge_targets: set[str] = set()
    for cand in registry_candidates:
        if cand.is_file():
            registry_path = cand
            data = load_json(cand)
            if isinstance(data, dict):
                agents_list = data.get("agents", [])
                if isinstance(agents_list, list):
                    for item in agents_list:
                        if not isinstance(item, dict):
                            continue
                        aid = item.get("id")
                        if isinstance(aid, str):
                            registry_ids.add(aid)
                        for key in ("calls", "calledBy"):
                            arr = item.get(key, [])
                            if isinstance(arr, list):
                                for x in arr:
                                    if isinstance(x, str) and x != "main-agent":
                                        registry_edge_targets.add(x)
            break

    # refs from command markdown
    refs_from_commands: set[str] = set()
    if commands_dir.is_dir():
        for cp in commands_dir.glob("*.md"):
            try:
                text = cp.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            refs_from_commands |= collect_refs_from_markdown(text, agent_ids)

    # refs from agent bodies (Task(...)) — leaf вызываются лидами
    refs_from_agents: set[str] = set()
    if agents_dir.is_dir():
        for ap in agents_dir.glob("*.md"):
            try:
                text = ap.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            refs_from_agents |= collect_refs_from_markdown(text, agent_ids)

    linked_refs = (
        refs_from_chains
        | refs_from_commands
        | refs_from_agents
        | registry_edge_targets
    )
    all_refs = linked_refs | registry_ids

    # orphans = на диске, но нет в registry (реальная дыра) → WARN.
    # soft_unreferenced = в registry, но нигде не вызван (info, без WARN).
    if registry_ids:
        orphans = sorted(aid for aid in agent_ids if aid not in registry_ids)
        soft_unreferenced = sorted(
            aid for aid in (registry_ids & agent_ids) if aid not in linked_refs
        )
    else:
        orphans = sorted(aid for aid in agent_ids if aid not in linked_refs)
        soft_unreferenced = []

    registry_missing_on_disk = sorted(rid for rid in registry_ids if rid not in agent_ids)
    on_disk_missing_registry = (
        sorted(aid for aid in agent_ids if aid not in registry_ids) if registry_ids else []
    )

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "plugin_root": str(plugin_root.resolve()),
        "plugin": plugin_meta,
        "counts": {
            "agents": len(agents),
            "skills": len(skill_names),
            "commands": len(command_names),
            "rules": len(rules_detail),
            "always_apply_rules": always_count,
            "chain_commands": len(chain_commands),
            "orphans_heuristic": len(orphans),
            "soft_unreferenced": len(soft_unreferenced),
        },
        "agents": agents,
        "skills": skill_names,
        "commands": command_names,
        "rules": rules_detail,
        "hooks": inventory_hooks(plugin_root),
        "command_chains": {
            "present": chains_present,
            "path": "shared/command-chains.json" if chains_present else None,
            "commands": chain_commands,
            "agent_refs": sorted(refs_from_chains),
        },
        "registry": {
            "present": registry_path is not None,
            "path": str(registry_path.relative_to(plugin_root)) if registry_path else None,
            "ids": sorted(registry_ids),
            "missing_on_disk": registry_missing_on_disk,
            "on_disk_not_in_registry": on_disk_missing_registry,
        },
        "refs": {
            "from_chains": sorted(refs_from_chains),
            "from_commands": sorted(refs_from_commands),
            "from_agents": sorted(refs_from_agents),
            "from_registry_edges": sorted(registry_edge_targets),
            "union": sorted(all_refs),
        },
        "orphans": orphans,
        "soft_unreferenced": soft_unreferenced,
    }


def build_scorecard(
    inv: dict[str, Any],
    strict_large: bool,
) -> dict[str, Any]:
    always = inv["counts"]["always_apply_rules"]
    soft_threshold = 10
    hard_threshold = 20
    soft_warn = always >= soft_threshold
    hard_fail = always >= hard_threshold

    verdict = "PASS"
    reasons: list[str] = []
    if not inv["plugin"].get("ok"):
        verdict = "FAIL"
        reasons.append("broken or missing plugin.json")
    elif strict_large and hard_fail:
        verdict = "FAIL"
        reasons.append(f"alwaysApply count {always} >= hard {hard_threshold} (large)")
    elif soft_warn:
        verdict = "WARN"
        reasons.append(f"alwaysApply count {always} >= soft {soft_threshold}")

    if inv["orphans"]:
        if verdict == "PASS":
            verdict = "WARN"
        reasons.append(f"orphan agents (not in registry): {len(inv['orphans'])}")

    soft = inv.get("soft_unreferenced") or []
    # soft_unreferenced — info only, не поднимает WARN

    return {
        "verdict": verdict,
        "always_apply": {
            "count": always,
            "soft_threshold": soft_threshold,
            "hard_threshold": hard_threshold,
            "soft_warn": soft_warn,
            "hard_fail": hard_fail,
            "strict_large": strict_large,
        },
        "plugin_json_ok": bool(inv["plugin"].get("ok")),
        "orphans_count": len(inv["orphans"]),
        "soft_unreferenced_count": len(soft),
        "reasons": reasons,
        "counts": inv["counts"],
    }


def render_graph_md(inv: dict[str, Any]) -> str:
    lines = [
        "# Plugin audit graph",
        "",
        f"Plugin: `{inv['plugin'].get('name')}` v`{inv['plugin'].get('version')}`",
        "",
        "## Counts",
        "",
        f"- agents: **{inv['counts']['agents']}**",
        f"- skills: **{inv['counts']['skills']}**",
        f"- commands: **{inv['counts']['commands']}**",
        f"- rules: **{inv['counts']['rules']}** (alwaysApply: **{inv['counts']['always_apply_rules']}**)",
        f"- orphans (not in registry): **{inv['counts']['orphans_heuristic']}**",
        f"- soft_unreferenced (info): **{inv['counts'].get('soft_unreferenced', 0)}**",
        "",
    ]

    chain_cmds = inv["command_chains"].get("commands") or []
    refs = inv["command_chains"].get("agent_refs") or []
    # Mermaid: limit size for readability
    show_cmds = chain_cmds[:25]
    show_agents = sorted(set(refs))[:40]

    if show_cmds or show_agents:
        lines.extend(
            [
                "## Mermaid (sample)",
                "",
                "```mermaid",
                "flowchart LR",
                "  subgraph commands",
            ]
        )
        for i, c in enumerate(show_cmds):
            safe = re.sub(r"[^a-zA-Z0-9_]", "_", c)
            lines.append(f'    C{i}["{c}"]')
        lines.append("  end")
        lines.append("  subgraph agents_sample")
        for i, a in enumerate(show_agents):
            safe = re.sub(r"[^a-zA-Z0-9_]", "_", a)
            lines.append(f'    A{i}["{a}"]')
        lines.append("  end")
        # link first few commands to first few agents (illustrative)
        if show_cmds and show_agents:
            lines.append(f"  C0 -.-> A0")
            if len(show_agents) > 1 and len(show_cmds) > 1:
                lines.append(f"  C1 -.-> A1")
        lines.extend(["```", ""])
        lines.append(
            "_Связи sample — полные refs в `inventory.json` → `command_chains.agent_refs`._"
        )
        lines.append("")

    if inv["orphans"]:
        lines.extend(["## Orphans (not in chains/commands)", ""])
        for o in inv["orphans"][:50]:
            lines.append(f"- `{o}`")
        if len(inv["orphans"]) > 50:
            lines.append(f"- … +{len(inv['orphans']) - 50} more")
        lines.append("")

    return "\n".join(lines) + "\n"


def render_machine_summary(inv: dict[str, Any], score: dict[str, Any]) -> str:
    lines = [
        "# Audit machine summary",
        "",
        f"**Verdict:** {score['verdict']}",
        f"**Plugin:** {inv['plugin'].get('name')} `{inv['plugin'].get('version')}`",
        f"**Root:** `{inv['plugin_root']}`",
        "",
        "## Counts",
        "",
        "| Kind | N |",
        "|------|---|",
        f"| agents | {inv['counts']['agents']} |",
        f"| skills | {inv['counts']['skills']} |",
        f"| commands | {inv['counts']['commands']} |",
        f"| rules | {inv['counts']['rules']} |",
        f"| alwaysApply | {inv['counts']['always_apply_rules']} |",
        f"| chain commands | {inv['counts']['chain_commands']} |",
        f"| orphans | {inv['counts']['orphans_heuristic']} |",
        "",
        "## Reasons",
        "",
    ]
    if score["reasons"]:
        for r in score["reasons"]:
            lines.append(f"- {r}")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("SoT: `inventory.json`, `scorecard.json`.")
    lines.append("")
    return "\n".join(lines)


def write_outputs(out_dir: Path, inv: dict[str, Any], score: dict[str, Any]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "inventory.json").write_text(
        json.dumps(inv, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (out_dir / "scorecard.json").write_text(
        json.dumps(score, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (out_dir / "graph.md").write_text(render_graph_md(inv), encoding="utf-8")
    (out_dir / "audit-machine-summary.md").write_text(
        render_machine_summary(inv, score), encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="T-800 plugin machine audit (v1.11)")
    parser.add_argument("--plugin-root", required=True, help="Path to plugin root")
    parser.add_argument("--out", required=True, help="Output directory (only write target)")
    parser.add_argument(
        "--strict-alwaysapply",
        choices=["large"],
        default=None,
        help="Fail exit if alwaysApply >= 20 (large)",
    )
    args = parser.parse_args()

    plugin_root = Path(args.plugin_root).expanduser().resolve()
    out_dir = Path(args.out).expanduser().resolve()

    if not plugin_root.is_dir():
        print(f"ERROR: plugin-root not a directory: {plugin_root}", file=sys.stderr)
        return 1

    inv = build_inventory(plugin_root)
    strict = args.strict_alwaysapply == "large"
    score = build_scorecard(inv, strict_large=strict)

    try:
        write_outputs(out_dir, inv, score)
    except OSError as e:
        print(f"ERROR: cannot write to --out: {e}", file=sys.stderr)
        return 1

    print(f"OK wrote {out_dir}")
    print(f"verdict={score['verdict']} agents={inv['counts']['agents']} "
          f"alwaysApply={inv['counts']['always_apply_rules']} orphans={inv['counts']['orphans_heuristic']}")

    if not score["plugin_json_ok"]:
        return 1
    if strict and score["always_apply"]["hard_fail"]:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
