from __future__ import annotations

import re
from datetime import date

from .models import Candidate


def score_candidate(candidate: Candidate, normalized_text: str) -> int:
    if candidate.candidate_class == "D":
        return 0
    score = 0
    score += min(30, int(candidate.topic_fit))
    score += min(20, int(candidate.audience_fit))
    score += 20 if candidate.candidate_class == "A" else 8 if candidate.candidate_class == "B" else 0
    score += editorial_quality_points(normalized_text)
    score += freshness_points(normalized_text)
    score += 5 if candidate.suggested_angle else 0
    score -= penalties(normalized_text)
    if candidate.candidate_class == "C":
        score = min(score, 39)
    return max(0, min(100, score))


def editorial_quality_points(text: str) -> int:
    points = 5
    if any(term in text for term in ["redaktion", "impressum", "presse", "über uns"]):
        points += 4
    if any(term in text for term in ["artikel", "beitrag", "podcast", "magazin", "rezension"]):
        points += 3
    if len(text) > 1200:
        points += 3
    return min(15, points)


def freshness_points(text: str) -> int:
    years = [int(match) for match in re.findall(r"\b(20[1-3][0-9])\b", text)]
    if not years:
        return 4
    newest = max(years)
    current = date.today().year
    if newest >= current - 1:
        return 10
    if newest >= current - 2:
        return 7
    if newest >= current - 4:
        return 4
    return 0


def penalties(text: str) -> int:
    penalty = 0
    if text.count("affiliate") > 2 or "werbelink" in text:
        penalty += 10
    if len(text) < 400:
        penalty += 10
    if any(term in text for term in ["automatisch erstellt", "maschinell erzeugt", "generischer gastartikel"]):
        penalty += 20
    years = [int(match) for match in re.findall(r"\b(20[0-2][0-9])\b", text)]
    if years and max(years) < date.today().year - 2:
        penalty += 15
    return min(50, penalty)
