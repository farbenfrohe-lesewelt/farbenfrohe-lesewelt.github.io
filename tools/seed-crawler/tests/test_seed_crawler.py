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

    def candidate_for(self, domain, pages, category_hint="cat_pet_media", title=""):
        result = app.SearchResult(f"https://{domain}/", title or domain, "", "file", "import01", "", category_hint)
        return app.evaluate_domain(result, pages, self.blocklists, self.scoring, 70)

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
                    entity_type={
                        "book_blog": "independent_book_blog",
                        "cat_pet_media": "cat_pet_editorial",
                        "parent_family_media": "parent_family_editorial",
                        "podcast": "podcast_show",
                    }[category],
                    hard_gate_passed=True,
                    candidate_mode="A",
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

    def test_regression_schreibtrieb_is_book_blog_not_cat_boosted_by_title(self):
        pages = [
            self.page(
                "https://buchblog.schreibtrieb.com/kontakt/",
                "Schreibtrieb Buchblog Kontakt",
                "Unabhaengiger Buchblog mit Rezensionen Buchvorstellung Sachbuch Ratgeber. Buchvorschlag und Rezensionsexemplare willkommen. Kontaktformular Impressum Autorin.",
                ["2026-04-01"],
                site_name="Schreibtrieb Buchblog",
            )
        ]
        candidate = self.candidate_for("buchblog.schreibtrieb.com", pages, "book_blog")
        self.assertEqual(candidate.entity_type, "independent_book_blog")
        self.assertEqual(candidate.category, "book_blog")
        self.assertTrue(candidate.hard_gate_passed)

    def test_regression_haustiger_and_katzenguru_are_cat_media_not_book_blog(self):
        haustiger = self.candidate_for(
            "haustiger.info",
            [self.page("https://haustiger.info/kontakt/", "Haustiger Katzenblog", "Katzenblog Katzenmagazin Haustier Katze Tierverhalten Tierschutz Redaktion kontaktieren Presseanfrage Kontakt Impressum Autorin.", ["2026-03-01"], site_name="Haustiger")],
            "cat_pet_media",
        )
        katzenguru = self.candidate_for(
            "katzenguru.de",
            [self.page("https://katzenguru.de/gastbeitrag/", "Katzenguru Gastbeitrag", "Katzenblog Katzenmagazin Haustier Katze Tierverhalten Tierschutz Gastbeitrag einreichen vollstaendiger unveroeffentlichter Gastartikel exklusive Nutzungsrechte Kontakt Impressum.", ["2026-02-01"], site_name="Katzenguru")],
            "cat_pet_media",
        )
        self.assertEqual(haustiger.category, "cat_pet_media")
        self.assertEqual(haustiger.entity_type, "cat_pet_editorial")
        self.assertEqual(katzenguru.category, "cat_pet_media")
        self.assertEqual(katzenguru.channel_type, "guest_post")
        self.assertNotEqual(katzenguru.channel_type, "review_copy")

    def test_regression_parent_family_media_acceptance_and_best_url(self):
        papammunity = self.candidate_for(
            "papammunity.de",
            [self.page("https://papammunity.de/interviews/", "Papammunity Elternblog", "Elternblog Familienmagazin Familie Baby Schwangerschaft Kind Kleinkind Interviews Fachbeitrag Gastbeitrag Themenvorschlag Buch PR Kontakt Impressum Autor.", ["2026-05-01"], site_name="Papammunity")],
            "parent_family_media",
        )
        article = self.page("https://elternmagazin.info/blog/fremder-elternblog/", "Artikel ueber anderen Elternblog", "Eltern Familie Baby fremder Blog Podcast Empfehlung.", ["2026-04-01"], site_name="Elternmagazin")
        contact = self.page("https://elternmagazin.info/redaktion/", "Redaktion", "Elternmagazin Familienmagazin Eltern Familie Baby Schwangerschaft Kind Kleinkind Redaktion kontaktieren Themenvorschlag Presseanfrage Kontakt Impressum.", ["2026-04-02"], site_name="Elternmagazin")
        elternmagazin = self.candidate_for("elternmagazin.info", [article, contact], "parent_family_media")
        self.assertEqual(papammunity.entity_type, "parent_family_editorial")
        self.assertTrue(papammunity.hard_gate_passed)
        self.assertEqual(elternmagazin.category, "parent_family_media")
        self.assertEqual(elternmagazin.final_seed_url, "https://elternmagazin.info/redaktion/")

    def test_regression_reject_publisher_personal_shop_coach(self):
        cases = [
            ("dorlingkindersley.de", "DK Verlag Verlagsshop Verlagsprogramm Buch bestellen Warenkorb Produkt ISBN Shop Ratgeber Kontakt Presse.", "publisher"),
            ("ralf-seeger.com", "Offizielle Website Ralf Seeger Vita Pressearchiv Termine Presse Hunde TV Kontakt.", "personal_official_site"),
            ("vtg-tiergesundheit.de", "Shop Tiergesundheit Warenkorb Produkt kaufen Versandkosten Magazin Katze Hund Ratgeber Kontakt.", "online_shop"),
            ("buchhebamme.de", "Schreibcoach Selfpublishing Beratung Coaching Kurs Rezensionsexemplare eigene Buecher versenden Autorinnenseite Kontakt.", "coach_or_service_provider"),
        ]
        for domain, text, entity_type in cases:
            with self.subTest(domain=domain):
                candidate = self.candidate_for(domain, [self.page(f"https://{domain}/", domain, text, ["2026-03-01"], site_name=domain)], "book_blog")
                self.assertEqual(candidate.entity_type, entity_type)
                self.assertEqual(candidate.status, "rejected")
                self.assertFalse(candidate.hard_gate_passed)

    def test_regression_sonnenkinderleben_old_article_is_not_podcast(self):
        page = self.page(
            "https://sonnenkinderleben.de/podcast-tipps/",
            "Podcast Empfehlungen fuer Eltern",
            "Artikel vom 23.02.2023. Familienblog Elternblog Familie Baby Kind Podcast Empfehlungen Spotify Apple Podcasts Liste fremder Podcasts Kontakt Impressum Archiv 2026 Termine 2027.",
            ["2023-02-23", "2027-01-01"],
            site_name="Sonnenkinderleben",
        )
        candidate = self.candidate_for("sonnenkinderleben.de", [page], "podcast")
        self.assertEqual(candidate.entity_type, "parent_family_editorial")
        self.assertNotEqual(candidate.category, "podcast")
        self.assertEqual(candidate.activity_evidence_date, "2023-02-23")
        self.assertEqual(candidate.status, "rejected")

    def test_regression_isolated_topic_words_do_not_create_high_relevance(self):
        page = self.page("https://example.org/", "Gemischte Seite", "Ein Artikel erwaehnt Katze Baby Podcast Rezensionsexemplar einmal. Kontakt Impressum.", ["2026-04-01"])
        candidate = self.candidate_for("example.org", [page], "cat_pet_media")
        self.assertLess(candidate.topic_score, 18)
        self.assertEqual(candidate.status, "rejected")

    def test_regression_real_podcast_show_is_detected(self):
        page = self.page(
            "https://familienpodcast.example/gaeste/",
            "Familienpodcast Gaeste",
            "Familienpodcast Podcastshow Episode Episoden Folge RSS Feed Show Interview Podcastgast werden Interviewvorschlag Eltern Familie Kontakt Impressum Redaktion.",
            ["2026-04-15"],
            site_name="Familienpodcast",
        )
        candidate = self.candidate_for("familienpodcast.example", [page], "podcast")
        self.assertEqual(candidate.entity_type, "podcast_show")
        self.assertEqual(candidate.category, "podcast")
        self.assertTrue(candidate.hard_gate_passed)

    def test_regression_name_extraction_ignores_suche_for_katzenguru(self):
        page = self.page("https://katzenguru.de/suche/", "Suche", "Katzenblog Katzenmagazin Haustier Katze Tierverhalten Tierschutz Kontakt Impressum.", ["2026-04-01"], site_name="Suche")
        self.assertEqual(app.determine_name(page, "katzenguru.de"), "Katzenguru")

    def test_social_links_and_cookie_text_do_not_override_own_domain_entity(self):
        page = self.page(
            "https://meinekatzenmaedchen.de/kooperation/",
            "Meine Katzenmaedchen Katzenblog Kooperation",
            "Katzenblog Katzenmagazin Haustier Katze Tierverhalten Tierschutz Blogarchiv Ratgeber Buchrezensionen Gastbeitrag Kooperation Kontakt Impressum. Cookie Einstellungen fuer Instagram YouTube Spotify.",
            ["2026-05-01"],
            links=[("https://instagram.com/meinekatzenmaedchen", "Instagram"), ("https://youtube.com/example", "YouTube")],
            site_name="Meine Katzenmaedchen",
        )
        candidate = self.candidate_for("meinekatzenmaedchen.de", [page], "cat_pet_media")
        self.assertEqual(candidate.entity_type, "cat_pet_editorial")
        self.assertEqual(candidate.category, "cat_pet_media")
        self.assertNotEqual(candidate.entity_type, "social_or_podcast_platform")
        self.assertGreaterEqual(candidate.social_links_detected, 2)

    def test_platform_entity_only_for_platform_domain(self):
        page = self.page("https://instagram.com/example/", "Instagram", "Katzenblog Katze Kontakt", ["2026-05-01"])
        candidate = self.candidate_for("instagram.com", [page], "cat_pet_media")
        self.assertEqual(candidate.entity_type, "social_or_podcast_platform")
        self.assertEqual(candidate.platform_domain_match, "instagram.com")
        self.assertFalse(candidate.entity_gate_passed)

    def test_real_second_pilot_media_are_typed_correctly(self):
        cases = [
            ("smallnature.de", "Smallnature Katzenblog", "Katzenblog Katzenmagazin Haustier Katze Tierverhalten Tierschutz Kooperation Gastbeitrag kostenpflichtige Kooperation Mediakit Kontakt Impressum Blogarchiv Ratgeber.", "cat_pet_editorial", "cat_pet_media"),
            ("lieblingskatze.net", "Lieblingskatze Katzenblog Kooperation", "Katzenblog Katzenmagazin Katze Haustier Tierverhalten Tierschutz Kooperationsseite Werbung Affiliate Kontakt Impressum Ratgeber Archiv.", "cat_pet_editorial", "cat_pet_media"),
            ("haustiger.info", "Haustiger Katzenblog Redaktion", "Katzenblog Katzenmagazin Katze Haustier Tierverhalten Tierschutz Redaktionskontakt Kontakt Impressum Ratgeber Archiv Autorin.", "cat_pet_editorial", "cat_pet_media"),
            ("pola-magazin.de", "Pola Familienmagazin Kooperation", "Familienmagazin Eltern Baby Kleinkind Familie Schwangerschaft Buecher Medien Kooperation Mediakit Kontakt Impressum Archiv Kategorien.", "parent_family_editorial", "parent_family_media"),
            ("grossekoepfe.de", "Grosse Koepfe Elternblog", "Elternblog Familienblog Eltern Familie Schwangerschaft Baby Lesen Kooperation Mediakit Presse Kontakt Impressum Archiv Autorinnen.", "parent_family_editorial", "parent_family_media"),
            ("kuckuck-magazin.de", "Kuckuck Familienmagazin", "Familienmagazin Babybereich Eltern Familie Baby Kind RSS Newsletter Mediadaten Kontakt Impressum Redaktion Archiv.", "parent_family_editorial", "parent_family_media"),
            ("papammunity.de", "Papammunity Elternblog", "Elternblog Familienblog werdende Eltern Familie Baby Schwangerschaft Kind Kleinkind Kontakt Impressum aktuelle Beitraege Fachbeitrag Interview Archiv.", "parent_family_editorial", "parent_family_media"),
            ("buchblog.schreibtrieb.com", "Schreibtrieb Buchblog", "Buchblog Rezensionen Buchvorstellung Sachbuch Ratgeber mehrere Rezensionen Kontakt Impressum Aktualisierung 2026 Autorin.", "independent_book_blog", "book_blog"),
        ]
        for domain, title, text, entity_type, category in cases:
            with self.subTest(domain=domain):
                candidate = self.candidate_for(domain, [self.page(f"https://{domain}/kontakt/", title, text, ["2026-05-01"], site_name=title)], category)
                self.assertEqual(candidate.entity_type, entity_type)
                self.assertEqual(candidate.category, category)
                self.assertNotEqual(candidate.entity_type, "social_or_podcast_platform")
                self.assertGreater(candidate.editorial_score, 0)

    def test_mediakit_and_single_affiliate_are_not_automatic_exclusion(self):
        candidate = self.candidate_for(
            "pola-magazin.de",
            [self.page("https://pola-magazin.de/kooperation/", "Pola Familienmagazin", "Familienmagazin Eltern Familie Baby Kleinkind Kooperation Mediakit Affiliate Kontakt Impressum Archiv Kategorien Autorin.", ["2026-04-01"], site_name="Pola Magazin")],
            "parent_family_media",
        )
        self.assertNotEqual(candidate.commercial_model, "paid_only")
        self.assertNotEqual(candidate.candidate_mode, "C")

    def test_paid_link_placement_remains_excluded(self):
        candidate = self.candidate_for(
            "spam.example",
            [self.page("https://spam.example/kooperation/", "Katzenblog", "Katzenblog Katzenmagazin Katze Haustier Tierverhalten Tierschutz Dofollow-Link kaufen Backlink kaufen garantierte Veroeffentlichung Kontakt Impressum.", ["2026-04-01"])],
            "cat_pet_media",
        )
        self.assertEqual(candidate.commercial_model, "paid_only")
        self.assertEqual(candidate.candidate_mode, "C")

    def test_general_contact_suffices_for_real_cat_and_family_media(self):
        cat = self.candidate_for("haustiger.info", [self.page("https://haustiger.info/kontakt/", "Haustiger Katzenblog", "Katzenblog Katzenmagazin Katze Haustier Tierverhalten Tierschutz Kontakt Impressum Archiv Ratgeber Autorin.", ["2026-05-01"])], "cat_pet_media")
        family = self.candidate_for("papammunity.de", [self.page("https://papammunity.de/kontakt/", "Papammunity Elternblog", "Elternblog Familienblog Eltern Familie Baby Schwangerschaft Kind Kleinkind Kontakt Impressum Archiv Autor.", ["2026-05-01"])], "parent_family_media")
        self.assertTrue(cat.quality_gate_passed)
        self.assertTrue(family.quality_gate_passed)

    def test_buchblog_with_reviews_and_contact_passes_without_review_copy_page(self):
        candidate = self.candidate_for(
            "buchblog.schreibtrieb.com",
            [self.page("https://buchblog.schreibtrieb.com/kontakt/", "Schreibtrieb Buchblog", "Buchblog Rezensionen Buchvorstellung Sachbuch Ratgeber mehrere Rezensionen Kontakt Impressum Autorin Archiv.", ["2026-05-01"])],
            "book_blog",
        )
        self.assertTrue(candidate.entity_gate_passed)
        self.assertTrue(candidate.quality_gate_passed)

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
                        entity_type={
                            "book_blog": "independent_book_blog",
                            "cat_pet_media": "cat_pet_editorial",
                            "parent_family_media": "parent_family_editorial",
                            "podcast": "podcast_show",
                        }[category],
                        hard_gate_passed=True,
                        candidate_mode="A",
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
                    category_text = "Buchblog Rezensionen Buchvorstellung Sachbuch Ratgeber Rezensionsexemplare willkommen Buchvorschlag Kontakt Impressum Autorin"
                elif host.startswith("cat"):
                    category_text = "Katzenblog Katzenmagazin Haustier Katze Tierverhalten Tierschutz Redaktion kontaktieren Presseanfrage Kontakt Impressum Autor"
                elif host.startswith("family"):
                    category_text = "Elternblog Familienmagazin Familie Baby Schwangerschaft Kind Kleinkind Gastbeitrag Themenvorschlag Kontakt Impressum Autorin"
                else:
                    category_text = "Elternpodcast Podcastshow Podcast Interview Podcastgast werden Episode Episoden Folge RSS Show Familie Kontakt Impressum Redaktion"
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
                    text = "Buchblog Rezensionen Buchvorstellung Sachbuch Ratgeber Rezensionsexemplare willkommen Buchvorschlag Kontakt Impressum Autorin"
                elif "cat_pet_media" in url:
                    text = "Katzenblog Katzenmagazin Haustier Katze Tierverhalten Tierschutz Redaktion kontaktieren Presseanfrage Kontakt Impressum Autor"
                elif "parent_family_media" in url:
                    text = "Elternblog Familienmagazin Familie Baby Schwangerschaft Kind Kleinkind Gastbeitrag Themenvorschlag Kontakt Impressum Autorin"
                else:
                    text = "Elternpodcast Podcastshow Podcast Interview Podcastgast werden Episode Episoden Folge RSS Show Familie Kontakt Impressum Redaktion"
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
