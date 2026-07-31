# Teya Adapter (Phase 1+2)

Граница между **generic T-800 Factory** и **Teya Pro onboarding + evidence**.

## Phase 2 Evidence Bridge

| Piece | Location |
|-------|----------|
| Handoff schema v2 | [schemas/factory-handoff.schema.json](schemas/factory-handoff.schema.json) |
| Evidence helpers | [evidence.py](evidence.py) |
| Contract | [evidence-bridge-contract.md](evidence-bridge-contract.md) |
| Verifier (Teya) | `$TEYA_PLUGIN_ROOT/scripts/legacy/teya_t800_handoff_verify.py` |
| Materializer HITL | `$TEYA_PLUGIN_ROOT/scripts/legacy/teya_t800_materialize_onboarding.py` |
| Stale check | `$TEYA_PLUGIN_ROOT/scripts/legacy/teya_t800_provenance_stale_check.py` |
| Release evidence | `$TEYA_PLUGIN_ROOT/scripts/legacy/teya_t800_release_evidence.py` |
| Hook readiness | `scripts/t800_teya_hook_enforce_ready.py` |

T-800 пишет `provenance_status=incomplete` only.  
`verified` / `released` — только Teya-side tools.

## Profiles

| Profile | Adapter | brain-teya |
|---------|---------|------------|
| `teya-plugin-dev` | yes | yes |
| `teya-client` | yes | yes |
| `teya-pro` (legacy) | yes (alias) | yes |
| `generic-plugin` | **no** | no |

## Forbidden

- mutate rollout_state / success_streak
- HITL promotion / green streak
- execute `/teya-release-sync` from T-800
- write `~/.cursor/plugins/local/teya`
- set provenance verified / released from T-800
- auto-enable hook enforce
