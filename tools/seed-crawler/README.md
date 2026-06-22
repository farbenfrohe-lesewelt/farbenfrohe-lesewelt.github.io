# Seed Crawler fuer Mention Radar

Der Seed Crawler findet, prueft und bewertet oeffentlich erreichbare Webseiten, die spaeter von Mention Radar untersucht werden koennen. Er sammelt nicht nur Suchtreffer, sondern dedupliziert Domains, crawlt jede Domain kontrolliert, waehlt die staerkste redaktionelle Einstiegsseite und schreibt eine kommagetrennte `seeds.csv`.

Ein Seed ist eine absolute HTTP- oder HTTPS-URL zu einer Website oder Unterseite, die fuer eine redaktionelle Erwaehnung, Rezension, ein Interview, einen Gastbeitrag oder eine Buchvorstellung in Frage kommt.

## Was gesucht wird

Geeignet sind vor allem:

- Buchblogs und Sachbuchrezensionen
- Katzen- und Haustierblogs oder kleine Medien
- Eltern-, Schwangerschafts- und Familienblogs
- eigene Podcast-Websites oder redaktionelle Podcast-Seiten
- kleinere redaktionelle Portale, Magazine, Newsletter oder Vereinsseiten

Besonders wertvoll sind Seiten mit klaren Signalen wie `Rezensionsexemplare willkommen`, `Buchvorschlaege`, `Themenvorschlaege`, `Podcastgaeste`, `Interview`, `Gastbeitrag`, `Presse` oder `Redaktion`.

## Was ausgeschlossen wird

Nicht aufgenommen werden Suchergebnisseiten, Social-Media-Profile, Amazon-/Shop-/Checkout-/Login-Seiten, grosse Plattformseiten wie Spotify oder Apple Podcasts, Linkverkauf, Dofollow-Angebote, Pressemitteilungsverteiler, reine Branchenbuecher, Contentfarmen, reine Hundeseiten, reine Onlineshops und thematisch unpassende Seiten.

Die Blocklisten liegen editierbar unter:

```text
tools/seed-crawler/config/domain_blocklist.txt
tools/seed-crawler/config/url_pattern_blocklist.txt
tools/seed-crawler/config/negative_terms.txt
```

## Installation

Voraussetzung ist Python 3.11 oder neuer. Der Kern nutzt die Python-Standardbibliothek.

```powershell
cd C:\Users\patri\Documents\Codex\2026-04-28\files-mentioned-by-the-user-5\farbenfrohe-lesewelt.github.io
python -m venv .\tools\seed-crawler\.venv
.\tools\seed-crawler\.venv\Scripts\python.exe -m pip install -r .\tools\seed-crawler\requirements.txt
.\tools\seed-crawler\.venv\Scripts\python.exe -m pip install -e .\tools\seed-crawler
```

Aktivieren:

```powershell
.\tools\seed-crawler\.venv\Scripts\Activate.ps1
```

## Suchanbieter konfigurieren

Der Crawler automatisiert keine Google-, Bing- oder andere Suchmaschinen-Weboberflaechen. Standardmaessig stehen zwei Modi bereit:

- `--provider brave`: offizieller Brave Search API Provider
- `--provider file`: lokaler Import vorhandener Ergebnis-URLs

Kopiere die Vorlage und trage lokale Werte ein:

```powershell
Copy-Item .\tools\seed-crawler\.env.example .\tools\seed-crawler\.env
```

Beispiel fuer die PowerShell-Umgebung:

```powershell
$env:SEED_CRAWLER_SEARCH_PROVIDER="brave"
$env:BRAVE_SEARCH_API_KEY="..."
```

Echte API-Schluessel gehoeren nicht ins Repository.

## Suchanfragen und Scoring bearbeiten

Die Suchanfragen stehen in:

```text
tools/seed-crawler/config/search_queries.yaml
```

Das Punktesystem steht in:

```text
tools/seed-crawler/config/scoring.yaml
```

Die Zielquoten sind:

- `book_blog`: 30
- `cat_pet_media`: 30
- `parent_family_media`: 25
- `podcast`: 15

Automatisch erzeugte Query-Varianten werden im `run_report.json` dokumentiert.

## Erster Dry-Run

Ein Dry-Run schreibt keine Ergebnisdateien:

```powershell
python -m seed_crawler discover --provider file --search-results .\local-data\mention-radar\search-results.csv --target 10 --dry-run
```

Alternativ steht nach der Installation auch der Konsolenbefehl `seed-crawler` zur Verfuegung.

## Schnellstart: 10-Seed-Pilot unter Windows

Diese Befehle ersetzen die produktive `local-data/mention-radar/seeds.csv` nicht. Der Pilot schreibt ausschliesslich nach `local-data/mention-radar/pilot-10/`.

1. Virtuelle Umgebung erstellen:

```powershell
cd C:\Users\patri\Documents\Codex\2026-04-28\files-mentioned-by-the-user-5\farbenfrohe-lesewelt.github.io
python -m venv .\tools\seed-crawler\.venv
```

2. Paket installieren:

```powershell
.\tools\seed-crawler\.venv\Scripts\python.exe -m pip install -r .\tools\seed-crawler\requirements.txt
.\tools\seed-crawler\.venv\Scripts\python.exe -m pip install -e .\tools\seed-crawler
```

3. `.env.example` kopieren:

```powershell
Copy-Item .\tools\seed-crawler\.env.example .\tools\seed-crawler\.env
```

4. `.env` bearbeiten:

```powershell
notepad .\tools\seed-crawler\.env
```

Erwartete Variablen:

```text
SEED_CRAWLER_SEARCH_PROVIDER=brave
BRAVE_SEARCH_API_KEY=
BRAVE_SEARCH_COUNTRY=de
BRAVE_SEARCH_LANG=de
```

Bereits gesetzte Windows-Umgebungsvariablen gewinnen vor Werten aus `.env`.

5. Ignore-Regeln pruefen:

```powershell
git check-ignore -v tools/seed-crawler/.env
git check-ignore -v tools/seed-crawler/.venv/
git check-ignore -v local-data/mention-radar/
```

6. `doctor` ausfuehren:

```powershell
.\tools\seed-crawler\.venv\Scripts\python.exe -m seed_crawler doctor
```

7. Pilot starten:

```powershell
.\tools\seed-crawler\.venv\Scripts\python.exe -m seed_crawler pilot --provider brave --output-dir local-data/mention-radar/pilot-10 --verbose
```

Einzeilige PowerShell-Variante:

```powershell
.\tools\seed-crawler\.venv\Scripts\python.exe -m seed_crawler pilot --provider brave --output-dir .\local-data\mention-radar\pilot-10 --verbose
```

8. Pilot validieren:

```powershell
.\tools\seed-crawler\.venv\Scripts\python.exe -m seed_crawler validate .\local-data\mention-radar\pilot-10\seeds.csv --target 10
```

9. Ergebnisse oeffnen:

```powershell
notepad .\local-data\mention-radar\pilot-10\pilot_summary.md
notepad .\local-data\mention-radar\pilot-10\run_report.json
```

10. Produktive Seeds noch nicht ersetzen:

```powershell
Write-Host "Pilot pruefen. local-data/mention-radar/seeds.csv bleibt unveraendert."
```

Der Datei-Import akzeptiert CSV-Spalten wie `url`, `title`, `snippet`, `category`, `query_id` und `query`. Fehlt `category`, versucht der Crawler die Kategorie spaeter aus dem Inhalt abzuleiten.

## Einzelne Website pruefen

```powershell
python -m seed_crawler inspect https://example.org/ --category book_blog
```

`inspect` crawlt kontrolliert eine Domain und zeigt Score, Kategorie, Signal und Ablehnungsgrund an. Es schreibt nicht automatisch in `seeds.csv`.

## Vollstaendigen 100-Seed-Lauf starten

Mit Brave API:

```powershell
python -m seed_crawler discover `
  --provider brave `
  --target 100 `
  --output .\local-data\mention-radar\seeds.csv
```

Mit lokalem Import:

```powershell
python -m seed_crawler discover `
  --provider file `
  --search-results .\local-data\mention-radar\search-results.csv `
  --target 100 `
  --output .\local-data\mention-radar\seeds.csv
```

Fuer eine einzelne Kategorie:

```powershell
python -m seed_crawler discover --provider brave --category book_blog --target 30 --output .\local-data\mention-radar\seeds.csv
```

## Lauf fortsetzen

Der Cache liegt standardmaessig unter:

```text
local-data/mention-radar/seed-crawler-cache/
```

Fortsetzen:

```powershell
python -m seed_crawler discover --provider brave --target 100 --resume --output .\local-data\mention-radar\seeds.csv
```

## Vorhandene seeds.csv sichern

Eine vorhandene `seeds.csv` wird nicht still ueberschrieben. Vor dem Schreiben wird automatisch eine zeitgestempelte Backup-Datei daneben angelegt, zum Beispiel:

```text
local-data/mention-radar/seeds.backup-20260622_104200.csv
```

Mit `--overwrite` wird der bewusste Ueberschreibmodus dokumentiert; die Backup-Sicherung bleibt trotzdem konservativ aktiv.

## CSV validieren

```powershell
python -m seed_crawler validate .\local-data\mention-radar\seeds.csv
```

Die Validierung prueft Header, Komma-Trennung, UTF-8, absolute URLs, leere Namen, doppelte Domains, Blocklisten, Login-/Shop-/Checkout-URLs, einzeilige Notes, Zielanzahl und Audit-Plausibilitaet.

## Ausgabedateien

Der Lauf schreibt neben der finalen Datei:

```text
local-data/mention-radar/seeds.csv
local-data/mention-radar/seed_audit.csv
local-data/mention-radar/run_report.json
```

`seeds.csv` besitzt exakt diese Spalten:

```csv
url,name,source,notes
```

`seed_audit.csv` enthaelt interne Spalten fuer Scorebestandteile, Kategorie, Signale, Status und Ablehnungsgruende.

`run_report.json` dokumentiert Start/Ende, Provider, Suchanfragen, Roh-URLs, gepruefte Domains, akzeptierte und abgelehnte Kandidaten, Ablehnungsgruende, finale Kategorien, fehlende Quoten, Fehler/Timeouts und Dateipfade.

## Ergebnis in Mention Radar uebernehmen

Mention Radar liest lokale Seed-Dateien aus `local-data/mention-radar/`. Nach erfolgreicher Validierung:

```powershell
.\tools\mention-radar\run-mention-radar.ps1 -InputCsv ".\local-data\mention-radar\seeds.csv"
```

Der Seed Crawler nimmt keine automatische Kontaktaufnahme vor, versendet keine E-Mails, fuellt keine Formulare aus und sammelt keine privaten Kontaktdaten.

## Neue Laeufe spaeter wiederholen

1. Suchanfragen und Blocklisten bei Bedarf aktualisieren.
2. API-Schluessel als Umgebungsvariable setzen.
3. Mit `--resume` Cache weiterverwenden oder ohne `--resume` frisch pruefen.
4. Neue `seeds.csv` validieren.
5. `seed_audit.csv` und `run_report.json` auf Ablehnungen und fehlende Quoten pruefen.

## Fehlerbehebung

- API-Limit: spaeter erneut starten, `run_report.json` pruefen, gegebenenfalls Query-Menge reduzieren.
- HTTP 403: Website blockiert automatisierte Abrufe; Kandidat wird abgewertet oder abgelehnt.
- HTTP 429: Retry-After wird als Grund dokumentiert; spaeter mit `--resume` fortsetzen.
- Timeout: Domain bleibt im Audit sichtbar, der Lauf bricht nicht ab.
- Zu wenige Seeds: keine schwachen Treffer auffuellen; Suchanfragen erweitern und Report-Quoten pruefen.

## Excel-Hinweis

Die Datei ist kommagetrennt und UTF-8-codiert.

In deutschem Excel:
Daten -> Aus Text/CSV
Datei auswaehlen
Zeichencodierung: UTF-8
Trennzeichen: Komma
