from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable, List

from .drafts import create_draft
from .models import Candidate
from .safety import ensure_output_dirs


CANDIDATE_COLUMNS = [
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

EXCLUDED_COLUMNS = ["URL", "Ausschlussgrund", "Klasse", "Datum"]


def export_all(candidates: Iterable[Candidate], output_dir: str | Path, generate_drafts: bool = True) -> Path:
    root = ensure_output_dirs(output_dir)
    items = list(candidates)
    write_candidates(items, root / "candidates.csv")
    write_excluded(items, root / "excluded.csv")
    write_opportunities(items, root / "opportunities.md")
    if generate_drafts:
        write_drafts(items, root / "drafts")
    return root


def write_candidates(candidates: List[Candidate], path: Path) -> None:
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CANDIDATE_COLUMNS)
        writer.writeheader()
        for candidate in candidates:
            writer.writerow({column: getattr(candidate, column) for column in CANDIDATE_COLUMNS})


def write_excluded(candidates: List[Candidate], path: Path) -> None:
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=EXCLUDED_COLUMNS)
        writer.writeheader()
        for candidate in candidates:
            if candidate.candidate_class in {"C", "D"}:
                writer.writerow(
                    {
                        "URL": candidate.relevant_page,
                        "Ausschlussgrund": candidate.notes or "Keine passende Einreichungsmoeglichkeit.",
                        "Klasse": candidate.candidate_class,
                        "Datum": candidate.fetched_at,
                    }
                )


def write_opportunities(candidates: List[Candidate], path: Path) -> None:
    selected = [candidate for candidate in candidates if candidate.candidate_class in {"A", "B"}]
    selected.sort(key=lambda item: (item.candidate_class, -item.score))
    selected = selected[:10]
    lines = [
        "# Mention Radar: pruefenswerte Moeglichkeiten",
        "",
        "Diese Liste ist eine lokale Arbeitsansicht. Bitte jeden Eintrag manuell pruefen, bevor Kontakt aufgenommen wird.",
        "",
    ]
    for candidate in selected:
        lines.extend(
            [
                f"## {candidate.name}",
                "",
                f"- Klasse: {candidate.candidate_class}",
                f"- Score: {candidate.score}",
                f"- Seed: {candidate.seed_url}",
                f"- Fundstelle: {candidate.relevant_page}",
                f"- Fundart: {candidate.discovery_source}",
                f"- Beleg: {candidate.permission_evidence or 'kein ausdruecklicher Einreichungshinweis'}",
                f"- Kontaktweg: {candidate.public_contact_method or 'manuell pruefen'}",
                f"- Vorschlag: {candidate.suggested_angle}",
                f"- Material: {candidate.suggested_material}",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_drafts(candidates: List[Candidate], drafts_dir: Path) -> None:
    drafts_dir.mkdir(parents=True, exist_ok=True)
    for candidate in candidates:
        if candidate.candidate_class != "A":
            continue
        draft = create_draft(candidate)
        if draft:
            (drafts_dir / f"{candidate.candidate_id}.md").write_text(draft + "\n", encoding="utf-8")
