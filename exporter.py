import argparse
import csv
from pathlib import Path


def export_rows(source, destination):
    with Path(source).open(newline="", encoding="utf-8") as stream:
        incoming = list(csv.DictReader(stream))
    destination = Path(destination)
    existing = []
    if destination.exists() and destination.stat().st_size > 0:
        with destination.open(newline="", encoding="utf-8") as stream:
            existing = list(csv.DictReader(stream))
    seen = {row["id"] for row in existing}
    new_rows = []
    for row in incoming:
        if row["id"] in seen:
            continue
        seen.add(row["id"])
        new_rows.append(row)
    if not new_rows:
        return
    has_header = destination.exists() and destination.stat().st_size > 0
    with destination.open("a", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=["id", "name"])
        if not has_header:
            writer.writeheader()
        writer.writerows(new_rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    export_rows(args.input, args.output)
