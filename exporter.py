import argparse
import csv
from pathlib import Path


def export_rows(source, destination):
    with Path(source).open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    destination = Path(destination)
    has_header = destination.exists() and destination.stat().st_size > 0
    with destination.open("a", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=["id", "name"])
        if not has_header:
            writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    export_rows(args.input, args.output)
