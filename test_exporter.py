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

    def test_retry_same_input_does_not_change_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "out.csv"
            export_rows("fixtures/first.csv", target)
            before = target.read_bytes()
            export_rows("fixtures/first.csv", target)
            self.assertEqual(target.read_bytes(), before)

    def test_overlap_keeps_first_id_and_adds_new_once(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "out.csv"
            export_rows("fixtures/first.csv", target)
            export_rows("fixtures/first.csv", target)
            export_rows("fixtures/next.csv", target)
            text = target.read_text(encoding="utf-8")
            self.assertTrue(text.startswith("id,name\n"))
            with target.open(newline="", encoding="utf-8") as stream:
                self.assertEqual(list(csv.DictReader(stream)), [
                    {"id": "1", "name": "Ada"},
                    {"id": "2", "name": "Lin"},
                    {"id": "3", "name": "Grace"},
                ])


if __name__ == "__main__":
    unittest.main()
