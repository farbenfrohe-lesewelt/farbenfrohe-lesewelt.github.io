import unittest
import sys
from pathlib import Path
from urllib.robotparser import RobotFileParser

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mention_radar.crawler import MentionCrawler
from mention_radar.safety import DEFAULT_CONFIG, dedupe_urls, load_config


class FakeResponse:
    def __init__(self, chunks, url="https://example.com/page", status_code=200):
        self._chunks = chunks
        self.url = url
        self.status_code = status_code
        self.encoding = "utf-8"
        self.headers = {"content-type": "text/html; charset=utf-8"}

    def iter_content(self, chunk_size=65536):
        yield from self._chunks


class FakeSession:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.headers = {}
        self.max_redirects = None
        self.calls = 0

    def get(self, *args, **kwargs):
        self.calls += 1
        if self.error:
            raise self.error
        return self.response


def crawler_without_init(config=None):
    crawler = MentionCrawler.__new__(MentionCrawler)
    crawler.config = dict(DEFAULT_CONFIG)
    if config:
        crawler.config.update(config)
    crawler.sleeper = lambda seconds: None
    crawler.clock = lambda: 1.0
    crawler.session = FakeSession(FakeResponse([b"<html><title>Ok</title><body>Baby und Katze</body></html>"]))
    crawler.robots_cache = {}
    crawler.last_request_by_domain = {}
    crawler.pages_by_domain = {}
    return crawler


class SafetyTest(unittest.TestCase):
    def test_robots_txt_is_respected(self):
        crawler = crawler_without_init()
        parser = RobotFileParser()
        parser.parse(["User-agent: *", "Disallow: /blocked"])
        crawler.robots_cache["https://example.com"] = parser
        result = crawler.fetch("https://example.com/blocked/page")
        self.assertIn("robots.txt", result.skipped_reason)
        self.assertEqual(crawler.session.calls, 0)

    def test_rate_limit_per_domain(self):
        waits = []
        times = iter([11.0, 13.0])
        crawler = crawler_without_init({"request_delay_seconds": 3})
        crawler.sleeper = waits.append
        crawler.clock = lambda: next(times)
        crawler.last_request_by_domain["example.com"] = 10.0
        crawler.wait_for_domain("example.com")
        self.assertEqual(waits, [2.0])

    def test_html_size_limit(self):
        crawler = crawler_without_init({"maximum_html_bytes": 5})
        parser = RobotFileParser()
        parser.parse(["User-agent: *", "Allow: /"])
        crawler.robots_cache["https://example.com"] = parser
        crawler.session = FakeSession(FakeResponse([b"1234", b"5678"]))
        result = crawler.fetch("https://example.com/page")
        self.assertIn("Größenlimit", result.skipped_reason)

    def test_redirect_limit_is_configured(self):
        if getattr(MentionCrawler, "__init__", None) is None:
            self.skipTest("Crawler nicht verfügbar")
        try:
            crawler = MentionCrawler({**DEFAULT_CONFIG, "maximum_redirects": 2})
        except RuntimeError:
            self.skipTest("requests nicht installiert")
        self.assertEqual(crawler.session.max_redirects, 2)

    def test_dedupe_urls_merges_duplicates(self):
        urls = dedupe_urls(["https://Example.com/a#x", "https://example.com/a", "example.org"])
        self.assertEqual(urls, ["https://example.com/a", "https://example.org/"])

    def test_tool_works_without_api_key(self):
        config = load_config()
        self.assertFalse(config["official_search_api"]["enabled"])

    def test_network_errors_are_recorded(self):
        crawler = crawler_without_init()
        parser = RobotFileParser()
        parser.parse(["User-agent: *", "Allow: /"])
        crawler.robots_cache["https://example.com"] = parser
        crawler.session = FakeSession(error=RuntimeError("network down"))
        result = crawler.fetch("https://example.com/page")
        self.assertIn("RuntimeError", result.error)

    def test_no_unwanted_capabilities_or_identity_terms_in_tool_files(self):
        root = Path(__file__).resolve().parents[1]
        combined = "\n".join(
            path.read_text(encoding="utf-8", errors="ignore")
            for path in root.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts
        )
        disallowed = [
            "sm" + "tplib",
            "send" + "mail",
            "SM" + "TP",
            "sele" + "nium",
            "play" + "wright",
            "submit" + "(",
            "google.com" + "/search",
            "Pseudo" + "nym",
            "Veröffentlichungs" + "name",
            "Autoren" + "pseudo" + "nym",
            "hinter Andrea" + " Blum",
        ]
        for term in disallowed:
            self.assertNotIn(term.lower(), combined.lower())

    def test_fixtures_have_no_private_mail_domains(self):
        fixtures = Path(__file__).resolve().parent / "fixtures"
        combined = "\n".join(path.read_text(encoding="utf-8", errors="ignore") for path in fixtures.rglob("*") if path.is_file())
        self.assertNotRegex(combined, r"@[a-z0-9.-]+\.[a-z]{2,}")


if __name__ == "__main__":
    unittest.main()
