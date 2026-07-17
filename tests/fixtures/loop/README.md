# Loop classifier fixtures

Success criterion: **zero false LOW**.

Run:

```bash
python3 scripts/t800_risk_classifier.py --fixture-dir tests/fixtures/loop
```

| Prefix | Meaning |
|--------|---------|
| `trap-*` | Must NOT be LOW (HIGH / BLOCK_CANDIDATE) |
| `ok-low-*` | Built-in allowlist LOW |

Denylist wins. Policy `{memory}/loop-policy.json` may only **narrow** allowlist.
