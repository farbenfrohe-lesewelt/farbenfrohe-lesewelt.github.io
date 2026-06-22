# Mention Radar

Mention Radar ist ein lokales Python-Werkzeug fuer menschengepruefte Recherche zu redaktionellen Erwaehnungsmoeglichkeiten. Es hilft dabei, oeffentlich zugaengliche Seiten, RSS-Feeds oder manuell exportierte URL-Listen zu pruefen, Einreichungshinweise zu dokumentieren und fuer passende Klasse-A-Faelle einen ersten Entwurf vorzubereiten.

Das Werkzeug sendet keine Nachrichten, legt keine Profile an, veroeffentlicht keine Kommentare und fuellt keine Formulare aus. Es ist ein Recherche- und Dokumentationshelfer; jede Kontaktaufnahme bleibt manuell.

## Grenzen der Automatisierung

- keine automatisierte Nutzung von Suchmaschinenergebnisseiten
- keine Umgehung von Logins, Captchas, Paywalls oder Zugriffsbeschraenkungen
- keine automatische Ermittlung privater Kontaktdaten
- keine gekauften, getauschten oder geforderten Backlinks
- keine Kopplung eines Rezensionsexemplars an Veroeffentlichung, Bewertung oder Verlinkung
- keine erfundenen Reichweiten-, Ranking- oder Autoritaetswerte
- keine automatische Kontaktaufnahme

## Erstinstallation

Voraussetzung ist Python 3.11 oder neuer.

```powershell
python -m venv .\tools\mention-radar\.venv
.\tools\mention-radar\.venv\Scripts\python.exe -m pip install -r .\tools\mention-radar\requirements.txt
```

Der Windows-Runner kann die Umgebung ebenfalls anlegen:

```powershell
.\tools\mention-radar\run-mention-radar.ps1 -Url "https://example.com/rezensionen"
```

Mit `-NoInstall` wird die Paketinstallation uebersprungen, wenn die Umgebung bereits eingerichtet ist.

## CSV-Aufbau

Eine manuelle Seed-Datei enthaelt mindestens die Spalte `url`.

```csv
url,name,source,notes
https://example.com/rezensionen,Beispiel Rezensionsseite,manual,Fiktive Beispielzeile
https://example.org/presse,Beispiel Presseseite,manual,Fiktive Beispielzeile
```

Echte Arbeitsdateien gehoeren nach `local-data/mention-radar/` und werden nicht versioniert.

## Erster CSV-Lauf

```powershell
.\tools\mention-radar\run-mention-radar.ps1 -InputCsv ".\local-data\mention-radar\seeds.csv"
```

## Einzelne URL

```powershell
.\tools\mention-radar\run-mention-radar.ps1 -Url "https://example.com/rezensionen"
```

## Mehrere URLs

```powershell
.\tools\mention-radar\run-mention-radar.ps1 `
  -Url "https://example.com/rezensionen" `
  -Url "https://example.org/presse"
```

## RSS-Feed

```powershell
.\tools\mention-radar\run-mention-radar.ps1 -Feed "https://example.com/feed.xml"
```

## Feed-Liste

Eine Feed-Liste ist eine lokale Textdatei mit einer Feed-URL pro Zeile. Leerzeilen und Zeilen mit `#` am Anfang werden ignoriert.

```powershell
.\tools\mention-radar\run-mention-radar.ps1 -FeedList ".\local-data\mention-radar\feeds.txt"
```

`feed-list.example.txt` ist nur eine fiktive Vorlage. Echte Feed-Sammlungen nicht committen.

## Datierte Runs

Ohne `--output-dir` beziehungsweise ohne `-OutputDir` schreibt jeder Lauf in einen eigenen Ordner:

```text
local-data/mention-radar/runs/YYYY-MM-DD_HHMMSS/
```

Dadurch werden aeltere Ergebnisse und Entwuerfe nicht unbemerkt ueberschrieben. Ein expliziter Ausgabeordner bleibt moeglich:

```powershell
.\tools\mention-radar\run-mention-radar.ps1 `
  -Url "https://example.com/rezensionen" `
  -OutputDir ".\local-data\mention-radar\manual-run"
```

## tracking.csv

Die dauerhafte lokale Datei `local-data/mention-radar/tracking.csv` bewahrt manuelle Felder anhand der `candidate_id`:

- `review_status`
- `notes`
- `contacted_at`
- `follow_up_at`
- `response`
- `publication_url`

Wenn ein Kandidat erneut gefunden wird, werden vorhandene manuelle Werte uebernommen und nicht auf `new` zurueckgesetzt.

## Ausgaben

Jeder Run erzeugt:

- `candidates.csv`: alle geprueften Kandidaten mit Klasse, Score, Seed, Fundstelle und Status
- `opportunities.md`: maximal zehn beste Klasse-A- und pruefenswerte Klasse-B-Eintraege
- `excluded.csv`: ausgeschlossene Klasse-C- und Klasse-D-Eintraege
- `drafts/`: Entwuerfe nur fuer Klasse A

Der Kandidatenexport zeigt in `discovery_source`, ob eine Einreichungsmoeglichkeit direkt auf der Seed-URL oder auf einer kontrolliert gefolgten Unterseite gefunden wurde.

## Kontrolliertes Folgen interner Links

Wenn eine ausdruecklich uebergebene Startseite passende interne Links enthaelt, prueft Mention Radar innerhalb derselben Domain bis zu fuenf zusaetzliche Seiten mit passenden Linktexten oder Pfaden, zum Beispiel Presse, Redaktion, Rezension, Buchvorstellung, Interview, Podcast oder Kooperation.

Dabei gelten weiterhin `robots.txt`, Rate-Limit, Domain-Seitenlimit, HTML-Groessenlimit und die Sperre fuer Login-, Konto- und Kaufbereiche. Externe Links werden nicht automatisch verfolgt.

## Klassen

- A: ausdrueckliche Einreichungsmoeglichkeit, etwa Rezensionsexemplar, Themenvorschlag, Interview oder Medienanfrage
- B: oeffentlicher redaktioneller Kontakt ohne eindeutige Einladung
- C: keine erkennbare Einreichungsmoeglichkeit
- D: ungeeignet oder riskant, etwa Linkverkauf, Veroeffentlichungsgarantie, Linktausch oder thematisch unpassende Seite

Nur Klasse A erhaelt einen Entwurf. Klasse B bleibt fuer manuelle Pruefung. Klasse C und D werden ausgeschlossen.

## Individuelle Outreach-Entwuerfe

Der separate Generator `mention_radar.tailored_drafts` erstellt nach einem Radar-Lauf individuellere Outreach-Entwuerfe aus `candidates.csv`. Er verwendet nicht die technischen Standardentwuerfe aus `drafts/` oder `drafts-technical-discarded/`, sendet keine Nachrichten und legt keine E-Mails an.

Beispiel:

```powershell
.\tools\mention-radar\.venv\Scripts\python.exe -m mention_radar.tailored_drafts `
  --candidates .\local-data\mention-radar\runs\initial-seed-batch-20260622-135140\candidates.csv `
  --output-dir .\local-data\mention-radar\runs\initial-seed-batch-20260622-135140\tailored-outreach
```

Alternativ:

```powershell
.\tools\mention-radar\generate-tailored-drafts.ps1 `
  -Candidates .\local-data\mention-radar\runs\initial-seed-batch-20260622-135140\candidates.csv `
  -OutputDir .\local-data\mention-radar\runs\initial-seed-batch-20260622-135140\tailored-outreach
```

Der Generator dedupliziert pro Website, verwirft Share- und Kommentarlinks als Kontaktwege, erzeugt fertige Markdown-Dateien nur fuer `ready`-Faelle und schreibt `manual_review.csv` sowie `rejected.csv` fuer unsichere oder unpassende Kandidaten.

## Woechentlicher 30-Minuten-Workflow

1. Fuenf bis zehn neue Start-URLs oder Feed-Treffer lokal sammeln.
2. Radar ausfuehren.
3. Nur Klasse A und starke Klasse B oeffnen und manuell pruefen.
4. Maximal drei Klasse-A-Kandidaten auswaehlen.
5. Entwuerfe individuell korrigieren.
6. Manuell ueber den ausdruecklich angebotenen Kontaktweg senden.
7. Status in `tracking.csv` dokumentieren.
8. Hoechstens einmal nachfassen, nur wenn die Einreichungsbedingungen dies erlauben.
