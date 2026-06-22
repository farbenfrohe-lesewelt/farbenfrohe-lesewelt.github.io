import csv
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mention_radar import tailored_drafts as td


FIELDS = [
    "candidate_id",
    "name",
    "website",
    "seed_url",
    "relevant_page",
    "discovery_source",
    "page_title",
    "candidate_class",
    "score",
    "topic_fit",
    "audience_fit",
    "submission_permission",
    "permission_evidence",
    "evidence_url",
    "public_contact_method",
    "suggested_angle",
    "suggested_material",
    "fetched_at",
    "review_status",
    "notes",
    "contacted_at",
    "follow_up_at",
    "response",
    "publication_url",
]


def row(**kwargs):
    base = {field: "" for field in FIELDS}
    base.update(
        {
            "candidate_id": "abc123def456",
            "name": "Beispiel",
            "website": "https://example.com/",
            "seed_url": "https://example.com/",
            "relevant_page": "https://example.com/kontakt/",
            "page_title": "Beispiel Kontakt",
            "candidate_class": "A",
            "score": "75",
            "topic_fit": "4",
            "audience_fit": "16",
            "submission_permission": "ja",
            "permission_evidence": "Rezensionsexemplare und Buchvorstellungen fuer passende Ratgeber sind moeglich.",
            "evidence_url": "https://example.com/kontakt/",
            "public_contact_method": "https://example.com/kontakt/",
            "suggested_angle": "Baby und Katze",
            "suggested_material": "https://farbenfrohe-lesewelt.github.io/presse/ | https://www.amazon.de/dp/B0GTDN1458",
            "review_status": "new",
        }
    )
    base.update(kwargs)
    return base


class TailoredDraftsTest(unittest.TestCase):
    def write_csv(self, path, rows):
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(rows)

    def test_fragment_and_comment_urls_are_deduplicated(self):
        rows = [
            row(candidate_id="a1", website="https://mutter-und-sohn.blog/", relevant_page="https://mutter-und-sohn.blog/2024/05/04/buch/#comments"),
            row(candidate_id="a2", website="https://mutter-und-sohn.blog/", relevant_page="https://mutter-und-sohn.blog/2024/05/04/buch/#more-20435", score="70"),
        ]
        candidates = [td.CandidateRow(item) for item in rows]
        self.assertEqual(len(td.dedupe_candidates(candidates)), 1)

    def test_share_and_comment_links_are_not_contacts(self):
        candidate = td.CandidateRow(
            row(
                website="https://www.vom-taubertal.de/",
                public_contact_method="https://www.facebook.com/sharer/sharer.php?u=x; https://www.vom-taubertal.de/blog/kooperationen-mit-den-taubertalperser/; https://www.vom-taubertal.de/blog/#comments",
            )
        )
        self.assertEqual(td.best_contact_url(candidate), "https://www.vom-taubertal.de/blog/kooperationen-mit-den-taubertalperser/")

    def test_comment_anchor_is_not_contact(self):
        candidate = td.CandidateRow(
            row(
                website="https://nixenzauber.home.blog/",
                public_contact_method="https://nixenzauber.home.blog/post/#comment-2522; https://nixenzauber.home.blog/post/#comments",
                evidence_url="https://nixenzauber.home.blog/post/#comments",
            )
        )
        self.assertEqual(td.best_contact_url(candidate), "")

    def test_one_website_creates_at_most_one_ready_draft(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            csv_path = tmp_path / "candidates.csv"
            self.write_csv(csv_path, [row(candidate_id="a1"), row(candidate_id="a2", relevant_page="https://example.com/rezensionen/#comments")])
            _all_rows, unique, decisions = td.generate(csv_path, tmp_path / "out")
            self.assertEqual(len(unique), 1)
            self.assertEqual(sum(1 for decision in decisions if decision.status == td.READY), 1)

    def test_filename_contains_name_domain_and_candidate_id(self):
        candidate = td.CandidateRow(row(candidate_id="1d65e6ff06b8", name="Die Taubertalperser", website="https://www.vom-taubertal.de/"))
        filename = td.draft_filename(1, candidate)
        self.assertTrue(filename.startswith("01-die-taubertalper"))
        self.assertIn("vom-taubertal-de", filename)
        self.assertTrue(filename.endswith("-1d65e6ff06b8.md"))

    def test_incomplete_evidence_is_not_quoted(self):
        candidate = td.CandidateRow(row(permission_evidence="e: Pet Expo Beijing Buchvorstellungen Wenn ihr ein Buch habt", website="https://www.vom-taubertal.de/", name="Die Taubertalperser"))
        basis = td.personalization_basis(candidate)
        self.assertIn("Kooperationsseite", basis)
        self.assertNotIn("Pet Expo", basis)

    def test_ready_draft_has_at_most_two_links_and_file_only_for_ready(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            csv_path = tmp_path / "candidates.csv"
            self.write_csv(
                csv_path,
                [
                    row(candidate_id="ready1", website="https://cat.example/", name="Katzenblog", public_contact_method="https://cat.example/kooperation/", evidence_url="https://cat.example/kooperation/"),
                    row(candidate_id="manual1", website="https://manual.example/", public_contact_method="https://facebook.com/sharer/x"),
                ],
            )
            td.generate(csv_path, tmp_path / "out")
            ready_files = list((tmp_path / "out" / "ready").glob("*.md"))
            self.assertEqual(len(ready_files), 1)
            text = ready_files[0].read_text(encoding="utf-8")
            body = text.split("---", 2)[-1]
            self.assertLessEqual(td.link_count(body), 2)

    def test_taubertalperser_ready_clean_candidate(self):
        candidate = td.CandidateRow(
            row(
                candidate_id="1d65e6ff06b8",
                name="Die Taubertalperser",
                website="https://www.vom-taubertal.de/",
                relevant_page="https://www.vom-taubertal.de/blog/kooperationen-mit-den-taubertalperser/",
                evidence_url="https://www.vom-taubertal.de/blog/kooperationen-mit-den-taubertalperser/",
                public_contact_method="https://www.facebook.com/sharer/sharer.php?u=x; https://www.vom-taubertal.de/blog/kooperationen-mit-den-taubertalperser/",
                permission_evidence="e: Pet Expo Beijing Buchvorstellungen Wenn ihr ein Buch habt, das thematisch zu mir und meinem Blog passt, stelle ich es sehr gerne vor.",
                suggested_angle="Baby kommt, Katze bleibt",
            )
        )
        decision = td.decide(candidate, 50)
        self.assertEqual(decision.status, td.READY)
        self.assertEqual(decision.contact_url, "https://www.vom-taubertal.de/blog/kooperationen-mit-den-taubertalperser/")
        self.assertIn("Buchvorstellungen", decision.personalization_basis)

    def test_mutter_und_sohn_no_multiple_drafts_without_own_contact(self):
        rows = [
            row(candidate_id="m1", name="mutter-und-sohn.", website="https://mutter-und-sohn.blog/", public_contact_method="https://anchor.fm/foo; https://familiebleiben-podcast.podigee.io/23", suggested_angle="Gespraech ueber Familienalltag mit Baby und Katze"),
            row(candidate_id="m2", name="mutter-und-sohn.", website="https://mutter-und-sohn.blog/", relevant_page="https://mutter-und-sohn.blog/post/#comments", public_contact_method="https://anchor.fm/foo"),
        ]
        unique = td.dedupe_candidates([td.CandidateRow(item) for item in rows])
        decisions = [td.decide(item, 50) for item in unique]
        self.assertEqual(len(decisions), 1)
        self.assertEqual(decisions[0].status, td.MANUAL)

    def test_nixenzauber_uses_no_comment_links(self):
        candidate = td.CandidateRow(
            row(
                name="Buecher Mermaid Autismus",
                website="https://nixenzauber.home.blog/",
                relevant_page="https://nixenzauber.home.blog/2022/06/29/woher-bekommt-man-rezensionsexemplare/#comments",
                public_contact_method="https://nixenzauber.home.blog/post/#comment-2522; https://nixenzauber.home.blog/post/#comments",
                permission_evidence="Wie bekomme ich Rezensionsexemplare? Buecher Mermaid Autismus Merma",
            )
        )
        decision = td.decide(candidate, 50)
        self.assertEqual(decision.status, td.MANUAL)
        self.assertEqual(decision.contact_url, "")

    def test_adhs_journal_without_direct_fit_is_rejected(self):
        candidate = td.CandidateRow(
            row(
                name="ADHS-Journal",
                website="https://www.adhs-journal.de/",
                page_title="ADHS in Love Interview",
                permission_evidence="Interview mit Paartherapeutin und Fachbuchautorin",
                suggested_angle="Orientierung fuer Familien mit Haustier und Baby",
                topic_fit="4",
                audience_fit="16",
            )
        )
        self.assertEqual(td.decide(candidate, 50).status, td.REJECTED)


if __name__ == "__main__":
    unittest.main()
