import csv
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mention_radar.classifier import classify
from mention_radar.exporters import CANDIDATE_COLUMNS, export_all
from mention_radar.models import FetchResult


class ExporterTest(unittest.TestCase):
    def test_csv_columns_and_drafts_only_for_class_a(self):
        candidates = [
            classify(
                FetchResult(
                    url="https://example.com/rezensionen",
                    final_url="https://example.com/rezensionen",
                    title="Buchblog",
                    text="Baby und Katze, Haustier und Kind. Rezensionsexemplare willkommen.",
                    fetched_at="2026-06-22T08:00:00+00:00",
                    contact_methods=["https://example.com/presse"],
                )
            ),
            classify(
                FetchResult(
                    url="https://example.org/redaktion",
                    final_url="https://example.org/redaktion",
                    title="Eltern",
                    text="Baby und Katze, Haustier und Kind. Redaktion.",
                    fetched_at="2026-06-22T08:00:00+00:00",
                    contact_methods=["https://example.org/redaktion"],
                )
            ),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            root = export_all(candidates, tmp)
            with open(root / "candidates.csv", encoding="utf-8", newline="") as handle:
                reader = csv.DictReader(handle)
                self.assertEqual(reader.fieldnames, CANDIDATE_COLUMNS)
            drafts = list((Path(root) / "drafts").glob("*.md"))
            self.assertEqual(len(drafts), 1)
            self.assertTrue((Path(root) / "opportunities.md").exists())
            self.assertTrue((Path(root) / "excluded.csv").exists())


if __name__ == "__main__":
    unittest.main()
