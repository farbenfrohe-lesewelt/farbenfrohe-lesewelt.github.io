import csv
import io
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from urllib.error import HTTPError
from urllib.robotparser import RobotFileParser

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from seed_crawler import app


class SeedCrawlerTest(unittest.TestCase):
    def setUp(self):
        self.tool_root = Path(__file__).resolve().parents[1]
        self.blocklists = app.Blocklists(self.tool_root / "config")
        self.scoring = app.load_scoring(self.tool_root / "config" / "scoring.yaml")

    def page(self, url, title, text, dates=None, links=None, site_name=""):
        return app.PageSnapshot(
            requested_url=url,
            final_url=url,
            status_code=200,
            title=title,
            site_name=site_name,
            headings=[title],
            text=text,
            links=links or [],
            dates=dates or [],
            fetched_at=app.now_iso(),
        )

    def test_csv_output_uses_comma_quotes_notes_and_utf8(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "seeds.csv"
            candidate = app.Candidate(
                candidate_url="https://example.com/",
                final_seed_url="https://example.com/rezensionsexemplare/",
                domain="example.com",
                name="Buecher & Familie",
                category="book_blog",
                discovery_source="crawler:file:book_blog:import01",
                query_id="import01",
                total_score=91,
                notes="Buchblog; Notiz mit Komma, korrekt; Score 91/100",
                status="accepted",
            )
            app.write_seed_csv(path, [candidate], overwrite=True)
            raw = path.read_text(encoding="utf-8")
            self.assertTrue(raw.startswith("url,name,source,notes"))
            self.assertIn('"Buchblog; Notiz mit Komma, korrekt; Score 91/100"', raw)
            with path.open("r", encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(rows[0]["name"], "Buecher & Familie")

    def test_url_normalization_removes_tracking_fragment_www_and_standard_port(self):
        normalized = app.normalize_url("HTTPS://WWW.Example.COM:443/a//b/?utm_source=x&keep=1&fbclid=y#part")
        self.assertEqual(normalized, "https://www.example.com/a/b/?keep=1")
        self.assertEqual(app.registered_domain(normalized), "example.com")

    def test_file_import_mode_reads_search_results(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "results.csv"
            path.write_text("url,title,category\nhttps://example.com/?utm_medium=x,Test,book_blog\n", encoding="utf-8")
            provider = app.FileSearchProvider(path)
            results = provider.search(app.QuerySpec("book_blog", "import01", "file-import"), 10)
            self.assertEqual(results[0].url, "https://example.com/")
            self.assertEqual(results[0].category_hint, "book_blog")

    def test_domain_deduplication_and_best_subpage_selection(self):
        pages = [
            self.page("https://blog.example/", "Start", "Familie Katze Kontakt Impressum", ["2026-03-01"]),
            self.page(
                "https://blog.example/rezensionsexemplare/",
                "Rezensionsexemplare",
                "Buchblog Sachbuch Ratgeber Familie Katze Rezensionsexemplare willkommen Kontakt Impressum Autorin.",
                ["2026-05-01"],
            ),
        ]
        result = app.SearchResult("https://blog.example/", provider="file", query_id="import01", category_hint="book_blog")
        candidate = app.evaluate_domain(result, pages, self.blocklists, self.scoring, 65)
        self.assertEqual(candidate.final_seed_url, "https://blog.example/rezensionsexemplare/")
        self.assertEqual(candidate.category, "book_blog")
        self.assertEqual(candidate.status, "accepted")

    def test_blocklists_exclude_social_search_shop_and_login_urls(self):
        self.assertIn("blocked_domain", self.blocklists.blocked_domain_reason("https://www.youtube.com/@x"))
        self.assertIn("blocked_domain", self.blocklists.blocked_domain_reason("https://www.google.com/search?q=x"))
        self.assertIn("blocked_url_pattern", self.blocklists.blocked_url_reason("https://example.com/login"))
        self.assertIn("blocked_url_pattern", self.blocklists.blocked_url_reason("https://example.com/shop/product"))

    def test_category_assignment_prefers_review_policy_for_cat_book_blog(self):
        text = app.slug_text("Katzenblog Buchblog Rezensionsexemplare Sachbuch Ratgeber Kontakt")
        self.assertEqual(app.assign_category("cat_pet_media", text, "https://example.com/"), "book_blog")
        podcast_text = app.slug_text("Elternpodcast Interview Gast Bewerbung Kontakt")
        self.assertEqual(app.assign_category("parent_family_media", podcast_text, "https://example.org/"), "podcast")

    def test_scoring_detects_review_and_podcast_guest_signals(self):
        review_score, review_signal = app.score_editorial("book_blog", app.slug_text("Rezensionsexemplare willkommen"))
        guest_score, guest_signal = app.score_editorial("podcast", app.slug_text("Podcastgast werden Interview"))
        self.assertEqual(review_score, 25)
        self.assertIn("Rezensionsexemplare", review_signal)
        self.assertEqual(guest_score, 20)
        self.assertIn("Podcast", guest_signal)

    def test_min_score_rejects_weak_candidate(self):
        pages = [self.page("https://weak.example/", "Start", "Kontakt Impressum etwas Text.", [])]
        result = app.SearchResult("https://weak.example/", provider="file", query_id="import01", category_hint="book_blog")
        candidate = app.evaluate_domain(result, pages, self.blocklists, self.scoring, 65)
        self.assertEqual(candidate.status, "rejected")
        self.assertIn("score_below_min", candidate.rejection_reason)

    def test_quota_logic_scales_target_and_keeps_category_order(self):
        quotas = app.compute_quotas({"book_blog": 30, "cat_pet_media": 30, "parent_family_media": 25, "podcast": 15}, 10)
        self.assertEqual(sum(quotas.values()), 10)
        self.assertEqual(quotas["book_blog"], 3)
        candidates = []
        for index, category in enumerate(app.CATEGORY_ORDER):
            candidates.append(
                app.Candidate(
                    "https://x.example/",
                    f"https://{category}.example/",
                    f"{category}.example",
                    category,
                    category,
                    f"crawler:file:{category}:import01",
                    "import01",
                    total_score=90 - index,
                    status="accepted",
                )
            )
        selected, _missing = app.select_final(candidates, quotas, 4)
        self.assertEqual([item.category for item in selected], app.CATEGORY_ORDER)

    def test_robots_rules_and_page_limit_are_respected(self):
        crawler = app.ControlledCrawler(self.blocklists, app.Cache(Path("unused"), enabled=False), max_pages_per_domain=1)
        parser = RobotFileParser()
        parser.parse(["User-agent: *", "Disallow: /blocked", "Allow: /"])
        crawler.robots["https://example.com"] = parser
        self.assertFalse(crawler.can_fetch("https://example.com/blocked"))
        self.assertTrue(crawler.can_fetch("https://example.com/open"))

        class FakeCrawler(app.ControlledCrawler):
            def fetch(self, url):
                return app.PageSnapshot(
                    url,
                    url,
                    text="Kontakt Impressum Katzenblog",
                    links=[("https://example.com/rezensionsexemplare/", "Rezensionsexemplare")],
                )

        fake = FakeCrawler(self.blocklists, app.Cache(Path("unused"), enabled=False), max_pages_per_domain=1)
        self.assertEqual(len(fake.crawl_domain("https://example.com/")), 1)

    def test_timeout_or_network_error_is_recorded(self):
        class TimeoutOpener:
            def open(self, *args, **kwargs):
                raise TimeoutError("slow")

        crawler = app.ControlledCrawler(self.blocklists, app.Cache(Path("unused"), enabled=False))
        parser = RobotFileParser()
        parser.parse(["User-agent: *", "Allow: /"])
        crawler.robots["https://example.com"] = parser
        crawler.opener = TimeoutOpener()
        result = crawler.fetch("https://example.com/")
        self.assertIn("TimeoutError", result.error)

    def test_inactive_website_gets_low_activity(self):
        old_page = self.page("https://old.example/", "Alt", "Buchblog Katze Kontakt Impressum", ["2020-01-01"])
        score, signal = app.score_activity([old_page])
        self.assertEqual(score, 0)
        self.assertIn("Monaten", signal)

    def test_validation_reports_duplicate_domain_and_extra_columns(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "seeds.csv"
            path.write_text(
                "url,name,source,notes,extra\n"
                "https://example.com/,A,crawler:file:book_blog:import01,ok,x\n"
                "https://www.example.com/b,B,crawler:file:book_blog:import02,ok,x\n",
                encoding="utf-8",
            )
            errors = app.validate_seed_csv(path, target=100, blocklists=self.blocklists)
            self.assertTrue(any("Header falsch" in error for error in errors))
            self.assertTrue(any("Domain mehrfach" in error for error in errors))

    def test_negative_terms_reject_dofollow_and_social_platforms(self):
        pages = [
            self.page(
                "https://spam.example/",
                "SEO",
                "Katzenblog Kontakt Impressum Dofollow-Link kaufen garantierte Veroeffentlichung.",
                ["2026-04-01"],
            )
        ]
        result = app.SearchResult("https://spam.example/", provider="file", query_id="import01", category_hint="cat_pet_media")
        candidate = app.evaluate_domain(result, pages, self.blocklists, self.scoring, 65)
        self.assertEqual(candidate.status, "rejected")
        self.assertIn("negative_term", candidate.rejection_reason)

    def test_env_file_is_loaded_without_overriding_os_environment(self):
        with tempfile.TemporaryDirectory() as tmp:
            env_file = Path(tmp) / ".env"
            env_file.write_text(
                "BRAVE_SEARCH_API_KEY=from-file\nBRAVE_SEARCH_COUNTRY=at\nBRAVE_SEARCH_LANG=de\n",
                encoding="utf-8",
            )
            old = {key: os.environ.get(key) for key in app.SEED_CRAWLER_ENV_KEYS}
            try:
                os.environ["BRAVE_SEARCH_API_KEY"] = "from-os"
                os.environ.pop("BRAVE_SEARCH_COUNTRY", None)
                self.assertTrue(app.load_env_file(env_file))
                self.assertEqual(os.environ["BRAVE_SEARCH_API_KEY"], "from-os")
                self.assertEqual(os.environ["BRAVE_SEARCH_COUNTRY"], "at")
            finally:
                for key, value in old.items():
                    if value is None:
                        os.environ.pop(key, None)
                    else:
                        os.environ[key] = value

    def test_api_key_is_redacted_from_errors(self):
        old = os.environ.get("BRAVE_SEARCH_API_KEY")
        try:
            os.environ["BRAVE_SEARCH_API_KEY"] = "secret-token-123"
            self.assertNotIn("secret-token-123", app.redact_secrets("failed secret-token-123"))
        finally:
            if old is None:
                os.environ.pop("BRAVE_SEARCH_API_KEY", None)
            else:
                os.environ["BRAVE_SEARCH_API_KEY"] = old

    def test_missing_brave_key_message_is_clear(self):
        old = os.environ.get("BRAVE_SEARCH_API_KEY")
        try:
            os.environ.pop("BRAVE_SEARCH_API_KEY", None)
            with self.assertRaisesRegex(ValueError, "BRAVE_SEARCH_API_KEY fehlt. Lege ihn als Umgebungsvariable oder in tools/seed-crawler/.env ab."):
                app.BraveSearchProvider("")
        finally:
            if old is not None:
                os.environ["BRAVE_SEARCH_API_KEY"] = old

    def test_private_or_local_network_targets_are_blocked(self):
        for url in ["http://localhost/", "http://127.0.0.1/", "http://10.0.0.1/", "ftp://example.com/"]:
            safe, reason = app.is_safe_public_url(url)
            self.assertFalse(safe, url)
            self.assertTrue(reason)

    def test_malformed_url_ports_and_ipv6_are_rejected(self):
        cases = [
            ("https://example.org:99999/path", "invalid_port"),
            ("https://example.org:-1/path", "invalid_port"),
            ("https://example.org:notaport/path", "invalid_port"),
            ("https://[::1/path", "url_parse_error"),
        ]
        for url, reason in cases:
            with self.subTest(url=url):
                normalized, actual_reason = app.normalize_url_with_reason(url)
                self.assertEqual(normalized, "")
                self.assertEqual(actual_reason, reason)
                safe, safe_reason = app.is_safe_public_url(url)
                self.assertFalse(safe)
                self.assertEqual(safe_reason, reason)

    def test_url_with_credentials_is_rejected(self):
        normalized, reason = app.normalize_url_with_reason("https://user:password@example.org/path")
        self.assertEqual(normalized, "")
        self.assertEqual(reason, "credentials_in_url")
        safe, safe_reason = app.is_safe_public_url("https://user:password@example.org/path")
        self.assertFalse(safe)
        self.assertEqual(safe_reason, "credentials_in_url")

    def test_redirect_to_private_target_is_blocked(self):
        class RedirectOpener:
            def open(self, request, *args, **kwargs):
                raise HTTPError(request.full_url, 302, "Found", {"Location": "http://127.0.0.1/private"}, None)

        crawler = app.ControlledCrawler(self.blocklists, app.Cache(Path("unused"), enabled=False))
        parser = RobotFileParser()
        parser.parse(["User-agent: *", "Allow: /"])
        crawler.robots["https://example.com"] = parser
        crawler.opener = RedirectOpener()
        result = crawler.fetch("https://example.com/")
        self.assertIn("private_or_local_host", result.skipped_reason)

    def test_invalid_redirect_url_is_blocked(self):
        class RedirectOpener:
            def open(self, request, *args, **kwargs):
                raise HTTPError(request.full_url, 302, "Found", {"Location": "https://example.org:99999/private"}, None)

        crawler = app.ControlledCrawler(self.blocklists, app.Cache(Path("unused"), enabled=False))
        parser = RobotFileParser()
        parser.parse(["User-agent: *", "Allow: /"])
        crawler.robots["https://example.com"] = parser
        crawler.opener = RedirectOpener()
        result = crawler.fetch("https://example.com/")
        self.assertEqual(result.skipped_reason, "redirect_invalid_port")

    def test_invalid_canonical_url_is_ignored(self):
        page = app.parse_html(
            '<html><head><link rel="canonical" href="https://example.org:99999/bad"></head><body><h1>Ok</h1>Kontakt Impressum Katze</body></html>',
            "https://example.org/",
        )
        self.assertEqual(page.canonical_url, "")
        self.assertEqual(page.text.startswith("Ok"), True)

    def test_pilot_quota_is_3_3_2_2_and_max_ten(self):
        candidates = []
        for category, count in app.PILOT_QUOTAS.items():
            for index in range(count + 2):
                candidates.append(
                    app.Candidate(
                        f"https://{category}{index}.example/",
                        f"https://{category}{index}.example/",
                        f"{category}{index}.example",
                        f"{category}{index}",
                        category,
                        f"crawler:file:{category}:import01",
                        "import01",
                        total_score=95 - index,
                        status="accepted",
                    )
                )
        selected, missing = app.select_final(candidates, app.PILOT_QUOTAS, app.PILOT_TARGET)
        self.assertEqual(len(selected), 10)
        self.assertEqual({category: sum(1 for item in selected if item.category == category) for category in app.CATEGORY_ORDER}, app.PILOT_QUOTAS)
        self.assertEqual(sum(missing.values()), 0)

    def test_min_score_is_not_lowered_to_fill_pilot(self):
        weak = [
            app.Candidate(
                "https://weak.example/",
                "https://weak.example/",
                "weak.example",
                "Weak",
                "book_blog",
                "crawler:file:book_blog:import01",
                "import01",
                total_score=64,
                status="rejected",
            )
        ]
        selected, missing = app.select_final(weak, app.PILOT_QUOTAS, app.PILOT_TARGET)
        self.assertEqual(selected, [])
        self.assertGreater(sum(missing.values()), 0)

    def test_pilot_summary_is_created_without_email_addresses(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "pilot_summary.md"
            candidate = app.Candidate(
                "https://example.com/",
                "https://example.com/",
                "example.com",
                "Pilot",
                "book_blog",
                "crawler:file:book_blog:import01",
                "import01",
                total_score=88,
                editorial_signal="Rezensionsexemplare ausdruecklich moeglich",
                activity_signal="letzter Inhalt vor 1 Monaten",
                notes="Buchblog; Kontakt test@example.com; Score 88/100",
                status="accepted",
            )
            app.write_pilot_summary(path, {"raw_url_count": 1, "checked_domains": 1, "estimated_search_api_requests": 1}, [candidate], [candidate])
            text = path.read_text(encoding="utf-8")
            self.assertIn("Akzeptierte Seeds", text)
            self.assertNotIn("test@example.com", text)

    def test_doctor_does_not_modify_productive_seed_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            seed_path = Path(tmp) / "seeds.csv"
            seed_path.write_text("url,name,source,notes\n", encoding="utf-8")
            old_dir = app.DEFAULT_LOCAL_DATA_DIR
            try:
                app.DEFAULT_LOCAL_DATA_DIR = Path(tmp)
                old_key = os.environ.get("BRAVE_SEARCH_API_KEY")
                os.environ.pop("BRAVE_SEARCH_API_KEY", None)
                out = io.StringIO()
                with redirect_stdout(out):
                    code = app.doctor(type("Args", (), {"provider": "brave"})())
                self.assertEqual(code, 2)
                self.assertEqual(seed_path.read_text(encoding="utf-8"), "url,name,source,notes\n")
                self.assertIn("BRAVE_SEARCH_API_KEY fehlt", out.getvalue())
            finally:
                app.DEFAULT_LOCAL_DATA_DIR = old_dir
                if old_key is not None:
                    os.environ["BRAVE_SEARCH_API_KEY"] = old_key

    def test_fixture_pilot_writes_only_isolated_output_and_keeps_productive_seed(self):
        class FakeCrawler:
            def __init__(self, *args, **kwargs):
                pass

            def crawl_domain(self, url):
                host = app.registered_domain(url).split(".")[0]
                if host.startswith("book"):
                    category_text = "Buchblog Sachbuch Ratgeber Rezensionsexemplare willkommen Familie Katze Kontakt Impressum Autorin"
                elif host.startswith("cat"):
                    category_text = "Katzenblog Haustier Katze Magazin Redaktion Presse Kontakt Impressum Autor"
                elif host.startswith("family"):
                    category_text = "Elternblog Familie Baby Schwangerschaft Gastbeitrag Themenvorschlag Kontakt Impressum Autorin"
                else:
                    category_text = "Elternpodcast Podcast Interview Podcastgast Familie Kontakt Impressum Episoden Redaktion"
                return [self_page(url, "Pilot", category_text)]

            errors = []

        def self_page(url, title, text):
            return app.PageSnapshot(url, url, 200, title, "Pilot", [title], text, [], "", ["2026-05-01"], "", "", app.now_iso())

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            search_csv = tmp_path / "results.csv"
            rows = ["url,title,category,query_id"]
            for category, prefix, count in [
                ("book_blog", "book", 4),
                ("cat_pet_media", "cat", 4),
                ("parent_family_media", "family", 3),
                ("podcast", "podcast", 3),
            ]:
                for index in range(count):
                    rows.append(f"https://{prefix}{index}.example/,Pilot,{category},import01")
            search_csv.write_text("\n".join(rows) + "\n", encoding="utf-8")
            output_dir = tmp_path / "pilot-10"
            product_seed = tmp_path / "seeds.csv"
            product_seed.write_text("url,name,source,notes\nhttps://old.example/,Old,manual,keep\n", encoding="utf-8")
            old_crawler = app.ControlledCrawler
            old_dir = app.DEFAULT_LOCAL_DATA_DIR
            try:
                app.ControlledCrawler = FakeCrawler
                app.DEFAULT_LOCAL_DATA_DIR = tmp_path
                args = type(
                    "Args",
                    (),
                    {
                        "provider": "file",
                        "output_dir": str(output_dir),
                        "search_results": str(search_csv),
                        "overwrite": False,
                        "resume": False,
                        "verbose": False,
                    },
                )()
                self.assertEqual(app.pilot(args), 0)
                self.assertTrue((output_dir / "seeds.csv").exists())
                self.assertTrue((output_dir / "seed_audit.csv").exists())
                self.assertTrue((output_dir / "run_report.json").exists())
                self.assertTrue((output_dir / "pilot_summary.md").exists())
                self.assertIn("old.example", product_seed.read_text(encoding="utf-8"))
                with (output_dir / "seeds.csv").open("r", encoding="utf-8", newline="") as handle:
                    self.assertLessEqual(len(list(csv.DictReader(handle))), 10)
            finally:
                app.ControlledCrawler = old_crawler
                app.DEFAULT_LOCAL_DATA_DIR = old_dir

    def test_invalid_brave_result_is_rejected_without_aborting_valid_results(self):
        class FakeProvider:
            name = "brave"

            def search(self, query, limit):
                return [
                    app.SearchResult("https://bad.example:99999/path", provider="brave", query_id=query.query_id, category_hint=query.category),
                    app.SearchResult(f"https://valid-{query.category}.example/", "Valid", "Snippet", "brave", query.query_id, query.text, query.category),
                ]

        class FakeCrawler:
            errors = []

            def __init__(self, *args, **kwargs):
                pass

            def crawl_domain(self, url):
                if "book_blog" in url:
                    text = "Buchblog Sachbuch Ratgeber Rezensionsexemplare willkommen Familie Katze Kontakt Impressum Autorin"
                elif "cat_pet_media" in url:
                    text = "Katzenblog Haustier Katze Magazin Redaktion Presse Kontakt Impressum Autor"
                elif "parent_family_media" in url:
                    text = "Elternblog Familie Baby Schwangerschaft Gastbeitrag Themenvorschlag Kontakt Impressum Autorin"
                else:
                    text = "Elternpodcast Podcast Interview Podcastgast Familie Kontakt Impressum Episoden Redaktion"
                return [app.PageSnapshot(url, url, 200, "Valid", "Valid", ["Valid"], text, [], "", ["2026-05-01"], "", "", app.now_iso())]

        with tempfile.TemporaryDirectory() as tmp:
            old_make_provider = app.make_provider
            old_crawler = app.ControlledCrawler
            try:
                app.make_provider = lambda args: FakeProvider()
                app.ControlledCrawler = FakeCrawler
                args = type(
                    "Args",
                    (),
                    {
                        "provider": "brave",
                        "target": 4,
                        "output": str(Path(tmp) / "seeds.csv"),
                        "dry_run": False,
                        "overwrite": False,
                        "resume": False,
                        "max_pages_per_domain": 6,
                        "min_score": 65,
                        "category": "",
                        "search_results": "",
                        "allow_unofficial_search": False,
                        "verbose": True,
                        "queries": "",
                        "scoring": "",
                        "cache_dir": str(Path(tmp) / "cache"),
                        "query_limit": 4,
                        "results_per_query": 10,
                        "max_candidate_domains": 120,
                    },
                )()
                out = io.StringIO()
                with redirect_stdout(out):
                    code, report, final = app.run_discovery(args)
                self.assertEqual(code, 0)
                self.assertIn("Ungueltige URL uebersprungen: invalid_port", out.getvalue())
                self.assertGreaterEqual(report["rejection_reasons"].get("invalid_port", 0), 1)
                self.assertGreater(len(final), 0)
                self.assertTrue((Path(tmp) / "seeds.csv").exists())
                self.assertTrue((Path(tmp) / "seed_audit.csv").exists())
                self.assertTrue((Path(tmp) / "run_report.json").exists())
            finally:
                app.make_provider = old_make_provider
                app.ControlledCrawler = old_crawler


if __name__ == "__main__":
    unittest.main()
