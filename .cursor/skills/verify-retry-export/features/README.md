# Retry-export verification map

This directory is the maintained source for verifying user-facing behavior of the
retry-export Python CLI. Read this index before driving, then use the matching
feature file as the recipe.

## Baseline preconditions

- Working directory is the repository root (`exporter.py`, `fixtures/`, `verify_runtime.py`).
- Python 3.9+ on `PATH` as `python3`.
- Set a fresh `RUN_ID` per verification session; temp data is `.runtime/verify-$RUN_ID/`.
- Run `python3 .cursor/skills/verify-retry-export/scripts/ctl.py doctor` and require `"status": "pass"`.
- Never weaken `verify_runtime.py` expected rows to make a check green.
- Never drive shared output files across concurrent runs; each run owns its runtime dir.

## Driving conventions

- Start every recipe from an empty output CSV in that run's runtime dir unless noted.
- Treat every command as literal. Keep flags and fixture paths unchanged.
- Drive through `ctl.py` or the documented `exporter.py` / `verify_runtime.py` invocations.
- After mutations, read the output CSV back as proof. Do not remove proof under `evidence/`.

## Proof and skip reporting

- CLI proof includes the command, stdout, stderr, and exit code under `evidence/<run-id>/`.
- Mutation proof includes the written CSV rows (or oracle stdout `actual:` line).
- Record the feature ID and `run_id` with every artifact (`status.json`).
- Separate **first-export harness PASS** from **retry/overlap product REPRODUCED**.
- Report an unreachable path with the attempted command and unmet precondition.
- Do not report a skipped entry point as verified through a different path.

## Feature entry contract

Each feature file starts with an H1 title and one paragraph describing the user-visible
behavior. It then uses exactly four H2 sections in this order.

1. `Sub-features` lists short IDs with one line for each behavior.
2. `How to get to it (user POV)` lists every user entry point.
3. `Driving it with ctl.py` starts with `Preconditions:` and uses labeled bullets that
   pair each user action with an exact command and observable result.
4. `Gotchas` lists traps that can waste or invalidate a verification run.

Keep implementation details out of the map. Name only user paths, fixture files,
commands, and observable proof.

## Features

- [First export](./first-export.md) writes id 1/Ada and 2/Lin from `fixtures/first.csv`.
- [Retry same input](./retry-same.md) re-exports `first.csv` without adding rows or changing bytes.
- [Overlap and new ids](./overlap-new.md) applies `next.csv`: first occurrence wins; only Grace is new.
