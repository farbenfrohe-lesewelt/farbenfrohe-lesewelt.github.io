import csv
import re
import sys
import tempfile
import unittest
from pathlib import Path
from urllib.robotparser import RobotFileParser

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mention_radar.classifier import OWN_MATERIAL_URLS, classify
from mention_radar.crawler import MentionCrawler
from mention_radar.exporters import export_all
from mention_radar.history import apply_tracking, load_tracking, write_tracking
from mention_radar.models import FetchResult
from mention_radar.safety import DEFAULT_CONFIG, default_run_dir, read_feed_list


class FakeResponse:
    def __init__(self, url, html):
        self.url = url
        self.status_code = 200
        self.encoding = "utf-8"
        self.headers = {"content-type": "text/html; charset=utf-8"}
        self.html = html.encode("utf-8")

    def iter_content(self, chunk_size=65536):
        yield self.html


class MapSession:
    def __init__(self, pages):
        self.pages = pages
        self.headers = {}
        self.max_redirects = None
        self.requested = []

    def get(self, url, *args, **kwargs):
        self.requested.append(url)
        if url not in self.pages:
            raise RuntimeError(f"Unexpected URL: {url}")
        return FakeResponse(url, self.pages[url])


def make_crawler(pages, config=None, disallow=None):
    crawler = MentionCrawler.__new__(MentionCrawler)
    crawler.config = dict(DEFAULT_CONFIG)
    crawler.config["request_delay_seconds"] = 0
    if config:
        crawler.config.update(config)
    crawler.sleeper = lambda seconds: None
    crawler.clock = lambda: 1.0
    crawler.session = MapSession(pages)
    parser = RobotFileParser()
    lines = ["User-agent: *"]
    for path in disallow or []:
        lines.append(f"Disallow: {path}")
    if not disallow:
        lines.append("Allow: /")
    parser.parse(lines)
    crawler.robots_cache = {"https://example.com": parser}
    crawler.last_request_by_domain = {}
    crawler.pages_by_domain = {}
    return crawler


class WorkflowV11Test(unittest.TestCase):
    def test_own_material_links_are_current(self):
        self.assertNotIn("https://farbenfrohe-lesewelt.github.io/schwangerschaft/", OWN_MATERIAL_URLS)
        self.assertNotIn("https://farbenfrohe-lesewelt.github.io/baby/", OWN_MATERIAL_URLS)
        self.assertIn("https://farbenfrohe-lesewelt.github.io/pinterest/toxoplasmose-katze-schwangerschaft/", OWN_MATERIAL_URLS)
        candidate = classify(
            FetchResult(
                url="https://example.com/rezensionen",
                final_url="https://example.com/rezensionen",
                title="Toxoplasmose Buchblog",
                text="Toxoplasmose Schwangerschaft Katze. Rezensionsexemplare willkommen.",
                fetched_at="2026-06-22T08:00:00+00:00",
            )
        )
        self.assertIn("pinterest/toxoplasmose-katze-schwangerschaft", candidate.suggested_material)

    def test_controlled_follow_of_matching_internal_links(self):
        pages = {
            "https://example.com/": '<html><title>Start</title><body><a href="/presse">Presse</a><a href="https://other.example/presse">Extern</a></body></html>',
            "https://example.com/presse": "<html><title>Presse</title><body>Baby und Katze. Rezensionsexemplare willkommen.</body></html>",
        }
        crawler = make_crawler(pages)
        results = crawler.fetch_seed_with_follow("https://example.com/")
        self.assertEqual([item.discovery_source for item in results], ["seed", "followed"])
        self.assertEqual(crawler.session.requested, ["https://example.com/", "https://example.com/presse"])

    def test_external_links_are_not_followed(self):
        pages = {
            "https://example.com/": '<html><title>Start</title><body><a href="https://other.example/presse">Presse extern</a></body></html>',
        }
        crawler = make_crawler(pages)
        results = crawler.fetch_seed_with_follow("https://example.com/")
        self.assertEqual(len(results), 1)
        self.assertEqual(crawler.session.requested, ["https://example.com/"])

    def test_domain_limit_applies_to_followed_pages(self):
        pages = {
            "https://example.com/": '<html><title>Start</title><body><a href="/presse">Presse</a></body></html>',
            "https://example.com/presse": "<html><title>Presse</title><body>Baby und Katze.</body></html>",
        }
        crawler = make_crawler(pages, {"maximum_pages_per_domain": 1})
        results = crawler.fetch_seed_with_follow("https://example.com/")
        self.assertEqual(len(results), 2)
        self.assertIn("Domain-Limit", results[1].skipped_reason)

    def test_robots_txt_applies_to_followed_pages(self):
        pages = {
            "https://example.com/": '<html><title>Start</title><body><a href="/presse">Presse</a></body></html>',
        }
        crawler = make_crawler(pages, disallow=["/presse"])
        results = crawler.fetch_seed_with_follow("https://example.com/")
        self.assertEqual(len(results), 2)
        self.assertIn("robots.txt", results[1].skipped_reason)

    def test_tracking_values_are_preserved(self):
        candidate = classify(
            FetchResult(
                url="https://example.com/rezensionen",
                final_url="https://example.com/rezensionen",
                title="Buchblog",
                text="Baby und Katze. Rezensionsexemplare willkommen.",
                fetched_at="2026-06-22T08:00:00+00:00",
            )
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "tracking.csv"
            with open(path, "w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=["candidate_id", "review_status", "notes", "contacted_at", "follow_up_at", "response", "publication_url"])
                writer.writeheader()
                writer.writerow({"candidate_id": candidate.candidate_id, "review_status": "manual_review", "notes": "Manuell gesetzt", "contacted_at": "", "follow_up_at": "", "response": "", "publication_url": ""})
            tracking = load_tracking(path)
            new_count, known_count = apply_tracking([candidate], tracking)
            self.assertEqual((new_count, known_count), (0, 1))
            self.assertEqual(candidate.review_status, "manual_review")
            self.assertEqual(candidate.notes, "Manuell gesetzt")
            write_tracking([candidate], path, tracking)
            self.assertIn("Manuell gesetzt", path.read_text(encoding="utf-8"))

    def test_default_run_dir_is_dated(self):
        run_dir = default_run_dir("local-data/mention-radar")
        self.assertRegex(str(run_dir).replace("\\", "/"), r"local-data/mention-radar/runs/\d{4}-\d{2}-\d{2}_\d{6}$")

    def test_feed_list_ignores_comments_and_blank_lines(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "feeds.txt"
            path.write_text("# Kommentar\n\nhttps://example.com/feed.xml\nhttps://example.org/rss\n", encoding="utf-8")
            self.assertEqual(read_feed_list(path), ["https://example.com/feed.xml", "https://example.org/rss"])

    def test_no_old_drafts_are_copied_between_runs(self):
        candidate = classify(
            FetchResult(
                url="https://example.com/rezensionen",
                final_url="https://example.com/rezensionen",
                title="Buchblog",
                text="Baby und Katze. Rezensionsexemplare willkommen.",
                fetched_at="2026-06-22T08:00:00+00:00",
            )
        )
        excluded = classify(
            FetchResult(
                url="https://example.com/unpassend",
                final_url="https://example.com/unpassend",
                title="Garten",
                text="Balkonpflanzen.",
                fetched_at="2026-06-22T08:00:00+00:00",
            )
        )
        with tempfile.TemporaryDirectory() as tmp:
            run1 = Path(tmp) / "runs" / "one"
            run2 = Path(tmp) / "runs" / "two"
            export_all([candidate], run1)
            export_all([excluded], run2)
            self.assertEqual(len(list((run1 / "drafts").glob("*.md"))), 1)
            self.assertEqual(len(list((run2 / "drafts").glob("*.md"))), 0)

    def test_runner_supports_new_inputs_and_no_install(self):
        runner = (Path(__file__).resolve().parents[1] / "run-mention-radar.ps1").read_text(encoding="utf-8")
        for token in ["$InputCsv", "$ImportCsv", "[string[]]$Url", "[string[]]$Feed", "$FeedList", "$NoInstall"]:
            self.assertIn(token, runner)
        self.assertIn("--feed-list", runner)
        self.assertIn("-not $NoInstall", runner)

    def test_no_real_contact_data_in_tool_files(self):
        root = Path(__file__).resolve().parents[1]
        combined = "\n".join(
            path.read_text(encoding="utf-8", errors="ignore")
            for path in root.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts and ".venv" not in path.parts
        )
        emails = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", combined)
        self.assertEqual(emails, [])


if __name__ == "__main__":
    unittest.main()
