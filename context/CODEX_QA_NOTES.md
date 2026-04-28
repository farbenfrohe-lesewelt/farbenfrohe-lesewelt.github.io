# Codex QA Notes - Checkliste

## Phase 4 - Partnerseiten und Offline-Bruecken

Datum: 2026-04-28

### Geaenderte Dateien

- `/assets/js/partner-pages.js`
- `/styles.css`
- `/index.html`
- `/checkliste/index.html`
- `/partner/index.html`
- `/partner/tierarztpraxen/index.html`
- `/partner/hebammen/index.html`
- `/partner/katzenschutz/index.html`
- `/material-anfragen/index.html`
- `/go/tierarzt-demo/index.html`
- `/go/hebamme-demo/index.html`
- `/go/katzenschutz-demo/index.html`
- `/tt/index.html`
- `/context/CODEX_QA_NOTES.md`

### Pruefung

- Partnerstruktur erstellt: Uebersicht, Seiten fuer Tierarztpraxen, Hebammen/Geburtseinrichtungen und Katzenschutz/Tierheime.
- Materialanfrage erstellt: Ja. `/material-anfragen/` ist mailto-basiert und zeigt eine ausfuellbare Anfragevorlage.
- Offline-Brueckenseiten erstellt: Ja. Die `/go/.../`-Seiten fuehren nicht direkt zu Amazon, sondern bieten Checkliste, Buchlink und Materialanfrage an.
- Amazon-Zielseite neutral: Ja. Buchlinks verweisen auf `https://www.amazon.de/dp/B0GTDN1458`.
- Google-Forms-Links entfernt: Ja. Der verbliebene Forms-Link in `/tt/` wurde durch den direkten Checklisten-Link ersetzt.
- URL-Parameter werden weitergereicht: Ja. `src`, `partner`, `campaign` und `medium` werden an interne Links mit `data-preserve-params` angehaengt; Offline-Bruecken setzen passende `src=offline`- und `partner=`-Werte.
- Events umgesetzt: `partner_page_view`, `checklist_click`, `material_request_click`, `amazon_click` ueber `data-event` und consent-respektierende Meta-Pixel-Logik.
- Disclaimer vorhanden: Ja. Sichtbar auf Partner-, Material- und Offline-Brueckenseiten.
- Sitemap: Keine Sitemap-Datei im Repo vorhanden; daher keine Ergaenzung noetig.
- Mobile Ansicht geprueft: Ja. Lokaler Browser-Check bei 390 px fuer alle neuen Seiten ohne horizontalen Overflow.
- CTA-Ziele geprueft: Ja. Checklisten- und Materiallinks bleiben intern mit Parametern, Amazon-Links sind neutral, Mailto bleibt nur auf der Materialanfrage.
- Suchergebnis: Alle geforderten Altparameter, Amazon-Produktlinks mit Query-String und Google-Forms-Kurzlinks jeweils 0 Treffer ausserhalb von `.git`.
- Claims geprueft: In den neuen und geaenderten Phase-4-Dateien wurden keine Garantien, keine medizinische/tieraerztliche Fachautoritaet, keine Paniksprache und keine Andrea-Blum-Kontaktrolle ergaenzt.

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

## Phase 2 - Checklisten-Landingpage

Datum: 2026-04-28

### Geänderte Dateien

- `/checkliste/index.html`
- `/context/CODEX_QA_NOTES.md`

### Prüfung

- Neue Seitenstruktur umgesetzt: Hero, Problemsektion, Vorschau der 5 Regeln, Buch-Brücke, Partner-Hinweis, Disclaimer und Footer.
- Checkliste sofort downloadbar: Ja. Der primäre CTA bleibt ein direkter Link auf `/checkliste/5-sicherheitsregeln.html` mit `download`-Attribut.
- Amazon-Zielseite neutral: Ja. Der Buchlink auf `/checkliste/` verweist auf `https://www.amazon.de/dp/B0GTDN1458`.
- Google-Forms-Links auf `/checkliste/`: Keine verwendet.
- URL-Parameter werden weitergereicht: Ja. `src`, `partner`, `campaign` und `medium` werden an interne Links mit `data-preserve-params` angehängt.
- Consent-/Tracking-Logik respektiert: Ja. Meta-Events werden nur nach vorhandener Einwilligung ausgelöst.
- Events/Labels umgesetzt: `checklist_download`, `amazon_click`, `material_request_click` über bestehende Eventlogik und zusätzliche `data-event`/`data-label`-Attribute.
- Ansprechpartner korrekt: Materialanfragen laufen über Farbenfrohe Lesewelt Verlag / Patrick Guttenberger.
- Disclaimer vorhanden: Ja. Sichtbar im unteren Seitenbereich.
- Mobile Ansicht geprüft: Ja. Lokaler Browser-Check bei 390 px Breite ohne horizontalen Overflow; Download-Link und Parameterweitergabe im DOM geprüft.
- Claims geprüft: Keine Garantien, keine medizinische/tierärztliche Fachautorität, keine Paniksprache und keine Andrea-Blum-Kontaktrolle ergänzt.

### Offene Punkte

- `/material-anfragen/` existiert derzeit nicht. Der Material-CTA nutzt deshalb vorerst den vorgesehenen Mailto-Link.

## Phase 3 - Druckbare Checkliste

Datum: 2026-04-28

### Geänderte Dateien

- `/checkliste/5-sicherheitsregeln.html`
- `/checkliste/index.html`
- `/assets/downloads/checkliste-baby-katze-5-sicherheitsregeln.pdf`
- `/context/CODEX_QA_NOTES.md`

### Prüfung

- Druckbare HTML-Checkliste überarbeitet: neuer Titel, Einstieg, fünf Regelmodule, Mini-Merker, Buch-Brücke, Website-Link, Disclaimer und Kontaktzeile.
- PDF erzeugt: Ja. Der Export wurde lokal über Chrome/Playwright erstellt und als PDF-Datei unter `/assets/downloads/checkliste-baby-katze-5-sicherheitsregeln.pdf` gespeichert.
- Download-Ziel auf `/checkliste/`: Ja. Die Downloadbuttons verweisen nun direkt auf die PDF-Datei.
- Amazon-Zielseite neutral: Ja. Der Buchlink in der druckbaren Checkliste verweist auf `https://www.amazon.de/dp/B0GTDN1458`.
- Google-Forms-Links auf `/checkliste/`: Keine verwendet.
- Druckansicht geprüft: Ja. PDF-Export erfolgreich, Dateikopf `%PDF-`, Dateigröße ca. 198 KB.
- Mobile Ansicht geprüft: Ja. Lokaler Browser-Check bei 390 px Breite ohne horizontalen Overflow.
- Claims geprüft: Keine Garantien, keine medizinische/tierärztliche Fachautorität, keine Paniksprache und keine Andrea-Blum-Kontaktrolle ergänzt.
