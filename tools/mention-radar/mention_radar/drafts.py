from __future__ import annotations

import textwrap

from .models import Candidate


STANDARD_CLOSING = (
    "Die redaktionelle Entscheidung liegt selbstverständlich vollständig bei Ihnen. "
    "Mit der Zusendung eines Exemplars ist weder eine Veröffentlichung noch eine positive Bewertung oder Verlinkung verbunden."
)


def create_draft(candidate: Candidate) -> str:
    if candidate.candidate_class != "A":
        return ""
    evidence = candidate.permission_evidence or "Ihre öffentlich sichtbare Einreichungsmöglichkeit"
    material = _format_material(candidate.suggested_material)
    body = f"""
    Guten Tag,

    auf Ihrer Seite habe ich den Hinweis gesehen: "{evidence}". Deshalb möchte ich Ihnen den Ratgeber "Baby und Katze sicher zusammenführen" aus dem Farbenfrohe Lesewelt Verlag kurz als möglichen redaktionellen Anlass vorstellen.

    Andrea Blum ist die Autorin des Buches. Der Ratgeber richtet sich an Familien, die Schwangerschaft, Babyalltag und das Zusammenleben mit Katze ruhig strukturieren möchten. Inhaltlich passt besonders der Winkel "{candidate.suggested_angle}".

    Bei Interesse können Sie die Presseinformationen hier prüfen: {material}. Ein Rezensionsexemplar kann unverbindlich angefragt werden; Format und Verfügbarkeit stimmen wir individuell ab.

    {STANDARD_CLOSING}

    Freundliche Grüße
    Farbenfrohe Lesewelt Verlag
    """
    return _limit_words(textwrap.dedent(body).strip(), 170)


def _format_material(material: str) -> str:
    items = [item.strip() for item in material.split("|") if item.strip()]
    return ", ".join(items[:3])


def _limit_words(text: str, max_words: int) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[: max_words - 1]).rstrip(".,;") + "."
