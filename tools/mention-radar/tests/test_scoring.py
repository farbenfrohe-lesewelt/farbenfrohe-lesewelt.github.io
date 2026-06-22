import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mention_radar.classifier import classify
from mention_radar.models import FetchResult


class ScoringTest(unittest.TestCase):
    def test_score_uses_no_external_metrics(self):
        fetch = FetchResult(
            url="https://example.com/rezensionen",
            final_url="https://example.com/rezensionen",
            title="Buchblog Ratgeber",
            text=(
                "Buchblog Ratgeber für Familie, Eltern, Baby und Katze. "
                "Rezensionsexemplare willkommen. Redaktionelle Beiträge und Rezensionen seit 2026. "
                "Baby und Katze, Katze und Baby, Haustier und Kind."
            ),
            fetched_at="2026-06-22T08:00:00+00:00",
            contact_methods=["https://example.com/presse"],
        )
        candidate = classify(fetch)
        self.assertGreaterEqual(candidate.score, 60)
        self.assertLessEqual(candidate.score, 100)

    def test_old_low_substance_page_gets_penalty(self):
        fetch = FetchResult(
            url="https://example.com/alt",
            final_url="https://example.com/alt",
            title="Alter Kurzbeitrag",
            text="Baby Katze Redaktion 2019.",
            fetched_at="2026-06-22T08:00:00+00:00",
            contact_methods=["https://example.com/kontakt"],
        )
        candidate = classify(fetch)
        self.assertLess(candidate.score, 50)


if __name__ == "__main__":
    unittest.main()
