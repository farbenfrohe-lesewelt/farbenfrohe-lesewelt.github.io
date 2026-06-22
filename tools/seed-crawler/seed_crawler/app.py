from __future__ import annotations

import argparse
import csv
import hashlib
import ipaddress
import json
import logging
import os
import re
import shutil
import sys
import time
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime, timedelta
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable, Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlencode, urljoin, urlparse, urlunparse
from urllib.request import HTTPRedirectHandler, Request, build_opener, urlopen
from urllib.robotparser import RobotFileParser


USER_AGENT = "FarbenfroheLesewelt-SeedCrawler/0.1 (+public editorial research)"
CATEGORY_ORDER = ["book_blog", "cat_pet_media", "parent_family_media", "podcast"]
CATEGORY_LABELS = {
    "book_blog": "Buchblog",
    "cat_pet_media": "Katzen- oder Haustiermedium",
    "parent_family_media": "Eltern- oder Familienmedium",
    "podcast": "Podcast",
}
DEFAULT_QUOTAS = {
    "book_blog": 30,
    "cat_pet_media": 30,
    "parent_family_media": 25,
    "podcast": 15,
}
PILOT_QUOTAS = {
    "book_blog": 3,
    "cat_pet_media": 3,
    "parent_family_media": 2,
    "podcast": 2,
}
PILOT_TARGET = 10
PILOT_MAX_QUERIES = 24
PILOT_RESULTS_PER_QUERY = 10
PILOT_MAX_DOMAINS = 120
PILOT_MAX_PAGES_PER_DOMAIN = 6
FINAL_MIN_SCORE = 70
DEFAULT_LOCAL_DATA_DIR = Path("local-data/mention-radar")
SEED_CRAWLER_ENV_KEYS = {
    "SEED_CRAWLER_SEARCH_PROVIDER",
    "BRAVE_SEARCH_API_KEY",
    "BRAVE_SEARCH_COUNTRY",
    "BRAVE_SEARCH_LANG",
}
TRACKING_PARAMS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_content",
    "utm_term",
    "fbclid",
    "gclid",
    "ref",
    "source",
    "campaign",
}
SLUG_PRIORITY = [
    ("rezensionsexemplar", 100),
    ("rezensionsexemplare", 100),
    ("buchvorschlag", 90),
    ("einsenden", 88),
    ("podcastgast", 84),
    ("gaeste", 82),
    ("gaste", 82),
    ("interview", 80),
    ("gastbeitrag", 76),
    ("themenvorschlag", 74),
    ("presse", 68),
    ("redaktion", 66),
    ("kontakt", 58),
    ("kooperation", 56),
    ("zusammenarbeit", 54),
    ("rezension", 52),
    ("buchvorstellung", 50),
]
FOLLOW_HINTS = tuple(slug for slug, _score in SLUG_PRIORITY) + (
    "media",
    "about",
    "ueber-uns",
    "uber-uns",
    "neuerscheinung",
    "gastautor",
)
HTML_EXTENSIONS_BLOCKED = {
    ".pdf",
    ".zip",
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".webp",
    ".svg",
    ".mp3",
    ".mp4",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
}
COMMON_MULTI_SUFFIXES = {
    "co.uk",
    "org.uk",
    "com.au",
    "com.br",
    "co.at",
}
ENTITY_TYPES = {
    "independent_book_blog",
    "cat_pet_editorial",
    "parent_family_editorial",
    "podcast_show",
    "publisher",
    "bookstore",
    "online_shop",
    "commercial_brand_blog",
    "personal_official_site",
    "author_site",
    "coach_or_service_provider",
    "forum",
    "directory_or_aggregator",
    "social_or_podcast_platform",
    "government_or_institution",
    "unknown",
}
REGULAR_ALLOWED_ENTITY_TYPES = {
    "independent_book_blog",
    "cat_pet_editorial",
    "parent_family_editorial",
    "podcast_show",
}
GENERIC_NAME_PARTS = {
    "suche",
    "menu",
    "menue",
    "kontakt",
    "impressum",
    "redaktion",
    "presse",
    "rezensionsexemplare",
    "rezensionsexemplar",
    "gastbeitrag",
    "gastbeitraege",
    "startseite",
    "home",
    "willkommen",
    "blog",
    "magazin",
}
FORCED_DOMAIN_ENTITY = {
    "buchblog.schreibtrieb.com": ("independent_book_blog", "bekannter unabhaengiger Buchblog"),
    "haustiger.info": ("cat_pet_editorial", "redaktioneller Katzenblog"),
    "katzenguru.de": ("cat_pet_editorial", "redaktioneller Katzenblog mit Gastbeitragsmoeglichkeit"),
    "papammunity.de": ("parent_family_editorial", "redaktioneller Elternblog"),
    "elternmagazin.info": ("parent_family_editorial", "redaktionelles Familienmedium"),
    "dorlingkindersley.de": ("publisher", "Verlag beziehungsweise Verlagsshop"),
    "ralf-seeger.com": ("personal_official_site", "persoenliche offizielle Website mit Pressearchiv"),
    "vtg-tiergesundheit.de": ("online_shop", "kommerzieller Shop mit Magazin"),
    "sonnenkinderleben.de": ("parent_family_editorial", "Familienblog, kein Podcast"),
    "buchhebamme.de": ("coach_or_service_provider", "Schreibcoach/Selfpublishing-Beratung"),
}
ENTITY_CATEGORY = {
    "independent_book_blog": "book_blog",
    "cat_pet_editorial": "cat_pet_media",
    "parent_family_editorial": "parent_family_media",
    "podcast_show": "podcast",
}


@dataclass(frozen=True)
class SearchResult:
    url: str
    title: str = ""
    snippet: str = ""
    provider: str = ""
    query_id: str = ""
    query: str = ""
    category_hint: str = ""


@dataclass(frozen=True)
class QuerySpec:
    category: str
    query_id: str
    text: str
    generated: bool = False


@dataclass
class PageSnapshot:
    requested_url: str
    final_url: str
    status_code: int = 0
    title: str = ""
    site_name: str = ""
    headings: list[str] = field(default_factory=list)
    text: str = ""
    links: list[tuple[str, str]] = field(default_factory=list)
    canonical_url: str = ""
    dates: list[str] = field(default_factory=list)
    error: str = ""
    skipped_reason: str = ""
    fetched_at: str = ""
    meta_description: str = ""
    jsonld_dates: list[str] = field(default_factory=list)


@dataclass
class Candidate:
    candidate_url: str
    final_seed_url: str
    domain: str
    name: str
    category: str
    discovery_source: str
    query_id: str
    topic_score: int = 0
    editorial_score: int = 0
    activity_score: int = 0
    credibility_score: int = 0
    approachability_score: int = 0
    penalty_score: int = 0
    total_score: int = 0
    contact_signal: str = ""
    activity_signal: str = ""
    editorial_signal: str = ""
    rejection_reason: str = ""
    status: str = "rejected"
    notes: str = ""
    entity_type: str = "unknown"
    entity_type_evidence: str = ""
    category_evidence: str = ""
    topic_evidence: str = ""
    contact_evidence_url: str = ""
    contact_evidence_text: str = ""
    activity_evidence_url: str = ""
    activity_evidence_date: str = ""
    activity_confidence: str = "low"
    hard_gate_passed: bool = False
    hard_gate_reason: str = ""
    channel_type: str = ""


class SearchProvider(Protocol):
    name: str

    def search(self, query: QuerySpec, limit: int) -> list[SearchResult]:
        ...


class NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
        return None


def _parse_url_safely(url: str):
    try:
        parsed = urlparse(url)
        _host = parsed.hostname
        _port = parsed.port
        return parsed, ""
    except ValueError as exc:
        message = str(exc).lower()
        if "port" in message:
            return None, "invalid_port"
        return None, "url_parse_error"


def _join_url_safely(base_url: str, href: str) -> tuple[str, str]:
    try:
        joined = urljoin(base_url, href)
    except ValueError as exc:
        message = str(exc).lower()
        return "", "invalid_port" if "port" in message else "url_parse_error"
    normalized, reason = normalize_url_with_reason(joined)
    return normalized, reason


class BraveSearchProvider:
    name = "brave"

    def __init__(self, api_key: str, timeout: float = 20.0, country: str = "de", language: str = "de") -> None:
        if not api_key:
            raise ValueError("BRAVE_SEARCH_API_KEY fehlt. Lege ihn als Umgebungsvariable oder in tools/seed-crawler/.env ab.")
        self.api_key = api_key
        self.timeout = timeout
        self.country = (country or "de").upper()
        self.language = (language or "de").lower()

    def search(self, query: QuerySpec, limit: int) -> list[SearchResult]:
        params = urlencode({"q": query.text, "count": max(1, min(limit, 20)), "search_lang": self.language, "country": self.country})
        request = Request(
            f"https://api.search.brave.com/res/v1/web/search?{params}",
            headers={
                "Accept": "application/json",
                "X-Subscription-Token": self.api_key,
                "User-Agent": USER_AGENT,
            },
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8", errors="replace"))
        except HTTPError as exc:
            retry_after = exc.headers.get("Retry-After", "")
            raise RuntimeError(f"Brave API HTTP {exc.code}; Retry-After={retry_after}") from exc
        except (URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"Brave API Fehler: {exc}") from exc
        results = payload.get("web", {}).get("results", []) or []
        mapped: list[SearchResult] = []
        for item in results:
            url = str(item.get("url") or "")
            if url:
                mapped.append(
                    SearchResult(
                        url=url,
                        title=str(item.get("title") or ""),
                        snippet=str(item.get("description") or ""),
                        provider=self.name,
                        query_id=query.query_id,
                        query=query.text,
                        category_hint=query.category,
                    )
                )
        return mapped


class FileSearchProvider:
    name = "file"

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.rows = read_search_results_file(self.path)
        self.emitted_by_category: set[str] = set()

    def search(self, query: QuerySpec, limit: int) -> list[SearchResult]:
        if query.category in self.emitted_by_category:
            return []
        self.emitted_by_category.add(query.category)
        selected: list[SearchResult] = []
        for index, row in enumerate(self.rows, start=1):
            row_category = row.category_hint or ""
            if row_category and row_category != query.category:
                continue
            selected.append(
                SearchResult(
                    url=row.url,
                    title=row.title,
                    snippet=row.snippet,
                    provider=self.name,
                    query_id=row.query_id or f"import{index:02d}",
                    query=row.query or "file-import",
                    category_hint=row_category or query.category,
                )
            )
            if len(selected) >= limit:
                break
        return selected


class TinyHTMLParser(HTMLParser):
    def __init__(self, base_url: str) -> None:
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.title_parts: list[str] = []
        self.site_name = ""
        self.meta_description = ""
        self.canonical_url = ""
        self.text_parts: list[str] = []
        self.links: list[tuple[str, str]] = []
        self.headings: list[str] = []
        self.dates: list[str] = []
        self.jsonld_dates: list[str] = []
        self._tag_stack: list[str] = []
        self._current_link: str = ""
        self._current_link_text: list[str] = []
        self._capture_title = False
        self._capture_heading = False
        self._heading_text: list[str] = []
        self._skip_depth = 0
        self._capture_jsonld = False
        self._jsonld_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        attrs_dict = {key.lower(): value or "" for key, value in attrs}
        self._tag_stack.append(tag)
        if tag == "script" and attrs_dict.get("type", "").lower() == "application/ld+json":
            self._capture_jsonld = True
            self._jsonld_parts = []
        elif tag in {"script", "style", "noscript"}:
            self._skip_depth += 1
        if tag == "title":
            self._capture_title = True
        if tag in {"h1", "h2"}:
            self._capture_heading = True
            self._heading_text = []
        if tag == "meta":
            prop = (attrs_dict.get("property") or attrs_dict.get("name") or "").lower()
            content = attrs_dict.get("content", "").strip()
            if prop == "og:site_name" and content:
                self.site_name = content
            if prop in {"description", "og:description"} and content:
                self.meta_description = content
            if prop in {"article:published_time", "article:modified_time", "date", "dc.date"} and content:
                self.dates.append(content)
        if tag == "link":
            rel = attrs_dict.get("rel", "").lower()
            href = attrs_dict.get("href", "").strip()
            if "canonical" in rel and href:
                canonical_url, _reason = _join_url_safely(self.base_url, href)
                if canonical_url:
                    self.canonical_url = canonical_url
        if tag == "time":
            dt = attrs_dict.get("datetime", "").strip()
            if dt:
                self.dates.append(dt)
        if tag == "a":
            href = attrs_dict.get("href", "").strip()
            if href:
                link_url, _reason = _join_url_safely(self.base_url, href)
                if link_url:
                    self._current_link = link_url
                    self._current_link_text = []

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "script" and self._capture_jsonld:
            self._capture_jsonld = False
            self._extract_jsonld_dates(" ".join(self._jsonld_parts))
            self._jsonld_parts = []
        if tag in {"script", "style", "noscript"} and self._skip_depth:
            self._skip_depth -= 1
        if tag == "title":
            self._capture_title = False
        if tag in {"h1", "h2"} and self._capture_heading:
            heading = clean_space(" ".join(self._heading_text))
            if heading:
                self.headings.append(heading)
            self._capture_heading = False
            self._heading_text = []
        if tag == "a" and self._current_link:
            label = clean_space(" ".join(self._current_link_text))
            self.links.append((self._current_link, label))
            self._current_link = ""
            self._current_link_text = []
        if self._tag_stack:
            self._tag_stack.pop()

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        if self._capture_jsonld:
            self._jsonld_parts.append(data)
            return
        text = clean_space(data)
        if not text:
            return
        if self._capture_title:
            self.title_parts.append(text)
        if self._capture_heading:
            self._heading_text.append(text)
        if self._current_link:
            self._current_link_text.append(text)
        self.text_parts.append(text)

    def _extract_jsonld_dates(self, raw_json: str) -> None:
        try:
            payload = json.loads(raw_json)
        except json.JSONDecodeError:
            return
        stack = [payload]
        while stack:
            item = stack.pop()
            if isinstance(item, dict):
                for key, value in item.items():
                    if key in {"datePublished", "dateModified"} and isinstance(value, str):
                        self.jsonld_dates.append(value)
                    elif isinstance(value, (dict, list)):
                        stack.append(value)
            elif isinstance(item, list):
                stack.extend(item)


def clean_space(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def slug_text(value: str) -> str:
    text = (value or "").lower()
    return (
        text.replace("ä", "ae")
        .replace("ö", "oe")
        .replace("ü", "ue")
        .replace("ß", "ss")
    )


def normalize_url_with_reason(url: str, prefer_https: bool = False) -> tuple[str, str]:
    url = clean_space(url)
    if not url:
        return "", "invalid_url"
    parsed, parse_reason = _parse_url_safely(url if "://" in url else f"https://{url}")
    if parsed is None:
        return "", parse_reason
    if parsed.scheme not in {"http", "https"}:
        return "", "blocked_scheme"
    if parsed.username or parsed.password:
        return "", "credentials_in_url"
    scheme = "https" if prefer_https else parsed.scheme.lower()
    host = (parsed.hostname or "").lower()
    if not host:
        return "", "invalid_url"
    try:
        port = parsed.port
    except ValueError:
        return "", "invalid_port"
    netloc = host
    if port and not ((scheme == "http" and port == 80) or (scheme == "https" and port == 443)):
        netloc = f"{host}:{port}"
    path = re.sub(r"/{2,}", "/", parsed.path or "/")
    query_pairs = []
    for key, value in parse_qsl(parsed.query, keep_blank_values=True):
        if key.lower() not in TRACKING_PARAMS:
            query_pairs.append((key, value))
    return urlunparse((scheme, netloc, path, "", urlencode(query_pairs, doseq=True), "")), ""


def normalize_url(url: str, prefer_https: bool = False) -> str:
    normalized, _reason = normalize_url_with_reason(url, prefer_https)
    return normalized


def is_private_or_reserved_host(host: str) -> bool:
    clean_host = (host or "").strip().strip("[]").lower()
    if not clean_host:
        return True
    if clean_host in {"localhost", "localhost.localdomain"} or clean_host.endswith(".localhost"):
        return True
    try:
        ip = ipaddress.ip_address(clean_host)
    except ValueError:
        return False
    return bool(
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_reserved
        or ip.is_multicast
        or ip.is_unspecified
    )


def is_safe_public_url(url: str) -> tuple[bool, str]:
    parsed, parse_reason = _parse_url_safely(url)
    if parsed is None:
        return False, parse_reason
    if parsed.scheme not in {"http", "https"}:
        return False, "blocked_scheme"
    if parsed.username or parsed.password:
        return False, "credentials_in_url"
    if is_private_or_reserved_host(parsed.hostname or ""):
        return False, "private_or_local_host"
    return True, ""


def registered_domain(url_or_host: str) -> str:
    if "://" in url_or_host:
        parsed, _reason = _parse_url_safely(url_or_host)
        host = parsed.hostname if parsed else ""
    else:
        host = url_or_host
    host = (host or "").lower().strip(".")
    if host.startswith("www."):
        host = host[4:]
    parts = [part for part in host.split(".") if part]
    if len(parts) <= 2:
        return host
    suffix2 = ".".join(parts[-2:])
    suffix3 = ".".join(parts[-3:])
    if suffix2 in COMMON_MULTI_SUFFIXES and len(parts) >= 3:
        return ".".join(parts[-3:])
    if suffix3 in COMMON_MULTI_SUFFIXES and len(parts) >= 4:
        return ".".join(parts[-4:])
    return ".".join(parts[-2:])


def is_absolute_http_url(url: str) -> bool:
    parsed, _reason = _parse_url_safely(url)
    if parsed is None:
        return False
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def load_lines(path: str | Path) -> list[str]:
    file_path = Path(path)
    if not file_path.exists():
        return []
    lines: list[str] = []
    with file_path.open("r", encoding="utf-8-sig") as handle:
        for line in handle:
            clean = line.strip()
            if clean and not clean.startswith("#"):
                lines.append(clean.lower())
    return lines


def tool_root() -> Path:
    return Path(__file__).resolve().parents[1]


def repo_root() -> Path:
    return tool_root().parents[1]


def resolve_workspace_path(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return repo_root() / candidate


def env_path() -> Path:
    return tool_root() / ".env"


def load_env_file(path: Path | None = None) -> bool:
    file_path = path or env_path()
    if not file_path.exists():
        return False
    with file_path.open("r", encoding="utf-8-sig") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            if key not in SEED_CRAWLER_ENV_KEYS or key in os.environ:
                continue
            value = value.strip().strip("'").strip('"')
            os.environ[key] = value
    return True


def configured_provider(default: str = "brave") -> str:
    return os.getenv("SEED_CRAWLER_SEARCH_PROVIDER", default).strip() or default


def api_key_present() -> bool:
    return bool(os.getenv("BRAVE_SEARCH_API_KEY", "").strip())


def redact_secrets(value: str) -> str:
    redacted = value or ""
    for key in SEED_CRAWLER_ENV_KEYS:
        secret = os.getenv(key, "")
        if key.endswith("_KEY") and secret:
            redacted = redacted.replace(secret, "[redacted]")
    return redacted


def load_search_queries(path: str | Path) -> tuple[dict[str, int], list[QuerySpec]]:
    quotas = dict(DEFAULT_QUOTAS)
    queries: list[QuerySpec] = []
    current_category = ""
    in_queries = False
    sequence: dict[str, int] = defaultdict(int)
    with Path(path).open("r", encoding="utf-8-sig") as handle:
        for raw_line in handle:
            line = raw_line.rstrip()
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if not line.startswith(" ") and stripped.endswith(":"):
                current_category = stripped[:-1]
                in_queries = False
                continue
            if current_category and stripped.startswith("quota:"):
                quotas[current_category] = int(stripped.split(":", 1)[1].strip())
                continue
            if current_category and stripped == "queries:":
                in_queries = True
                continue
            if current_category and in_queries and stripped.startswith("- "):
                text = stripped[2:].strip()
                if (text.startswith("'") and text.endswith("'")) or (text.startswith('"') and text.endswith('"')):
                    text = text[1:-1]
                sequence[current_category] += 1
                queries.append(QuerySpec(current_category, f"q{sequence[current_category]:02d}", text))
    generated = generate_query_variants(queries, sequence)
    return quotas, queries + generated


def generate_query_variants(base_queries: list[QuerySpec], sequence: dict[str, int]) -> list[QuerySpec]:
    category_terms = {
        "book_blog": ["Buchblog Rezension", "Sachbuch Ratgeber Rezension"],
        "cat_pet_media": ["Katzenblog", "Katzenmagazin"],
        "parent_family_media": ["Elternblog", "Familienmagazin"],
        "podcast": ["Elternpodcast", "Katzenpodcast", "Familienpodcast"],
    }
    modifiers = ["inurl:rezension", "inurl:rezensionsexemplar", "inurl:presse", "inurl:kooperation", "inurl:gastbeitrag", "inurl:redaktion", "inurl:interview", "inurl:gaeste", "inurl:kontakt"]
    existing = {(query.category, query.text.lower()) for query in base_queries}
    generated: list[QuerySpec] = []
    for category, terms in category_terms.items():
        for term in terms:
            for modifier in modifiers:
                text = f"{term} {modifier}"
                if (category, text.lower()) in existing:
                    continue
                sequence[category] += 1
                generated.append(QuerySpec(category, f"auto{sequence[category]:02d}", text, generated=True))
    return generated


def load_scoring(path: str | Path) -> dict[str, int]:
    defaults = {
        "min_score": 65,
        "topic_max": 30,
        "editorial_max": 25,
        "activity_max": 20,
        "credibility_max": 15,
        "approachability_max": 10,
        "penalty_paid_publication": 40,
        "penalty_dofollow_sale": 60,
        "penalty_affiliate": 15,
        "penalty_contentfarm": 30,
        "penalty_no_contact": 10,
        "penalty_large_portal": 15,
        "penalty_inactive": 20,
        "penalty_romance_only": 25,
    }
    file_path = Path(path)
    if not file_path.exists():
        return defaults
    with file_path.open("r", encoding="utf-8-sig") as handle:
        for line in handle:
            clean = line.strip()
            if not clean or clean.startswith("#") or ":" not in clean:
                continue
            key, value = clean.split(":", 1)
            value = value.strip()
            if re.fullmatch(r"-?\d+", value):
                defaults[key.strip()] = int(value)
    return defaults


def read_search_results_file(path: Path) -> list[SearchResult]:
    if not path.exists():
        raise FileNotFoundError(path)
    rows: list[SearchResult] = []
    url_pattern = re.compile(r"https?://[^\s,;\"']+", re.IGNORECASE)
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        sample = handle.read(4096)
        handle.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
        except csv.Error:
            dialect = csv.excel
        reader = csv.DictReader(handle, dialect=dialect)
        if reader.fieldnames:
            for row in reader:
                url = row.get("url") or row.get("URL") or row.get("link") or row.get("Link") or ""
                if not url:
                    for cell in row.values():
                        match = url_pattern.search(cell or "")
                        if match:
                            url = match.group(0)
                            break
                normalized, _reason = normalize_url_with_reason(url)
                if normalized or clean_space(url):
                    rows.append(
                        SearchResult(
                            url=normalized or clean_space(url),
                            title=row.get("title", "") or row.get("name", "") or row.get("Name", ""),
                            snippet=row.get("snippet", "") or row.get("notes", ""),
                            provider="file",
                            query_id=row.get("query_id", "") or row.get("query", ""),
                            query=row.get("query", ""),
                            category_hint=row.get("category", ""),
                        )
                    )
        else:
            handle.seek(0)
            for raw in handle:
                for match in url_pattern.finditer(raw):
                    raw_url = match.group(0)
                    normalized, _reason = normalize_url_with_reason(raw_url)
                    if normalized or clean_space(raw_url):
                        rows.append(SearchResult(url=normalized or clean_space(raw_url), provider="file"))
    return rows


class Blocklists:
    def __init__(self, config_dir: Path) -> None:
        self.domain_terms = load_lines(config_dir / "domain_blocklist.txt")
        self.url_patterns = load_lines(config_dir / "url_pattern_blocklist.txt")
        self.negative_terms = load_lines(config_dir / "negative_terms.txt")

    def blocked_domain_reason(self, url: str) -> str:
        parsed, reason = _parse_url_safely(url)
        if parsed is None:
            return reason
        host = (parsed.hostname or "").lower()
        for term in self.domain_terms:
            if term in host:
                return f"blocked_domain:{term}"
        return ""

    def blocked_url_reason(self, url: str) -> str:
        parsed, reason = _parse_url_safely(url)
        if parsed is None:
            return reason
        lowered = url.lower()
        path = parsed.path.lower()
        for pattern in self.url_patterns:
            if pattern in lowered or pattern in path:
                return f"blocked_url_pattern:{pattern}"
        if any(path.endswith(ext) for ext in HTML_EXTENSIONS_BLOCKED):
            return "non_html_extension"
        return ""


class Cache:
    def __init__(self, root: Path, ttl_days: int = 14, enabled: bool = True) -> None:
        self.root = root
        self.ttl = timedelta(days=ttl_days)
        self.enabled = enabled
        if enabled:
            self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
        return self.root / f"{digest}.json"

    def get(self, key: str) -> dict | None:
        if not self.enabled:
            return None
        path = self._path(key)
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            cached_at = datetime.fromisoformat(data.get("cached_at", ""))
        except (ValueError, OSError, json.JSONDecodeError):
            return None
        if datetime.now(UTC) - cached_at > self.ttl:
            return None
        return data.get("payload")

    def set(self, key: str, payload: dict) -> None:
        if not self.enabled:
            return
        data = {"cached_at": datetime.now(UTC).isoformat(), "payload": payload}
        self._path(key).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


class ControlledCrawler:
    def __init__(
        self,
        blocklists: Blocklists,
        cache: Cache,
        max_pages_per_domain: int = 8,
        timeout: float = 15.0,
        max_bytes: int = 2_000_000,
        request_delay: float = 1.2,
        max_redirects: int = 5,
    ) -> None:
        self.blocklists = blocklists
        self.cache = cache
        self.max_pages_per_domain = max_pages_per_domain
        self.timeout = timeout
        self.max_bytes = max_bytes
        self.request_delay = request_delay
        self.max_redirects = max_redirects
        self.robots: dict[str, RobotFileParser] = {}
        self.last_request_at: dict[str, float] = {}
        self.errors: list[str] = []
        self.opener = build_opener(NoRedirectHandler)

    def crawl_domain(self, landing_url: str) -> list[PageSnapshot]:
        normalized = normalize_url(landing_url)
        if not normalized:
            return [PageSnapshot(landing_url, landing_url, skipped_reason="invalid_url", fetched_at=now_iso())]
        urls = self._initial_urls(normalized)
        snapshots: list[PageSnapshot] = []
        seen: set[str] = set()
        for url in urls:
            if len(snapshots) >= self.max_pages_per_domain:
                break
            if normalize_url(url) in seen:
                continue
            seen.add(normalize_url(url))
            page = self.fetch(url)
            snapshots.append(page)
            for link in relevant_internal_links(page):
                if len(urls) + len(snapshots) >= self.max_pages_per_domain * 3:
                    break
                if normalize_url(link) not in seen:
                    urls.append(link)
        return snapshots[: self.max_pages_per_domain]

    def _initial_urls(self, url: str) -> list[str]:
        parsed, _reason = _parse_url_safely(url)
        if parsed is None:
            return [url]
        home = urlunparse((parsed.scheme, parsed.netloc, "/", "", "", ""))
        urls = [url]
        if home != url:
            urls.append(home)
        for slug in ["rezensionsexemplare", "rezensionsexemplar", "presse", "redaktion", "kooperation", "gastbeitrag", "kontakt", "gaeste", "interview"]:
            urls.append(urljoin(home, slug + "/"))
        return urls

    def _robots_for(self, url: str) -> RobotFileParser:
        parsed, _reason = _parse_url_safely(url)
        if parsed is None:
            parser = RobotFileParser()
            parser.parse(["User-agent: *", "Disallow: /"])
            return parser
        base = f"{parsed.scheme}://{parsed.netloc}"
        if base in self.robots:
            return self.robots[base]
        parser = RobotFileParser()
        robots_url = urljoin(base, "/robots.txt")
        parser.set_url(robots_url)
        try:
            request = Request(robots_url, headers={"User-Agent": USER_AGENT, "Accept": "text/plain,*/*"})
            with self.opener.open(request, timeout=self.timeout) as response:
                body = response.read(200_000).decode(response.headers.get_content_charset() or "utf-8", errors="replace")
            parser.parse(body.splitlines())
        except Exception:
            parser.parse(["User-agent: *", "Allow: /"])
        self.robots[base] = parser
        return parser

    def can_fetch(self, url: str) -> bool:
        return self._robots_for(url).can_fetch(USER_AGENT, url)

    def fetch(self, url: str) -> PageSnapshot:
        fetched_at = now_iso()
        normalized = normalize_url(url)
        if not normalized:
            return PageSnapshot(url, url, fetched_at=fetched_at, skipped_reason="invalid_url")
        safe, unsafe_reason = is_safe_public_url(normalized)
        if not safe:
            return PageSnapshot(url, normalized, fetched_at=fetched_at, skipped_reason=unsafe_reason)
        domain_reason = self.blocklists.blocked_domain_reason(normalized)
        if domain_reason:
            return PageSnapshot(url, normalized, fetched_at=fetched_at, skipped_reason=domain_reason)
        url_reason = self.blocklists.blocked_url_reason(normalized)
        if url_reason:
            return PageSnapshot(url, normalized, fetched_at=fetched_at, skipped_reason=url_reason)
        if not self.can_fetch(normalized):
            return PageSnapshot(url, normalized, fetched_at=fetched_at, skipped_reason="robots_txt_disallow")
        cached = self.cache.get(normalized)
        if cached:
            return PageSnapshot(**cached)
        parsed, parse_reason = _parse_url_safely(normalized)
        if parsed is None:
            return PageSnapshot(url, normalized, fetched_at=fetched_at, skipped_reason=parse_reason)
        host = parsed.netloc.lower()
        self._wait(host)
        current_url = normalized
        try:
            for redirect_count in range(self.max_redirects + 1):
                safe, unsafe_reason = is_safe_public_url(current_url)
                if not safe:
                    snapshot = PageSnapshot(url, current_url, fetched_at=fetched_at, skipped_reason=f"redirect_{unsafe_reason}" if redirect_count else unsafe_reason)
                    self.cache.set(normalized, asdict(snapshot))
                    return snapshot
                request = Request(current_url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"})
                try:
                    response = self.opener.open(request, timeout=self.timeout)
                    break
                except HTTPError as exc:
                    if exc.code in {301, 302, 303, 307, 308} and exc.headers.get("Location"):
                        if redirect_count >= self.max_redirects:
                            snapshot = PageSnapshot(url, current_url, status_code=exc.code, fetched_at=fetched_at, skipped_reason="redirect_limit")
                            self.cache.set(normalized, asdict(snapshot))
                            return snapshot
                        redirect_url, redirect_reason = _join_url_safely(current_url, exc.headers["Location"])
                        if not redirect_url:
                            snapshot = PageSnapshot(url, current_url, status_code=exc.code, fetched_at=fetched_at, skipped_reason=f"redirect_{redirect_reason or 'invalid_url'}")
                            self.cache.set(normalized, asdict(snapshot))
                            return snapshot
                        current_url = redirect_url
                        continue
                    raise
            else:
                snapshot = PageSnapshot(url, current_url, fetched_at=fetched_at, skipped_reason="redirect_limit")
                self.cache.set(normalized, asdict(snapshot))
                return snapshot
            with response:
                status = getattr(response, "status", 0) or 0
                content_type = response.headers.get("content-type", "").lower()
                final_url, final_reason = normalize_url_with_reason(response.geturl())
                if not final_url:
                    snapshot = PageSnapshot(url, current_url, status_code=status, fetched_at=fetched_at, skipped_reason=f"redirect_{final_reason or 'invalid_url'}")
                    self.cache.set(normalized, asdict(snapshot))
                    return snapshot
                safe, unsafe_reason = is_safe_public_url(final_url)
                if not safe:
                    snapshot = PageSnapshot(url, final_url, status_code=status, fetched_at=fetched_at, skipped_reason=f"redirect_{unsafe_reason}")
                    self.cache.set(normalized, asdict(snapshot))
                    return snapshot
                if content_type and "text/html" not in content_type and "application/xhtml+xml" not in content_type:
                    snapshot = PageSnapshot(url, final_url, status_code=status, fetched_at=fetched_at, skipped_reason=f"non_html:{content_type}")
                    self.cache.set(normalized, asdict(snapshot))
                    return snapshot
                chunks: list[bytes] = []
                total = 0
                while True:
                    chunk = response.read(65536)
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > self.max_bytes:
                        snapshot = PageSnapshot(url, final_url, status_code=status, fetched_at=fetched_at, skipped_reason="html_size_limit")
                        self.cache.set(normalized, asdict(snapshot))
                        return snapshot
                    chunks.append(chunk)
                encoding = response.headers.get_content_charset() or "utf-8"
                html = b"".join(chunks).decode(encoding, errors="replace")
        except HTTPError as exc:
            reason = f"http_{exc.code}"
            if exc.code == 429:
                retry_after = exc.headers.get("Retry-After")
                reason = f"http_429_retry_after_{retry_after or 'missing'}"
            snapshot = PageSnapshot(url, normalized, status_code=exc.code, fetched_at=fetched_at, skipped_reason=reason)
            self.cache.set(normalized, asdict(snapshot))
            return snapshot
        except (URLError, TimeoutError, OSError) as exc:
            error = f"{type(exc).__name__}: {exc}"
            self.errors.append(error)
            return PageSnapshot(url, normalized, fetched_at=fetched_at, error=error)
        snapshot = parse_html(html, normalized)
        snapshot.requested_url = url
        snapshot.status_code = status
        snapshot.fetched_at = fetched_at
        if snapshot.canonical_url:
            canonical_url, canonical_reason = normalize_url_with_reason(snapshot.canonical_url)
            snapshot.final_url = canonical_url or final_url
            if not canonical_url and canonical_reason:
                snapshot.skipped_reason = f"canonical_{canonical_reason}"
        else:
            snapshot.final_url = normalize_url(final_url) or normalized
        self.cache.set(normalized, asdict(snapshot))
        return snapshot

    def _wait(self, host: str) -> None:
        last = self.last_request_at.get(host)
        now = time.monotonic()
        if last is not None:
            delay = self.request_delay - (now - last)
            if delay > 0:
                time.sleep(delay)
        self.last_request_at[host] = time.monotonic()


def parse_html(html: str, base_url: str) -> PageSnapshot:
    parser = TinyHTMLParser(base_url)
    try:
        parser.feed(html)
    except Exception:
        pass
    text = clean_space(" ".join(parser.text_parts))
    for match in re.finditer(r"\b20\d{2}-\d{2}-\d{2}\b|\b\d{1,2}\.\d{1,2}\.20\d{2}\b", text):
        parser.dates.append(match.group(0))
    title = clean_space(" ".join(parser.title_parts))
    return PageSnapshot(
        requested_url=base_url,
        final_url=base_url,
        title=title,
        site_name=clean_space(parser.site_name),
        headings=parser.headings[:10],
        text=text[:20000],
        links=dedupe_links(parser.links),
        canonical_url=parser.canonical_url,
        dates=parser.dates[:20],
        meta_description=clean_space(parser.meta_description),
        jsonld_dates=parser.jsonld_dates[:20],
    )


def dedupe_links(links: Iterable[tuple[str, str]]) -> list[tuple[str, str]]:
    seen: set[str] = set()
    result: list[tuple[str, str]] = []
    for url, label in links:
        normalized = normalize_url(url)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        result.append((normalized, label))
    return result


def relevant_internal_links(page: PageSnapshot) -> list[str]:
    base_domain = registered_domain(page.final_url)
    if not base_domain:
        return []
    scored: list[tuple[int, str]] = []
    for url, label in page.links:
        if registered_domain(url) != base_domain:
            continue
        parsed, _reason = _parse_url_safely(url)
        if parsed is None:
            continue
        haystack = slug_text(parsed.path + " " + label)
        score = max((weight for slug, weight in SLUG_PRIORITY if slug in haystack), default=0)
        if score:
            scored.append((score, url))
    scored.sort(key=lambda item: (-item[0], item[1]))
    return [url for _score, url in scored]


def exact_host(url: str) -> str:
    parsed, _reason = _parse_url_safely(url)
    host = (parsed.hostname if parsed else "") or ""
    return host.lower().removeprefix("www.")


def page_context(page: PageSnapshot, chars: int = 6000) -> str:
    return slug_text(" ".join([page.final_url, page.title, page.site_name, page.meta_description, " ".join(page.headings), page.text[:chars]]))


def combined_context(pages: list[PageSnapshot], search_result: SearchResult) -> str:
    return slug_text(
        " ".join(
            [search_result.title, search_result.snippet]
            + [page.final_url + " " + page.title + " " + page.site_name + " " + page.meta_description + " " + " ".join(page.headings) + " " + page.text[:6000] for page in pages]
        )
    )


def count_terms(text: str, terms: Iterable[str]) -> int:
    return sum(1 for term in terms if term in text)


def infer_entity_type(domain: str, pages: list[PageSnapshot], search_result: SearchResult) -> tuple[str, str]:
    host = exact_host(search_result.url) or domain
    if host in FORCED_DOMAIN_ENTITY:
        return FORCED_DOMAIN_ENTITY[host]
    if domain in FORCED_DOMAIN_ENTITY:
        return FORCED_DOMAIN_ENTITY[domain]
    text = combined_context(pages, search_result)
    title_context = slug_text(" ".join([domain] + [page.title + " " + page.site_name + " " + " ".join(page.headings[:2]) for page in pages[:3]]))
    if any(term in text for term in ["spotify", "apple podcasts", "youtube kanal", "instagram", "facebook"]):
        return "social_or_podcast_platform", "Plattform- oder Social-Signal"
    if any(term in text for term in ["forum", "community", "thread", "beitrag beantworten"]):
        return "forum", "Forum-/Community-Signal"
    if any(term in text for term in ["branchenbuch", "webverzeichnis", "directory", "portal eintragen"]):
        return "directory_or_aggregator", "Verzeichnis-/Aggregator-Signal"
    if any(term in text for term in ["ministerium", "behoerde", "stadtverwaltung", "universitaet", "institut"]):
        return "government_or_institution", "Institutionelles Signal"
    if any(term in text for term in ["verlag", "verlagsprogramm", "unsere autoren", "buch bestellen"]) and any(term in text for term in ["warenkorb", "shop", "produkt", "isbn"]):
        return "publisher", "Verlag/Verlagsshop-Signal"
    if any(term in text for term in ["buchhandlung", "buchshop", "buecher kaufen"]):
        return "bookstore", "Buchhandlungs-/Buchshop-Signal"
    if any(term in text for term in ["warenkorb", "checkout", "in den warenkorb", "produkt kaufen", "versandkosten"]) and not any(term in title_context for term in ["blog", "magazin", "podcast"]):
        return "online_shop", "Shop-Signal ohne unabhaengiges Medium"
    if any(term in text for term in ["coaching", "coach", "beratung", "kurs", "mentoring", "selfpublishing", "schreibberatung", "buchmarketing"]):
        return "coach_or_service_provider", "Coaching-/Serviceanbieter-Signal"
    if any(term in text for term in ["offizielle website", "pressearchiv", "vita", "termine", "tour", "ueber mich"]) and not any(term in title_context for term in ["blog", "magazin"]):
        return "personal_official_site", "persoenliche offizielle Website"
    if any(term in text for term in ["mein buch", "meine buecher", "autorenseite", "autorin", "autor"]) and any(term in text for term in ["lesungen", "buch kaufen", "mein roman"]):
        return "author_site", "Autorinnen-/Autorenseite"
    podcast_strong = count_terms(text, ["podcast", "episoden", "episode", "rss", "feed", "show", "podcastgast", "interviewgast"])
    if podcast_strong >= 3 and (any(term in title_context for term in ["podcast", "show", "folge", "episoden"]) or any(term in text for term in ["elternpodcast", "familienpodcast", "katzenpodcast", "podcastshow"])):
        return "podcast_show", "eigene Podcastshow mit Episodensignalen"
    if (count_terms(title_context, ["katze", "katzen", "haustier", "tiermagazin", "tierblog"]) >= 1 or any(term in text for term in ["katzenblog", "katzenmagazin", "haustiermagazin"])) and count_terms(text, ["katze", "katzen", "haustier", "tierverhalten", "tierschutz", "katzenblog"]) >= 2:
        return "cat_pet_editorial", "Katzen-/Haustierfokus in Titel und Inhalt"
    if (count_terms(title_context, ["eltern", "familie", "baby", "schwangerschaft", "mama", "papa"]) >= 1 or any(term in text for term in ["elternblog", "familienblog", "familienmagazin"])) and count_terms(text, ["eltern", "familie", "baby", "schwangerschaft", "kind", "kleinkind", "elternblog"]) >= 2:
        return "parent_family_editorial", "Eltern-/Familienfokus in Titel und Inhalt"
    review_count = count_terms(text, ["rezension", "rezensionen", "buchvorstellung", "gelesen", "lesemonat", "buecherblog", "buchblog"])
    if ("buchblog" in title_context or "buecherblog" in title_context or "buchblog" in text or review_count >= 3) and not any(term in text for term in ["verlagsprogramm", "coaching", "buchhandlung"]):
        return "independent_book_blog", "unabhaengige Buch-/Rezensionssignale"
    if any(term in text for term in ["shop", "produkt", "marke", "unternehmen"]) and any(term in text for term in ["magazin", "blog", "ratgeber"]):
        return "commercial_brand_blog", "kommerzielles Markenblog/Magazin"
    return "unknown", "kein eindeutiger Medientyp"


def category_for_entity(entity_type: str, category_hint: str, text: str) -> tuple[str, str]:
    if entity_type in ENTITY_CATEGORY:
        return ENTITY_CATEGORY[entity_type], f"entity_type={entity_type}"
    if entity_type == "commercial_brand_blog":
        if count_terms(text, ["katze", "katzen", "haustier"]) >= count_terms(text, ["baby", "familie", "eltern"]):
            return "cat_pet_media", "commercial_brand_blog mit Tierfokus"
        return "parent_family_media", "commercial_brand_blog mit Familienfokus"
    if category_hint in CATEGORY_ORDER and category_hint != "podcast":
        return category_hint, "nur Suchhint; Hard Gate erforderlich"
    return "cat_pet_media", "Fallback ohne Hard-Gate"


def contact_terms_for(category: str) -> list[tuple[str, str, str]]:
    common = [
        ("redaktion kontaktieren", "Redaktion kontaktieren", "editorial_contact"),
        ("pressekontakt", "Pressekontakt", "press_contact"),
        ("presseanfrage", "Presseanfrage", "press_contact"),
        ("themenvorschlag", "Themenvorschlag", "topic_pitch"),
        ("gastbeitrag", "Gastbeitrag einreichen", "guest_post"),
        ("gastartikel", "Gastbeitrag einreichen", "guest_post"),
        ("kontaktformular", "Kontaktformular", "general_contact"),
    ]
    if category == "book_blog":
        return [
            ("rezensionsexemplar anfragen", "Rezensionsexemplar anfragen/einsenden", "review_copy"),
            ("rezensionsexemplar einsenden", "Rezensionsexemplar anfragen/einsenden", "review_copy"),
            ("rezensionsexemplare willkommen", "Rezensionsexemplare willkommen", "review_copy"),
            ("buch vorschlagen", "Buch vorschlagen", "book_pitch"),
            ("buchvorschlag", "Buch vorschlagen", "book_pitch"),
            ("neuerscheinungen einsenden", "Neuerscheinungen einsenden", "book_pitch"),
        ] + common
    if category == "podcast":
        return [
            ("podcastgast werden", "Podcastgast werden", "podcast_guest"),
            ("gast im podcast", "Podcastgast werden", "podcast_guest"),
            ("interviewvorschlag", "Interviewvorschlag", "interview_pitch"),
            ("interviewgast", "Interviewgast", "interview_pitch"),
        ] + common
    return common


def find_contact_evidence(pages: list[PageSnapshot], category: str, entity_type: str) -> tuple[int, str, str, str, str]:
    best: tuple[int, str, str, str, str] = (0, "", "", "", "")
    for page in pages:
        context = page_context(page, 5000)
        path_bonus = 6 if any(slug in slug_text(page.final_url) for slug in ["kontakt", "presse", "redaktion", "kooperation", "gast", "rezension", "themenvorschlag"]) else 0
        if entity_type in {"personal_official_site", "author_site"} and "presse" in context:
            continue
        for term, label, channel in contact_terms_for(category):
            if term in context:
                score = 16 + path_bonus
                if channel in {"review_copy", "book_pitch", "podcast_guest", "interview_pitch", "guest_post", "topic_pitch"}:
                    score += 8
                snippet = evidence_snippet(page.text, term)
                candidate = (min(25, score), label, page.final_url, snippet or label, channel)
                if candidate[0] > best[0]:
                    best = candidate
        if best[0] < 8 and any(term in context for term in ["kontakt", "impressum"]):
            best = (6, "Allgemeiner Kontaktweg", page.final_url, "Kontakt/Impressum vorhanden", "general_contact")
    return best


def evidence_snippet(text: str, term: str) -> str:
    clean = safe_summary_text(text)
    lower = slug_text(clean)
    index = lower.find(term)
    if index < 0:
        return ""
    return clean[max(0, index - 80) : index + 160]


def topic_score_and_evidence(category: str, pages: list[PageSnapshot], search_result: SearchResult) -> tuple[int, str]:
    title_context = slug_text(" ".join([search_result.title, search_result.snippet] + [page.title + " " + page.site_name + " " + page.meta_description + " " + " ".join(page.headings[:2]) for page in pages]))
    body_context = combined_context(pages, search_result)
    if category == "book_blog":
        strong = count_terms(title_context, ["buchblog", "buecherblog", "rezension", "buchvorstellung"])
        body = count_terms(body_context, ["rezension", "rezensionen", "buchvorstellung", "sachbuch", "ratgeber", "buchblog"])
        return min(30, strong * 10 + body * 3), f"Buch-/Rezensionssignale strong={strong} body={body}"
    if category == "cat_pet_media":
        strong = count_terms(title_context, ["katze", "katzen", "haustier", "tiermagazin"])
        body = count_terms(body_context, ["katze", "katzen", "haustier", "tierverhalten", "tierschutz"])
        return min(30, strong * 12 + body * 3), f"Katzen-/Haustiersignale strong={strong} body={body}"
    if category == "parent_family_media":
        strong = count_terms(title_context, ["eltern", "familie", "baby", "schwangerschaft", "mama", "papa"])
        body = count_terms(body_context, ["eltern", "familie", "baby", "schwangerschaft", "kind", "kleinkind"])
        return min(30, strong * 10 + body * 3), f"Eltern-/Familiensignale strong={strong} body={body}"
    if category == "podcast":
        strong = count_terms(title_context, ["podcast", "show", "episode", "folge"])
        body = count_terms(body_context, ["podcast", "episoden", "episode", "folge", "rss", "podcastgast"])
        return min(30, strong * 10 + body * 3), f"Podcastsignale strong={strong} body={body}"
    return 0, "keine belastbare Themenpassung"


def assess_activity(pages: list[PageSnapshot]) -> tuple[int, str, str, str, str]:
    now = datetime.now(UTC)
    evidence: list[tuple[int, datetime, str, str]] = []
    for page in pages:
        for raw in page.jsonld_dates:
            parsed = parse_date(raw)
            if parsed and parsed <= now:
                evidence.append((1, parsed, page.final_url, raw))
        for raw in page.dates:
            parsed = parse_date(raw)
            if parsed and parsed <= now:
                page_context_short = page_context(page, 2500)
                if any(term in page_context_short for term in ["archiv", "copyright", "kommentar", "veranstaltung", "termine"]) and "article" not in page_context_short and "artikel" not in page_context_short and "episode" not in page_context_short:
                    continue
                evidence.append((2, parsed, page.final_url, raw))
    if evidence:
        evidence.sort(key=lambda item: (item[1], -item[0]), reverse=True)
        _priority, newest, url, raw = evidence[0]
        months = max(0, int((now - newest).days / 30))
        if newest >= now - timedelta(days=365):
            return (20 if newest >= now - timedelta(days=183) else 15, f"letzter Inhalt vor {months} Monaten", url, newest.date().isoformat(), "high")
        if newest >= now - timedelta(days=548):
            return 4, f"letzter datierter Inhalt vor {months} Monaten", url, newest.date().isoformat(), "medium"
        return 0, f"letzter datierter Inhalt vor {months} Monaten", url, newest.date().isoformat(), "high"
    combined = slug_text(" ".join(page.title + " " + page.text[:2000] for page in pages))
    if any(term in combined for term in ["aktuelle beitraege", "neueste beitraege", "neue folge", "aktuelle folge"]):
        return 6, "Aktivitaet nicht eindeutig datierbar", "", "", "low"
    return 2, "Aktivitaet nicht eindeutig datierbar", "", "", "low"


def hard_gate_check(
    entity_type: str,
    category: str,
    topic_score: int,
    contact_score: int,
    activity_score: int,
    activity_confidence: str,
    text: str,
) -> tuple[bool, str]:
    if entity_type not in REGULAR_ALLOWED_ENTITY_TYPES:
        if entity_type == "commercial_brand_blog" and contact_score >= 18 and topic_score >= 24:
            return True, "commercial_brand_blog mit konkreter redaktioneller Offenheit"
        return False, f"entity_type_not_allowed:{entity_type}"
    expected = ENTITY_CATEGORY.get(entity_type)
    if expected != category:
        return False, f"category_entity_mismatch:{entity_type}->{category}"
    if topic_score < 18:
        return False, "weak_topic_fit"
    if contact_score < 12:
        return False, "no_editorial_contact_evidence"
    if activity_confidence == "low" and activity_score < 7:
        return False, "activity_confidence_low"
    if activity_score == 0:
        return False, "inactive_or_stale"
    if category == "podcast":
        podcast_signals = count_terms(text, ["podcast", "episoden", "episode", "folge", "rss", "podcastgast", "show"])
        if podcast_signals < 3:
            return False, "insufficient_own_podcast_signals"
    if category == "book_blog" and entity_type != "independent_book_blog":
        return False, "not_independent_book_blog"
    return True, "passed"


def evaluate_domain(
    search_result: SearchResult,
    pages: list[PageSnapshot],
    blocklists: Blocklists,
    scoring: dict[str, int],
    min_score: int,
) -> Candidate:
    domain = registered_domain(search_result.url)
    usable_pages = [page for page in pages if not page.error and not page.skipped_reason and page.text]
    if not usable_pages:
        reason = pages[0].skipped_reason or pages[0].error if pages else "no_pages"
        return Candidate(search_result.url, normalize_url(search_result.url), domain, domain, search_result.category_hint, source_for(search_result), search_result.query_id, rejection_reason=reason, status="rejected", hard_gate_reason=reason)
    best_page = choose_best_page(usable_pages)
    lowered = combined_context(usable_pages, search_result)
    entity_type, entity_evidence = infer_entity_type(domain, usable_pages, search_result)
    category, category_evidence = category_for_entity(entity_type, search_result.category_hint, lowered)
    block_reason = negative_content_reason(lowered, blocklists.negative_terms)
    name = determine_name(best_page, domain)
    topic_score, topic_evidence = topic_score_and_evidence(category, usable_pages, search_result)
    editorial_score, editorial_signal, contact_url, contact_text, channel_type = find_contact_evidence(usable_pages, category, entity_type)
    activity_score, activity_signal, activity_url, activity_date, activity_confidence = assess_activity(usable_pages)
    credibility_score = score_credibility(usable_pages, lowered)
    approachability_score = score_approachability(usable_pages, lowered)
    penalty_score, penalty_reasons = score_penalties(lowered, scoring)
    if editorial_score < 12:
        penalty_score += scoring["penalty_no_contact"]
        penalty_reasons.append("kein Kontaktweg")
    total = max(0, min(100, topic_score + editorial_score + activity_score + credibility_score + approachability_score - penalty_score))
    hard_gate_passed, hard_gate_reason = hard_gate_check(entity_type, category, topic_score, editorial_score, activity_score, activity_confidence, lowered)
    rejection_reason = block_reason or ("" if hard_gate_passed else hard_gate_reason)
    status = "accepted" if hard_gate_passed else "rejected"
    if block_reason:
        status = "rejected"
        total = min(total, 40)
        hard_gate_passed = False
        hard_gate_reason = block_reason
    elif total < max(min_score, FINAL_MIN_SCORE):
        status = "rejected"
        rejection_reason = f"score_below_min:{total}"
        hard_gate_passed = False
        hard_gate_reason = rejection_reason
    contact_signal = channel_type or contact_signal_for(lowered)
    notes = build_notes(category, editorial_signal, lowered, activity_signal, total)
    final_seed_url = normalize_url(best_page.final_url, prefer_https=best_page.final_url.lower().startswith("https://")) or normalize_url(search_result.url)
    return Candidate(
        candidate_url=search_result.url,
        final_seed_url=final_seed_url,
        domain=domain,
        name=name,
        category=category,
        discovery_source=source_for(search_result),
        query_id=search_result.query_id,
        topic_score=topic_score,
        editorial_score=editorial_score,
        activity_score=activity_score,
        credibility_score=credibility_score,
        approachability_score=approachability_score,
        penalty_score=penalty_score,
        total_score=total,
        contact_signal=contact_signal,
        activity_signal=activity_signal,
        editorial_signal=editorial_signal,
        rejection_reason=rejection_reason or "; ".join(penalty_reasons),
        status=status,
        notes=notes,
        entity_type=entity_type,
        entity_type_evidence=entity_evidence,
        category_evidence=category_evidence,
        topic_evidence=topic_evidence,
        contact_evidence_url=contact_url,
        contact_evidence_text=safe_summary_text(contact_text),
        activity_evidence_url=activity_url,
        activity_evidence_date=activity_date,
        activity_confidence=activity_confidence,
        hard_gate_passed=hard_gate_passed,
        hard_gate_reason=hard_gate_reason,
        channel_type=channel_type,
    )


def choose_best_page(pages: list[PageSnapshot]) -> PageSnapshot:
    def page_score(page: PageSnapshot) -> tuple[int, int, str]:
        haystack = slug_text(page.final_url + " " + page.title + " " + " ".join(page.headings) + " " + page.text[:2000])
        path = slug_text(page.final_url)
        priority = 20
        if any(slug in path for slug in ["rezensionsexemplar", "buchvorschlag", "themenvorschlag", "podcastgast", "gaeste", "gastbeitrag", "redaktion", "presse"]):
            priority = 120
        elif any(slug in path for slug in ["kontakt", "ueber-uns", "about"]):
            priority = 95
        elif any(slug in path for slug in ["archiv", "rezensionen", "magazin", "blog"]):
            priority = 55
        elif path.endswith("/"):
            priority = 45
        priority = max(priority, max((weight for slug, weight in SLUG_PRIORITY if slug in haystack), default=20))
        if any(slug in path for slug in ["suche", "search", "produkt", "shop", "warenkorb", "pressearchiv"]):
            priority -= 80
        text_score = 0
        if "rezensionsexemplar" in haystack:
            text_score += 20
        if "podcastgast" in haystack or "interview" in haystack:
            text_score += 15
        if "gastbeitrag" in haystack or "themenvorschlag" in haystack:
            text_score += 12
        return (priority + text_score, len(page.text), page.final_url)

    return sorted(pages, key=page_score, reverse=True)[0]


def assign_category(category_hint: str, text: str, url: str) -> str:
    if category_hint in CATEGORY_ORDER:
        hinted = category_hint
    else:
        hinted = ""
    if "podcast" in text or any(term in text for term in ["episode", "episoden", "podcastgast"]):
        return "podcast"
    has_review_policy = any(term in text for term in ["rezensionsexemplar", "buecher zur rezension", "buchvorschlaege", "neuerscheinungen einsenden"])
    has_book = any(term in text for term in ["buchblog", "buchrezension", "sachbuch", "ratgeber", "buchvorstellung"])
    has_cat = any(term in text for term in ["katze", "katzen", "haustier", "tiermagazin"])
    has_family = any(term in text for term in ["eltern", "familie", "baby", "schwangerschaft", "kleinkind"])
    if has_review_policy and has_book:
        return "book_blog"
    if hinted:
        return hinted
    if has_cat and not has_family:
        return "cat_pet_media"
    if has_family:
        return "parent_family_media"
    if has_book:
        return "book_blog"
    return "cat_pet_media"


def score_topic(category: str, text: str) -> int:
    family = sum(1 for term in ["baby", "eltern", "familie", "schwangerschaft", "kleinkind", "geburt"] if term in text)
    cats = sum(1 for term in ["katze", "katzen", "haustier", "tierverhalten", "tierschutz"] if term in text)
    books = sum(1 for term in ["buchblog", "buchrezension", "rezensionsexemplar", "sachbuch", "ratgeber", "buchvorstellung"] if term in text)
    podcasts = sum(1 for term in ["podcast", "episode", "interview", "podcastgast", "gaeste"] if term in text)
    if category == "book_blog":
        return min(30, books * 6 + family * 3 + cats * 3)
    if category == "cat_pet_media":
        return min(30, cats * 8 + family * 4 + books * 2)
    if category == "parent_family_media":
        return min(30, family * 7 + cats * 3 + books * 2)
    if category == "podcast":
        return min(30, podcasts * 8 + family * 4 + cats * 4 + books * 2)
    return min(30, family * 5 + cats * 5 + books * 3)


def score_editorial(category: str, text: str) -> tuple[int, str]:
    checks = [
        (25, "Rezensionsexemplare ausdruecklich moeglich", ["rezensionsexemplar", "rezensionsexemplare", "buecher zur rezension"]),
        (20, "Buch- oder Themenvorschlaege moeglich", ["buchvorschlag", "buchvorschlaege", "neuerscheinungen einsenden", "themenvorschlag", "themenvorschlaege"]),
        (20, "Podcastgaeste oder Interviews moeglich", ["podcastgast", "gast im podcast", "interviewgast", "interview"]),
        (18, "Gastbeitraege moeglich", ["gastbeitrag", "gastautor", "gastartikel"]),
        (15, "Presse- oder Redaktionskontakt", ["presseanfrage", "redaktion kontaktieren", "redaktion", "presse"]),
        (6, "Allgemeiner Kontaktweg", ["kontakt", "impressum", "kontaktformular"]),
    ]
    for score, label, terms in checks:
        if any(term in text for term in terms):
            return score, label
    return 0, "Kein redaktionelles Signal"


def parse_date(value: str) -> datetime | None:
    clean = value.strip()
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S.%f%z", "%d.%m.%Y"):
        try:
            parsed = datetime.strptime(clean[: len(datetime.now().strftime(fmt.replace("%z", "")))], fmt) if "%z" not in fmt else datetime.strptime(clean.replace("Z", "+0000"), fmt)
            return parsed.replace(tzinfo=UTC) if parsed.tzinfo is None else parsed.astimezone(UTC)
        except ValueError:
            continue
    match = re.search(r"(20\d{2})-(\d{2})-(\d{2})", clean)
    if match:
        try:
            return datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)), tzinfo=UTC)
        except ValueError:
            return None
    match = re.search(r"(\d{1,2})\.(\d{1,2})\.(20\d{2})", clean)
    if match:
        try:
            return datetime(int(match.group(3)), int(match.group(2)), int(match.group(1)), tzinfo=UTC)
        except ValueError:
            return None
    return None


def score_activity(pages: list[PageSnapshot]) -> tuple[int, str]:
    score, signal, _url, _date, _confidence = assess_activity(pages)
    return score, signal


def score_credibility(pages: list[PageSnapshot], text: str) -> int:
    score = 0
    if any(term in text for term in ["autor", "autorin", "redaktion", "ueber uns", "uber uns"]):
        score += 4
    if "impressum" in text:
        score += 3
    if any(term in text for term in ["artikel", "rezension", "magazin", "podcastfolge", "episode"]):
        score += 3
    if any(term in text for term in ["meinung", "erfahrung", "kritik", "bewertung"]):
        score += 2
    if sum(1 for page in pages if len(page.text) > 500) >= 2:
        score += 3
    return min(15, score)


def score_approachability(pages: list[PageSnapshot], text: str) -> int:
    score = 0
    if has_contact_signal(text):
        score += 4
    if any(term in text for term in ["blog", "freie redaktion", "kleines team", "inhaber", "herausgeber"]):
        score += 3
    if any(term in text for term in ["nischen", "katzen", "familie", "eltern", "buchblog"]):
        score += 3
    if any(term in text for term in ["konzern", "ag ", "gmbh", "gruppe", "international"]):
        score -= 2
    return max(0, min(10, score))


def score_penalties(text: str, scoring: dict[str, int]) -> tuple[int, list[str]]:
    penalty = 0
    reasons: list[str] = []
    if any(term in text for term in ["dofollow-link kaufen", "dofollow link kaufen", "backlink kaufen", "linkverkauf"]):
        penalty += scoring["penalty_dofollow_sale"]
        reasons.append("Dofollow- oder Linkverkauf")
    if any(term in text for term in ["garantierte veroeffentlichung", "garantierte publikation", "gegen bezahlung veroeffentlichen"]):
        penalty += scoring["penalty_paid_publication"]
        reasons.append("bezahlte Veroeffentlichung")
    if text.count("affiliate") >= 3 or "affiliate-link" in text:
        penalty += scoring["penalty_affiliate"]
        reasons.append("Affiliate-lastig")
    if any(term in text for term in ["contentfarm", "ki generiert", "automatisch generiert"]):
        penalty += scoring["penalty_contentfarm"]
        reasons.append("Contentfarm-Signal")
    if any(term in text for term in ["konzern", "riesiges portal", "masssenportal"]):
        penalty += scoring["penalty_large_portal"]
        reasons.append("sehr grosse Website")
    if any(term in text for term in ["romance", "thriller", "fantasy"]):
        if not any(term in text for term in ["sachbuch", "ratgeber", "familie", "katze", "haustier"]):
            penalty += scoring["penalty_romance_only"]
            reasons.append("reiner Belletristik-Fokus")
    return penalty, reasons


def negative_content_reason(text: str, negative_terms: list[str]) -> str:
    for term in negative_terms:
        if term in text:
            return f"negative_term:{term}"
    if "hund" in text and "katze" not in text and "haustier" not in text:
        return "dog_only"
    if any(term in text for term in ["warenkorb", "checkout", "produkt kaufen"]) and not any(term in text for term in ["magazin", "blog", "ratgeber"]):
        return "shop_without_editorial_context"
    return ""


def has_contact_signal(text: str) -> bool:
    return any(term in text for term in ["kontakt", "impressum", "kontaktformular", "redaktion", "presse", "gastbeitrag", "podcastgast", "rezensionsexemplar"])


def contact_signal_for(text: str) -> str:
    if "rezensionsexemplar" in text:
        return "review_copies"
    if "podcastgast" in text or "interview" in text:
        return "guest_or_interview"
    if "gastbeitrag" in text:
        return "guest_post"
    if "redaktion" in text or "presse" in text:
        return "editorial_contact"
    if "kontakt" in text or "impressum" in text:
        return "general_contact"
    return ""


def determine_name(page: PageSnapshot, domain: str) -> str:
    candidates = [page.site_name, *page.headings[:2], page.title]
    suffixes = list(GENERIC_NAME_PARTS)
    for candidate in candidates:
        clean = clean_space(candidate)
        if not clean:
            continue
        clean = re.split(r"\s+[|\-–]\s+", clean)[0].strip()
        lowered = slug_text(clean)
        if lowered in GENERIC_NAME_PARTS or clean.lower().startswith("http"):
            continue
        for suffix in suffixes:
            clean = re.sub(rf"\b{re.escape(suffix)}\b", "", clean, flags=re.IGNORECASE).strip(" -|")
        if slug_text(clean) in GENERIC_NAME_PARTS:
            continue
        if clean and "." not in clean:
            return clean[:120]
        if clean and len(clean) < 80:
            return clean
    domain_name = domain.split(".")[0].replace("-", " ").title()
    return domain_name or domain


def source_for(result: SearchResult) -> str:
    category = result.category_hint if result.category_hint in CATEGORY_ORDER else "unknown"
    query_id = result.query_id or "import01"
    return f"crawler:{result.provider or 'unknown'}:{category}:{query_id}".replace(",", "")


def build_notes(category: str, editorial_signal: str, text: str, activity_signal: str, score: int) -> str:
    topics: list[str] = []
    if any(term in text for term in ["katze", "katzen"]):
        topics.append("Katzenthemen")
    if any(term in text for term in ["baby", "eltern", "familie", "schwangerschaft"]):
        topics.append("Familienthemen")
    if any(term in text for term in ["sachbuch", "ratgeber", "buchrezension"]):
        topics.append("Sachbuch/Ratgeber")
    if any(term in text for term in ["podcast", "episode"]):
        topics.append("Podcast")
    topic = " und ".join(topics[:2]) if topics else "thematisch passend"
    parts = [CATEGORY_LABELS.get(category, category), editorial_signal, topic, activity_signal, f"Score {score}/100"]
    return clean_space("; ".join(part for part in parts if part)).replace("\n", " ")


def select_final(candidates: list[Candidate], quotas: dict[str, int], target: int) -> tuple[list[Candidate], dict[str, int]]:
    accepted = [
        candidate
        for candidate in candidates
        if candidate.status == "accepted"
        and candidate.hard_gate_passed
        and candidate.entity_type in (REGULAR_ALLOWED_ENTITY_TYPES | {"commercial_brand_blog"})
        and candidate.total_score >= FINAL_MIN_SCORE
    ]
    by_domain: dict[str, Candidate] = {}
    for candidate in sorted(accepted, key=lambda item: (-item.total_score, item.domain, item.final_seed_url)):
        existing = by_domain.get(candidate.domain)
        if existing is None or candidate.total_score > existing.total_score:
            by_domain[candidate.domain] = candidate
    unique = list(by_domain.values())
    effective_quotas = compute_quotas(quotas, target)
    selected: list[Candidate] = []
    selected_domains: set[str] = set()
    for category in CATEGORY_ORDER:
        quota = effective_quotas.get(category, 0)
        pool = sorted([item for item in unique if item.category == category], key=lambda item: (-item.total_score, item.domain))
        for item in pool[:quota]:
            selected.append(item)
            selected_domains.add(item.domain)
    if len(selected) < target:
        overflow = sorted(
            [item for item in unique if item.domain not in selected_domains and item.total_score >= 80],
            key=lambda item: (CATEGORY_ORDER.index(item.category) if item.category in CATEGORY_ORDER else 99, -item.total_score, item.domain),
        )
        for item in overflow:
            if len(selected) >= target:
                break
            selected.append(item)
            selected_domains.add(item.domain)
    selected.sort(key=lambda item: (CATEGORY_ORDER.index(item.category) if item.category in CATEGORY_ORDER else 99, -item.total_score, item.domain))
    missing = {category: max(0, effective_quotas.get(category, 0) - sum(1 for item in selected if item.category == category)) for category in CATEGORY_ORDER}
    return selected[:target], missing


def compute_quotas(quotas: dict[str, int], target: int) -> dict[str, int]:
    total = sum(quotas.get(category, 0) for category in CATEGORY_ORDER) or 1
    if target == total:
        return {category: quotas.get(category, 0) for category in CATEGORY_ORDER}
    raw = {category: target * quotas.get(category, 0) / total for category in CATEGORY_ORDER}
    computed = {category: int(raw[category]) for category in CATEGORY_ORDER}
    while sum(computed.values()) < target:
        category = max(CATEGORY_ORDER, key=lambda item: raw[item] - computed[item])
        computed[category] += 1
    return computed


def write_seed_csv(path: Path, candidates: list[Candidate], overwrite: bool) -> Path | None:
    backup: Path | None = None
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = path.with_name(f"{path.stem}.backup-{timestamp}{path.suffix}")
        path.replace(backup)
        if not overwrite:
            logging.warning("Bestehende seeds.csv wurde vor dem Ueberschreiben gesichert: %s", backup)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["url", "name", "source", "notes"])
        writer.writeheader()
        for candidate in candidates:
            writer.writerow({"url": candidate.final_seed_url, "name": candidate.name, "source": candidate.discovery_source, "notes": candidate.notes})
    return backup


def write_audit_csv(path: Path, candidates: list[Candidate]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "candidate_url",
        "final_seed_url",
        "domain",
        "name",
        "category",
        "entity_type",
        "entity_type_evidence",
        "category_evidence",
        "topic_evidence",
        "discovery_source",
        "query_id",
        "topic_score",
        "editorial_score",
        "activity_score",
        "credibility_score",
        "approachability_score",
        "penalty_score",
        "total_score",
        "contact_signal",
        "contact_evidence_url",
        "contact_evidence_text",
        "activity_signal",
        "activity_evidence_url",
        "activity_evidence_date",
        "activity_confidence",
        "editorial_signal",
        "hard_gate_passed",
        "hard_gate_reason",
        "channel_type",
        "rejection_reason",
        "status",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for candidate in candidates:
            writer.writerow({field_name: getattr(candidate, field_name) for field_name in fields})


def write_report(path: Path, report: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


def safe_summary_text(value: str) -> str:
    without_email = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "[Kontakt entfernt]", value or "")
    return clean_space(without_email).replace("|", "-")


def thematic_signal(candidate: Candidate) -> str:
    notes = candidate.notes
    for marker in ["Katzenthemen", "Familienthemen", "Sachbuch/Ratgeber", "Podcast"]:
        if marker in notes:
            return marker
    return CATEGORY_LABELS.get(candidate.category, candidate.category)


def warning_signal(candidate: Candidate) -> str:
    if candidate.penalty_score:
        return f"Abzuege: {candidate.penalty_score}"
    if "nicht eindeutig" in candidate.activity_signal.lower():
        return "Aktivitaet nicht eindeutig datierbar"
    return ""


def write_pilot_summary(path: Path, report: dict, final: list[Candidate], candidates: list[Candidate]) -> None:
    rejection_counter = Counter(item.rejection_reason or "none" for item in candidates if item.status != "accepted")
    lines = [
        "# Seed-Crawler Pilot-Zusammenfassung",
        "",
        f"- Rohresultate: {report.get('raw_url_count', 0)}",
        f"- Gepruefte Domains: {report.get('checked_domains', 0)}",
        f"- Akzeptierte Seeds: {len(final)}",
        f"- Geschaetzte Search-API-Anfragen: {report.get('estimated_search_api_requests', 0)}",
        f"- Ablehnungen: {sum(rejection_counter.values())}",
        "",
        "## Kategorieverteilung",
        "",
    ]
    category_counts = Counter(item.category for item in final)
    for category in CATEGORY_ORDER:
        lines.append(f"- {category}: {category_counts.get(category, 0)}")
    lines.extend(["", "## Haeufigste Ablehnungsgruende", ""])
    for reason, count in rejection_counter.most_common(8):
        lines.append(f"- {safe_summary_text(reason)}: {count}")
    if not rejection_counter:
        lines.append("- Keine")
    lines.extend(["", "## Akzeptierte Seeds", ""])
    if final:
        lines.append("| Name | URL | Kategorie | Score | Thema | Kontakt/Redaktion | Aktivitaet | Warnhinweise |")
        lines.append("| --- | --- | --- | ---: | --- | --- | --- | --- |")
        for item in final:
            lines.append(
                "| "
                + " | ".join(
                    [
                        safe_summary_text(item.name),
                        safe_summary_text(item.final_seed_url),
                        item.category,
                        str(item.total_score),
                        safe_summary_text(thematic_signal(item)),
                        safe_summary_text(item.editorial_signal or item.contact_signal),
                        safe_summary_text(item.activity_signal),
                        safe_summary_text(warning_signal(item)),
                    ]
                )
                + " |"
            )
    else:
        lines.append("Keine ausreichend guten Seeds gefunden.")
    if len(final) < PILOT_TARGET:
        lines.extend(["", f"Hinweis: Es wurden weniger als {PILOT_TARGET} ausreichend gute Seeds gefunden. Der Mindestscore wurde nicht abgesenkt."])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def validate_seed_csv(path: Path, target: int = 100, blocklists: Blocklists | None = None, audit_path: Path | None = None) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return [f"Datei nicht gefunden: {path}"]
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            sample = handle.read(4096)
            handle.seek(0)
            if ";" in sample.splitlines()[0] if sample.splitlines() else False:
                errors.append("Header nutzt offenbar Semikolon statt Komma.")
            reader = csv.DictReader(handle)
            if reader.fieldnames != ["url", "name", "source", "notes"]:
                errors.append(f"Header falsch: {reader.fieldnames}")
            seen_domains: set[str] = set()
            for line_no, row in enumerate(reader, start=2):
                if set(row.keys()) != {"url", "name", "source", "notes"}:
                    errors.append(f"Zeile {line_no}: zusaetzliche oder fehlende Spalten.")
                url = row.get("url", "")
                name = row.get("name", "")
                notes = row.get("notes", "")
                if not url:
                    errors.append(f"Zeile {line_no}: URL leer.")
                if not name:
                    errors.append(f"Zeile {line_no}: Name leer.")
                if not is_absolute_http_url(url):
                    errors.append(f"Zeile {line_no}: URL ist nicht absolut HTTP(S).")
                if "\n" in notes or "\r" in notes:
                    errors.append(f"Zeile {line_no}: Notes sind mehrzeilig.")
                domain = registered_domain(url)
                if domain in seen_domains:
                    errors.append(f"Zeile {line_no}: Domain mehrfach vorhanden: {domain}")
                seen_domains.add(domain)
                if blocklists:
                    reason = blocklists.blocked_domain_reason(url) or blocklists.blocked_url_reason(url)
                    if reason:
                        errors.append(f"Zeile {line_no}: blockierte URL ({reason}).")
            if len(seen_domains) > target:
                errors.append(f"Mehr als Zielanzahl enthalten: {len(seen_domains)} > {target}.")
    except UnicodeDecodeError as exc:
        errors.append(f"UTF-8-Fehler: {exc}")
    if audit_path and audit_path.exists():
        audit_counts = Counter()
        with audit_path.open("r", encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                if row.get("status") == "accepted":
                    audit_counts[row.get("category", "")] += 1
        if not audit_counts:
            errors.append("Audit enthaelt keine akzeptierten Kandidaten; Quoten nicht plausibilisierbar.")
    return errors


def make_provider(args: argparse.Namespace) -> SearchProvider:
    if args.provider == "brave":
        return BraveSearchProvider(
            os.getenv("BRAVE_SEARCH_API_KEY", ""),
            country=os.getenv("BRAVE_SEARCH_COUNTRY", "de"),
            language=os.getenv("BRAVE_SEARCH_LANG", "de"),
        )
    if args.provider == "file":
        if not args.search_results:
            raise SystemExit("--search-results ist fuer --provider file erforderlich.")
        return FileSearchProvider(args.search_results)
    if args.allow_unofficial_search:
        raise SystemExit("Inoffizielle Suche ist bewusst nicht als Standard implementiert. Bitte offiziellen API-Provider oder --provider file verwenden.")
    raise SystemExit(f"Unbekannter Provider: {args.provider}")


def discover(args: argparse.Namespace) -> int:
    code, _report, _final = run_discovery(args)
    return code


def pilot(args: argparse.Namespace) -> int:
    output_dir = resolve_workspace_path(args.output_dir)
    product_seed = resolve_workspace_path(DEFAULT_LOCAL_DATA_DIR) / "seeds.csv"
    pilot_seed = output_dir / "seeds.csv"
    if pilot_seed.resolve() == product_seed.resolve():
        print("Pilot darf local-data/mention-radar/seeds.csv nicht ersetzen.", file=sys.stderr)
        return 2
    output_dir.mkdir(parents=True, exist_ok=True)
    persistent_cache = resolve_workspace_path(getattr(args, "cache_dir", "") or DEFAULT_LOCAL_DATA_DIR / "seed-crawler-cache")
    legacy_cache = output_dir / "seed-crawler-cache"
    copy_cache_if_present(legacy_cache, persistent_cache)
    discover_args = argparse.Namespace(
        provider=args.provider,
        target=PILOT_TARGET,
        output=str(pilot_seed),
        dry_run=False,
        overwrite=args.overwrite,
        resume=args.resume,
        max_pages_per_domain=PILOT_MAX_PAGES_PER_DOMAIN,
        min_score=FINAL_MIN_SCORE,
        category="",
        search_results=args.search_results,
        allow_unofficial_search=False,
        verbose=args.verbose,
        queries="",
        scoring="",
        cache_dir=str(persistent_cache),
        query_limit=PILOT_MAX_QUERIES,
        results_per_query=PILOT_RESULTS_PER_QUERY,
        max_candidate_domains=PILOT_MAX_DOMAINS,
    )
    code, _report, _final = run_discovery(discover_args, pilot_mode=True)
    return code


def copy_cache_if_present(source: Path, target: Path) -> None:
    if not source.exists() or source.resolve() == target.resolve():
        return
    for file_path in source.rglob("*.json"):
        relative = file_path.relative_to(source)
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if not destination.exists():
            shutil.copy2(file_path, destination)


def run_discovery(args: argparse.Namespace, *, pilot_mode: bool = False) -> tuple[int, dict, list[Candidate]]:
    start = now_iso()
    root = tool_root()
    config_dir = root / "config"
    quotas, all_queries = load_search_queries(args.queries or config_dir / "search_queries.yaml")
    if pilot_mode:
        quotas = dict(PILOT_QUOTAS)
    scoring = load_scoring(args.scoring or config_dir / "scoring.yaml")
    min_score = int(args.min_score or scoring["min_score"])
    blocklists = Blocklists(config_dir)
    selected_categories = [args.category] if args.category else CATEGORY_ORDER
    queries = [query for query in all_queries if query.category in selected_categories]
    if args.provider == "file":
        queries = [QuerySpec(category, "import01", "file-import") for category in selected_categories]
    if getattr(args, "query_limit", 0):
        limited: list[QuerySpec] = []
        per_category_counts: dict[str, int] = defaultdict(int)
        per_category_limit = max(1, int(args.query_limit) // max(1, len(selected_categories)))
        for query in queries:
            if per_category_counts[query.category] < per_category_limit and len(limited) < int(args.query_limit):
                limited.append(query)
                per_category_counts[query.category] += 1
        queries = limited
    provider = make_provider(args)
    cache_root = resolve_workspace_path(args.cache_dir or DEFAULT_LOCAL_DATA_DIR / "seed-crawler-cache")
    page_cache = Cache(cache_root / "pages", enabled=not args.dry_run or args.resume)
    search_cache = Cache(cache_root / "search", enabled=not args.dry_run or args.resume)
    crawler = ControlledCrawler(blocklists, page_cache, max_pages_per_domain=args.max_pages_per_domain)
    raw_results: list[SearchResult] = []
    errors: list[str] = []
    per_query_limit = int(getattr(args, "results_per_query", 0) or max(10, min(50, args.target)))
    for query_index, query in enumerate(queries, start=1):
        if getattr(args, "verbose", False):
            print(f"Query {query_index}/{len(queries)}: {query.text}")
        try:
            cache_key = f"search:{provider.name}:{query.category}:{query.query_id}:{query.text}:{per_query_limit}"
            cached_results = search_cache.get(cache_key)
            if cached_results:
                raw_results.extend(SearchResult(**item) for item in cached_results)
            else:
                found = provider.search(query, per_query_limit)
                search_cache.set(cache_key, [asdict(item) for item in found])
                raw_results.extend(found)
            if getattr(args, "verbose", False):
                print(f"Rohresultate bisher: {len(raw_results)}")
        except Exception as exc:
            errors.append(f"{query.query_id}:{type(exc).__name__}:{exc}")
    deduped_results: dict[str, SearchResult] = {}
    rejected: list[Candidate] = []
    for result in raw_results:
        normalized, invalid_reason = normalize_url_with_reason(result.url)
        if not normalized:
            reason = invalid_reason or "invalid_url"
            if getattr(args, "verbose", False):
                print(f"Ungueltige URL uebersprungen: {reason}")
            rejected.append(Candidate(result.url, "", "", "", result.category_hint, source_for(result), result.query_id, rejection_reason=reason))
            continue
        domain_reason = blocklists.blocked_domain_reason(normalized)
        url_reason = blocklists.blocked_url_reason(normalized)
        if domain_reason or url_reason:
            rejected.append(Candidate(result.url, normalized, registered_domain(normalized), "", result.category_hint, source_for(result), result.query_id, rejection_reason=domain_reason or url_reason))
            continue
        domain = registered_domain(normalized)
        if len(deduped_results) >= int(getattr(args, "max_candidate_domains", 10_000)) and domain not in deduped_results:
            continue
        deduped_results.setdefault(domain, SearchResult(normalized, result.title, result.snippet, provider.name, result.query_id, result.query, result.category_hint))
    candidates = rejected[:]
    sorted_results = sorted(deduped_results.items())
    for domain_index, (domain, result) in enumerate(sorted_results, start=1):
        if getattr(args, "verbose", False):
            print(f"Domain {domain_index}/{len(sorted_results)}: {domain}")
        pages = crawler.crawl_domain(result.url)
        candidate = evaluate_domain(result, pages, blocklists, scoring, min_score)
        candidates.append(candidate)
        if getattr(args, "verbose", False):
            if candidate.status == "accepted":
                print(f"akzeptiert: category={candidate.category} score={candidate.total_score}")
            else:
                print(f"uebersprungen: entity_type={candidate.entity_type} reason={candidate.hard_gate_reason or candidate.rejection_reason}")
    if args.category:
        quotas = {category: (args.target if category == args.category else 0) for category in CATEGORY_ORDER}
    final, missing = select_final(candidates, quotas, args.target)
    output_path = resolve_workspace_path(args.output)
    audit_path = output_path.with_name("seed_audit.csv")
    report_path = output_path.with_name("run_report.json")
    summary_path = output_path.with_name("pilot_summary.md")
    backup_path = None
    if not args.dry_run:
        backup_path = write_seed_csv(output_path, final, args.overwrite)
        write_audit_csv(audit_path, candidates)
    generated_queries = [asdict(query) for query in queries if query.generated]
    report = {
        "started_at": start,
        "ended_at": now_iso(),
        "provider": provider.name,
        "target": args.target,
        "min_score": min_score,
        "search_query_count": len(queries),
        "estimated_search_api_requests": len(queries),
        "results_per_query": per_query_limit,
        "max_candidate_domains": int(getattr(args, "max_candidate_domains", 10_000)),
        "generated_queries": generated_queries,
        "raw_url_count": len(raw_results),
        "checked_domains": len(deduped_results),
        "accepted_candidates": sum(1 for item in candidates if item.status == "accepted"),
        "rejected_candidates": sum(1 for item in candidates if item.status != "accepted"),
        "rejection_reasons": dict(Counter(item.rejection_reason or "none" for item in candidates if item.status != "accepted")),
        "final_count_by_category": dict(Counter(item.category for item in final)),
        "missing_category_quotas": missing,
        "errors_and_timeouts": errors + crawler.errors,
        "output_paths": {
            "seeds_csv": str(output_path),
            "seed_audit_csv": str(audit_path),
            "run_report_json": str(report_path),
            "pilot_summary_md": str(summary_path) if pilot_mode else "",
            "backup_csv": str(backup_path) if backup_path else "",
        },
        "dry_run": args.dry_run,
        "pilot_mode": pilot_mode,
        "allow_unofficial_search": bool(args.allow_unofficial_search),
    }
    if not args.dry_run:
        write_report(report_path, report)
        if pilot_mode:
            write_pilot_summary(summary_path, report, final, candidates)
    else:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"Roh-URLs: {len(raw_results)}")
    print(f"Gepruefte Domains: {len(deduped_results)}")
    print(f"Finale Seeds: {len(final)}")
    if not args.dry_run:
        print(f"seeds.csv: {output_path}")
        print(f"seed_audit.csv: {audit_path}")
        print(f"run_report.json: {report_path}")
        if pilot_mode:
            print(f"pilot_summary.md: {summary_path}")
    return 0, report, final


def doctor(args: argparse.Namespace) -> int:
    root = tool_root()
    dotenv_found = env_path().exists()
    provider = args.provider or configured_provider("brave")
    output_dir = resolve_workspace_path(DEFAULT_LOCAL_DATA_DIR)
    print(f"Python-Version: {sys.version.split()[0]}")
    print(f"Paket gefunden: ja ({root})")
    print(f"Konfiguration gefunden: {'ja' if (root / 'config' / 'search_queries.yaml').exists() else 'nein'}")
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        probe = output_dir / ".seed-crawler-write-test.tmp"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        writable = "ja"
    except OSError:
        writable = "nein"
    print(f"Schreibzugriff local-data/mention-radar/: {writable}")
    print(f"Search Provider: {provider}")
    print(f"Brave-Key vorhanden: {'ja' if api_key_present() else 'nein'}")
    print(f".env gefunden: {'ja' if dotenv_found else 'nein'}")
    print("Outputpfade:")
    print(f"  seeds.csv: {output_dir / 'seeds.csv'}")
    print(f"  Pilot: {output_dir / 'pilot-10'}")
    if provider != "brave":
        print("Internet/Brave-API: uebersprungen, weil Provider nicht brave ist.")
        return 0
    if not api_key_present():
        print("Brave-API-Healthcheck: uebersprungen.")
        print("BRAVE_SEARCH_API_KEY fehlt. Lege ihn als Umgebungsvariable oder in tools/seed-crawler/.env ab.")
        return 2
    try:
        brave = BraveSearchProvider(
            os.getenv("BRAVE_SEARCH_API_KEY", ""),
            timeout=10.0,
            country=os.getenv("BRAVE_SEARCH_COUNTRY", "de"),
            language=os.getenv("BRAVE_SEARCH_LANG", "de"),
        )
        results = brave.search(QuerySpec("book_blog", "doctor01", "Buchblog Rezensionsexemplar Familie"), 1)
        print("Internet/Brave-API: erreichbar")
        print(f"Minimaler API-Healthcheck: ok ({len(results)} Ergebnis/se)")
        return 0
    except Exception as exc:
        print("Internet/Brave-API: nicht erfolgreich")
        print(f"Minimaler API-Healthcheck: {redact_secrets(str(exc))}")
        return 1


def inspect(args: argparse.Namespace) -> int:
    root = tool_root()
    config_dir = root / "config"
    blocklists = Blocklists(config_dir)
    scoring = load_scoring(config_dir / "scoring.yaml")
    cache = Cache(resolve_workspace_path(args.cache_dir or DEFAULT_LOCAL_DATA_DIR / "seed-crawler-cache"), enabled=args.resume)
    crawler = ControlledCrawler(blocklists, cache, max_pages_per_domain=args.max_pages_per_domain)
    result = SearchResult(url=args.url, provider="inspect", query_id="inspect01", category_hint=args.category or "")
    pages = crawler.crawl_domain(args.url)
    candidate = evaluate_domain(result, pages, blocklists, scoring, int(args.min_score or scoring["min_score"]))
    print(f"URL: {candidate.final_seed_url}")
    print(f"Domain: {candidate.domain}")
    print(f"Name: {candidate.name}")
    print(f"Kategorie: {candidate.category}")
    print(f"Score: {candidate.total_score}/100")
    print(f"Status: {candidate.status}")
    print(f"Editorial: {candidate.editorial_signal}")
    print(f"Aktivitaet: {candidate.activity_signal}")
    if candidate.rejection_reason:
        print(f"Ablehnung/Abzug: {candidate.rejection_reason}")
    print(f"Notes: {candidate.notes}")
    return 0


def report(args: argparse.Namespace) -> int:
    path = resolve_workspace_path(args.path or DEFAULT_LOCAL_DATA_DIR / "run_report.json")
    if not path.exists():
        print(f"Report nicht gefunden: {path}", file=sys.stderr)
        return 2
    data = json.loads(path.read_text(encoding="utf-8"))
    print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0


def validate(args: argparse.Namespace) -> int:
    root = tool_root()
    blocklists = Blocklists(root / "config")
    path = resolve_workspace_path(args.csv_path)
    audit_path = path.with_name("seed_audit.csv")
    errors = validate_seed_csv(path, target=args.target, blocklists=blocklists, audit_path=audit_path)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"OK: {path}")
    return 0


def now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Seed Crawler fuer Mention Radar.")
    sub = parser.add_subparsers(dest="command", required=True)
    discover_parser = sub.add_parser("discover", help="Suchergebnisse finden, Domains pruefen und seeds.csv erzeugen.")
    discover_parser.add_argument("--provider", required=True, choices=["brave", "file"], help="Offizieller Suchanbieter oder lokaler Import.")
    discover_parser.add_argument("--target", type=int, default=100)
    discover_parser.add_argument("--output", default="local-data/mention-radar/seeds.csv")
    discover_parser.add_argument("--dry-run", action="store_true")
    discover_parser.add_argument("--overwrite", action="store_true")
    discover_parser.add_argument("--resume", action="store_true")
    discover_parser.add_argument("--max-pages-per-domain", type=int, default=8)
    discover_parser.add_argument("--min-score", type=int, default=0)
    discover_parser.add_argument("--category", choices=CATEGORY_ORDER)
    discover_parser.add_argument("--search-results", default="")
    discover_parser.add_argument("--allow-unofficial-search", action="store_true")
    discover_parser.add_argument("--verbose", action="store_true")
    discover_parser.add_argument("--queries", default="")
    discover_parser.add_argument("--scoring", default="")
    discover_parser.add_argument("--cache-dir", default="")
    discover_parser.add_argument("--query-limit", type=int, default=0)
    discover_parser.add_argument("--results-per-query", type=int, default=0)
    discover_parser.add_argument("--max-candidate-domains", type=int, default=10000)
    discover_parser.set_defaults(func=discover)

    pilot_parser = sub.add_parser("pilot", help="Sicherer 10-Seed-Pilotlauf in isoliertem Ausgabeordner.")
    pilot_parser.add_argument("--provider", default="", choices=["", "brave", "file"])
    pilot_parser.add_argument("--output-dir", default="local-data/mention-radar/pilot-10")
    pilot_parser.add_argument("--search-results", default="")
    pilot_parser.add_argument("--cache-dir", default="")
    pilot_parser.add_argument("--overwrite", action="store_true")
    pilot_parser.add_argument("--resume", action="store_true")
    pilot_parser.add_argument("--verbose", action="store_true")
    pilot_parser.set_defaults(func=pilot)

    doctor_parser = sub.add_parser("doctor", help="Lokale Konfiguration und Brave-Erreichbarkeit pruefen.")
    doctor_parser.add_argument("--provider", default="")
    doctor_parser.set_defaults(func=doctor)

    inspect_parser = sub.add_parser("inspect", help="Einzelne URL kontrolliert untersuchen.")
    inspect_parser.add_argument("url")
    inspect_parser.add_argument("--category", choices=CATEGORY_ORDER, default="")
    inspect_parser.add_argument("--max-pages-per-domain", type=int, default=8)
    inspect_parser.add_argument("--min-score", type=int, default=0)
    inspect_parser.add_argument("--resume", action="store_true")
    inspect_parser.add_argument("--cache-dir", default="")
    inspect_parser.set_defaults(func=inspect)

    validate_parser = sub.add_parser("validate", help="seeds.csv fuer Mention Radar pruefen.")
    validate_parser.add_argument("csv_path")
    validate_parser.add_argument("--target", type=int, default=100)
    validate_parser.set_defaults(func=validate)

    report_parser = sub.add_parser("report", help="run_report.json anzeigen.")
    report_parser.add_argument("path", nargs="?")
    report_parser.set_defaults(func=report)
    return parser


def main(argv: list[str] | None = None) -> int:
    load_env_file()
    args = build_parser().parse_args(argv)
    if getattr(args, "provider", "") == "":
        args.provider = configured_provider("brave")
    logging.basicConfig(level=logging.DEBUG if getattr(args, "verbose", False) else logging.INFO, format="%(levelname)s: %(message)s")
    try:
        return int(args.func(args))
    except (ValueError, RuntimeError) as exc:
        print(redact_secrets(str(exc)), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
