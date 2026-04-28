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

## Amazon-Link-Bereinigung

Datum: 2026-04-28

### Gefundene alte Linktypen

- Amazon-Produktlinks mit Marketing- und Affiliate-ähnlichen Query-Parametern.
- Partnerabhängige Amazon-Link-Maps auf der Startseite und in der Leseprobe.
- Datenschutz-Hinweis auf frühere Amazon-Marketingparameter.

### Geänderte Dateien

- `/assets/js/links.js`
- `/index.html`
- `/baby/index.html`
- `/schwangerschaft/index.html`
- `/checkliste/index.html`
- `/leseprobe/index.html`
- `/pinterest/index.html`
- `/pinterest/alltag-mit-baby-und-katze/index.html`
- `/pinterest/baby-und-katze-zusammenfuehren/index.html`
- `/pinterest/erste-begegnung-baby-und-katze/index.html`
- `/pinterest/katze-eifersuechtig-baby/index.html`
- `/pinterest/katze-im-babybett/index.html`
- `/pinterest/toxoplasmose-katze-schwangerschaft/index.html`
- `/legal/datenschutz.html`
- `/context/CODEX_QA_NOTES.md`

### Ergebnis der Nachsuche

- Entfernte Amazon-Marketingparameter: 0 verbleibende Treffer.
- Amazon-Produktlinks mit Query-String: 0 verbleibende Treffer.
- Google-Forms-Links auf `/checkliste/`: 0 verbleibende Treffer.
- Review-Link: 0 verbleibende Treffer; es wurden keine neuen Rezensionslinks eingeführt.
