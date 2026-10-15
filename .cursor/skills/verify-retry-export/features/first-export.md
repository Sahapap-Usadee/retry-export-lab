# First export

First export writes a fresh CSV from `fixtures/first.csv` so the user gets exactly
two records: id `1` / Ada and id `2` / Lin, with header `id,name`.

## Sub-features

- `first-cli` runs `exporter.py` once against an empty output path.
- `first-rows` proves the output rows match the fixture expectation.
- `first-harness` distinguishes this harness PASS from the retry product bug.

## How to get to it (user POV)

- Run `python3 exporter.py --input fixtures/first.csv --output <out.csv>` from the repo root when `<out.csv>` does not exist yet (or is empty).

## Driving it with ctl.py

Preconditions:

- Doctor reports `"status": "pass"`.
- A fresh `RUN_ID` is chosen; `.runtime/verify-$RUN_ID/` is unused.
- Output target is that run's `first-out.csv` (created by the helper).

- **Export once.** Drive the real CLI through the helper. Run `python3 .cursor/skills/verify-retry-export/scripts/ctl.py first-export --run-id "$RUN_ID"`. Exit code `0` and JSON `"status": "pass"`.
- **Confirm rows.** Read evidence `evidence/$RUN_ID/first-export/actual.json`. It equals `[{"id":"1","name":"Ada"},{"id":"2","name":"Lin"}]` and matches `fixtures/first.csv`.
- **Proof.** Keep `cli.cmd.txt`, `cli.exit.txt`, `cli.stdout.txt`, `cli.stderr.txt`, `output.csv`, and `status.json` under `evidence/$RUN_ID/first-export/`.
- **Cleanup temp.** Run `python3 .cursor/skills/verify-retry-export/scripts/ctl.py cleanup --run-id "$RUN_ID"`. `.runtime/verify-$RUN_ID/` is gone; evidence directory still exists.

## Gotchas

- Unit-test import of `export_rows` is not the user path. Prefer the CLI helper for proof.
- A PASS here only means first export works. It does **not** clear the retry/overlap bug.
- Do not reuse an output file that already has rows; start from the run's empty runtime dir.
- Cleanup must not delete `evidence/$RUN_ID/`; if evidence is missing after cleanup, the skill failed.
