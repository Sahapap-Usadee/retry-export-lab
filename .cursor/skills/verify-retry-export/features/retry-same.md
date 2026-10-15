# Retry same input

Retry same input re-exports `fixtures/first.csv` into an output that already holds
the first-export rows. The user-visible result must keep one row per id: still only
Ada and Lin, with unchanged bytes for those records (no second copy of id 1 or 2).

## Sub-features

- `retry-no-dup` does not append duplicate rows for ids already present.
- `retry-bytes` does not rewrite existing names when the same ids appear again.
- `retry-oracle` uses `verify_runtime.py` (first then first again) as the shared oracle step.

## How to get to it (user POV)

- After a successful first export to `<out.csv>`, run `python3 exporter.py --input fixtures/first.csv --output <out.csv>` again with the same paths.

## Driving it with ctl.py

Preconditions:

- Doctor reports `"status": "pass"`.
- Prefer the full oracle for this lab baseline (covers retry then overlap in one drive).
- Do not change expected rows inside `verify_runtime.py`.

- **Oracle drive.** Run `python3 .cursor/skills/verify-retry-export/scripts/ctl.py retry-oracle --run-id "$RUN_ID"`. On baseline, expect ctl exit `3` and `"status": "reproduced"` — not harness pass.
- **Observe failure shape.** Evidence `cli.stdout.txt` / `cli.stderr.txt` show `actual:` with **7** dicts including a second Ada/Lin pair, while expected remains three rows (Ada, Lin, Grace).
- **Proof.** Retain `evidence/$RUN_ID/retry-oracle/status.json` with `"status": "reproduced"` and the captured command/exit/output. This is product-bug evidence, not a reason to edit the oracle.

## Gotchas

- Baseline append-only exporter produces 7 rows. That is the bug to evidence (`reproduced`), not a cue to loosen expected results.
- Separating first-export PASS from this REPRODUCED status is required in any report.
- Manual two-call CLI proof is valid only if the output path is isolated under `.runtime/verify-$RUN_ID/` and both invocations are logged.
- Passing `python3 -m unittest` alone does not prove retry behavior.
