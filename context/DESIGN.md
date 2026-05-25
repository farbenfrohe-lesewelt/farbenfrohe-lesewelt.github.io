# Design Direction - Baby und Katze sicher zusammenfuehren

## Zielwirkung

Die Website soll wie ein ruhiger, hochwertiger Ratgeber wirken: warm, klar, modern, vertrauenswuerdig und auf dem Smartphone sofort lesbar. Sie darf nicht nach Tech-SaaS, generischer KI-Landingpage, Affiliate-Seite, medizinischer Fachseite oder verspieltem Elternblog aussehen.

Die Gestaltung soll Eltern entlasten. Jede Seite muss das Gefuehl geben: Hier wird nichts dramatisiert, aber auch nichts verharmlost. Die visuelle Sprache unterstuetzt den Buchtenor: klare Routinen, sichere Standardregeln, Alltag statt Perfektion.

## Inspirationsprinzipien

- Apple: Ruhe, Weissraum, klare Produktinszenierung, wenige starke Signale.
- Notion: Lesbarkeit, logische Inhaltsbloecke, klare Hierarchie.
- Linear: praezise Kartenstruktur, saubere UI-Hierarchie, dezente Linien.
- Airbnb: menschliche Waerme, Vertrauen, consumer-freundliche Lesefuehrung.

Nicht uebernehmen: Markenfarben, typische Layouts, bekannte Hero-Muster, Logos, produktfremde UI-Details oder erkennbare Markenidentitaeten.

## Farbwelt

### Grundfarben

- Page canvas: `#fbf7f0` oder eine ruhigere Variante `#f7f2ea`
- Lifted surface: `#fffdf8`
- Card surface: `rgba(255,255,255,.86)` oder `#fffefa`
- Soft section: `#f3eee6`
- Text primary: `#1d2430`
- Text secondary: `#566173`
- Text muted: `#7a869a`
- Hairline: `rgba(29,36,48,.12)`

### Akzentfarben

- Primary action: `#2f5f6f` oder `#315f66` (ruhiges Petrol/Sage)
- Primary action hover/active: `#264f58`
- Warm accent: `#d8a24a` oder `#c98f3b`
- Soft warm tint: `rgba(216,162,74,.14)`
- Trust tint: `rgba(47,95,111,.10)`

### Regeln

- Maximal eine dominante Aktionsfarbe pro Viewport.
- Blau nur sparsam, falls bereits im Bestand noetig. Kein dominantes SaaS-Blau.
- Keine grossen violetten, neonfarbenen, knallroten oder gradient-lastigen Flaechen.
- Warme Cremeflaechen duerfen dominieren, aber nicht beige-matschig wirken: immer mit klarem dunklem Text und praezisen Hairlines kombinieren.
- Rot nur fuer echte Warn-/Fehlerzustaende, nicht fuer Marketingdringlichkeit.

## Typografie

### Font Stack

Nutze Systemfonts, keine externen Fonts:

`system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif`

### Groessen

- H1 desktop: `clamp(2.35rem, 4vw, 4rem)`, line-height `1.04`
- H1 mobile: `clamp(2rem, 9vw, 2.85rem)`, line-height `1.06`
- H2: `clamp(1.45rem, 2.3vw, 2.15rem)`, line-height `1.15`
- H3/card title: `1.05rem` bis `1.18rem`, line-height `1.25`
- Lead: `1.08rem` bis `1.22rem`, line-height `1.55`
- Body: `1rem`, line-height `1.58`
- Small/caption: `.88rem` bis `.94rem`, line-height `1.45`

### Regeln

- Keine viewport-basierten Fontgroessen ausser `clamp()` mit festen Min-/Max-Werten.
- Keine negativen Letter-Spacings als allgemeiner Stil. Falls ueberhaupt, nur sehr subtil in grossen Headlines.
- Bodytexte muessen muede Eltern auf mobilen Screens ohne Zoomen lesen koennen.
- Headlines sollen kurz und konkret sein. Keine langen H1 mit mehreren Ideen.
- Starke Woerter sparsam verwenden. Nicht jede zweite Zeile fett setzen.

## Abstand und Rhythmus

### Spacing Scale

- 4px: Mikroabstand
- 8px: enge Gruppierung
- 12px: kleine UI-Gaps
- 16px: Standard-Gap
- 24px: Karteninnenraum / Gruppen
- 32px: Abschnittsinnenraum klein
- 48px: Abschnittsabstand mobil/kompakt
- 72px: Abschnittsabstand desktop
- 96px: nur fuer grosse Landing-Hero- oder Abschlussbereiche

### Regeln

- Mehr Luft zwischen Abschnitten, weniger einzelne Kleinteile innerhalb eines Abschnitts.
- Nicht jede Information braucht eine Card. Manchmal reicht eine klare Zeile, Liste oder Bandflaeche.
- Wiederholte 2x2- und 3x3-Kartenraster reduzieren. Sie wirken schnell generisch.
- Inhalte zuerst gruppieren: Problem, Orientierung, konkreter naechster Schritt.

## Buttons

### Primary Button

- Hintergrund: ruhiges Petrol/Sage
- Text: Weiss
- Radius: 10-12px, nicht pill-foermig als Standard
- Mindesthoehe: 44px desktop, 48px mobil
- Padding: `12px 18px` mobil, `13px 20px` desktop
- Font-weight: 700

### Secondary Button

- Hintergrund: transparent oder `rgba(255,255,255,.72)`
- Text: `#1d2430`
- Border: `1px solid rgba(29,36,48,.16)`
- Radius: wie Primary

### Link Button

- Nur fuer sehr niedrige Prioritaet.
- Kein CTA-Wettbewerb in der Hero-Sektion.

### Regeln

- Pro Hero maximal zwei sichtbare CTAs.
- Primary CTA steht immer zuerst, Secondary CTA danach.
- Buttons muessen konkrete Handlung nennen: "Checkliste herunterladen", "Buch ansehen", "Material anfragen".
- Keine manipulativen Labels wie "Jetzt sichern", "Nur heute", "Unbedingt".
- Keine Icons, wenn sie die Handlung nicht schneller erfassbar machen.

## Cards

### Standard Card

- Hintergrund: `rgba(255,255,255,.86)`
- Border: `1px solid rgba(29,36,48,.10)`
- Radius: 12px bis 16px
- Schatten: sehr sparsam, maximal `0 12px 32px rgba(18,24,35,.06)`
- Padding: 18-24px

### Highlight Card

- Hintergrund: warme oder trustige Tintflaeche
- Border etwas staerker, kein schwerer Shadow
- Nur fuer echte Entscheidungshilfen, Buch-Bruecken oder Checklisten-Vorschau.

### Regeln

- Cards dienen der Struktur, nicht der Dekoration.
- Keine Card-in-Card.
- Karten muessen inhaltlich gleichwertig sein, wenn sie im Grid stehen.
- Bei langen Texten lieber Liste oder Leseband statt Card.
- Auf mobilen Screens Karten stapeln und jeden Block kurz halten.

## Hero-Sektionen

### Ziel

Der Hero muss in 5 Sekunden beantworten:

- Fuer wen ist das?
- Was bekomme ich?
- Was ist der naechste Schritt?

### Struktur

1. Kurze Eyebrow mit Zielgruppe.
2. Klare H1 ohne Nebensaetze.
3. Lead mit maximal 2-3 Saetzen.
4. Primary CTA und ein Secondary CTA.
5. Ein ruhiger Trust-Hinweis oder Produkt-/Checklisten-Vorschau.

### Regeln

- Nicht mehr als ein Micro-Proof-Block im Hero.
- Kein langer Story-Text oberhalb der ersten CTA.
- Buchcover, Checklisten-Vorschau oder Alltagsszene sollen sichtbar, ruhig und hochwertig eingesetzt werden.
- Keine dekorativen Orbs, abstrakten Gradients oder KI-artigen Shapes.
- Hero darf warm sein, aber nicht nach Wellness-Coaching aussehen.

## Trust-Elemente

Geeignete Trust-Elemente:

- "Kostenfreie Checkliste, ohne Formular"
- "Alltagsratgeber, ersetzt keine individuelle Beratung"
- "Von Schwangerschaft bis Kleinkind"
- "Klare Standards statt widerspruechlicher Tipps"
- Checklisten-Vorschau
- Leseprobe
- Partner-/Einrichtungsbezug auf Partnerseiten

Regeln:

- Trust nicht als aggressive Badge-Sammlung darstellen.
- Keine Sternebewertungen ohne echte Quelle.
- Keine Autoritaetsclaims wie "tierarztlich empfohlen" oder "medizinisch geprueft", sofern nicht belegt.
- Trust-Texte muessen ruhig und nachpruefbar sein.

## FAQ-Bloecke

- FAQ soll Einwaende klaeren, nicht SEO-Text stapeln.
- Fragen kurz halten.
- Antworten mit 2-5 Saetzen begrenzen.
- FAQ-Cards duerfen flach sein: Hairline, wenig Shadow.
- Erste FAQ-Frage pro Verkaufsseite soll die groesste Sorge beantworten.
- Rechtliche/medizinische Hinweise sachlich formulieren und nicht verstecken.

## Rechtliche Seiten

Rechtliche Seiten sollen ruhig, lesbar und unaufgeregt sein.

- Max-width: 760-840px
- Body line-height: mindestens 1.6
- H1 klar, keine Marketinghero.
- Keine Sticky-CTA auf rechtlichen Seiten.
- Footer schlicht.
- Links sichtbar, aber nicht in CTA-Farbe dominierend.
- Keine rechtlichen Inhalte veraendern, wenn nur Designarbeit gefragt ist.

## Bildsprache

- Warmes, echtes Alltagsgefuehl.
- Produktbilder muessen erkennbar sein: Buchcover, Checkliste, Leseprobe.
- Keine dunklen, unscharfen, generischen Stock-Atmosphaeren.
- Keine niedlichen Illustrationswelten, die das Thema verharmlosen.
- Wenn Bilder fehlen: lieber ruhige Layoutflaechen als generische Deko.

## No-Go-Liste

- Tech-SaaS-Darkmode als Hauptlook.
- Hero mit abstraktem Gradient und schwebenden Cards.
- Uebertriebene Dringlichkeit.
- Affiliate-artige Button-Wiederholung alle paar Scrollzentimeter.
- Medizinisch-klinische Anmutung.
- Verspielte Baby-Optik mit Pastell-Ueberladung.
- Zu viele Badges, Emojis oder Checkmark-Pills.
- Fremde Marken sichtbar nachbauen.
