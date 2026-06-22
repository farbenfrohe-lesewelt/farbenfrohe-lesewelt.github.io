import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mention_radar.classifier import classify
from mention_radar.models import FetchResult


class ClassifierTest(unittest.TestCase):
    def test_class_a_requires_visible_permission(self):
        fetch = FetchResult(
            url="https://example.com/rezensionen",
            final_url="https://example.com/rezensionen",
            title="Beispiel Buchblog",
            text="Baby und Katze, Haustier und Kind. Rezensionsexemplare willkommen für Buchvorstellungen 2026.",
            fetched_at="2026-06-22T08:00:00+00:00",
            contact_methods=["https://example.com/presse"],
        )
        candidate = classify(fetch)
        self.assertEqual(candidate.candidate_class, "A")
        self.assertIn("Rezensionsexemplare willkommen", candidate.permission_evidence)
        self.assertEqual(candidate.submission_permission, "ja")

    def test_class_b_has_no_explicit_permission(self):
        fetch = FetchResult(
            url="https://example.org/redaktion",
            final_url="https://example.org/redaktion",
            title="Elternmagazin",
            text="Schwangerschaft, Baby, Katze und Familienalltag. Kontakt zur Redaktion.",
            fetched_at="2026-06-22T08:00:00+00:00",
            contact_methods=["https://example.org/redaktion"],
        )
        candidate = classify(fetch)
        self.assertEqual(candidate.candidate_class, "B")
        self.assertEqual(candidate.submission_permission, "nein")

    def test_class_c_without_fit(self):
        fetch = FetchResult(
            url="https://example.net",
            final_url="https://example.net",
            title="Garten",
            text="Ein kurzer Text über Balkonpflanzen.",
            fetched_at="2026-06-22T08:00:00+00:00",
        )
        candidate = classify(fetch)
        self.assertEqual(candidate.candidate_class, "C")

    def test_link_selling_is_excluded(self):
        fetch = FetchResult(
            url="https://example.com/angebote",
            final_url="https://example.com/angebote",
            title="Angebot",
            text="Baby und Katze. Linkverkauf und garantierte Veröffentlichung für Partner.",
            fetched_at="2026-06-22T08:00:00+00:00",
        )
        candidate = classify(fetch)
        self.assertEqual(candidate.candidate_class, "D")
        self.assertEqual(candidate.score, 0)


if __name__ == "__main__":
    unittest.main()
