#!/usr/bin/env python3
"""Verification control for retry-export-lab (Python CLI exporter).

Run from repository root. Temp data lives under .runtime/; evidence under
.cursor/skills/verify-retry-export/evidence/. Cleanup never deletes evidence.
"""
from __future__ import annotations

import argparse
import ast
import csv
import json
import os
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT_MARKERS = ("exporter.py", "verify_runtime.py", "fixtures")
EXPECTED_FIRST = [
    {"id": "1", "name": "Ada"},
    {"id": "2", "name": "Lin"},
]
# Oracle expected rows — must match verify_runtime.py exactly. Do not change.
ORACLE_EXPECTED = [
    {"id": "1", "name": "Ada"},
    {"id": "2", "name": "Lin"},
    {"id": "3", "name": "Grace"},
]
BASELINE_BUG_ROW_COUNT = 7


def find_repo_root(start: Path | None = None) -> Path | None:
    cur = (start or Path.cwd()).resolve()
    for candidate in [cur, *cur.parents]:
        if all((candidate / m).exists() for m in REPO_ROOT_MARKERS):
            return candidate
    return None


def run_id_default() -> str:
    return time.strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:8]


def evidence_dir(run_id: str) -> Path:
    return SKILL_DIR / "evidence" / run_id


def runtime_dir(repo: Path, run_id: str) -> Path:
    return repo / ".runtime" / f"verify-{run_id}"


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def capture_run(
    cmd: list[str],
    *,
    cwd: Path,
    log_dir: Path,
    name: str,
) -> subprocess.CompletedProcess[str]:
    log_dir.mkdir(parents=True, exist_ok=True)
    write_text(log_dir / f"{name}.cmd.txt", " ".join(cmd) + "\n")
    proc = subprocess.run(
        cmd,
        cwd=str(cwd),
        capture_output=True,
        text=True,
    )
    write_text(log_dir / f"{name}.stdout.txt", proc.stdout)
    write_text(log_dir / f"{name}.stderr.txt", proc.stderr)
    write_text(log_dir / f"{name}.exit.txt", f"{proc.returncode}\n")
    return proc


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def cmd_doctor(_: argparse.Namespace) -> int:
    repo = find_repo_root()
    checks: list[dict[str, object]] = []
    ok = True

    def note(name: str, passed: bool, detail: str) -> None:
        nonlocal ok
        checks.append({"check": name, "pass": passed, "detail": detail})
        if not passed:
            ok = False

    if repo is None:
        note("cwd", False, f"not repo root; cwd={Path.cwd()} missing {REPO_ROOT_MARKERS}")
        print(json.dumps({"status": "blocked", "checks": checks}, indent=2))
        return 2
    note("cwd", True, str(repo))

    version = sys.version_info
    py_ok = version >= (3, 9)
    note("python", py_ok, f"{sys.executable} {sys.version.split()[0]}")

    first = repo / "fixtures" / "first.csv"
    next_csv = repo / "fixtures" / "next.csv"
    note("fixtures/first.csv", first.is_file(), str(first))
    note("fixtures/next.csv", next_csv.is_file(), str(next_csv))

    if first.is_file():
        try:
            rows = read_csv_rows(first)
            match = rows == EXPECTED_FIRST
            note("fixtures/first.csv content", match, f"rows={rows}")
        except Exception as exc:  # noqa: BLE001 — doctor must report any read failure
            note("fixtures/first.csv content", False, str(exc))

    exporter = repo / "exporter.py"
    oracle = repo / "verify_runtime.py"
    note("exporter.py", exporter.is_file(), str(exporter))
    note("verify_runtime.py", oracle.is_file(), str(oracle))

    if exporter.is_file() and py_ok:
        help_proc = subprocess.run(
            [sys.executable, str(exporter), "--help"],
            cwd=str(repo),
            capture_output=True,
            text=True,
        )
        help_ok = help_proc.returncode == 0 and "--input" in help_proc.stdout and "--output" in help_proc.stdout
        note(
            "cli --help",
            help_ok,
            f"exit={help_proc.returncode} stdout_has_flags={('--input' in help_proc.stdout)}",
        )

    status = "pass" if ok else "blocked"
    print(json.dumps({"status": status, "repo": str(repo), "checks": checks}, indent=2))
    return 0 if ok else 2


def cmd_first_export(args: argparse.Namespace) -> int:
    repo = find_repo_root()
    if repo is None:
        print(json.dumps({"status": "blocked", "reason": "cwd is not repo root"}, indent=2))
        return 2

    run_id = args.run_id or run_id_default()
    ev = evidence_dir(run_id)
    rt = runtime_dir(repo, run_id)
    rt.mkdir(parents=True, exist_ok=True)
    out_csv = rt / "first-out.csv"
    feature_ev = ev / "first-export"
    feature_ev.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable,
        "exporter.py",
        "--input",
        "fixtures/first.csv",
        "--output",
        str(out_csv),
    ]
    proc = capture_run(cmd, cwd=repo, log_dir=feature_ev, name="cli")

    result: dict[str, object] = {
        "feature": "first-export",
        "run_id": run_id,
        "command": cmd,
        "exit_code": proc.returncode,
        "runtime_dir": str(rt),
        "evidence_dir": str(feature_ev),
        "output_csv": str(out_csv),
    }

    if proc.returncode != 0:
        result["status"] = "fail"
        result["reason"] = "CLI exited non-zero"
        write_json(feature_ev / "status.json", result)
        print(json.dumps(result, indent=2))
        return 1

    if not out_csv.is_file():
        result["status"] = "fail"
        result["reason"] = "output CSV missing"
        write_json(feature_ev / "status.json", result)
        print(json.dumps(result, indent=2))
        return 1

    actual = read_csv_rows(out_csv)
    write_text(feature_ev / "output.csv", out_csv.read_text(encoding="utf-8"))
    write_json(feature_ev / "actual.json", actual)
    write_json(feature_ev / "expected.json", EXPECTED_FIRST)
    result["actual"] = actual
    result["expected"] = EXPECTED_FIRST

    if actual == EXPECTED_FIRST:
        result["status"] = "pass"
        write_json(feature_ev / "status.json", result)
        print(json.dumps(result, indent=2))
        return 0

    result["status"] = "fail"
    result["reason"] = "output rows != fixtures/first.csv expectation"
    write_json(feature_ev / "status.json", result)
    print(json.dumps(result, indent=2))
    return 1


def cmd_retry_oracle(args: argparse.Namespace) -> int:
    """Drive the product via verify_runtime.py. Do not alter its expected rows.

    Baseline product bug yields 7 actual rows vs 3 expected → status reproduced.
    """
    repo = find_repo_root()
    if repo is None:
        print(json.dumps({"status": "blocked", "reason": "cwd is not repo root"}, indent=2))
        return 2

    run_id = args.run_id or run_id_default()
    ev = evidence_dir(run_id) / "retry-oracle"
    ev.mkdir(parents=True, exist_ok=True)
    # Isolate CWD only; oracle uses its own TemporaryDirectory for output.
    rt = runtime_dir(repo, run_id)
    rt.mkdir(parents=True, exist_ok=True)

    cmd = [sys.executable, "verify_runtime.py"]
    env = os.environ.copy()
    env["VERIFY_RETRY_EXPORT_RUN_ID"] = run_id
    write_text(ev / "cli.cmd.txt", " ".join(cmd) + "\n")
    proc = subprocess.run(
        cmd,
        cwd=str(repo),
        capture_output=True,
        text=True,
        env=env,
    )
    write_text(ev / "cli.stdout.txt", proc.stdout)
    write_text(ev / "cli.stderr.txt", proc.stderr)
    write_text(ev / "cli.exit.txt", f"{proc.returncode}\n")

    combined = (proc.stdout or "") + (proc.stderr or "")
    result: dict[str, object] = {
        "feature": "retry-oracle",
        "run_id": run_id,
        "command": cmd,
        "exit_code": proc.returncode,
        "oracle": "verify_runtime.py",
        "oracle_expected": ORACLE_EXPECTED,
        "baseline_bug_row_count": BASELINE_BUG_ROW_COUNT,
        "evidence_dir": str(ev),
        "runtime_dir": str(rt),
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }

    if proc.returncode == 0 and "PASS: retry and overlap preserve one row per id" in proc.stdout:
        result["status"] = "pass"
        result["note"] = "product matches oracle; retry/overlap bug is fixed"
        write_json(ev / "status.json", result)
        print(json.dumps(result, indent=2))
        return 0

    # Parse actual list from oracle stdout when present.
    actual_rows = None
    for line in (proc.stdout or "").splitlines():
        if line.startswith("actual:"):
            try:
                actual_rows = ast.literal_eval(line[len("actual:") :].strip())
            except (SyntaxError, ValueError):
                actual_rows = None
            break
    if actual_rows is not None:
        result["actual"] = actual_rows
        result["actual_row_count"] = len(actual_rows)

    assert_failed = proc.returncode != 0 and "AssertionError" in combined
    looks_like_baseline = (
        isinstance(actual_rows, list)
        and len(actual_rows) == BASELINE_BUG_ROW_COUNT
        and actual_rows != ORACLE_EXPECTED
    )

    if assert_failed and looks_like_baseline:
        result["status"] = "reproduced"
        result["note"] = (
            "Oracle expected 3 deduped rows; product appended to 7. "
            "This is the product bug — do not weaken verify_runtime.py expected."
        )
        write_json(ev / "status.json", result)
        print(json.dumps(result, indent=2))
        return 3  # reproduced (distinct from harness fail)

    if assert_failed:
        result["status"] = "reproduced"
        result["note"] = (
            "Oracle assertion failed (product mismatch). Evidence captured; "
            "do not change expected results in verify_runtime.py."
        )
        write_json(ev / "status.json", result)
        print(json.dumps(result, indent=2))
        return 3

    result["status"] = "blocked"
    result["reason"] = "oracle did not pass and did not yield a clear AssertionError"
    write_json(ev / "status.json", result)
    print(json.dumps(result, indent=2))
    return 2


def cmd_cleanup(args: argparse.Namespace) -> int:
    repo = find_repo_root()
    if repo is None:
        print(json.dumps({"status": "blocked", "reason": "cwd is not repo root"}, indent=2))
        return 2
    if not args.run_id:
        print(json.dumps({"status": "blocked", "reason": "--run-id required"}, indent=2))
        return 2

    rt = runtime_dir(repo, args.run_id)
    removed = False
    if rt.exists():
        shutil.rmtree(rt)
        removed = True
    ev = evidence_dir(args.run_id)
    result = {
        "status": "pass",
        "run_id": args.run_id,
        "removed_runtime_dir": str(rt) if removed else None,
        "runtime_gone": not rt.exists(),
        "evidence_retained": str(ev) if ev.exists() else None,
        "evidence_exists_after_cleanup": ev.exists(),
    }
    print(json.dumps(result, indent=2))
    if rt.exists():
        return 1
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="verify-retry-export control CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_doctor = sub.add_parser("doctor", help="Read-only readiness check")
    p_doctor.set_defaults(func=cmd_doctor)

    p_first = sub.add_parser("first-export", help="Prove first export via real exporter CLI")
    p_first.add_argument("--run-id", default=None)
    p_first.set_defaults(func=cmd_first_export)

    p_retry = sub.add_parser(
        "retry-oracle",
        help="Run verify_runtime.py oracle; baseline 7-row mismatch is REPRODUCED",
    )
    p_retry.add_argument("--run-id", default=None)
    p_retry.set_defaults(func=cmd_retry_oracle)

    p_clean = sub.add_parser("cleanup", help="Remove .runtime/verify-<run-id>; keep evidence")
    p_clean.add_argument("--run-id", required=True)
    p_clean.set_defaults(func=cmd_cleanup)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
