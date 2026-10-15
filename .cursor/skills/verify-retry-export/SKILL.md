---
name: verify-retry-export
description: >-
  Drive the retry-export-lab Python CLI (exporter.py) with fixtures and the
  verify_runtime.py oracle. Use when verifying first export, reproducing the
  retry/overlap duplicate-id bug, or collecting CLI evidence for this repo.
---

# Verify retry-export-lab

Surface: short-lived Python CLI (`exporter.py --input <csv> --output <csv>`).
No server. Isolation: each run uses its own `.runtime/verify-<run-id>/` data dir;
evidence goes under this skill's `evidence/<run-id>/` and survives cleanup.

Oracle: repo-root `verify_runtime.py`. **Never change its expected rows.** Baseline
failure (actual 7 rows vs expected 3) is the product bug → report `reproduced`,
do not weaken the harness to make it pass.

## Launch

From repository root (directory that contains `exporter.py`, `fixtures/`, `verify_runtime.py`):

```bash
python3 --version   # require 3.9+
python3 .cursor/skills/verify-retry-export/scripts/ctl.py doctor
```

Ready when doctor prints `"status": "pass"`. There is no long-lived process to keep
alive; each drive starts a fresh CLI subprocess.

Teardown: `python3 .cursor/skills/verify-retry-export/scripts/ctl.py cleanup --run-id <id>`

## Doctor

```bash
python3 .cursor/skills/verify-retry-export/scripts/ctl.py doctor
```

Checks: cwd is repo root, Python ≥ 3.9, `fixtures/first.csv` and `fixtures/next.csv`
exist, first fixture content is id 1/Ada and 2/Lin, `exporter.py` and
`verify_runtime.py` exist, `exporter.py --help` exposes `--input` / `--output`.
Exit `0` = pass, `2` = blocked.

## Drive

Always doctor first when anything looks off. Prefer the control CLI below; commands
are literal.

**First export (harness PASS path):**

```bash
RUN_ID=$(date +%Y%m%dT%H%M%S)-$$
python3 .cursor/skills/verify-retry-export/scripts/ctl.py first-export --run-id "$RUN_ID"
```

Real user path: `python3 exporter.py --input fixtures/first.csv --output <runtime>/first-out.csv`.
PASS only when output rows are exactly `[{id:1,name:Ada},{id:2,name:Lin}]` matching
`fixtures/first.csv`. This is harness health — separate from the retry product bug.

**Retry / overlap oracle (product REPRODUCED on baseline):**

```bash
python3 .cursor/skills/verify-retry-export/scripts/ctl.py retry-oracle --run-id "$RUN_ID"
```

Runs unmodified `python3 verify_runtime.py` (first → first again → next). Exit codes
from ctl: `0` pass (bug fixed), `3` reproduced (oracle AssertionError — keep expected),
`2` blocked. Do not edit `verify_runtime.py` expected results to green the check.

Feature recipes: [features/README.md](features/README.md).

## Evidence

Location: `.cursor/skills/verify-retry-export/evidence/<run-id>/<feature>/`

Each drive writes: `cli.cmd.txt`, `cli.stdout.txt`, `cli.stderr.txt`, `cli.exit.txt`,
`status.json`, plus feature-specific files (`output.csv`, `actual.json`, …). Capture
the real command, exit code, and process output — not paraphrased summaries.

Statuses: `pass` | `fail` | `reproduced` | `blocked`.
First-export green = harness `pass`. Oracle 7-row mismatch = product `reproduced`.

## Cleanup

```bash
python3 .cursor/skills/verify-retry-export/scripts/ctl.py cleanup --run-id "$RUN_ID"
```

Removes only `.runtime/verify-<run-id>/`. **Never deletes** `evidence/<run-id>/`.
After cleanup, confirm evidence paths still exist before reporting success.

## Helpers

Executable control script (invocation above):

`python3 .cursor/skills/verify-retry-export/scripts/ctl.py <doctor|first-export|retry-oracle|cleanup>`

- `doctor` — readiness
- `first-export [--run-id ID]` — real CLI first export proof
- `retry-oracle [--run-id ID]` — `verify_runtime.py` oracle; baseline → reproduced
- `cleanup --run-id ID` — drop temp data, keep evidence

## Maintenance

Use `/maintain-verification-skill` when exporter CLI, fixtures, or acceptance criteria change.
