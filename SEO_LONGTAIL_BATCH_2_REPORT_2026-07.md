# SEO Longtail Batch 2 – Baby und Katze

Stand: 24. Juli 2026

## Ziel des Projekts

Sechs eigenständige Longtail-Ratgeberseiten beantworten eng begrenzte Suchfragen von Eltern mit Baby oder Kleinkind und Katze. Jede Seite liefert zuerst eine vollständige, fachlich defensive Antwort und führt erst danach zu Ratgeber, Leseprobe und Checkliste.

Ausgangsstand:

- Branch: `main`
- Ausgangscommit: `78d411cab8db3062cc3e99ec177afa4ed43127de`
- Ausgangsstatus: sauber, synchron mit `origin/main`

## Neue URLs und Suchintentionen

| URL | Primäre Suchintention | Klare Abgrenzung |
|---|---|---|
| `/ratgeber/katzenkratzer-baby-was-tun/` | Akut wissen, was nach einem Katzenkratzer beim Baby zu tun ist | Behandelt Wund-Sofortablauf und medizinische Warnzeichen; `/ratgeber/katze-faucht-baby-an/` behandelt Verhalten vor einer Verletzung, `/ratgeber/baby-katze-unbeaufsichtigt/` die Aufsichtsregel |
| `/ratgeber/katze-pinkelt-seit-baby-da-ist/` | Ursachen und erste Schritte bei neuer Unsauberkeit nach der Geburt sortieren | Keine allgemeine Eifersuchtsseite und keine reine Katzenklo-Absicherung; verbindet Hygiene, tierärztliche Abklärung, Beobachtung und Ressourcen-Check |
| `/ratgeber/katzenhaare-baby-gefaehrlich/` | Katzenhaare im Babyalltag und notwendigen Reinigungsaufwand einordnen | Keine Toxoplasmose- oder Schwangerschaftsseite; Fokus auf Haare, sensible Babyflächen, realistische Haushaltshygiene und Beschwerden |
| `/ratgeber/katze-leckt-baby-ab/` | Nach einem Schleckkontakt richtig reinigen und Grenzen setzen | Keine allgemeine Hygiene- oder Kontaktseite; differenziert Hände, Gesicht, Schleimhäute, intakte und offene Haut |
| `/ratgeber/katze-versteckt-sich-seit-baby-da-ist/` | Rückzug der Katze nach der Geburt einordnen und Grundversorgung sichern | Keine allgemeine Eifersuchts- oder erste-Begegnungsseite; Fokus auf geschützten Rückzug, Ressourcen, Appetit, Ausscheidungen und freiwilligen Kontakt |
| `/ratgeber/kleinkind-zieht-katze-am-schwanz/` | Ziehen, Hauen oder Festhalten durch ein Kleinkind sofort stoppen und kindgerecht üben | Keine allgemeine Zusammenführungs- oder Aufsichtsseite; Fokus auf erwachsene Verantwortung, körperliche Führung, Familiensätze und Kleinkindphase |

Ergebnis der Kannibalisierungsprüfung: Alle sechs Seiten besitzen eine eigenständige Hauptintention. Keine geplante Seite musste wegen eines Intent-Konflikts gestoppt werden.

## Title und Meta-Description

### Katzenkratzer

- Title: `Katze hat Baby gekratzt: Was jetzt zu tun ist | Farbenfrohe Lesewelt`
- Meta-Description: `Katze hat das Baby gekratzt? Wunde ruhig reinigen, Blutung stillen, Warnzeichen beobachten und wissen, wann ärztliche Rücksprache sinnvoll ist.`

### Unsauberkeit

- Title: `Katze pinkelt seit das Baby da ist: ruhig vorgehen | Farbenfrohe Lesewelt`
- Meta-Description: `Katze ist seit der Geburt des Babys unsauber? Körperliche Ursachen abklären, Babyflächen sichern, Katzenklos und Veränderungen strukturiert prüfen.`

### Katzenhaare

- Title: `Sind Katzenhaare für Babys gefährlich? Ruhige Einordnung | Farbenfrohe Lesewelt`
- Meta-Description: `Katzenhaare bei Baby oder Neugeborenem ruhig einordnen: sensible Flächen sauber halten, realistisch reinigen und Warnzeichen ärztlich abklären.`

### Ablecken

- Title: `Darf die Katze das Baby ablecken? Klare Regeln | Farbenfrohe Lesewelt`
- Meta-Description: `Katze leckt Baby an Händen oder Gesicht? Ruhig reinigen, sensible Stellen schützen, die Katze umlenken und klare Wenn-Dann-Regeln nutzen.`

### Verstecken

- Title: `Katze versteckt sich seit das Baby da ist: Was tun? | Farbenfrohe Lesewelt`
- Meta-Description: `Katze versteckt sich seit der Geburt? Abstand geben, Rückzug schützen, Futter und Katzenklo erreichbar halten und Warnzeichen ruhig prüfen.`

### Kleinkind zieht Katze

- Title: `Kleinkind zieht Katze am Schwanz: richtig reagieren | Farbenfrohe Lesewelt`
- Meta-Description: `Kleinkind zieht Katze am Schwanz oder Fell? Sofort ruhig trennen, Katze schützen, sanfte Hand üben und Aufsicht sowie Rückzug klar organisieren.`

## Verwendete Claim- und Context-Grundlagen

Vollständig geprüft:

- `context/BOOK_CONTEXT.md`
- `context/CLAIM_GUARDRAILS.md`
- `context/MANUSCRIPT_EXCERPTS.md`
- `context/STYLE_GUIDE.md`
- `context/CTA_RULES.md`
- `context/DESIGN.md`
- `context/MOBILE_RULES.md`
- `context/UX_RULES.md`
- `context/PARTNER_PAGES_BRIEF.md`
- `context/CODEX_QA_NOTES.md`

Übernommene, gedeckte Prinzipien:

- Aufsicht oder Barriere
- Schlafplatz des Babys frei halten
- Baby-Zone, Katzen-Zone und Übergangszone
- Rückzugsorte und Ressourcen erreichbar halten
- ruhig trennen, nicht schimpfen
- bei Verletzungen, deutlichen Verhaltensänderungen oder Gesundheitsfragen fachliche Hilfe einbeziehen
- keine Eifersuchts-, Trotz- oder Aggressionsdiagnose aus der Ferne
- Standard-Hygiene statt Sterilitätsdruck
- Erwachsene bleiben in der Kleinkindphase verantwortlich

Zusätzlich geprüfte öffentliche Fachquellen:

- CDC: Katzen, Kratzer, Hygiene und offene Wunden
- American Academy of Pediatrics / HealthyChildren.org: Katzenkratzer bei Kindern
- Cornell Feline Health Center: House-Soiling, Erkrankungen der unteren Harnwege, Fressverhalten
- AAFP/ISFM: House-Soiling-Leitlinie

Bewusste Begrenzungen:

- keine Ferndiagnose
- keine feste Heil-, Eingewöhnungs- oder Rückzugsfrist
- keine Allergieprognose
- keine erfundenen Grenzwerte oder Häufigkeiten
- keine universelle Katzenklo-Formel
- keine unbelegte Produkt- oder Reinigungsmittelvorgabe
- keine pauschale Entwarnung
- keine vorschnelle Abgabeempfehlung

## Individuelle Sofortabläufe und Buchbrücken

| Seite | Sofortablauf | Buchbrücke |
|---|---|---|
| Katzenkratzer | Abstand, Reinigen, Blutung stillen, Stelle prüfen, Warnzeichen beobachten | Vom einzelnen Wundablauf zu Aufsicht, Rückzug, Zonen und Risikomomenten |
| Unsauberkeit | Babyfläche sperren, passend reinigen, dokumentieren, Tierarztkontakt | Vom akuten Hygiene- und Ressourcen-Check zum Reparaturkasten aus Zonen, Ressourcen und Routinen |
| Katzenhaare | Sichtbares Haar ruhig entfernen, sensible Flächen priorisieren, Beschwerden getrennt beurteilen | Von Haaren zu einem Gesamtplan für Hygiene, Katzenklo, Babyflächen und Schlafplatz |
| Ablecken | Kontakt beenden, Stelle unterscheiden, ruhig reinigen, sensible Stellen fachlich klären | Von der einzelnen Schleck-Situation zu dauerhaften Grenzen, Aufsicht und erlaubter Nähe |
| Verstecken | Abstand erlauben, Rückzug schützen, Grundversorgung prüfen, Verlauf dokumentieren | Von akutem Rückzug zu einem System aus Orten, Wegen, Geräuschen, Ressourcen und freiwilligen Kontakten |
| Kleinkind zieht Katze | Hand lösen, Abstand schaffen, kurz benennen, Kontakt beenden | Von einer konkreten Grenzsituation zur gesamten Phase vom mobilen Baby bis zum Kleinkind |

Auf jeder Seite folgt die Buchbrücke erst nach substanzieller Problemlösung. Verwendet werden die bestehende neutrale Amazon-URL, `rel="noopener nofollow"`, die bestehende Leseprobe und die Checkliste. Die vorhandene Consent- und Trackinglogik wurde nicht verändert.

## Interne Verlinkung

### Ratgeberhub

`/ratgeber/` ordnet nun 10 konkrete Alltagssituationen in vier Gruppen:

- akute Sicherheit
- Verhalten und Stress
- Hygiene und Alltag
- mobiles Baby und Kleinkind

### Neue Inbound-Links

- Katzenkratzer: Hub, Aufsichtsseite, Fauchen-Seite
- Unsauberkeit: Hub, Katzenklo-Seite, Eifersucht-/Stressseite
- Katzenhaare: Hub, Alltagsseite, Toxoplasmose-/Hygieneseite
- Ablecken: Hub, Alltagsseite; zusätzlich natürlicher Querverweis von der neuen Katzenhaar-Seite
- Verstecken: Hub, Fauchen-Seite, Eifersucht-/Stressseite, erste Begegnung
- Kleinkind zieht Katze: Hub, Aufsichtsseite; zusätzlich Querverweis von der neuen Kratzer-Seite

Automatisch gezählte eingehende HTML-Seiten:

- Katzenkratzer: 4
- Unsauberkeit: 4
- Katzenhaare: 4
- Ablecken: 3
- Verstecken: 5
- Kleinkind zieht Katze: 3

Pro bestehender Seite wurden höchstens zwei neue Links ergänzt.

## Design und CSS

`styles.css` enthält neue wiederverwendbare Longtail-Komponenten:

- `.answer-hero-card`
- `.answer-quick-list`
- `.answer-timeline` und `.answer-time`
- `.answer-book-bridge` und `.answer-book-cover`
- `.answer-sentence`
- `.answer-check-grid` und `.answer-check`

Der Ratgeberhub nutzt zusätzlich kompakte Cluster-Abstände für die vier Themenbereiche. Bestehende Farben, Typografie, Buttons, Abstände, Karten, Breakpoints und Assets bleiben Grundlage. Es wurden keine Stockfotos, externen Fonts oder neuen Trackingdienste ergänzt.

## Strukturierte Daten

Jede neue Seite enthält genau einen validen JSON-LD-Graph mit:

- `WebPage`
- `BreadcrumbList`
- `Article`

Verwendete IDs:

- Website: `https://farbenfrohe-lesewelt.github.io/#website`
- Organisation: `https://farbenfrohe-lesewelt.github.io/#organization`
- Autorin: `https://farbenfrohe-lesewelt.github.io/ueber-den-ratgeber/#andrea-blum`

Autorin, Verlag, Logo, URL, Beschreibung, Veröffentlichungs- und Änderungsdatum sind verbunden. Nicht verwendet wurden `FAQPage`, Ratings, Reviews, Offers, Preise oder Qualifikationsclaims.

## Sitemap

Aktualisiert:

- `sitemap.xml`
- `sitemap.txt`

Ergebnis:

- 22 URLs in XML und TXT
- beide Dateien enthalten dieselbe URL-Auswahl und Reihenfolge
- keine Duplikate
- keine URL-Parameter
- alle sechs neuen URLs mit `lastmod` 2026-07-24
- `/baby/`, `/schwangerschaft/`, `/go/`, Partner- und `noindex`-Seiten bleiben ausgeschlossen

## Durchgeführte Prüfungen

### Automatisierte HTML- und Inhaltsprüfung

- sechs neue Dateien vorhanden
- genau eine H1 pro Seite
- eindeutige Titles und Meta-Descriptions
- selbstreferenzierende Canonicals
- keine Robots-Dopplung und kein `noindex`
- alle Bilder mit Alt-Text
- keine leeren Buttons
- alle internen HTML-Ziele vorhanden
- Wortumfang: 924 bis 978 Wörter pro Seite
- alle sechs Hauptfragen im Hero direkt beantwortet
- individuelle Sofortabläufe und Buchbrücken vorhanden

### JSON-LD

- alle sechs Blöcke syntaktisch als JSON geparst
- `WebPage`, `BreadcrumbList` und `Article` je Seite vorhanden
- keine verbotenen Schema-Typen oder Verkaufsfelder

### Sitemap und Links

- XML-/TXT-Synchronität geprüft
- keine Duplikate oder Parameter
- alle sechs URLs enthalten
- interne Ziele repo-weit gegen vorhandene Dateien geprüft
- alle Amazon-Links nutzen das vorhandene Ziel und `rel="noopener nofollow"`

### Darstellung

Alle sechs neuen Seiten wurden gerendert bei:

- 390 × 844 px
- 768 × 1024 px
- 1440 × 1000 px

Ergebnis:

- kein horizontaler Overflow
- keine abgeschnittenen H1
- kontrollierte responsive Hero-Spalten
- mobile Buttons mindestens 48 px hoch und Abschluss-CTAs vollbreit
- keine defekten eager geladenen Bilder
- Buchcover vorhanden, aber erst in der späteren Buchbrücke
- keine Konsolenwarnungen oder Konsolenfehler

Der aktualisierte Ratgeberhub wurde zusätzlich bei 768 px geprüft: vier Themencluster, 16 Karten insgesamt, kein horizontaler Overflow.

### Diff- und Scope-Prüfung

- keine Änderung an Consent-, Tracking- oder zentraler Amazon-Linklogik
- keine gelöschten Inhalte
- keine Änderungen an `/baby/`, `/schwangerschaft/`, `/go/`, Partner- oder Rechtstexten
- keine fremden Änderungen im Working Tree

## Bekannte Einschränkungen

- Keine externe Search-Console- oder Rich-Results-Einreichung wurde automatisiert.
- Die Seiten geben bewusst keine individuelle medizinische, kinderärztliche, tierärztliche oder verhaltensfachliche Beurteilung.
- Suchvolumen, Rankings und Conversion-Wirkung werden nicht behauptet.
- Die GitHub-Pages-Veröffentlichung hängt vom erfolgreichen Push und der anschließenden Verarbeitung durch GitHub Pages ab.

## Manuell in der Google Search Console einzureichen

1. https://farbenfrohe-lesewelt.github.io/ratgeber/katzenkratzer-baby-was-tun/
2. https://farbenfrohe-lesewelt.github.io/ratgeber/katze-pinkelt-seit-baby-da-ist/
3. https://farbenfrohe-lesewelt.github.io/ratgeber/katzenhaare-baby-gefaehrlich/
4. https://farbenfrohe-lesewelt.github.io/ratgeber/katze-leckt-baby-ab/
5. https://farbenfrohe-lesewelt.github.io/ratgeber/katze-versteckt-sich-seit-baby-da-ist/
6. https://farbenfrohe-lesewelt.github.io/ratgeber/kleinkind-zieht-katze-am-schwanz/

Zusätzlich nach dem Deployment erneut prüfen:

- https://farbenfrohe-lesewelt.github.io/ratgeber/
- https://farbenfrohe-lesewelt.github.io/sitemap.xml
