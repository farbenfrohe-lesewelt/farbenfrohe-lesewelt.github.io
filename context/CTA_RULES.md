# CTA Rules - Baby und Katze sicher zusammenfuehren

## Conversion-Ziele

Prioritaet der Website:

1. Checkliste herunterladen
2. Buch ansehen
3. Material fuer Einrichtungen anfragen

Die Prioritaet kann je nach Seite wechseln, aber nie unklar werden.

## Globale CTA-Hierarchie

### Primaer

Der primaere CTA ist die wichtigste Handlung dieser Seite.

Beispiele:

- "Checkliste herunterladen"
- "Buch ansehen"
- "Material anfragen"
- "Leseprobe oeffnen"

### Sekundaer

Der sekundaere CTA ist der risikoarme oder alternative naechste Schritt.

Beispiele:

- "Erst kurz reinlesen"
- "Mehr zum Ratgeber"
- "Checkliste ansehen"
- "Zur Partneruebersicht"

### Tertiaer

Tertiaere CTAs sind Textlinks oder unauffaellige Buttons.

Beispiele:

- "Themen ansehen"
- "Zurueck"
- "Weitere Fragen lesen"

## CTA-Prioritaet nach Seitentyp

### Startseite `/`

Primaer: Buch ansehen oder Leseprobe, je nach Phase der Seite.  
Empfehlung fuer neue Designs: im Hero "Leseprobe oeffnen" als risikoarmer Secondary und "Buch ansehen" als Primary klar paaren.

Nicht mehr als:

- 1 Primary im Hero
- 1 Secondary im Hero
- 1 Sticky CTA mobil

### `/schwangerschaft/` und `/baby/`

Primaer: Leseprobe passend zur Situation oder Buch ansehen.  
Sekundaer: Buch ansehen oder Leseprobe, je nach Hero-Fokus.

Regel: Segmentseiten muessen spezifischer wirken als die Startseite. CTA-Kontext nennt die Phase.

### `/checkliste/`

Primaer: "Checkliste herunterladen"  
Sekundaer: "Erst kurz ansehen" oder "Mehr zum Ratgeber"

Regeln:

- Download darf nicht hinter Formular, Modal oder langem Text versteckt sein.
- "Ohne Formular" darf als Trust-Hinweis erscheinen.
- Buch-CTA kommt erst nach dem Checklistenwert.

### `/leseprobe/`

Primaer: "Buch ansehen"  
Sekundaer: "Zurueck zur Buchseite"

Regeln:

- Sticky CTA ist erlaubt, aber muss den Reader nicht bedruecken.
- Buch-CTA darf nach einigen Probeseiten wiederholt werden.
- Zurueck-Link muss sichtbar bleiben.

### `/partner/` und Unterseiten

Primaer: "Material anfragen"  
Sekundaer: "Checkliste ansehen"

Regeln:

- Buch ansehen ist tertiaer.
- Keine aggressive Verkaufsformulierung.
- CTA soll nach Einrichtungskontext klingen: "Materialpaket fuer die Praxis anfragen", "Infomaterial fuer Familien anfragen".

### `/material-anfragen/`

Primaer: "E-Mail oeffnen" oder "Materialpaket per E-Mail anfragen"  
Sekundaer: "Checkliste ansehen"

Regeln:

- Mailto-Hinweis klar machen.
- Vorlage sichtbar halten.
- Keine Buch-CTA im Hero.

### `/go/*`

Primaer: "Checkliste ansehen"  
Sekundaer: "Mehr zum Buch"  
Tertiaer: "Material anfragen"

Regeln:

- Offline-Partnerkontext zuerst bestaetigen.
- Kein direkter Amazon-Druck im ersten Satz.

### `/pinterest/*`

Primaer: "Checkliste ansehen"  
Sekundaer: "Mehr zum Buch" oder thematisch naechste Seite

Regeln:

- Checkliste frueh anbieten.
- Buch erst als vollstaendiger Plan positionieren.
- Nicht jeden Artikelblock mit drei Buttons beenden.

### Rechtliche Seiten

Keine Verkaufs-CTA. Nur Navigation und rechtlich relevante Links.

## Button-Design

### Primary

- Farbe: ruhiges Petrol/Sage
- Text: Weiss
- Gewicht: 700
- Radius: 10-12px
- Mindesthoehe mobil: 48px
- Breite mobil: oft 100%, wenn im CTA-Paar

### Secondary

- Farbe: transparent oder helle Surface
- Text: `#1d2430`
- Border: Hairline
- Gewicht: 650-700
- Mindesthoehe mobil: 48px

### Ghost / Text Link

- Nur fuer Navigation oder sehr niedrige Prioritaet.
- Nicht fuer wichtigste Conversion nutzen.

## CTA-Texte

### Gut

- "Checkliste herunterladen"
- "Checkliste ansehen"
- "Buch ansehen"
- "Kostenlose Leseprobe oeffnen"
- "Direkt reinlesen"
- "Materialpaket anfragen"
- "Infomaterial fuer Familien anfragen"
- "Mehr zum Ratgeber"

### Vermeiden

- "Jetzt kaufen!"
- "Sofort sichern!"
- "Unbedingt lesen"
- "Risiko vermeiden"
- "Schuetze dein Baby jetzt"
- "Nur heute"
- "Geheimtipp"
- "Der Trick"

## CTA-Dichte

- Hero: maximal 2 CTAs.
- Pro Abschnitt: maximal 1 CTA-Gruppe.
- CTA-Gruppe: maximal 2 Buttons plus optional 1 Textlink.
- Auf mobilen Seiten nicht mehrere CTA-Gruppen direkt hintereinander.
- Sticky CTA ersetzt mobile Wiederholung, sie ergaenzt sie nicht beliebig.

## Sticky CTA

Erlaubt auf:

- Startseite
- Baby-/Schwangerschaftsseiten
- Checklisten-Funnel
- Leseprobe

Nicht erlaubt auf:

- Impressum
- Datenschutz
- Druck-/PDF-Seiten

Regeln:

- Muss klein, lesbar und nicht panisch wirken.
- Darf Consent-Banner nicht ueberdecken.
- Darf Footer nicht unlesbar machen.
- Buttontext mobil kurz halten: "Buch ansehen", "Download", "Leseprobe".

## CTA-Kontext

Jede CTA braucht einen kleinen Kontext, wenn die Handlung nicht selbsterklaerend ist.

Beispiele:

- "Die Leseprobe oeffnet direkt im Reader."
- "Der Download startet ohne Formular."
- "Die Anfrage oeffnet eine vorbereitete E-Mail."

Keine langen CTA-Erklaerungen. Ein Satz reicht.

## Tracking und Parameter

- Bestehende Links, Pfade, Trackingparameter und `data-*` Attribute nicht ohne ausdruecklichen Auftrag aendern.
- `data-preserve-params` beibehalten, wo vorhanden.
- Eventnamen und Labels nicht umbenennen, wenn nur Designarbeit gefragt ist.
- PDF-Download nicht mit Trackingparametern verschmutzen, sofern die bestehende Logik das vermeidet.

## CTA-Pruefliste

- Gibt es genau einen klaren Primaer-CTA pro Viewport?
- Passt der CTA zur Nutzerintention dieser Seite?
- Ist der Button mobil mindestens 48px hoch?
- Ist der Text konkret und ruhig?
- Gibt es keine manipulative Dringlichkeit?
- Bleiben Checkliste, Buch und Materialanfrage klar unterscheidbar?
- Sind bestehende Trackingattribute unveraendert?
