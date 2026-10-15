# Overlap and new ids

Overlap and new ids applies `fixtures/next.csv` after first (and ideally after a
correct retry). The user should see id `2` keep the original name Lin (first
occurrence wins over Changed-Lin), id `3` / Grace appear once, and Ignored-Grace
must not create a second id `3` row. Acceptance target after the full sequence:
exactly Ada, Lin, Grace.

## Sub-features

- `overlap-keep` keeps the first name for overlapping id `2`.
- `new-once` adds id `3` / Grace a single time.
- `dup-ignore` drops the duplicate Grace row inside `next.csv`.
- `full-oracle` proves the combined journey via unmodified `verify_runtime.py`.

## How to get to it (user POV)

- With an existing export file from `fixtures/first.csv`, run `python3 exporter.py --input fixtures/next.csv --output <out.csv>`.

## Driving it with ctl.py

Preconditions:

- Doctor reports `"status": "pass"`.
- Oracle expected list stays `[{id:1,name:Ada},{id:2,name:Lin},{id:3,name:Grace}]` as in `verify_runtime.py`.
- On baseline product code, treat AssertionError as `reproduced`, not harness failure.

- **Full journey.** Run `python3 .cursor/skills/verify-retry-export/scripts/ctl.py retry-oracle --run-id "$RUN_ID"` (oracle feeds first, first, next). Baseline → `"status": "reproduced"`, actual length `7`.
- **Name the mismatches.** Actual includes duplicate Ada/Lin, `Changed-Lin`, and `Ignored-Grace`. Expected never includes those; do not update expected to match actual.
- **Proof.** Evidence under `evidence/$RUN_ID/retry-oracle/` holds command, exit, stdout/stderr, and `status.json` with `oracle_expected` and `actual_row_count`.

## Gotchas

- `next.csv` intentionally contains Changed-Lin and Ignored-Grace to stress first-wins and dedupe. Matching those strings in the output is a product failure.
- Fixing the product is out of scope for skill generation; only report `reproduced` with evidence.
- Do not collapse this feature into "unit test passed" — unittest covers only first export today.
- When the product is fixed later, the same oracle command must flip to `"status": "pass"` without editing expected rows.
