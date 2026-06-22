from __future__ import annotations

import argparse
import csv
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse, urlunparse


PRESS_URL = "https://farbenfrohe-lesewelt.github.io/presse/"
BOOK_URL = "https://www.amazon.de/dp/B0GTDN1458"
READY = "ready"
MANUAL = "manual_review"
REJECTED = "rejected"
SHARE_HOSTS = {
    "facebook.com",
    "www.facebook.com",
    "twitter.com",
    "www.twitter.com",
    "x.com",
    "www.x.com",
    "api.whatsapp.com",
    "bsky.app",
    "pinterest.com",
    "www.pinterest.com",
}
PODCAST_PLATFORM_HOSTS = {
    "anchor.fm",
    "podigee.io",
    "open.spotify.com",
    "spotify.com",
    "podcasts.apple.com",
}
BAD_CONTACT_FRAGMENTS = ("comments", "comment-", "respond", "more-")
TOPIC_TERMS = {
    "cat": ("katze", "katzen", "haustier", "haustiere", "tiermedium", "katzenblog", "katzenhaltung"),
    "family": ("familie", "eltern", "baby", "schwangerschaft", "kleinkind", "mutter", "vater", "papammunity"),
    "book": ("buch", "buchblog", "rezension", "rezensionsexemplar", "buchvorstellung", "ratgeber", "sachbuch"),
}
UNSUITABLE_DOMAINS = {"adhs-journal.de"}
BANNED_DRAFT_PHRASES = (
    "möglicher redaktioneller Anlass",
    "moeglicher redaktioneller Anlass",
    "Synergie",
    "Mehrwert für Ihre Zielgruppe",
    "Win-win",
    "hochwertiger Content",
    "spannende Kooperation",
)


@dataclass(frozen=True)
class CandidateRow:
    row: dict[str, str]

    @property
    def candidate_id(self) -> str:
        return self.row.get("candidate_id", "").strip()

    @property
    def name(self) -> str:
        return clean_space(self.row.get("name") or self.domain)

    @property
    def website(self) -> str:
        return self.row.get("website", "").strip()

    @property
    def seed_url(self) -> str:
        return self.row.get("seed_url", "").strip()

    @property
    def relevant_page(self) -> str:
        return self.row.get("relevant_page", "").strip()

    @property
    def candidate_class(self) -> str:
        return (self.row.get("candidate_class") or "").strip().upper()

    @property
    def score(self) -> int:
        try:
            return int(float(self.row.get("score", "0") or 0))
        except ValueError:
            return 0

    @property
    def topic_fit(self) -> int:
        try:
            return int(float(self.row.get("topic_fit", "0") or 0))
        except ValueError:
            return 0

    @property
    def audience_fit(self) -> int:
        try:
            return int(float(self.row.get("audience_fit", "0") or 0))
        except ValueError:
            return 0

    @property
    def permission_evidence(self) -> str:
        return self.row.get("permission_evidence", "")

    @property
    def evidence_url(self) -> str:
        return self.row.get("evidence_url", "").strip()

    @property
    def public_contact_method(self) -> str:
        return self.row.get("public_contact_method", "")

    @property
    def suggested_angle(self) -> str:
        return self.row.get("suggested_angle", "")

    @property
    def page_title(self) -> str:
        return self.row.get("page_title", "")

    @property
    def review_status(self) -> str:
        return self.row.get("review_status", "")

    @property
    def source_url(self) -> str:
        return self.relevant_page or self.seed_url or self.website

    @property
    def domain(self) -> str:
        return website_key(self.website or self.seed_url or self.relevant_page)


@dataclass
class DraftDecision:
    candidate: CandidateRow
    status: str
    draft_type: str
    subject: str
    salutation: str
    contact_url: str
    evidence_url: str
    personalization_basis: str
    review_notes: str
    draft_file: str = ""
    draft_text: str = ""


def clean_space(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def slug_text(value: str) -> str:
    return (
        (value or "")
        .lower()
        .replace("ä", "ae")
        .replace("ö", "oe")
        .replace("ü", "ue")
        .replace("ß", "ss")
    )


def parse_url_safe(url: str):
    try:
        return urlparse((url or "").strip())
    except ValueError:
        return urlparse("")


def website_key(url: str) -> str:
    parsed = parse_url_safe(url)
    host = (parsed.hostname or url or "").lower().strip()
    if host.startswith("www."):
        host = host[4:]
    return host.strip("/")


def remove_fragment_url(url: str) -> str:
    parsed = parse_url_safe(url)
    if not parsed.scheme or not parsed.netloc:
        return url.strip()
    path = re.sub(r"/{2,}", "/", parsed.path or "/")
    return urlunparse((parsed.scheme.lower(), parsed.netloc.lower(), path, "", parsed.query, ""))


def is_comment_or_fragment_url(url: str) -> bool:
    parsed = parse_url_safe(url)
    fragment = (parsed.fragment or "").lower()
    return any(fragment.startswith(prefix) or fragment == prefix for prefix in BAD_CONTACT_FRAGMENTS)


def is_share_or_external_noise(url: str, own_domain: str) -> bool:
    parsed = parse_url_safe(url)
    host = (parsed.hostname or "").lower()
    path = (parsed.path or "").lower()
    if host in SHARE_HOSTS:
        return True
    if host in PODCAST_PLATFORM_HOSTS or any(host.endswith("." + item) for item in PODCAST_PLATFORM_HOSTS):
        return True
    if "sharer" in path or "intent" in path or "share" in path and host != own_domain:
        return True
    if is_comment_or_fragment_url(url):
        return True
    return False


def split_urls(value: str) -> list[str]:
    urls: list[str] = []
    for item in re.split(r"[;|]", value or ""):
        clean = item.strip()
        if clean:
            urls.append(clean)
    return urls


def is_own_contact_url(url: str, domain: str) -> bool:
    if url.startswith("mailto:"):
        return True
    parsed = parse_url_safe(url)
    if not parsed.scheme or parsed.scheme not in {"http", "https"}:
        return False
    host = website_key(url)
    if host != domain:
        return False
    if is_share_or_external_noise(url, domain):
        return False
    path = slug_text(parsed.path)
    if not path or path == "/":
        return False
    if any(term in path for term in ("woher-bekommt", "wie-bekomme", "erklaert", "ratgeber-artikel")):
        return False
    return any(term in path for term in ("kontakt", "redaktion", "presse", "kooperation", "rezension", "buchvorstellung", "impressum"))


def best_contact_url(candidate: CandidateRow) -> str:
    urls = split_urls(candidate.public_contact_method)
    domain = candidate.domain
    valid = [remove_fragment_url(url) if not url.startswith("mailto:") else url for url in urls if is_own_contact_url(url, domain)]
    if valid:
        return sorted(set(valid), key=contact_priority)[0]
    evidence = remove_fragment_url(candidate.evidence_url)
    if evidence and is_own_contact_url(evidence, domain):
        return evidence
    source = remove_fragment_url(candidate.source_url)
    if source and is_own_contact_url(source, domain):
        return source
    return ""


def contact_priority(url: str) -> tuple[int, str]:
    haystack = slug_text(url)
    if url.startswith("mailto:"):
        return (0, url)
    for index, term in enumerate(("rezension", "buchvorstellung", "kooperation", "redaktion", "presse", "kontakt", "impressum")):
        if term in haystack:
            return (index + 1, url)
    return (99, url)


def topic_counts(candidate: CandidateRow) -> dict[str, int]:
    text = slug_text(
        " ".join(
            [
                candidate.name,
                candidate.website,
                candidate.seed_url,
                candidate.relevant_page,
                candidate.page_title,
                candidate.permission_evidence,
                candidate.suggested_angle,
            ]
        )
    )
    return {key: sum(1 for term in terms if term in text) for key, terms in TOPIC_TERMS.items()}


def has_clear_topic_fit(candidate: CandidateRow) -> bool:
    if candidate.domain in UNSUITABLE_DOMAINS:
        return False
    counts = topic_counts(candidate)
    if counts["cat"] >= 1:
        return True
    if counts["family"] >= 2:
        return True
    if counts["book"] >= 2 and candidate.topic_fit >= 2:
        return True
    if "baby und katze" in slug_text(candidate.suggested_angle):
        return True
    return candidate.topic_fit >= 4 and candidate.audience_fit >= 12 and (counts["family"] or counts["book"])


def evidence_is_usable(candidate: CandidateRow) -> bool:
    evidence = clean_space(candidate.permission_evidence)
    if not evidence:
        return False
    if len(evidence) < 35:
        return False
    if evidence.endswith((" Merma", " H", " G", " Ein", " mit")):
        return False
    lowered = slug_text(evidence)
    if any(term in lowered for term in ("teilen mit", "wird in neuem fenster", "gefaellt mir", "whatsapp", "facebook")):
        return False
    return True


def personalization_basis(candidate: CandidateRow) -> str:
    text = slug_text(" ".join([candidate.name, candidate.relevant_page, candidate.page_title, candidate.permission_evidence, candidate.suggested_angle]))
    if candidate.domain == "vom-taubertal.de":
        return "Kooperationsseite mit Hinweis auf thematisch passende Buchvorstellungen zu Katzen- und Ratgeberthemen."
    if "rezensionsexemplar" in text and evidence_is_usable(candidate):
        return "Oeffentlich sichtbarer Hinweis auf Rezensionsexemplare oder Buchvorstellungen; Evidenz wurde paraphrasiert."
    if "buchrezension" in text or "rezension" in text:
        return "Eigene Buchrezensionen beziehungsweise Buchvorstellungen auf der Website."
    if "kontakt" in text or "kooperation" in text or "redaktion" in text:
        return "Eigener Kontakt- oder Kooperationsweg der Website."
    return ""


def draft_type_for(candidate: CandidateRow) -> str:
    text = slug_text(" ".join([candidate.name, candidate.relevant_page, candidate.page_title, candidate.suggested_angle]))
    if "buch" in text or "rezension" in text:
        return "book_review"
    if "katze" in text or "haustier" in text or candidate.domain == "vom-taubertal.de":
        return "cat_book_feature"
    if "familie" in text or "eltern" in text or "baby" in text:
        return "family_topic"
    return "topic_pitch"


def subject_for(draft_type: str) -> str:
    if draft_type == "book_review":
        return "Rezensionsexemplar: Praxisratgeber fuer Familien mit Baby und Katze"
    if draft_type == "cat_book_feature":
        return "Buchvorstellung: Baby kommt, Katze bleibt"
    if draft_type == "family_topic":
        return "Themenvorschlag: Familienalltag mit Baby und Katze"
    return "Themenvorschlag: Baby und Katze ruhig vorbereiten"


def candidate_sort_key(candidate: CandidateRow) -> tuple[int, int, int, int, int, str]:
    class_rank = {"A": 0, "B": 1}.get(candidate.candidate_class, 2)
    contact = 0 if best_contact_url(candidate) else 1
    evidence = 0 if evidence_is_usable(candidate) or personalization_basis(candidate) else 1
    return (class_rank, evidence, contact, -candidate.topic_fit, -candidate.score, candidate.source_url)


def load_candidates(path: Path) -> list[CandidateRow]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [CandidateRow(row) for row in csv.DictReader(handle)]


def dedupe_candidates(candidates: list[CandidateRow]) -> list[CandidateRow]:
    grouped: dict[str, list[CandidateRow]] = {}
    for candidate in candidates:
        key = candidate.domain
        if not key:
            continue
        grouped.setdefault(key, []).append(candidate)
    return [sorted(rows, key=candidate_sort_key)[0] for _key, rows in sorted(grouped.items())]


def decide(candidate: CandidateRow, minimum_score: int) -> DraftDecision:
    contact_url = best_contact_url(candidate)
    basis = personalization_basis(candidate)
    evidence_url = remove_fragment_url(candidate.evidence_url or candidate.source_url)
    draft_type = draft_type_for(candidate)
    subject = subject_for(draft_type)
    notes: list[str] = []
    if candidate.candidate_class not in {"A", "B"} or candidate.score < minimum_score:
        notes.append("Candidate class or score below threshold.")
    if not has_clear_topic_fit(candidate):
        notes.append("Keine ausreichende konkrete Passung zu Katze, Baby, Familienratgeber oder Buchvorstellung.")
    if not contact_url:
        notes.append("Kein plausibler eigener Kontaktweg gefunden; Share-/Kommentar-/Podcastlinks wurden verworfen.")
    if not basis:
        notes.append("Keine belastbare Personalisierungsgrundlage ohne technische oder fragmentarische Evidenz.")
    if not has_clear_topic_fit(candidate):
        status = REJECTED
    elif notes:
        status = MANUAL
    else:
        status = READY
    return DraftDecision(
        candidate=candidate,
        status=status,
        draft_type=draft_type,
        subject=subject,
        salutation="Guten Tag",
        contact_url=contact_url,
        evidence_url=evidence_url,
        personalization_basis=basis,
        review_notes=" ".join(notes),
    )


def build_message(decision: DraftDecision) -> str:
    candidate = decision.candidate
    name = display_name(candidate)
    draft_type = decision.draft_type
    if draft_type == "book_review":
        opening = f"auf {name} habe ich Ihre Buchrezensionen gesehen. Deshalb frage ich kurz und unverbindlich an, ob ein praxisnaher Ratgeber fuer werdende Eltern und Familien mit Katze grundsaetzlich in Ihr Rezensionsprofil passen koennte."
        ask = "Gern sende ich bei Interesse unverbindlich ein Rezensionsexemplar."
    elif draft_type == "cat_book_feature":
        opening = f"auf {name} ist der Katzenalltag sichtbar der rote Faden. Auf dieser Grundlage moechte ich Ihnen ein Buchthema fuer eine moegliche Vorstellung vorschlagen: Baby kommt, Katze bleibt."
        ask = "Gern sende ich bei Interesse unverbindlich ein Rezensionsexemplar oder weitere Buchinformationen."
    elif draft_type == "family_topic":
        opening = f"auf {name} geht es um Familienalltag und Elternfragen. Dazu passt ein ruhiger Themenvorschlag fuer Haushalte, in denen mit dem Baby auch die Katze ihren Platz behalten soll."
        ask = "Duerfte ich Ihnen dazu die Presseinformationen und bei Interesse ein Rezensionsexemplar schicken?"
    else:
        opening = f"auf {name} habe ich einen passenden redaktionellen Kontaktweg gefunden. Deshalb frage ich kurz an, ob das Thema Baby und Katze grundsaetzlich in Ihren Rahmen passt."
        ask = "Gern sende ich bei Interesse weitere Informationen."
    body = (
        f"{decision.salutation},\n\n"
        f"{opening}\n\n"
        "Das Buch \"Baby und Katze sicher zusammenfuehren\" ist ein praxisnaher Ratgeber fuer Schwangerschaft, Geburt und Babyalltag mit Katze. "
        "Es ordnet typische Unsicherheiten in klare Routinen, statt widerspruechliche Online-Tipps zu wiederholen, und beruecksichtigt Sicherheit des Babys und Beduerfnisse der Katze gemeinsam, ruhig und ohne Alarmismus.\n\n"
        f"{ask} Die Zusendung ist selbstverstaendlich unverbindlich und nicht an eine Veroeffentlichung, positive Bewertung oder Verlinkung geknuepft.\n\n"
        f"Presseinformationen: {PRESS_URL}\n"
        f"Buchseite: {BOOK_URL}\n\n"
        "Herzliche Gruesse\n"
        "Andrea Blum\n"
        "Farbenfrohe Lesewelt Verlag"
    )
    return body


def word_count_message(text: str) -> int:
    without_links = re.sub(r"https?://\S+", "", text)
    return len(re.findall(r"\b[\wÄÖÜäöüß-]+\b", without_links))


def link_count(text: str) -> int:
    return len(re.findall(r"https?://\S+", text))


def quality_check(decision: DraftDecision) -> list[str]:
    if decision.status != READY:
        return []
    errors: list[str] = []
    if not decision.contact_url or is_share_or_external_noise(decision.contact_url, decision.candidate.domain):
        errors.append("invalid_contact_url")
    if not decision.personalization_basis:
        errors.append("missing_personalization_basis")
    if link_count(decision.draft_text) > 2:
        errors.append("too_many_links")
    words = word_count_message(decision.draft_text)
    if words < 100 or words > 160:
        errors.append(f"word_count:{words}")
    for phrase in BANNED_DRAFT_PHRASES:
        if phrase.lower() in decision.draft_text.lower():
            errors.append("banned_phrase")
            break
    return errors


def display_name(candidate: CandidateRow) -> str:
    name = clean_space(candidate.name).strip(".")
    if not name or name.lower().startswith("http"):
        return candidate.domain
    return name


def safe_filename_part(value: str, limit: int = 38) -> str:
    value = slug_text(value)
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value[:limit].strip("-") or "website"


def draft_filename(rank: int, candidate: CandidateRow) -> str:
    return f"{rank:02d}-{safe_filename_part(display_name(candidate), 18)}-{safe_filename_part(candidate.domain, 18)}-{candidate.candidate_id}.md"


def yaml_value(value: str | int) -> str:
    text = str(value or "").replace('"', '\\"')
    return f'"{text}"'


def markdown_for(decision: DraftDecision) -> str:
    candidate = decision.candidate
    meta = {
        "candidate_id": candidate.candidate_id,
        "name": display_name(candidate),
        "domain": candidate.domain,
        "candidate_class": candidate.candidate_class,
        "score": candidate.score,
        "draft_type": decision.draft_type,
        "source_url": candidate.source_url,
        "evidence_url": decision.evidence_url,
        "contact_url": decision.contact_url,
        "personalization_basis": decision.personalization_basis,
        "status": READY,
    }
    lines = ["---"]
    for key, value in meta.items():
        lines.append(f"{key}: {yaml_value(value)}")
    lines.extend(["---", "", f"Betreff: {decision.subject}", "", decision.draft_text, ""])
    return "\n".join(lines)


def write_outputs(decisions: list[DraftDecision], output_dir: Path) -> dict[str, int]:
    ready_dir = output_dir / "ready"
    ready_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    for stale in ready_dir.glob("*.md"):
        stale.unlink()
    index_rows: list[dict[str, str | int]] = []
    manual_rows: list[dict[str, str | int]] = []
    rejected_rows: list[dict[str, str | int]] = []
    ready_count = 0
    for rank, decision in enumerate(decisions, start=1):
        candidate = decision.candidate
        if decision.status == READY:
            ready_count += 1
            filename = draft_filename(rank, candidate)
            decision.draft_file = f"ready/{filename}"
            (ready_dir / filename).write_text(markdown_for(decision), encoding="utf-8")
        row = index_row(rank, decision)
        index_rows.append(row)
        if decision.status == MANUAL:
            manual_rows.append(row)
        if decision.status == REJECTED:
            rejected_rows.append(row)
    write_dict_csv(output_dir / "draft_index.csv", index_rows, INDEX_FIELDS)
    write_dict_csv(output_dir / "manual_review.csv", manual_rows, INDEX_FIELDS)
    write_dict_csv(output_dir / "rejected.csv", rejected_rows, INDEX_FIELDS)
    write_overview(output_dir / "overview.md", decisions)
    return {
        "ready": ready_count,
        "manual_review": len(manual_rows),
        "rejected": len(rejected_rows),
        "drafts": ready_count,
    }


INDEX_FIELDS = [
    "rank",
    "candidate_id",
    "name",
    "domain",
    "candidate_class",
    "score",
    "draft_file",
    "draft_type",
    "subject",
    "salutation",
    "source_url",
    "evidence_url",
    "contact_url",
    "personalization_basis",
    "status",
    "review_notes",
]


def index_row(rank: int, decision: DraftDecision) -> dict[str, str | int]:
    candidate = decision.candidate
    return {
        "rank": rank,
        "candidate_id": candidate.candidate_id,
        "name": display_name(candidate),
        "domain": candidate.domain,
        "candidate_class": candidate.candidate_class,
        "score": candidate.score,
        "draft_file": decision.draft_file,
        "draft_type": decision.draft_type,
        "subject": decision.subject,
        "salutation": decision.salutation,
        "source_url": remove_fragment_url(candidate.source_url),
        "evidence_url": decision.evidence_url,
        "contact_url": decision.contact_url,
        "personalization_basis": decision.personalization_basis,
        "status": decision.status,
        "review_notes": decision.review_notes,
    }


def write_dict_csv(path: Path, rows: list[dict[str, str | int]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_overview(path: Path, decisions: list[DraftDecision]) -> None:
    counts = {status: sum(1 for decision in decisions if decision.status == status) for status in (READY, MANUAL, REJECTED)}
    lines = [
        "# Tailored Outreach Overview",
        "",
        f"- Eindeutige Websites: {len(decisions)}",
        f"- Ready: {counts[READY]}",
        f"- Manual Review: {counts[MANUAL]}",
        f"- Rejected: {counts[REJECTED]}",
        "",
        "## Ready",
        "",
    ]
    for decision in decisions:
        if decision.status == READY:
            lines.append(f"- {display_name(decision.candidate)} ({decision.candidate.domain}) -> {decision.draft_file}")
    lines.extend(["", "## Hinweise", "", "Es wurden keine Nachrichten versendet und keine Formulare ausgefuellt."])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def generate(
    candidates_path: Path,
    output_dir: Path,
    minimum_score: int = 50,
    maximum_drafts: int | None = None,
) -> tuple[list[CandidateRow], list[CandidateRow], list[DraftDecision]]:
    candidates = load_candidates(candidates_path)
    unique = dedupe_candidates(candidates)
    decisions: list[DraftDecision] = []
    ready_seen = 0
    for candidate in sorted(unique, key=candidate_sort_key):
        decision = decide(candidate, minimum_score)
        if decision.status == READY:
            if maximum_drafts is not None and ready_seen >= maximum_drafts:
                decision.status = MANUAL
                decision.review_notes = "Maximum ready draft limit reached."
            else:
                decision.draft_text = build_message(decision)
                errors = quality_check(decision)
                if errors:
                    decision.status = MANUAL
                    decision.review_notes = "Automatische Qualitaetskontrolle: " + ", ".join(errors)
                    decision.draft_text = ""
                else:
                    ready_seen += 1
        decisions.append(decision)
    write_outputs(decisions, output_dir)
    return candidates, unique, decisions


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate tailored Mention Radar outreach drafts.")
    parser.add_argument("--candidates", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--seeds", type=Path, default=None, help="Optional; accepted for workflow compatibility.")
    parser.add_argument("--minimum-score", type=int, default=50)
    parser.add_argument("--maximum-drafts", type=int, default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    candidates, unique, decisions = generate(args.candidates, args.output_dir, args.minimum_score, args.maximum_drafts)
    print(f"candidates_read={len(candidates)}")
    print(f"unique_websites={len(unique)}")
    print(f"ready={sum(1 for decision in decisions if decision.status == READY)}")
    print(f"manual_review={sum(1 for decision in decisions if decision.status == MANUAL)}")
    print(f"rejected={sum(1 for decision in decisions if decision.status == REJECTED)}")
    print(f"output_dir={args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
