from __future__ import annotations

import re
import time
from datetime import datetime, timezone
from html import unescape
from typing import Callable, Dict, List
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

try:
    import feedparser
except ImportError:  # pragma: no cover
    feedparser = None

try:
    import requests
except ImportError:  # pragma: no cover
    requests = None

try:
    from bs4 import BeautifulSoup
except ImportError:  # pragma: no cover
    BeautifulSoup = None

from .models import FetchResult
from .safety import USER_AGENT, is_blocked_path, is_probably_html_url


CONTACT_HINTS = (
    "presse",
    "kontakt",
    "redaktion",
    "rezension",
    "gastbeitrag",
    "interview",
    "podcast",
    "medienanfrage",
)


class MentionCrawler:
    def __init__(
        self,
        config: dict,
        sleeper: Callable[[float], None] = time.sleep,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if requests is None:
            raise RuntimeError("requests wird zum Abrufen öffentlicher Seiten benötigt.")
        self.config = config
        self.sleeper = sleeper
        self.clock = clock
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"})
        self.session.max_redirects = int(config.get("maximum_redirects", 5))
        self.robots_cache: Dict[str, RobotFileParser] = {}
        self.last_request_by_domain: Dict[str, float] = {}
        self.pages_by_domain: Dict[str, int] = {}

    def parse_feed(self, feed_url: str) -> List[str]:
        if feedparser is None:
            raise RuntimeError("feedparser wird zum Lesen von RSS- oder Atom-Feeds benötigt.")
        parsed = feedparser.parse(feed_url)
        return [entry.get("link") for entry in parsed.entries if entry.get("link")]

    def _robots_for(self, url: str) -> RobotFileParser:
        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        if base not in self.robots_cache:
            parser = RobotFileParser()
            parser.set_url(urljoin(base, "/robots.txt"))
            try:
                parser.read()
            except Exception:
                parser.parse([])
            self.robots_cache[base] = parser
        return self.robots_cache[base]

    def can_fetch(self, url: str) -> bool:
        return self._robots_for(url).can_fetch(USER_AGENT, url)

    def wait_for_domain(self, domain: str) -> None:
        delay = float(self.config.get("request_delay_seconds", 3))
        last = self.last_request_by_domain.get(domain)
        now = self.clock()
        if last is not None:
            wait = delay - (now - last)
            if wait > 0:
                self.sleeper(wait)
        self.last_request_by_domain[domain] = self.clock()

    def _domain_allowed(self, domain: str) -> bool:
        limit = int(self.config.get("maximum_pages_per_domain", 5))
        return self.pages_by_domain.get(domain, 0) < limit

    def _mark_domain(self, domain: str) -> None:
        self.pages_by_domain[domain] = self.pages_by_domain.get(domain, 0) + 1

    def fetch(self, url: str) -> FetchResult:
        fetched_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        if not parsed.scheme.startswith("http"):
            return FetchResult(url=url, final_url=url, fetched_at=fetched_at, skipped_reason="Nur HTTP(S)-URLs werden verarbeitet.")
        if is_blocked_path(url):
            return FetchResult(url=url, final_url=url, fetched_at=fetched_at, skipped_reason="Geschützter Konto-, Login- oder Kaufbereich übersprungen.")
        if not is_probably_html_url(url):
            return FetchResult(url=url, final_url=url, fetched_at=fetched_at, skipped_reason="Nicht-HTML-Datei übersprungen.")
        if not self._domain_allowed(domain):
            return FetchResult(url=url, final_url=url, fetched_at=fetched_at, skipped_reason="Domain-Limit erreicht.")
        if not self.can_fetch(url):
            return FetchResult(url=url, final_url=url, fetched_at=fetched_at, skipped_reason="Durch robots.txt nicht erlaubt.")

        self.wait_for_domain(domain)
        try:
            response = self.session.get(
                url,
                timeout=float(self.config.get("timeout_seconds", 15)),
                allow_redirects=True,
                stream=True,
            )
            content_type = response.headers.get("content-type", "").lower()
            if content_type and "text/html" not in content_type and "application/xhtml+xml" not in content_type:
                return FetchResult(url=url, final_url=response.url, status_code=response.status_code, fetched_at=fetched_at, skipped_reason=f"Nicht-HTML-Inhalt: {content_type}")
            max_bytes = int(self.config.get("maximum_html_bytes", 2_000_000))
            chunks: List[bytes] = []
            total = 0
            for chunk in response.iter_content(chunk_size=65536):
                if not chunk:
                    continue
                total += len(chunk)
                if total > max_bytes:
                    return FetchResult(url=url, final_url=response.url, status_code=response.status_code, fetched_at=fetched_at, skipped_reason="HTML-Größenlimit überschritten.")
                chunks.append(chunk)
            self._mark_domain(domain)
            html = b"".join(chunks).decode(response.encoding or "utf-8", errors="replace")
            title, text, contacts = parse_html(html, response.url)
            return FetchResult(url=url, final_url=response.url, status_code=response.status_code, title=title, text=text, html=html, fetched_at=fetched_at, contact_methods=contacts)
        except Exception as exc:
            return FetchResult(url=url, final_url=url, fetched_at=fetched_at, error=f"{type(exc).__name__}: {exc}")


def parse_html(html: str, base_url: str) -> tuple[str, str, List[str]]:
    if BeautifulSoup is not None:
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        title = soup.title.get_text(" ", strip=True) if soup.title else ""
        text = soup.get_text(" ", strip=True)
        contacts: List[str] = []
        for link in soup.find_all("a", href=True):
            href = link.get("href", "").strip()
            label = link.get_text(" ", strip=True).lower()
            href_lower = href.lower()
            if href_lower.startswith("mailto:") or any(hint in href_lower or hint in label for hint in CONTACT_HINTS):
                contacts.append(urljoin(base_url, href))
        return title, re.sub(r"\s+", " ", text), sorted(set(contacts))

    title_match = re.search(r"<title[^>]*>(.*?)</title>", html, flags=re.IGNORECASE | re.DOTALL)
    title = unescape(re.sub(r"\s+", " ", title_match.group(1)).strip()) if title_match else ""
    text = unescape(re.sub(r"<[^>]+>", " ", html))
    return title, re.sub(r"\s+", " ", text).strip(), []
