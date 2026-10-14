import csv
import tempfile
import unittest
from pathlib import Path
from exporter import export_rows


class ExportTest(unittest.TestCase):
    def test_first_export(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "out.csv"
            export_rows("fixtures/first.csv", target)
            with target.open(newline="", encoding="utf-8") as stream:
                self.assertEqual(list(csv.DictReader(stream)), [
                    {"id": "1", "name": "Ada"},
                    {"id": "2", "name": "Lin"},
                ])


if __name__ == "__main__":
    unittest.main()
