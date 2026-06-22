# Mention Radar

Mention Radar ist ein lokales Python-Werkzeug für menschengeprüfte Recherche zu redaktionellen Erwähnungsmöglichkeiten. Es unterstützt dabei, öffentlich zugängliche Seiten, RSS-Feeds oder manuell exportierte URL-Listen zu prüfen, Hinweise auf Einreichungsmöglichkeiten zu dokumentieren und für passende Fälle einen ersten Entwurf vorzubereiten.

Das Werkzeug sendet keine Nachrichten, legt keine Profile an, veröffentlicht keine Kommentare und füllt keine Formulare aus. Es dient nur der Vorbereitung. Die Entscheidung, ob und wie ein Kontakt erfolgt, bleibt immer manuell.

## Grenzen

- keine automatisierte Nutzung von Suchmaschinenergebnisseiten
- keine Umgehung von Logins, Captchas, Paywalls oder Zugriffsbeschränkungen
- keine automatische Ermittlung privater Kontaktdaten
- keine gekauften, getauschten oder geforderten Backlinks
- keine Kopplung eines Rezensionsexemplars an Veröffentlichung, Bewertung oder Verlinkung
- keine erfundenen Reichweiten-, Ranking- oder Autoritätswerte

## Installation

Voraussetzung ist Python 3.11 oder neuer.

```powershell
python -m venv .\tools\mention-radar\.venv
.\tools\mention-radar\.venv\Scripts\python.exe -m pip install -r .\tools\mention-radar\requirements.txt
```

## CSV-Aufbau

Eine manuelle Seed-Datei enthält mindestens die Spalte `url`.

```csv
url,name,source,notes
https://example.com/rezensionen,Beispiel Rezensionsseite,manual,Fiktive Beispielzeile
https://example.org/presse,Beispiel Presseseite,manual,Fiktive Beispielzeile
```

Echte Arbeitsdateien gehören nach `local-data/mention-radar/` und werden nicht versioniert.

## Beispiele

Einzelne URL prüfen:

```powershell
python .\tools\mention-radar\mention_radar.py --url "https://example.com/rezensionen"
```

Manuelle CSV prüfen:

```powershell
python .\tools\mention-radar\mention_radar.py --input-csv ".\local-data\mention-radar\seeds.csv"
```

RSS- oder Atom-Feed einlesen:

```powershell
python .\tools\mention-radar\mention_radar.py --feed "https://example.com/feed.xml"
```

Windows-Workflow:

```powershell
.\tools\mention-radar\run-mention-radar.ps1 -InputCsv ".\local-data\mention-radar\seeds.csv"
```

## Ausgaben

Alle lokalen Ergebnisse werden unter `local-data/mention-radar/` geschrieben:

- `candidates.csv`: alle geprüften Kandidaten mit Klasse, Score, Beleg und Status
- `opportunities.md`: maximal zehn beste Klasse-A- und prüfenswerte Klasse-B-Einträge
- `excluded.csv`: ausgeschlossene Klasse-C- und Klasse-D-Einträge
- `drafts/`: Entwürfe nur für Klasse A

## Klassen

- A: ausdrückliche Einreichungsmöglichkeit, etwa Rezensionsexemplar, Themenvorschlag, Interview oder Medienanfrage
- B: öffentlicher redaktioneller Kontakt ohne eindeutige Einladung
- C: keine erkennbare Einreichungsmöglichkeit
- D: ungeeignet oder riskant, etwa Linkverkauf, Veröffentlichungsgarantie, Linktausch oder thematisch unpassende Seite

Nur Klasse A erhält einen Entwurf. Klasse B bleibt für manuelle Prüfung. Klasse C und D werden ausgeschlossen.

## Scoring

Der Score liegt zwischen 0 und 100:

- thematische Übereinstimmung: bis 30
- Zielgruppenübereinstimmung: bis 20
- ausdrückliche Einreichungsmöglichkeit: bis 20
- redaktionelle Qualität: bis 15
- Aktualität: bis 10
- Anschlussfähigkeit an vorhandenes Material: bis 5

Abzüge gibt es unter anderem für überwiegende Werbeinhalte, geringe redaktionelle Substanz, veraltete Seiten oder generisch wirkende Inhalte. SEO-Metriken werden nicht erfunden.

## Datenschutz und Kontaktwege

Das Werkzeug erfasst nur Kontaktwege, die auf der geprüften Seite öffentlich sichtbar angeboten werden, bevorzugt als URL einer Presse-, Kontakt- oder Einreichungsseite. Echte Arbeitslisten, sichtbare E-Mail-Adressen, Notizen und Entwürfe bleiben lokal im ignorierten Ordner.

## robots.txt und Rate-Limits

Der Crawler verwendet den User-Agent `FarbenfroheLesewelt-MentionResearch/1.0`, prüft `robots.txt`, wartet standardmäßig mindestens drei Sekunden zwischen Abrufen derselben Domain, begrenzt die Seitenzahl pro Domain und lädt keine Binärdateien. Login-, Konto- und Kaufbereiche werden übersprungen.

## Entwürfe prüfen

Entwürfe sind Arbeitsmaterial. Bitte jeden Text individuell kürzen, korrigieren und mit der Fundstelle abgleichen. Mention Radar behauptet nicht, eine komplette Website gelesen zu haben, wenn nur eine Einreichungsseite geprüft wurde.

## 30-Minuten-Wochenworkflow

1. Fünf bis zehn neue Start-URLs oder Feed-Treffer in eine lokale CSV eintragen.
2. Radar ausführen.
3. Nur Klasse A und starke Klasse B öffnen und manuell prüfen.
4. Maximal drei Klasse-A-Kandidaten auswählen.
5. Entwürfe individuell korrigieren.
6. Manuell über den ausdrücklich angebotenen Kontaktweg senden.
7. Status in der lokalen Arbeitsdatei dokumentieren.
8. Höchstens einmal nachfassen, nur wenn die Einreichungsbedingungen dies erlauben.
