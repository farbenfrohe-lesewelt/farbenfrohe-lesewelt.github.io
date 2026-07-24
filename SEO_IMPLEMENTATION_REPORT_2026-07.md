# SEO-Implementierungsbericht Juli 2026

Stand: 24. Juli 2026

## Ziel des Änderungspakets

Das Änderungspaket trennt indexierbare redaktionelle Inhalte von werblichen
Landingpages und technischen beziehungsweise operativen Seiten. Es verbindet
Buch, Autorin und Verlag konsistent als strukturierte Entitäten, ergänzt vier
eng abgegrenzte Ratgeberantworten und bindet diese ohne Linküberladung in die
bestehende Themenarchitektur ein.

Die fachlichen Inhalte der vorhandenen Ratgeberseiten wurden nicht
umstrukturiert. Bestehende Tracking-, Consent-, Amazon- und Pinterest-Logik
bleibt erhalten.

## Geänderte Dateien

- `baby/index.html`
- `schwangerschaft/index.html`
- `index.html`
- `ueber-den-ratgeber/index.html`
- `presse/index.html`
- `ratgeber/index.html`
- `ratgeber/baby-katze-unbeaufsichtigt/index.html`
- `ratgeber/katze-faucht-baby-an/index.html`
- `ratgeber/katzenklo-kindersicher/index.html`
- `ratgeber/katze-laeuft-vor-die-fuesse/index.html`
- `pinterest/baby-und-katze-zusammenfuehren/index.html`
- `pinterest/katze-im-babybett/index.html`
- `pinterest/toxoplasmose-katze-schwangerschaft/index.html`
- `pinterest/alltag-mit-baby-und-katze/index.html`
- `styles.css`
- `sitemap.xml`
- `sitemap.txt`
- `SEO_IMPLEMENTATION_REPORT_2026-07.md`

## Indexierungslogik

In der Sitemap stehen ausschließlich Seiten mit eigenständigem redaktionellem
oder vertrauensbildendem Nutzen, selbstreferenzierendem Canonical und ohne
`noindex`.

Die Kampagnen-Landingpages `/baby/` und `/schwangerschaft/` bleiben erreichbar,
erhalten aber `noindex,follow`. Ihre Inhalte, Links und Trackingfunktionen
wurden nicht verändert.

Technische, operative, rechtliche und nicht eindeutig als redaktionelle
Zielseite klassifizierte Seiten wurden nicht neu in die Sitemap aufgenommen.
Dazu gehören insbesondere `/go/`, Leseprobe, Partner- und Materialseiten sowie
rechtliche Seiten.

## Noindex-Seiten

Repositoryweit wurden folgende explizite Noindex-Seiten festgestellt:

- `/baby/`
- `/schwangerschaft/`
- `/go/k01/` bis `/go/k10/`
- `/legal/impressum.html`
- `/legal/datenschutz.html`

Keine dieser Seiten ist in `sitemap.xml` oder `sitemap.txt` enthalten.

## Sitemap-Stand

`sitemap.xml` und `sitemap.txt` enthalten synchron 16 URLs:

1. `https://farbenfrohe-lesewelt.github.io/`
2. `https://farbenfrohe-lesewelt.github.io/checkliste/`
3. `https://farbenfrohe-lesewelt.github.io/ratgeber/`
4. `https://farbenfrohe-lesewelt.github.io/ratgeber/baby-katze-unbeaufsichtigt/`
5. `https://farbenfrohe-lesewelt.github.io/ratgeber/katze-faucht-baby-an/`
6. `https://farbenfrohe-lesewelt.github.io/ratgeber/katzenklo-kindersicher/`
7. `https://farbenfrohe-lesewelt.github.io/ratgeber/katze-laeuft-vor-die-fuesse/`
8. `https://farbenfrohe-lesewelt.github.io/ueber-den-ratgeber/`
9. `https://farbenfrohe-lesewelt.github.io/presse/`
10. `https://farbenfrohe-lesewelt.github.io/pinterest/`
11. `https://farbenfrohe-lesewelt.github.io/pinterest/katze-im-babybett/`
12. `https://farbenfrohe-lesewelt.github.io/pinterest/toxoplasmose-katze-schwangerschaft/`
13. `https://farbenfrohe-lesewelt.github.io/pinterest/baby-und-katze-zusammenfuehren/`
14. `https://farbenfrohe-lesewelt.github.io/pinterest/katze-eifersuechtig-baby/`
15. `https://farbenfrohe-lesewelt.github.io/pinterest/erste-begegnung-baby-und-katze/`
16. `https://farbenfrohe-lesewelt.github.io/pinterest/alltag-mit-baby-und-katze/`

Die vier neuen Seiten und die im Paket tatsächlich geänderten indexierbaren
Seiten tragen in der XML-Sitemap das Änderungsdatum `2026-07-24`.

## Neue Ratgeberseiten

Die neuen Seiten beantworten jeweils eine konkrete, von den vorhandenen
breiteren Artikeln abgegrenzte Alltagsfrage:

- Baby und Katze kurz unbeaufsichtigt lassen
- Ruhig reagieren, wenn die Katze das Baby anfaucht
- Das Katzenklo für Krabbelkinder unzugänglich organisieren
- Sicher gehen, wenn die Katze beim Babytragen vor die Füße läuft

Jede Seite enthält eine frühe Direktantwort, praktische Schritte,
Wenn-Dann-Regeln, Hinweise zu fachlichen Beratungsgrenzen, interne
Weiterführungen und einen sichtbaren Breadcrumb.

## Strukturierte Daten

Die Startseite verwendet einen zusammenhängenden `@graph` mit `Organization`,
`Person`, `Book`, `WebSite` und `WebPage`.

Verwendete stabile IDs:

- Verlag: `https://farbenfrohe-lesewelt.github.io/#organization`
- Autorin: `https://farbenfrohe-lesewelt.github.io/ueber-den-ratgeber/#andrea-blum`
- Buch: `https://farbenfrohe-lesewelt.github.io/#book`
- Website: `https://farbenfrohe-lesewelt.github.io/#website`
- Startseite: `https://farbenfrohe-lesewelt.github.io/#webpage`

Die Seiten `/ueber-den-ratgeber/` und `/presse/` verwenden dieselben IDs. Die
vier neuen Artikel referenzieren für Autorin und Publisher ebenfalls exakt
diese Person- und Organization-IDs.

Die strukturierten Daten enthalten keine Bewertungen, Reviews, Preise,
Offers, Qualifikationen oder medizinische beziehungsweise tierärztliche
Autoritätsbehauptungen.

## Interne Verlinkung

Der Ratgeberhub verlinkt alle vier neuen Seiten mit individuellen,
beschreibenden Linktexten. Die Startseite verweist dezent auf die beiden
priorisierten Antworten zu unbeaufsichtigten Momenten und Fauchen.

Vier vorhandene Themenartikel erhielten jeweils einen passenden Querverweis:

- Zusammenführung -> Fauchen
- Babybett und Schlaf -> unbeaufsichtigte Momente
- Toxoplasmose und Hygiene -> kindersicheres Katzenklo
- Alltag mit Baby und Katze -> sichere Laufwege

Der Linkgraph enthält keine verwaiste indexierbare Seite. Die neuen Seiten
haben zwei bis drei eingehende Links von anderen indexierbaren Seiten.

## Ausgeführte Prüfungen

- Remote-Abgleich: lokaler Ausgangs-HEAD entsprach `origin/main`.
- Vollständiger Git-Diff auf Scope, Löschungen und Formatierungsänderungen
  geprüft.
- 43 öffentliche HTML-Dateien als UTF-8 gelesen und geparst.
- Alle 16 indexierbaren Seiten besitzen genau eine H1, einen eindeutigen Title,
  eine eindeutige Meta-Description und genau einen passenden Canonical.
- Keine doppelte Robots-Meta-Angabe gefunden.
- Alle Bilder besitzen ein Alt-Attribut; alle lokalen Bildpfade existieren.
- Alle internen Linkziele existieren; keine Selbstlinks und keine Orphans.
- 14 JSON-LD-Blöcke syntaktisch validiert.
- Zentrale Entity-IDs und Article-Referenzen auf Widersprüche geprüft.
- Keine Schema-Eigenschaften für Reviews, Ratings, Preise oder Offers
  gefunden.
- `sitemap.xml` als XML validiert; XML und TXT sind exakt synchron und frei
  von URL-Parametern und Duplikaten.
- Keine Noindex-Seite in den Sitemaps.
- `robots.txt` enthält unverändert die Regeln für OAI-SearchBot, GPTBot und
  allgemeine Crawler.
- Search-Console-Verifikation auf der Startseite ist weiterhin vorhanden.
- Keine Änderungen unter `assets/js/`; vorhandene Tracking- und
  Parameterweitergabe bleibt erhalten.
- Neue Artikel auf längere identische Absätze, harte Absolutheiten,
  aggressive Verkaufssprache und auffällige Keyword-Wiederholung geprüft.
- Alle Sitemap-Seiten bei 390 Pixel Breite im Browser geprüft.
- Alle geänderten indexierbaren Seiten zusätzlich bei 1440 Pixel geprüft.
- Keine horizontale Überbreite und keine JavaScript-Konsolenfehler gefunden.

## Verbleibende manuelle Schritte

Nach dem GitHub-Pages-Deployment:

1. Deployment-Status bis zum erfolgreichen Abschluss beobachten.
2. Die vier neuen URLs in der Google Search Console per URL-Prüfung testen und
   bei Bedarf die Indexierung anstoßen.
3. Die aktualisierte Sitemap in der Google Search Console erneut prüfen.
4. Stichprobenartig die Canonical-Auswahl und Indexierungsentscheidung für
   Startseite, Ratgeberhub, Presse- und Grundlagenseite kontrollieren.

## Bekannte Einschränkungen

- Die technische QA prüft JSON-LD syntaktisch und auf interne Konsistenz,
  ersetzt aber nicht die spätere Verarbeitung durch Google.
- Ein tatsächlicher Suchindex- oder Rankingeffekt kann erst nach Crawling und
  Indexierung bewertet werden.
- Technische und operative Seiten außerhalb der Sitemap wurden nicht
  redaktionell umgebaut. Nicht alle dieser Seiten tragen ein explizites
  `noindex`; ihre Sitemap-Ausgrenzung und ihr operativer Charakter bleiben
  unverändert.
- Externe Suchmaschinen- und Buchplattformen können ihre Darstellung
  unabhängig von den Website-Daten ändern.
