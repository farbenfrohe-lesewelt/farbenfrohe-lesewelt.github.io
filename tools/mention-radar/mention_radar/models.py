from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class Seed:
    url: str
    name: str = ""
    source: str = "manual"
    notes: str = ""


@dataclass
class FetchResult:
    url: str
    final_url: str
    status_code: int = 0
    title: str = ""
    text: str = ""
    html: str = ""
    fetched_at: str = ""
    error: str = ""
    skipped_reason: str = ""
    contact_methods: List[str] = field(default_factory=list)
    follow_links: List[str] = field(default_factory=list)
    seed_url: str = ""
    discovery_source: str = "seed"


@dataclass
class Candidate:
    candidate_id: str
    name: str
    website: str
    relevant_page: str
    page_title: str
    candidate_class: str
    score: int
    topic_fit: int
    audience_fit: int
    submission_permission: str
    permission_evidence: str
    evidence_url: str
    public_contact_method: str
    suggested_angle: str
    suggested_material: str
    fetched_at: str
    review_status: str = "new"
    notes: str = ""
    seed_url: str = ""
    discovery_source: str = "seed"
    contacted_at: str = ""
    follow_up_at: str = ""
    response: str = ""
    publication_url: str = ""
    known_candidate: bool = False
