import csv
import subprocess
import sys
import tempfile
from pathlib import Path

with tempfile.TemporaryDirectory() as directory:
    target = Path(directory) / "out.csv"
    for source in ["fixtures/first.csv", "fixtures/first.csv", "fixtures/next.csv"]:
        subprocess.run([
            sys.executable, "exporter.py", "--input", source, "--output", str(target)
        ], check=True)
    with target.open(newline="", encoding="utf-8") as stream:
        actual = list(csv.DictReader(stream))
    expected = [
        {"id": "1", "name": "Ada"},
        {"id": "2", "name": "Lin"},
        {"id": "3", "name": "Grace"},
    ]
    print("actual:", actual, flush=True)
    assert actual == expected, (actual, expected)
    print("PASS: retry and overlap preserve one row per id")
