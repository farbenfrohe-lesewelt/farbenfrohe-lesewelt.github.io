# Codex QA Notes - Checkliste

Datum: 2026-04-28

## Geänderte Dateien

- `/checkliste/index.html`
- `/checkliste/5-sicherheitsregeln.html`
- `/context/CODEX_QA_NOTES.md`

## Prüfung

- Checkliste sofort downloadbar: Ja. Der primäre CTA verlinkt direkt auf `/checkliste/5-sicherheitsregeln.html` mit `download`-Attribut. Es gibt keine Formularpflicht und keine manuelle PDF-Versendung.
- Disclaimer vorhanden: Ja. Sichtbar auf `/checkliste/` und in der druckbaren HTML-Checkliste.
- URL-Parameter werden weitergereicht: Ja. `src`, `partner`, `campaign` und `medium` werden per JavaScript an interne Links mit `data-preserve-params` angehängt.
- Consent-/Tracking-Logik respektiert: Ja. Die Seite nutzt die bestehende `flw_meta_consent`-Logik mit Banner. Das Meta-Pixel wird erst nach Einwilligung geladen.
- Events umgesetzt: `checklist_page_view`, `checklist_download`, `amazon_click`, `material_request_click`.
- Keine verbotenen Claims gefunden: In den geänderten Dateien wurden keine Garantien, keine medizinische/tierärztliche Fachautorität, keine Paniksprache und keine Autorinnen-Kontaktrolle verwendet.

## Offene Punkte

- Im Repo liegt keine PDF-Datei für die Checkliste. Deshalb wurde gemäß Vorgabe eine druckbare HTML-Version erstellt.
- Der HTML-Download kann je nach Browser entweder direkt gespeichert oder als Datei geöffnet werden; der Inhalt ist druckoptimiert.
