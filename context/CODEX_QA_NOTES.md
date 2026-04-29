# Codex QA Notes - Checkliste

## Refine checklist design and partner wording

Datum: 2026-04-29

### Geaenderte Dateien

- `/assets/downloads/checkliste-baby-katze-5-sicherheitsregeln.pdf`
- `/checkliste/5-sicherheitsregeln.html`
- `/checkliste/index.html`
- `/partner/index.html`
- `/partner/tierarztpraxen/index.html`
- `/partner/hebammen/index.html`
- `/partner/katzenschutz/index.html`
- `/material-anfragen/index.html`
- `/go/hebamme-demo/index.html`
- `/go/katzenschutz-demo/index.html`
- `/context/CODEX_QA_NOTES.md`

### Entscheidung und Wording

- Die fruehere Checklisten-Logik wurde als Designbasis aufgegriffen: 3 A4-Abschnitte, grosse Nummern 1 bis 5, konkrete Alltagssituationen, Zonen-Grafik, hervorgehobener 10-Sekunden-Reset und Buch-Bruecke.
- Claims wurden entschärft: keine harten Sicherheitsversprechen, keine Paniksprache, keine medizinische oder tieraerztliche Autoritaetsrolle.
- Partnerseiten wurden staerker aus Sicht der Einrichtungen formuliert: Wartezimmer, Kursraum, Nachgespraech, Beratung, Website, Newsletter, QR-Karte und Mitnahmematerial.
- Materialanfrage nutzt einen freundlicheren vorbereiteten E-Mail-Body und nennt digitales oder gedrucktes Material nach Absprache.
- Go-Seiten fuer Hebamme und Katzenschutz nutzen jetzt dieselbe ruhige Fuehrung wie die Tierarzt-Brueckenseite.
- Checklisten-Preview auf `/checkliste/` beschreibt die neue Mini-Workbook-PDF mit Beispielen, Zonen-System und 10-Sekunden-Reset.

### PDF-Pruefung

- PDF neu erzeugt: Ja.
- PDF-Dateigroesse: 417812 Bytes.
- PDF-Header: gueltig.
- HTML-Layout der druckbaren Checkliste: 3 Seiten, kein horizontaler Overflow, keine JavaScript-Fehler.
- Sichtbare URLs in der Abschlussbox bleiben ohne Umbruch in ihrer Box.

### QA-Ergebnis

- Alte Amazon-Trackingmuster: 0 Treffer.
- Amazon-Produktlinks mit Query-String: 0 Treffer.
- Google-Forms-Kurzlinks: 0 Treffer.
- Amazon-Zielseite neutral: Ja, Buchlinks zeigen auf `https://www.amazon.de/dp/B0GTDN1458`.
- PDF-Download auf `/checkliste/`: zeigt direkt auf `/assets/downloads/checkliste-baby-katze-5-sicherheitsregeln.pdf`.
- Materialanfrage-Mailto: Body vorhanden, inklusive Einrichtung, Ansprechpartner, Adresse, gewuenschtem Material und Einsatzort.
- Offline-Bruecken: Links behalten `src=offline` und den jeweiligen Partnerwert.
- Pinterest-Checklistenlinks: Kampagnenparameter fuer die jeweiligen Themen bleiben vorhanden.
- Mobile Ansicht: lokal bei 390 px fuer Checkliste, Partner-, Material-, Go- und Pinterest-Seiten geprueft; kein horizontaler Overflow.
- Konsolenpruefung: keine JavaScript-Fehler auf den lokal geprueften Seiten.

### Offene Punkte

- Keine bekannten offenen Punkte aus dieser Runde.

## Funnel-Polish Partner, Pinterest und Checkliste

Datum: 2026-04-29

### Geaenderte Dateien

- `/assets/js/partner-pages.js`
- `/assets/js/pinterest-funnel.js`
- `/assets/downloads/checkliste-baby-katze-5-sicherheitsregeln.pdf`
- `/styles.css`
- `/checkliste/index.html`
- `/checkliste/5-sicherheitsregeln.html`
- `/partner/index.html`
- `/partner/tierarztpraxen/index.html`
- `/partner/hebammen/index.html`
- `/partner/katzenschutz/index.html`
- `/material-anfragen/index.html`
- `/go/tierarzt-demo/index.html`
- `/go/hebamme-demo/index.html`
- `/go/katzenschutz-demo/index.html`
- `/pinterest/index.html`
- `/pinterest/katze-im-babybett/index.html`
- `/pinterest/toxoplasmose-katze-schwangerschaft/index.html`
- `/pinterest/baby-und-katze-zusammenfuehren/index.html`
- `/pinterest/katze-eifersuechtig-baby/index.html`
- `/pinterest/erste-begegnung-baby-und-katze/index.html`
- `/pinterest/alltag-mit-baby-und-katze/index.html`
- `/context/CODEX_QA_NOTES.md`

### Wichtigste Wording-Aenderungen

- Clickbait-nahe Formulierungen auf Pinterest entschärft, besonders bei Babybett, Toxoplasmose, Eifersucht und ersten Begegnungen.
- Checklisten-Seite ruhiger formuliert; PDF-Downloadlinks geben keine URL-Parameter mehr an die PDF weiter.
- Partnerseiten stärker auf konkreten Nutzen für Einrichtungen ausgerichtet: wiederkehrende Fragen auffangen, QR-Link, Aushang, Mitnahmekarte und kurzer Hinweistext.
- `/go/`-Brückenseiten menschlicher formuliert und mit korrekten Umlauten versehen.
- Materialanfrage mit vorbereitetem E-Mail-Body ergänzt.

### Tracking und Consent

- Option A umgesetzt: Partner-, Go- und Pinterest-Seiten erhalten über die bestehenden lokalen JS-Dateien einen kleinen Consent-Banner.
- Tracking bleibt an `flw_meta_consent = granted` gebunden; ohne Einwilligung werden keine Meta-Events gesendet.
- URL-Parameter werden weitergereicht, ohne vorhandene feste Kampagnenwerte auf Checklisten- und Offline-Links zu überschreiben.

### Pruefung

- PDF neu erzeugt: Ja. Die druckbare HTML-Checkliste wurde geändert; PDF wurde ersetzt und mit gültigem `%PDF-`-Header geprüft.
- Mobile Ansicht geprüft: Ja. Lokaler Browser-Check bei 390 px für Checkliste, Partner-, Material-, Go- und Pinterest-Seiten ohne horizontalen Overflow.
- Konsolenprüfung: Ja. Keine JavaScript-Fehler auf den lokal geprüften Seiten.
- Checklisten-Download: Direkter PDF-Link funktioniert, ohne angehängte Tracking-Parameter.
- Materialanfrage: Mailto-Links enthalten den vorbereiteten Body mit Einrichtung, Ansprechpartner, Adresse, gewünschtem Material und Einsatzort.
- Offline-Brücken: Links behalten `src=offline` und den jeweiligen Partnerwert.
- Pinterest-Funnel: Checklistenlinks behalten `src=pinterest` und die jeweilige Kampagne; Amazon steht nicht mehr im ersten Funnel-Kasten.
- Amazon-Zielseite neutral: Ja. Produktlinks bleiben queryfrei.
- Suchergebnis: Amazon-Altparameter, Amazon-Produktlinks mit Query-String und Google-Forms-Kurzlinks jeweils 0 Treffer im Repo.
- Claims geprüft: Keine neuen Garantien, keine harten Sicherheitsversprechen, keine Paniksprache, keine Andrea-Blum-Kontaktrolle und keine medizinische/tierärztliche Fachautorität ergänzt.

### Offene Punkte

- Keine bekannten offenen Punkte aus dieser Polishing-Runde.

## Phase 5 - Pinterest-Funnel

Datum: 2026-04-29

### Geaenderte Dateien

- `/assets/js/pinterest-funnel.js`
- `/styles.css`
- `/pinterest/index.html`
- `/pinterest/katze-im-babybett/index.html`
- `/pinterest/toxoplasmose-katze-schwangerschaft/index.html`
- `/pinterest/baby-und-katze-zusammenfuehren/index.html`
- `/pinterest/katze-eifersuechtig-baby/index.html`
- `/pinterest/erste-begegnung-baby-und-katze/index.html`
- `/pinterest/alltag-mit-baby-und-katze/index.html`
- `/context/CODEX_QA_NOTES.md`

### Pruefung

- Pinterest-Funnel umgesetzt: Jede Pinterest-Seite hat eine primaere Checklisten-Ebene, eine neutrale Amazon-Buchebene und eine thematisch passende Weiterleitung.
- Themenspezifische CTA-Boxen umgesetzt: Ja. Die sechs Unterseiten verwenden die vorgegebenen Headlines, Kurztexte und den Button `Checkliste ansehen`.
- Checklisten-Parameter gesetzt: Ja. Alle Unterseiten verlinken auf `/checkliste/?src=pinterest&campaign={slug}`; die Hauptseite nutzt `campaign=pinterest-hauptseite`.
- URL-Parameter werden weitergereicht: Ja. `src`, `campaign` und `medium` werden per `data-preserve-params` nur ergaenzt, wenn sie im Ziel-Link noch nicht gesetzt sind.
- Events umgesetzt: `checklist_click` und `amazon_click` ueber `data-event`/`data-label` und consent-respektierende Meta-Pixel-Logik.
- Amazon-Zielseite neutral: Ja. Amazon-Links verweisen auf `https://www.amazon.de/dp/B0GTDN1458`.
- Google-Forms-Links: Keine verwendet.
- Mobile Ansicht geprueft: Ja. Lokaler Browser-Check bei 390 px fuer alle sieben Pinterest-Seiten ohne horizontalen Overflow.
- Suchergebnis: Amazon-Altparameter, Amazon-Produktlinks mit Query-String und Google-Forms-Kurzlinks jeweils 0 Treffer ausserhalb von `.git`.
- Claims geprueft: In den neuen CTA-Texten wurden keine Garantien, keine medizinische/tieraerztliche Fachautoritaet, keine Paniksprache und keine Andrea-Blum-Kontaktrolle ergaenzt.

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
