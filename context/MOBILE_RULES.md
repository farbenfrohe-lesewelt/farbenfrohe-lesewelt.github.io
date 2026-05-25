# Mobile Rules - Baby und Katze sicher zusammenfuehren

## Mobile First Ziel

Die meisten Nutzerinnen lesen die Seite auf dem Smartphone, oft muede, mit wenig Zeit und hoher Unsicherheit. Mobile UX ist deshalb nicht die komprimierte Desktop-Version, sondern die wichtigste Fassung.

Ziel: schnell verstehen, ruhig bleiben, sicher tippen koennen.

## Breakpoints

Empfohlene Breakpoints:

- `360px`: sehr kleine Smartphones, harte Text-/Button-Pruefung
- `390px`: Standard-Testbreite fuer moderne Smartphones
- `480px`: grosse Smartphones
- `640px`: mobile Layoutgrenze fuer Header/CTA/Grids
- `740px`: Wechsel von Mobile zu Tablet
- `920px`: Hero-/Zweispaltenwechsel
- `1120px`: Desktop-Komfortbreite

Regel: Kritische Tests immer bei 360px, 390px und 740px machen.

## Grundlayout

- Body darf keinen horizontalen Overflow haben.
- Container mobil: `width: min(100% - 24px, var(--max))`
- Sehr kleine Screens: horizontaler Rand mindestens 14px, besser 16px.
- Grids werden unter 740px einspaltig.
- Zweispaltige Heroes werden unter 920px einspaltig.
- Keine UI darf auf `vw`-Fontskalierung angewiesen sein.

## Mobile Typografie

- H1: 32-44px, je nach Laenge.
- H2: 24-32px.
- H3: 18-21px.
- Body: mindestens 16px.
- Small text: mindestens 14px, rechtliche Hinweise mindestens 13px.
- Line-height Body: 1.55-1.65.
- Buttontext: 15-16px.

Regeln:

- Keine langen Headline-Zeilen erzwingen.
- Lange deutsche Woerter mit `overflow-wrap: break-word` absichern.
- Keine negative Letter-Spacing auf kleinen Screens.
- Keine Texte in Buttons abschneiden, ausser bewusst gekuerzte mobile Labels.

## Header Mobile

Ziel: Orientierung ohne Platzverschwendung.

Regeln:

- Header darf maximal eine Zeile plus kleine Hoehenreserve einnehmen.
- Logo/Brand darf schrumpfen, aber nicht unleserlich wirken.
- Maximal zwei Header-Aktionen.
- Bei engen Screens nur wichtigste Aktion anzeigen oder Buttonlabel kuerzen.
- Header darf nie horizontal scrollen.
- Sticky Header muss genug z-index haben, aber Cookie-Banner und Modals nicht kaputt ueberlagern.

Empfehlung:

- Elternseiten: Brand + "Leseprobe"/"Buch" oder "Checkliste".
- Partnerseiten: Brand + "Checkliste" + "Material".
- Legal: Brand + reduzierte Navigation.

## Mobile Hero

Above the fold muss schnell wirken:

- Eyebrow kurz.
- H1 sichtbar.
- Lead maximal 2-3 Saetze.
- Primaerer CTA frueh.
- Vorschau/Buchcover erst danach, wenn Platz knapp ist.

Regeln:

- Keine 6+ Proof-Pills im Hero.
- Keine langen Micro-Proof-Karten vor CTA.
- Hero-Cards duerfen unter den Text wandern.
- Cover/Preview max-width mobil begrenzen, damit nicht der ganze erste Screen Bild wird.

## Mobile CTAs

- Touch target mindestens 44px, bevorzugt 48px.
- CTA-Paare unter 640px untereinander stapeln.
- Primary und Secondary gleiche Breite, wenn sie zusammenstehen.
- Sticky CTA darf maximal eine knappe Textzeile plus Button zeigen.
- Sticky CTA muss Safe-Area beruecksichtigen: `env(safe-area-inset-bottom)`.
- Body/Footer brauchen Padding, damit Sticky CTA nichts verdeckt.

Mobile Buttonlabels:

- "Checkliste herunterladen" darf zu "Download" werden, wenn Platz knapp ist.
- "Buch auf Amazon ansehen" darf zu "Buch ansehen" werden.
- "Kostenlose Leseprobe oeffnen" darf zu "Leseprobe" werden.

Keine reinen Icon-CTAs fuer Hauptaktionen.

## Cards Mobile

- Eine Card pro Zeile.
- Padding 16-20px.
- Radius 12-16px.
- Schatten reduzieren.
- Lange Karten vermeiden.
- Card-Titel und CTA duerfen nicht auseinanderfallen.
- Keine Card-in-Card.

Wenn ein Abschnitt mobil wie eine endlose Card-Liste wirkt, muss er gekuerzt oder in ein ruhigeres Leseband umgebaut werden.

## FAQ Mobile

- Eine Spalte.
- Summary mindestens 48px tappbar.
- Frage kurz.
- Antwort mit genug Zeilenhoehe.
- Keine FAQ direkt unter Sticky CTA ohne Footer-Padding.

## Trust Mobile

Trust-Elemente muessen scannbar sein.

Geeignet:

- 2-3 kurze Zeilen
- eine kompakte Vorschau
- ein ruhiger Hinweis
- einzelne Mini-Liste

Ungeeignet:

- viele Badges nebeneinander
- kleine Icons mit langen Texten
- horizontale Pill-Reihen, die umbrechen und chaotisch wirken

## Leseprobe Mobile

- Reader-Bilder muessen volle Breite nutzen, aber nicht horizontal ueberlaufen.
- Sticky Actions duerfen den unteren Bildbereich nicht dauerhaft verdecken.
- Back-Link und Buch-CTA klar getrennt.
- Bilder lazy-loaden, erste 1-2 Seiten eager.
- Keine Textueberlagerung auf den Seitenbildern.

## Checkliste Mobile

- Download-CTA im Hero sichtbar.
- Preview-Bild nach CTA oder daneben nur auf breiteren Screens.
- Regelvorschau einspaltig unter 620px.
- Download ohne Formular klar sagen.
- PDF-Link darf keine Parameteranhaengsel durch Parameterweitergabe bekommen, wenn bestehende Logik das verhindert.

## Partnerseiten Mobile

- Sie-Ansprache beibehalten.
- Materialanfrage und Checkliste frueh anbieten.
- Partner-Panel unter Hero-Text stapeln.
- Keine drei gleichwertigen Buttons im Hero.
- Materialvorlage in einspaltige Zeilen umwandeln.

## Rechtliche Seiten Mobile

- Keine Sticky CTA.
- Maximal lesbare Textbreite, aber volle mobile Breite nutzen.
- Kleine Schrift vermeiden.
- Abschnitte mit Ueberschriften klar trennen.
- Links ausreichend Abstand geben.

## Consent Banner Mobile

- Darf Haupt-CTA nicht dauerhaft blockieren.
- Max-width und bottom spacing beachten, wenn Sticky CTA vorhanden ist.
- Buttons im Banner muessen 44px hoch sein.
- Text knapp halten.
- Datenschutz-Link lesbar.

## Performance und Stabilitaet

- Keine Layout-Shifts durch spaet ladende Bilder: `width`, `height` oder `aspect-ratio` setzen.
- Keine externen Fonts.
- Hero-Bild nicht riesig laden, wenn mobile kleinere Version reicht.
- CSS-Gradients sparsam; keine schweren Dekoebenen.
- Animationen optional und sehr subtil; keine Scroll-Magie.

## Mobile QA

Vor Freigabe bei 360px, 390px, 740px pruefen:

- Kein horizontaler Overflow.
- Header nicht abgeschnitten.
- H1 passt ohne haessliche Einzelbuchstaben-Umbrueche.
- Primary CTA sichtbar und tappbar.
- Sticky CTA verdeckt keinen wichtigen Inhalt.
- Cookie-Banner und Sticky CTA kollidieren nicht.
- Cards stapeln sauber.
- Footer bleibt erreichbar.
- Rechtliche Seiten haben keine Verkaufs-Sticky.
- Alle langen Links/Woerter brechen sauber.
