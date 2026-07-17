#!/usr/bin/env python3
"""t800_risk_classifier.py — deterministic risk_class (Loop Engineering v2).

risk_class ONLY by this script. LLM/agent MUST NOT assign LOW.

Rules (denylist wins):
  - Default: not allowlisted → HIGH
  - Built-in conservative LOW allowlist (narrow only via {memory}/loop-policy.json)
  - Always HIGH for orchestration, hooks, alwaysApply, gate weaken,
    create/delete agents, credentials, >1 agent file, >3 files

Usage:
  python3 scripts/t800_risk_classifier.py --patch JSON|--patch-file PATH [--memory-path PATH]
  python3 scripts/t800_risk_classifier.py --fixture-dir DIR [--memory-path PATH]

Exit: 0 pass (incl. fixture suite), 1 fail / false-LOW detected.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "1.0"
LABELS = ("LOW", "MEDIUM", "HIGH", "BLOCK_CANDIDATE")

# Built-in LOW allowlist ids (conservative). Policy may ONLY remove / narrow.
BUILTIN_LOW_RULES = (
    "single_leaf_agent_no_graph",
    "single_ban_line",
    "link_existing_shared_contract",
    "typo_or_path_fix",
    "description_sync",
    "docs_or_changelog_only",
)

AGENT_FILE_RE = re.compile(r"(^|/)agents/[^/]+\.md$", re.I)
SHARED_CONTRACT_RE = re.compile(r"(^|/)shared/[a-z0-9_.-]+\.md$", re.I)
DOCS_RE = re.compile(
    r"(^|/)(docs/|knowledge-base/CHANGELOG\.md|CHANGELOG\.md|README\.md)",
    re.I,
)
HOOKS_RE = re.compile(r"(^|/)(hooks\.json|hooks/|\.cursor/hooks)", re.I)
RULE_RE = re.compile(r"(^|/)\.?cursor/rules/|rules/.*\.mdc$", re.I)
GATE_RE = re.compile(
    r"t800_run_gate|validate-agents|audit-agent-graph|verify-install|"
    r"factory_bypass_gate|before-artifact-edit",
    re.I,
)
ORCH_RE = re.compile(
    r"department-orchestration|loop-engineering-contract|"
    r"plan-to-factory-handoff|mandatory-routing",
    re.I,
)
CRED_RE = re.compile(
    r"(\.env|credentials|api[_-]?key|secret|token|password|teya\.env)",
    re.I,
)
TYPO_RE = re.compile(
    r"\b(typo|опечатк|path.?fix|путь|rename.?path|fix.?path)\b",
    re.I,
)
DESC_SYNC_RE = re.compile(
    r"\b(description.?sync|sync.?description|Use when|Do NOT|"
    r"описание|frontmatter.?description)\b",
    re.I,
)
BAN_LINE_RE = re.compile(r"\b(ban|запрет|Do NOT|block.?list|denylist)\b", re.I)
LINK_CONTRACT_RE = re.compile(
    r"\b(link|ссылк|see also|см\.|shared/[a-z0-9_.-]+-contract)\b",
    re.I,
)


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_files(files: list[Any]) -> list[str]:
    out: list[str] = []
    for f in files:
        if isinstance(f, dict):
            p = f.get("path") or f.get("file") or f.get("name")
            if p:
                out.append(str(p).replace("\\", "/"))
        elif f is not None:
            out.append(str(f).replace("\\", "/"))
    return out


def load_policy(memory_path: Path | None) -> dict[str, Any]:
    if memory_path is None:
        return {}
    path = memory_path / "loop-policy.json"
    if not path.is_file():
        return {}
    try:
        data = load_json(path)
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def effective_allowlist(policy: dict[str, Any]) -> set[str]:
    """Policy may ONLY narrow built-in allowlist (remove ids), never expand."""
    allowed = set(BUILTIN_LOW_RULES)
    disable = as_list(policy.get("disable_low_rules") or policy.get("narrow_low") or [])
    for item in disable:
        allowed.discard(str(item))
    # Explicit allow_low_rules in policy cannot ADD beyond built-in
    explicit = as_list(policy.get("allow_low_rules") or [])
    if explicit:
        allowed &= {str(x) for x in explicit}
    return allowed


def agent_files(files: list[str]) -> list[str]:
    return [f for f in files if AGENT_FILE_RE.search(f)]


def detect_always_high(patch: dict[str, Any], files: list[str], text: str) -> str | None:
    """Return reason if must be HIGH / BLOCK. Denylist wins."""
    kind = str(patch.get("kind") or patch.get("change_kind") or "").lower()
    flags = {str(x).lower() for x in as_list(patch.get("flags"))}

    if patch.get("create_agent") or patch.get("delete_agent") or kind in {
        "create_agent",
        "delete_agent",
        "create",
        "delete",
    }:
        return "create_or_delete_agent"
    if "create_agent" in flags or "delete_agent" in flags:
        return "create_or_delete_agent"

    if any(CRED_RE.search(f) for f in files) or CRED_RE.search(text):
        return "credentials_or_secrets"

    if any(HOOKS_RE.search(f) for f in files) or "hooks" in kind:
        return "hooks_change"

    if any(RULE_RE.search(f) for f in files):
        joined = "\n".join(files) + "\n" + text
        if re.search(r"alwaysApply\s*:\s*true", joined, re.I) or "alwaysapply" in text.lower():
            return "alwaysApply_change"
        # any rule file change is HIGH by default (not in LOW allowlist)
        return "rules_change"

    if any(GATE_RE.search(f) for f in files) or GATE_RE.search(text):
        if re.search(r"weaken|ослаб|skip.?gate|bypass|exit\s*0\s*always|fail.?open.?gate", text, re.I):
            return "gate_weaken"
        # touching gate scripts is HIGH unless somehow allowlisted (never)
        return "gate_script_touch"

    if any(ORCH_RE.search(f) for f in files) or ORCH_RE.search(text):
        return "orchestration_or_department_contract"

    if "orchestration" in kind or "department" in kind:
        return "orchestration_or_department_contract"

    agents = agent_files(files)
    if len(agents) > 1:
        return "more_than_one_agent_file"
    if len(files) > 3:
        return "more_than_three_files"

    # Graph / readonly changes on agents → HIGH
    if agents and (
        re.search(r"\b(calls|calledBy|called_by|readonly)\b", text, re.I)
        or patch.get("touches_calls")
        or patch.get("touches_calledBy")
        or patch.get("touches_readonly")
        or "readonly_change" in flags
        or "graph_change" in flags
    ):
        return "agent_graph_or_readonly_change"

    return None


def match_low_rule(
    patch: dict[str, Any], files: list[str], text: str, allow: set[str]
) -> str | None:
    """Return matched LOW rule id or None. Only if allow contains the rule."""
    agents = agent_files(files)
    kind = str(patch.get("kind") or patch.get("change_kind") or "").lower()

    # link to existing shared contract (before broad docs-only)
    if "link_existing_shared_contract" in allow:
        if LINK_CONTRACT_RE.search(text) or kind == "link_contract":
            if len(files) <= 2 and all(
                DOCS_RE.search(f) or SHARED_CONTRACT_RE.search(f) for f in files
            ):
                if not any(ORCH_RE.search(f) for f in files):
                    return "link_existing_shared_contract"

    # docs / changelog only
    if "docs_or_changelog_only" in allow and files and all(DOCS_RE.search(f) for f in files):
        if not agents and not any(HOOKS_RE.search(f) for f in files):
            return "docs_or_changelog_only"

    # single leaf agent, no graph
    if "single_leaf_agent_no_graph" in allow and len(files) == 1 and len(agents) == 1:
        if not re.search(r"\b(calls|calledBy|called_by|readonly)\b", text, re.I):
            if kind in ("", "leaf_edit", "agent_leaf", "typo", "description", "ban_line"):
                # kind-specific first (Do NOT appears in both ban + description text)
                if kind == "ban_line" and "single_ban_line" in allow:
                    return "single_ban_line"
                if kind in ("description", "description_sync") and "description_sync" in allow:
                    return "description_sync"
                if kind == "typo" and "typo_or_path_fix" in allow:
                    return "typo_or_path_fix"
                if BAN_LINE_RE.search(text) and "single_ban_line" in allow:
                    return "single_ban_line"
                if TYPO_RE.search(text) and "typo_or_path_fix" in allow:
                    return "typo_or_path_fix"
                if DESC_SYNC_RE.search(text) and "description_sync" in allow:
                    return "description_sync"
                # bare leaf body fix without graph keywords
                if kind in ("leaf_edit", "agent_leaf", ""):
                    return "single_leaf_agent_no_graph"

    # typo/path even on non-agent single file (not hooks/rules/gates)
    if "typo_or_path_fix" in allow and len(files) == 1 and (TYPO_RE.search(text) or kind == "typo"):
        f = files[0]
        if not HOOKS_RE.search(f) and not RULE_RE.search(f) and not GATE_RE.search(f):
            if not ORCH_RE.search(f):
                return "typo_or_path_fix"

    # description sync — single agent
    if (
        "description_sync" in allow
        and len(agents) == 1
        and len(files) <= 2
        and (DESC_SYNC_RE.search(text) or kind in ("description", "description_sync"))
    ):
        return "description_sync"

    # single ban line — single agent
    if (
        "single_ban_line" in allow
        and len(agents) == 1
        and len(files) == 1
        and (BAN_LINE_RE.search(text) or kind == "ban_line")
    ):
        return "single_ban_line"

    return None


def classify(patch: dict[str, Any], memory_path: Path | None = None) -> dict[str, Any]:
    files = normalize_files(as_list(patch.get("files") or patch.get("paths") or []))
    text_parts = [
        str(patch.get("change") or ""),
        str(patch.get("symptom") or ""),
        str(patch.get("description") or ""),
        str(patch.get("proposed_patch", {}).get("change") or "")
        if isinstance(patch.get("proposed_patch"), dict)
        else "",
        " ".join(str(x) for x in as_list(patch.get("evidence"))),
    ]
    text = "\n".join(text_parts)

    policy = load_policy(memory_path)
    allow = effective_allowlist(policy)

    high_reason = detect_always_high(patch, files, text)
    if high_reason:
        label = "BLOCK_CANDIDATE" if high_reason == "credentials_or_secrets" else "HIGH"
        # gate weaken is HIGH (not auto BLOCK unless credentials)
        if high_reason == "gate_weaken":
            label = "HIGH"
        return {
            "schema_version": SCHEMA_VERSION,
            "risk_class": label,
            "matched_rule": None,
            "deny_reason": high_reason,
            "files": files,
            "allowlist_effective": sorted(allow),
            "policy_narrowed": sorted(set(BUILTIN_LOW_RULES) - allow),
        }

    low_rule = match_low_rule(patch, files, text, allow)
    if low_rule:
        return {
            "schema_version": SCHEMA_VERSION,
            "risk_class": "LOW",
            "matched_rule": low_rule,
            "deny_reason": None,
            "files": files,
            "allowlist_effective": sorted(allow),
            "policy_narrowed": sorted(set(BUILTIN_LOW_RULES) - allow),
        }

    # Default: not allowlisted → HIGH (zero false LOW)
    return {
        "schema_version": SCHEMA_VERSION,
        "risk_class": "HIGH",
        "matched_rule": None,
        "deny_reason": "not_allowlisted",
        "files": files,
        "allowlist_effective": sorted(allow),
        "policy_narrowed": sorted(set(BUILTIN_LOW_RULES) - allow),
    }


def run_fixtures(fixture_dir: Path, memory_path: Path | None) -> dict[str, Any]:
    cases: list[Path] = []
    for p in sorted(fixture_dir.rglob("*")):
        if p.is_file() and p.suffix == ".json" and p.name != "README.json":
            # skip expected-only wrappers named expected.json at top of subdirs? include all
            if p.name.endswith(".expected.json"):
                continue
            cases.append(p)

    results: list[dict[str, Any]] = []
    false_low = 0
    failed = 0
    for case in cases:
        try:
            data = load_json(case)
        except (OSError, json.JSONDecodeError) as exc:
            failed += 1
            results.append({"case": str(case), "ok": False, "error": str(exc)})
            continue

        patch = data.get("patch") if isinstance(data, dict) and "patch" in data else data
        if not isinstance(patch, dict):
            failed += 1
            results.append({"case": str(case), "ok": False, "error": "patch not object"})
            continue

        expect = data.get("expect_risk_class") if isinstance(data, dict) else None
        if expect is None:
            # sidecar
            side = case.with_suffix(".expected.json")
            if side.is_file():
                try:
                    expect = load_json(side).get("risk_class")
                except (OSError, json.JSONDecodeError):
                    expect = None

        got = classify(patch, memory_path)
        risk = got["risk_class"]
        ok = True
        note = None
        if expect:
            expect_u = str(expect).upper()
            if risk != expect_u:
                ok = False
                failed += 1
                note = f"expected {expect_u}, got {risk}"
            # Trap cases: expect HIGH but got LOW → false LOW
            if expect_u in {"HIGH", "BLOCK_CANDIDATE", "MEDIUM"} and risk == "LOW":
                false_low += 1
                note = (note or "") + " FALSE_LOW"
        else:
            # No expect: still count LOW on trap-* names as false LOW
            if case.name.startswith("trap-") and risk == "LOW":
                ok = False
                false_low += 1
                failed += 1
                note = "trap case returned LOW"

        results.append(
            {
                "case": case.name,
                "ok": ok,
                "risk_class": risk,
                "expect": expect,
                "deny_reason": got.get("deny_reason"),
                "matched_rule": got.get("matched_rule"),
                "note": note,
            }
        )

    return {
        "schema_version": SCHEMA_VERSION,
        "ok": failed == 0 and false_low == 0,
        "fixture_dir": str(fixture_dir),
        "case_count": len(cases),
        "failed": failed,
        "false_low": false_low,
        "zero_false_LOW": false_low == 0,
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="T-800 deterministic risk classifier")
    parser.add_argument("--memory-path", default=None)
    parser.add_argument("--patch", default=None, help="JSON patch object")
    parser.add_argument("--patch-file", default=None)
    parser.add_argument("--fixture-dir", default=None, help="Run fixture suite")
    parser.add_argument("--stdin", action="store_true")
    args = parser.parse_args()

    memory_path = (
        Path(args.memory_path).expanduser().resolve() if args.memory_path else None
    )

    if args.fixture_dir:
        fixture_dir = Path(args.fixture_dir).expanduser().resolve()
        if not fixture_dir.is_dir():
            print(f"FAIL: нет fixture-dir: {fixture_dir}", file=sys.stderr)
            return 1
        report = run_fixtures(fixture_dir, memory_path)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        if not report["ok"]:
            print(
                f"FAIL: fixtures failed={report['failed']} false_LOW={report['false_low']}",
                file=sys.stderr,
            )
            return 1
        print("PASS: zero false LOW", file=sys.stderr)
        return 0

    try:
        if args.patch_file:
            raw = Path(args.patch_file).expanduser().resolve().read_text(encoding="utf-8")
            data = json.loads(raw)
        elif args.patch:
            data = json.loads(args.patch)
        elif args.stdin or not sys.stdin.isatty():
            raw = sys.stdin.read()
            data = json.loads(raw)
        else:
            print("FAIL: нужен --patch, --patch-file, --stdin или --fixture-dir", file=sys.stderr)
            return 1
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    patch = data.get("patch") if isinstance(data, dict) and "patch" in data else data
    if not isinstance(patch, dict):
        print("FAIL: patch должен быть объектом", file=sys.stderr)
        return 1

    result = classify(patch, memory_path)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
