from __future__ import annotations

import csv
import os
import re
from pathlib import Path
from typing import Iterable, List
from urllib.parse import urldefrag, urlparse, urlunparse

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

from .models import Seed


USER_AGENT = "FarbenfroheLesewelt-MentionResearch/1.0"

DEFAULT_CONFIG = {
    "request_delay_seconds": 3,
    "maximum_pages_per_domain": 5,
    "timeout_seconds": 15,
    "maximum_html_bytes": 2_000_000,
    "maximum_redirects": 5,
    "output_dir": "local-data/mention-radar",
    "generate_drafts": True,
    "official_search_api": {"enabled": False, "provider": "", "api_key_env": ""},
}

STATUS_VALUES = {
    "new",
    "manual_review",
    "approved_for_contact",
    "contacted_manually",
    "response_received",
    "sample_requested",
    "sample_sent",
    "published",
    "declined",
    "no_response",
    "excluded",
}

BLOCKED_PATH_PARTS = {
    "login",
    "konto",
    "account",
    "checkout",
    "cart",
    "warenkorb",
    "wp-login",
    "admin",
    "auth",
    "password",
}

NON_HTML_EXTENSIONS = {
    ".pdf",
    ".zip",
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".webp",
    ".svg",
    ".mp4",
    ".mp3",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
}

RISK_PATTERNS = [
    "linkverkauf",
    "link kaufen",
    "dofollow-link kaufen",
    "bezahlte dofollow",
    "linktausch",
    "backlink erforderlich",
    "garantierte veröffentlichung",
    "garantierte publikation",
    "veröffentlichungsgarantie",
    "positive rezension erforderlich",
    "nur positive bewertungen",
    "presseportal",
    "webverzeichnis",
]


def load_config(path: str | None = None) -> dict:
    config = dict(DEFAULT_CONFIG)
    config["official_search_api"] = dict(DEFAULT_CONFIG["official_search_api"])
    if path:
        if yaml is None:
            raise RuntimeError("PyYAML wird zum Lesen der Konfiguration benötigt.")
        with open(path, "r", encoding="utf-8") as handle:
            loaded = yaml.safe_load(handle) or {}
        for key, value in loaded.items():
            if key == "official_search_api" and isinstance(value, dict):
                config[key].update(value)
            else:
                config[key] = value
    api = config.get("official_search_api", {})
    if bool(api.get("enabled")) and api.get("api_key_env") and not os.getenv(str(api.get("api_key_env"))):
        config["official_search_api"]["enabled"] = False
    return config


def ensure_output_dirs(output_dir: str | Path) -> Path:
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    (root / "drafts").mkdir(parents=True, exist_ok=True)
    return root


def normalize_url(url: str) -> str:
    url = (url or "").strip()
    if not url:
        return ""
    parsed = urlparse(url if "://" in url else f"https://{url}")
    clean = parsed._replace(fragment="", scheme=parsed.scheme.lower(), netloc=parsed.netloc.lower())
    clean = clean._replace(path=clean.path or "/")
    return urlunparse(clean)


def dedupe_urls(urls: Iterable[str]) -> List[str]:
    seen: set[str] = set()
    result: List[str] = []
    for url in urls:
        normalized, _fragment = urldefrag(normalize_url(url))
        if normalized and normalized not in seen:
            seen.add(normalized)
            result.append(normalized)
    return result


def is_probably_html_url(url: str) -> bool:
    path = urlparse(url).path.lower()
    return not any(path.endswith(ext) for ext in NON_HTML_EXTENSIONS)


def is_blocked_path(url: str) -> bool:
    path = urlparse(url).path.lower()
    return any(part in path for part in BLOCKED_PATH_PARTS)


def contains_risk_signal(text: str) -> str:
    haystack = re.sub(r"\s+", " ", (text or "").lower())
    for pattern in RISK_PATTERNS:
        if pattern in haystack:
            return pattern
    return ""


def read_seed_csv(path: str | Path) -> List[Seed]:
    seeds: List[Seed] = []
    with open(path, "r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            url = row.get("url") or row.get("URL") or row.get("link") or row.get("Link") or ""
            if url.strip():
                seeds.append(
                    Seed(
                        url=normalize_url(url),
                        name=row.get("name", "") or row.get("Name", ""),
                        source=row.get("source", "manual"),
                        notes=row.get("notes", ""),
                    )
                )
    return seeds


def extract_urls_from_csv(path: str | Path) -> List[str]:
    urls: List[str] = []
    pattern = re.compile(r"https?://[^\s,;\"']+", re.IGNORECASE)
    with open(path, "r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.reader(handle):
            for cell in row:
                urls.extend(match.group(0).rstrip(").]") for match in pattern.finditer(cell or ""))
    return dedupe_urls(urls)
