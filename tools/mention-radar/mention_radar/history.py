from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, Iterable

from .models import Candidate
from .safety import TRACKING_COLUMNS


def tracking_path(base_dir: str | Path = "local-data/mention-radar") -> Path:
    return Path(base_dir) / "tracking.csv"


def load_tracking(path: str | Path) -> Dict[str, dict]:
    file_path = Path(path)
    if not file_path.exists():
        return {}
    with open(file_path, "r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return {row.get("candidate_id", ""): row for row in reader if row.get("candidate_id")}


def apply_tracking(candidates: Iterable[Candidate], tracking: Dict[str, dict]) -> tuple[int, int]:
    new_count = 0
    known_count = 0
    for candidate in candidates:
        record = tracking.get(candidate.candidate_id)
        if record:
            known_count += 1
            candidate.known_candidate = True
            candidate.review_status = record.get("review_status") or candidate.review_status
            candidate.notes = record.get("notes") or candidate.notes
            candidate.contacted_at = record.get("contacted_at", "")
            candidate.follow_up_at = record.get("follow_up_at", "")
            candidate.response = record.get("response", "")
            candidate.publication_url = record.get("publication_url", "")
        else:
            new_count += 1
    return new_count, known_count


def write_tracking(candidates: Iterable[Candidate], path: str | Path, existing: Dict[str, dict]) -> None:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    merged = dict(existing)
    for candidate in candidates:
        current = merged.get(candidate.candidate_id, {})
        merged[candidate.candidate_id] = {
            "candidate_id": candidate.candidate_id,
            "review_status": current.get("review_status") or candidate.review_status,
            "notes": current.get("notes") or candidate.notes,
            "contacted_at": current.get("contacted_at") or candidate.contacted_at,
            "follow_up_at": current.get("follow_up_at") or candidate.follow_up_at,
            "response": current.get("response") or candidate.response,
            "publication_url": current.get("publication_url") or candidate.publication_url,
        }
    with open(file_path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=TRACKING_COLUMNS)
        writer.writeheader()
        for candidate_id in sorted(merged):
            row = {column: merged[candidate_id].get(column, "") for column in TRACKING_COLUMNS}
            row["candidate_id"] = candidate_id
            writer.writerow(row)
