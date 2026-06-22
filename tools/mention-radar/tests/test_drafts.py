import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mention_radar.classifier import classify
from mention_radar.drafts import STANDARD_CLOSING, create_draft
from mention_radar.models import FetchResult


class DraftTest(unittest.TestCase):
    def test_class_a_gets_limited_draft(self):
        candidate = classify(
            FetchResult(
                url="https://example.com/rezensionen",
                final_url="https://example.com/rezensionen",
                title="Beispiel Buchblog",
                text="Baby und Katze, Sachbuch Familie. Rezensionsexemplare willkommen für Buchvorstellungen.",
                fetched_at="2026-06-22T08:00:00+00:00",
                contact_methods=["https://example.com/presse"],
            )
        )
        draft = create_draft(candidate)
        self.assertIn("Andrea Blum ist die Autorin des Buches", draft)
        self.assertIn("Farbenfrohe Lesewelt Verlag", draft)
        self.assertIn(STANDARD_CLOSING, draft)
        self.assertLessEqual(len(draft.split()), 170)

    def test_class_b_gets_no_draft(self):
        candidate = classify(
            FetchResult(
                url="https://example.org/redaktion",
                final_url="https://example.org/redaktion",
                title="Elternmagazin",
                text="Baby und Katze im Familienalltag. Kontakt zur Redaktion.",
                fetched_at="2026-06-22T08:00:00+00:00",
                contact_methods=["https://example.org/redaktion"],
            )
        )
        self.assertEqual(candidate.candidate_class, "B")
        self.assertEqual(create_draft(candidate), "")

    def test_class_c_gets_no_draft(self):
        candidate = classify(
            FetchResult(
                url="https://example.net",
                final_url="https://example.net",
                title="Unpassend",
                text="Balkonpflanzen und Gartentipps.",
                fetched_at="2026-06-22T08:00:00+00:00",
            )
        )
        self.assertEqual(create_draft(candidate), "")


if __name__ == "__main__":
    unittest.main()
