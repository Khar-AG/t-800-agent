# HEALTH-REPORT

**Generated:** 2026-07-12 17:33
**Status:** OK
**Failed:** 0
**Warnings:** 0

| Status | Check | Details |
|--------|-------|---------|
| OK | t-800-operator subagent | agents/t-800-operator.md |
| OK | t-800-maintainer subagent | agents/t-800-maintainer.md |
| OK | maintainer skill disabled | skills/t-800-knowledge-base/SKILL.md |
| OK | health command installed | commands/t-800-health.md |
| OK | global mandatory-routing | ~/.cursor/rules/t-800-mandatory-routing.mdc |
| OK | plugin dest agents | ~/.cursor/plugins/local/t-800-agent/agents |
| OK | no stale user-home mirrors | clean |
| OK | manifest freshness | Latest sync: 2026-07-02 (10 days) |
| OK | validate-agents | passed |
| OK | audit-agent-graph | passed |
| OK | coverage audit | Missing=0 |

## Next step

If status is FAIL, run: bash scripts/install-plugin.sh && bash scripts/verify-install.sh
