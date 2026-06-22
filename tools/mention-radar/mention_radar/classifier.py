from __future__ import annotations

import hashlib
import re
from urllib.parse import urlparse

from .models import Candidate, FetchResult
from .safety import contains_risk_signal
from .scoring import score_candidate


OWN_MATERIAL_URLS = [
    "https://farbenfrohe-lesewelt.github.io/presse/",
    "https://farbenfrohe-lesewelt.github.io/ueber-den-ratgeber/",
    "https://farbenfrohe-lesewelt.github.io/ratgeber/",
    "https://farbenfrohe-lesewelt.github.io/checkliste/",
    "https://farbenfrohe-lesewelt.github.io/pinterest/toxoplasmose-katze-schwangerschaft/",
    "https://farbenfrohe-lesewelt.github.io/pinterest/baby-und-katze-zusammenfuehren/",
    "https://farbenfrohe-lesewelt.github.io/pinterest/erste-begegnung-baby-und-katze/",
    "https://farbenfrohe-lesewelt.github.io/pinterest/katze-im-babybett/",
    "https://www.amazon.de/dp/B0GTDN1458",
]

TOPIC_TERMS = [
    "baby und katze",
    "katze und baby",
    "schwangerschaft mit katze",
    "katze und neugeborenes",
    "katze an baby gewoehnen",
    "erste begegnung baby und katze",
    "katze im babybett",
    "katze im beistellbett",
    "katzenverhalten und baby",
    "toxoplasmose schwangerschaft katze",
    "familienratgeber haustiere",
    "haustier und kind",
    "elternblog mit katze",
    "katzenblog",
    "buchblog ratgeber",
    "sachbuch familie",
    "ratgeber schwangerschaft",
    "elternpodcast",
    "haustierpodcast",
]

AUDIENCE_TERMS = [
    "familie",
    "familien",
    "eltern",
    "schwangerschaft",
    "baby",
    "neugeborenes",
    "katze",
    "katzen",
    "haustier",
    "buchblog",
    "podcast",
    "ratgeber",
]

PERMISSION_TERMS = [
    "rezensionsexemplar",
    "rezensionsexemplare willkommen",
    "buecher zur rezension",
    "buchvorstellungen",
    "neuerscheinungen einsenden",
    "themenvorschlag",
    "themenvorschlaege",
    "presseanfrage",
    "redaktionskontakt",
    "gastbeitrag einreichen",
    "gastautor",
    "interviewanfrage",
    "podcastgast",
    "kooperation anfragen",
    "medienanfrage",
]

CONTACT_TERMS = ["redaktion", "presse", "kontakt", "medien", "rezension", "interview", "podcast"]


def classify(fetch: FetchResult, seed_name: str = "") -> Candidate:
    page_text = " ".join([fetch.title, fetch.text]).strip()
    normalized = _normalize(page_text)
    parsed = urlparse(fetch.final_url or fetch.url)
    website = f"{parsed.scheme}://{parsed.netloc}/" if parsed.scheme and parsed.netloc else fetch.url
    name = seed_name or fetch.title or parsed.netloc or fetch.url
    evidence = _find_evidence(page_text, PERMISSION_TERMS)
    topic_hits = _count_hits(normalized, TOPIC_TERMS)
    audience_hits = _count_hits(normalized, AUDIENCE_TERMS)
    contact_hint = _find_evidence(page_text, CONTACT_TERMS)
    contact_method = "; ".join(fetch.contact_methods[:3])
    risk = contains_risk_signal(page_text)

    candidate_class = "C"
    notes = ""
    if fetch.error:
        notes = fetch.error
    if fetch.skipped_reason:
        notes = fetch.skipped_reason
    if risk:
        candidate_class = "D"
        notes = f"Ausschluss: {risk}"
    elif topic_hits == 0 and audience_hits < 2:
        candidate_class = "C"
        notes = "Keine ausreichende thematische Passung."
    elif evidence:
        candidate_class = "A"
    elif contact_method or contact_hint:
        candidate_class = "B"
    else:
        candidate_class = "C"
        notes = "Keine erkennbare Einreichungsmoeglichkeit."

    topic_fit = min(30, topic_hits * 8 + min(6, audience_hits))
    audience_fit = min(20, audience_hits * 4)
    suggested_angle = suggest_angle(normalized)
    candidate = Candidate(
        candidate_id=_candidate_id(fetch.final_url or fetch.url),
        name=name[:120],
        website=website,
        relevant_page=fetch.final_url or fetch.url,
        page_title=fetch.title,
        candidate_class=candidate_class,
        score=0,
        topic_fit=topic_fit,
        audience_fit=audience_fit,
        submission_permission="ja" if candidate_class == "A" else "nein",
        permission_evidence=evidence,
        evidence_url=(fetch.final_url or fetch.url) if evidence else "",
        public_contact_method=contact_method,
        suggested_angle=suggested_angle,
        suggested_material=suggest_material(suggested_angle, candidate_class),
        fetched_at=fetch.fetched_at,
        review_status="new" if candidate_class in {"A", "B"} else "excluded",
        notes=notes,
        seed_url=fetch.seed_url or fetch.url,
        discovery_source=fetch.discovery_source,
    )
    candidate.score = score_candidate(candidate, normalized)
    return candidate


def suggest_angle(text: str) -> str:
    if "toxoplasmose" in text:
        return "Toxoplasmose ruhig einordnen"
    if "babybett" in text or "beistellbett" in text:
        return "Schlafplatz und Babybett einordnen"
    if "erste begegnung" in text:
        return "Erste Begegnung Baby und Katze"
    if "podcast" in text:
        return "Gespraech ueber Familienalltag mit Baby und Katze"
    if "buchblog" in text or "rezension" in text:
        return "Sachlicher Ratgeber fuer Familien mit Baby und Katze"
    if "katze" in text:
        return "Baby kommt, Katze bleibt"
    return "Orientierung fuer Familien mit Haustier und Baby"


def suggest_material(angle: str, candidate_class: str) -> str:
    if candidate_class not in {"A", "B"}:
        return ""
    material_map = {
        "Toxoplasmose ruhig einordnen": [
            "https://farbenfrohe-lesewelt.github.io/pinterest/toxoplasmose-katze-schwangerschaft/",
            "https://farbenfrohe-lesewelt.github.io/presse/",
            "https://www.amazon.de/dp/B0GTDN1458",
        ],
        "Schlafplatz und Babybett einordnen": [
            "https://farbenfrohe-lesewelt.github.io/pinterest/katze-im-babybett/",
            "https://farbenfrohe-lesewelt.github.io/presse/",
            "Rezensionsexemplar",
        ],
        "Erste Begegnung Baby und Katze": [
            "https://farbenfrohe-lesewelt.github.io/pinterest/erste-begegnung-baby-und-katze/",
            "https://farbenfrohe-lesewelt.github.io/presse/",
            "Rezensionsexemplar",
        ],
        "Gespraech ueber Familienalltag mit Baby und Katze": [
            "https://farbenfrohe-lesewelt.github.io/presse/",
            "https://farbenfrohe-lesewelt.github.io/ueber-den-ratgeber/",
            "https://farbenfrohe-lesewelt.github.io/ratgeber/",
        ],
        "Sachlicher Ratgeber fuer Familien mit Baby und Katze": [
            "https://farbenfrohe-lesewelt.github.io/presse/",
            "https://www.amazon.de/dp/B0GTDN1458",
            "Rezensionsexemplar",
        ],
        "Baby kommt, Katze bleibt": [
            "https://farbenfrohe-lesewelt.github.io/pinterest/baby-und-katze-zusammenfuehren/",
            "https://farbenfrohe-lesewelt.github.io/presse/",
            "Rezensionsexemplar",
        ],
        "Orientierung fuer Familien mit Haustier und Baby": [
            "https://farbenfrohe-lesewelt.github.io/ratgeber/",
            "https://farbenfrohe-lesewelt.github.io/presse/",
            "https://farbenfrohe-lesewelt.github.io/checkliste/",
        ],
    }
    return " | ".join(material_map.get(angle, material_map["Orientierung fuer Familien mit Haustier und Baby"])[:3])


def _normalize(text: str) -> str:
    replacements = str.maketrans({"ä": "ae", "ö": "oe", "ü": "ue", "Ä": "ae", "Ö": "oe", "Ü": "ue", "ß": "ss"})
    return re.sub(r"\s+", " ", (text or "").translate(replacements).lower())


def _count_hits(text: str, terms: list[str]) -> int:
    return sum(1 for term in terms if term in text)


def _find_evidence(text: str, terms: list[str]) -> str:
    compact = re.sub(r"\s+", " ", text or "")
    compact_lower = _normalize(compact)
    for term in terms:
        index = compact_lower.find(term)
        if index >= 0:
            start = max(0, index - 70)
            end = min(len(compact), index + len(term) + 90)
            return compact[start:end].strip()
    return ""


def _candidate_id(url: str) -> str:
    return hashlib.sha1(url.encode("utf-8")).hexdigest()[:12]
