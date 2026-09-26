# SEO Stage 3a – Treatment- und Messprotokoll

Stand: 26. September 2026. **Lokal bearbeitet; noch nicht gepusht oder veröffentlicht.** Dieses Protokoll legt die Auswertung vor dem Deployment fest. Es enthält keine gemessenen Stage-3a-Ergebnisse.

## Ausgangslage und Eingriff

- Repository: `farbenfrohe-lesewelt/farbenfrohe-lesewelt.github.io`, Branch `main`.
- Ausgangscommit: `b5949603b11d7d735360a1c2f985e648ca3279f6` (zugleich der zuletzt extern bestätigte Remote-Stand laut Auftrag). Der Working Tree war vor der Bearbeitung sauber.
- Aktuelle Remote-Prüfung am 26.09.: `git fetch origin main` scheiterte mit `SEC_E_NO_CREDENTIALS`; der lesende GitHub-API-Aufruf scheiterte an der lokalen SSL-Verbindung. Ein neuerer Remote-Stand konnte daher nicht unabhängig bestätigt werden. Keine Credential-Einstellungen geändert.
- Treatment A: `https://farbenfrohe-lesewelt.github.io/ratgeber/katze-faucht-baby-an/`. Title, H1, Meta-/OG- und JSON-LD-Text benennen nun die Frage nach der Bedeutung des Fauchens und dem unmittelbaren Vorgehen. Der Lead trennt ein mögliches Abstandssignal von einer unbelegten Angriffsprognose oder Entwarnung. Die erste Zwischenüberschrift benennt die Einordnung direkter.
- Treatment B: `https://farbenfrohe-lesewelt.github.io/ratgeber/katze-pinkelt-seit-baby-da-ist/`. Title, H1, Meta-/OG- und JSON-LD-Text stellen die Ursachenfrage in den Vordergrund. Der Lead verbindet mögliche Ursachen mit dem vorhandenen Ablauf: Babyflächen sichern, tierärztlich abklären, Veränderungen prüfen. Die erste Zwischenüberschrift benennt die Ursachenfrage. Keine Neuausrichtung auf das Babybett.
- Beide Seiten bleiben in Inhalt, URL, Canonical, `datePublished`, CTA-Zielen und späteren Handlungsabschnitten ansonsten weitgehend unverändert. `dateModified` und ihre beiden Sitemap-`lastmod`-Werte tragen das tatsächliche Bearbeitungsdatum `2026-09-26`.

**Arbeitshypothese:** Schon nützliche Inhalte könnten für passende Suchanfragen sichtbarer werden, wenn Title, H1 und Einstieg die konkrete Leserfrage klarer ausdrücken. Vorgeschlagene Formulierungen wie „Katze faucht Baby an – was bedeutet das?“ und „Katze pinkelt seit der Geburt außerhalb des Katzenklos – warum?“ sind **Suchintent-Hypothesen**, keine gemessenen Suchanfragen oder Suchvolumina. Auch ein positiver Verlauf würde die Ursache nicht isolieren.

## Quellen und redaktionelle Grenze

Für die fachliche Kontrolle der neuen Formulierungen wurden die Inhalte dieser Quellen gelesen, nicht nur deren Linktexte: [Cornell zu Aggressionsverhalten](https://www.vet.cornell.edu/departments-centers-and-institutes/cornell-feline-health-center/health-information/feline-health-topics/feline-behavior-problems-aggression), [Cornell zu Unsauberkeit](https://www.vet.cornell.edu/departments-centers-and-institutes/cornell-feline-health-center/health-information/feline-health-topics/feline-behavior-problems-house-soiling), [Cornell zu Erkrankungen der unteren Harnwege](https://www.vet.cornell.edu/departments-centers-and-institutes/cornell-feline-health-center/health-information/feline-health-topics/feline-lower-urinary-tract-disease) und [FelineVMA/AAFP-ISFM-Leitlinienseite zu Unsauberkeit](https://catvets.com/resource/aafp-isfm-house-soiling-guidelines/). Die Seiten begründen mögliche, individuell abzuklärende Faktoren und die Vorsicht bei Warnzeichen. Sie belegen weder eine Ursache bei einer konkreten Katze noch einen SEO-Effekt.

## Vergleich und mögliche Störfaktoren

| Rolle | URL |
|---|---|
| Primäre unveränderte Vergleichsseite | `https://farbenfrohe-lesewelt.github.io/ratgeber/katzenklo-kindersicher/` |
| Ergänzende unveränderte Vergleichsseite | `https://farbenfrohe-lesewelt.github.io/ratgeber/katze-laeuft-vor-die-fuesse/` |
| Ergänzende unveränderte Vergleichsseite | `https://farbenfrohe-lesewelt.github.io/ratgeber/baby-katze-unbeaufsichtigt/` |
| Ergänzende unveränderte Vergleichsseite | `https://farbenfrohe-lesewelt.github.io/ratgeber/katzenkratzer-baby-was-tun/` |

Diese Seiten sind weder randomisiert noch nach Nachfrage perfekt vergleichbar. Für jede URL wird die Veränderung **gegen ihre eigene Baseline** betrachtet; absolute Impressionen verschiedener Themen sind kein fairer direkter Vergleich. Die eingefrorenen erfolgreichen und neutralen/negativen Seiten bleiben historische Evidenz, nicht neue Treatments.

Alternative Erklärungen für Veränderungen: allgemeine Domainbewegung (die Primärkontrolle stieg bereits in Stage 2), Nachfrage- und Saisonschwankungen, Suchergebnisänderungen, Crawling-/Indexierungsverzug, veränderter Query-Mix und gleichzeitige externe Signale. Der Kinderbuch-/Inklusionsausbau vom 18.09. fügte Seiten und globale Navigation hinzu; **Commit und tatsächliches Deployment sind getrennt zu prüfen**. Die beiden Treatments laufen außerdem zeitgleich und sind keine unabhängige Kausalisolierung.

## Deployment und feste Zeitfenster

| Feld | Nach Deployment eintragen |
|---|---|
| Live-Zeitpunkt mit Zeitzone (z. B. ISO 8601, Europe/Berlin) | offen |
| Deployment-Tag `D` (Europe/Berlin) | offen |
| Live-Nachweis: ausgerollter Commit, beide URLs und sichtbarer Title/H1 | offen |
| PRE: exakt `D-28` bis `D-1`, einschließlich | nach D berechnen |
| POST: exakt `D+1` bis `D+28`, einschließlich | nach D berechnen |
| Deskriptiver Zwischenblick: `D+1` bis `D+14` | nach D berechnen |

`D` selbst gehört zu keinem Fenster. Der Zwischenblick erfolgt erst nach 14 **vollständigen** Post-Tagen; die Hauptauswertung erst nach 28 vollständigen Post-Tagen und verfügbarer Search-Console-Verarbeitung. Kein Erfolgsurteil anhand eines einzelnen Peaks. Für jede URL und beide Zeitfenster in Google Search Console denselben Seitentyp, dieselben Filter und **exakte Datumsgrenzen** verwenden. „Letzte 28 Tage“ ist keine automatisch gültige Vorperiode.

## Erfassung und Auswertung

Für **jede** der zwei Treatment- und vier Vergleichs-URLs separat PRE und POST festhalten:

1. Gesamte Impressionen, Impressionen pro vollständigem Kalendertag, Tage mit mindestens einer Impression und Impressionen in vier aufeinanderfolgenden Siebentageblöcken.
2. Gesamtklicks und CTR als `Gesamtklicks / Gesamtimpressionen`; bei null Impressionen CTR als „nicht definiert“ ausweisen.
3. Die von GSC für das exakt gefilterte Fenster ausgewiesene durchschnittliche Position. Positionsänderungen vorhandener identischer Suchanfragen, soweit ausweisbar, zusätzlich getrennt ansehen.
4. Ausweisbare Suchanfragen und deren thematische Passung zur konkreten Leserfrage, mit PRE-/POST-Impressionen. Nicht ausgewiesene Queries als **„nicht ausweisbar“**, nicht als null Nachfrage oder fehlende Relevanz eintragen.
5. Absolute Änderung und Verhältnis der Impressionen/Tag je URL. Bei null oder sehr kleiner Baseline die absoluten Zahlen voranstellen; keine unendliche oder überdehnte Prozentsteigerung berichten. Entwicklung der Vergleichsseiten jeweils relativ zur eigenen PRE-Phase beschreiben.

Eine schlechtere aggregierte Position kann durch neu hinzugekommene Queries entstehen und beweist keinen Rankingverlust bisheriger Queries. **Sichtbarkeitsveränderung** und eine **belegte Erweiterung relevanter ausweisbarer Queries** sind getrennte Befunde. Zwei explorative Treatments validieren keine allgemeine Auswahlregel und isolieren keine Ursache. GSC-Klicks belegen keine Buchkäufe.

## Nach dem Deployment auszufüllen

| URL-Kürzel | PRE-Impr. / Tage / Klicks / CTR / Position | POST-Impr. / Tage / Klicks / CTR / Position | Ausweisbare passende Queries und Datenlücken | Befund |
|---|---|---|---|---|
| Faucht | offen | offen | offen | offen |
| Pinkelt | offen | offen | offen | offen |
| Katzenklo (primär) | offen | offen | offen | offen |
| Laufweg | offen | offen | offen | offen |
| Unbeaufsichtigt | offen | offen | offen | offen |
| Kratzer | offen | offen | offen | offen |
