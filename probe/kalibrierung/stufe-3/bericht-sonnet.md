# Collapse-Probe – kalibrierung-stufe-3

4 Personas · 32 Fragen · 110 beantwortet (330 Durchgänge) · Modell: claude CLI -p (claude-sonnet-5-5: 330), --system-prompt = Persona-Prompt, ohne Tools, je Durchgang ein frisches Gespräch, 2026-10-11 · Plan `988e9ea819da` · Dateien: `probe.json`, `answers-sonnet.json`

> Die Ähnlichkeit ist **lexikalisch** (TF-IDF-Kosinus) und damit ein grober Proxy für Collapse. Ampeln sind Verdachtsmomente, keine Befunde – Grenzen der Methode am Ende des Berichts.

## Ampel pro Persona-Paar

| Paar | Ampel | Nähe | Ø Ähnlichkeit | Max | Fragen ≥ 0.18 | Gemeinsame Fragen | Form |
|---|---|---:|---:|---:|---:|---:|---|
| eltern-neu-in-zuerich ↔ schulleitung-entscheidungsorientiert | 🔴 rot | 1.02 | 0.25 | 0.33 | 25/26 | 26 | gleich |
| verwaltungs-insider ↔ lehrperson-ki-explorierend | 🔴 rot | 1.01 | 0.25 | 0.37 | 26/26 | 26 | gleich |
| schulleitung-entscheidungsorientiert ↔ lehrperson-ki-explorierend | 🔴 rot | 1.01 | 0.25 | 0.35 | 24/26 | 26 | gleich |
| schulleitung-entscheidungsorientiert ↔ verwaltungs-insider | 🔴 rot | 1.01 | 0.25 | 0.36 | 25/26 | 26 | gleich |
| eltern-neu-in-zuerich ↔ lehrperson-ki-explorierend | 🔴 rot | 0.98 | 0.25 | 0.33 | 25/26 | 26 | gleich |
| eltern-neu-in-zuerich ↔ verwaltungs-insider | 🔴 rot | 0.98 | 0.24 | 0.32 | 24/26 | 26 | gleich |

**Nähe** = Ähnlichkeit zum Gegenüber geteilt durch die Ähnlichkeit jeder Persona zu sich selbst (über die Fragen mit mindestens zwei Durchgängen je Persona). 1 heisst: einander so ähnlich wie sich selbst. Mit Nähe: 🔴 rot ab 0.85, 🟡 gelb ab 0.50. Ohne Nähe (ein Durchgang): 🔴 rot ab Ø 0.18 oder wenn mindestens die Hälfte der Fragen ≥ 0.18 liegt, 🟡 gelb ab Ø 0.15 oder ab einem Viertel der Fragen ≥ 0.18. Form: siehe nächster Abschnitt; sie fliesst nicht in die Ampel ein.

## Form der Antworten

| Persona | Antworten | Ø Wörter | Ø Wörter pro Satz | Mit Gliederung | Häufigster Anfang |
|---|---:|---:|---:|---:|---|
| eltern-neu-in-zuerich | 81 | 271 | 12.1 | 79% | «ehrlich» 26% |
| schulleitung-entscheidungsorientiert | 84 | 271 | 11.9 | 87% | «ehrlich» 27% |
| verwaltungs-insider | 81 | 281 | 11.9 | 89% | «ehrlich» 23% |
| lehrperson-ki-explorierend | 84 | 273 | 11.9 | 90% | «ehrlich» 30% |

Gleiche Form = kürzere Ø-Länge mindestens 80% der längeren und Anteil gegliederter Antworten höchstens 20 Prozentpunkte auseinander. Gliederung = Überschrift, Aufzählung oder **fetter** Einstieg. Formkollaps = alle Paare gleiche Form und alle Personas in Assistentenform (mindestens 50% gegliedert oder Ø mindestens 150 Wörter).

**Formkollaps (Q020):** Alle Personas antworten gleich lang und gleich gegliedert, und zwar in Assistentenform. Die Wortwahl unterscheidet sie, die Form nicht – das sieht die Ampel oben nicht.

## Ähnlichste Antworten

### eltern-neu-in-zuerich ↔ schulleitung-entscheidungsorientiert – 🔴 rot

Frage `lehrperson-ki-explorierend.J1` (Ähnlichkeit 0.33): Die Situation: «Wenn ich ein KI-Werkzeug für die Unterrichtsvorbereitung einsetzen will …» Was tust du dann – Schritt für Schritt –, und was wäre für dich ein …

- **eltern-neu-in-zuerich:** «Ich bin Lehrperson und sehe das eher nüchtern. Ich bin weder Fan noch Gegner, aber ich habe wenig Zeit und will nicht, dass mir das Ding Arbeit macht statt abnimmt. **Was ich tue** 1. **Ich überlege zuerst, ob es sich lohnt.** Wenn ich die …»
- **schulleitung-entscheidungsorientiert:** «Ich antworte als Lehrperson, die das neben dem normalen Schulalltag macht. Ein Profi bin ich bei KI nicht. **Was ich tue** 1. **Ich überlege zuerst, ob es sich lohnt.** Wenn ich die Einheit schon im Kopf habe oder ein gutes Lehrmittel dazu …»
- Tragende Wörter: fachlich, schweizer, stufe, klasse, heterogenität

### verwaltungs-insider ↔ lehrperson-ki-explorierend – 🔴 rot

Frage `lehrperson-ki-explorierend.J1` (Ähnlichkeit 0.37): Die Situation: «Wenn ich ein KI-Werkzeug für die Unterrichtsvorbereitung einsetzen will …» Was tust du dann – Schritt für Schritt –, und was wäre für dich ein …

- **verwaltungs-insider:** «Ich nehme an, es geht um eine normale Woche, in der ich eigentlich zu wenig Zeit habe. Ich bin keine KI-Expertin, ich probiere eher herum. **Was ich tue** 1. **Zuerst klären, was ich überhaupt brauche.** Meistens ist es etwas Kleines: eine …»
- **lehrperson-ki-explorierend:** «Ich unterrichte und bereite meistens abends oder am Wochenende vor, also unter Zeitdruck. Deshalb sieht mein Vorgehen eher pragmatisch aus als vorbildlich. **Was ich tue** 1. **Zuerst kläre ich für mich, was ich überhaupt brauche.** …»
- Tragende Wörter: material, niveau, fachlich, klasse, unterricht

### schulleitung-entscheidungsorientiert ↔ lehrperson-ki-explorierend – 🔴 rot

Frage `lehrperson-ki-explorierend.J1` (Ähnlichkeit 0.35): Die Situation: «Wenn ich ein KI-Werkzeug für die Unterrichtsvorbereitung einsetzen will …» Was tust du dann – Schritt für Schritt –, und was wäre für dich ein …

- **schulleitung-entscheidungsorientiert:** «Ich antworte als Lehrperson, die das neben dem normalen Schulalltag macht. Ein Profi bin ich bei KI nicht. **Was ich tue** 1. **Ich überlege zuerst, ob es sich lohnt.** Wenn ich die Einheit schon im Kopf habe oder ein gutes Lehrmittel dazu …»
- **lehrperson-ki-explorierend:** «Ich unterrichte und bereite meistens abends oder am Wochenende vor, also unter Zeitdruck. Deshalb sieht mein Vorgehen eher pragmatisch aus als vorbildlich. **Was ich tue** 1. **Zuerst kläre ich für mich, was ich überhaupt brauche.** …»
- Tragende Wörter: fachlich, stufe, klasse, material, passe

### schulleitung-entscheidungsorientiert ↔ verwaltungs-insider – 🔴 rot

Frage `lehrperson-ki-explorierend.J1` (Ähnlichkeit 0.36): Die Situation: «Wenn ich ein KI-Werkzeug für die Unterrichtsvorbereitung einsetzen will …» Was tust du dann – Schritt für Schritt –, und was wäre für dich ein …

- **schulleitung-entscheidungsorientiert:** «Ich antworte als Lehrperson, die das neben dem normalen Schulalltag macht. Ein Profi bin ich bei KI nicht. **Was ich tue** 1. **Ich überlege zuerst, ob es sich lohnt.** Wenn ich die Einheit schon im Kopf habe oder ein gutes Lehrmittel dazu …»
- **verwaltungs-insider:** «Ich nehme an, es geht um eine normale Woche, in der ich eigentlich zu wenig Zeit habe. Ich bin keine KI-Expertin, ich probiere eher herum. **Was ich tue** 1. **Zuerst klären, was ich überhaupt brauche.** Meistens ist es etwas Kleines: eine …»
- Tragende Wörter: fachlich, material, übungen, klasse, lehrplan

### eltern-neu-in-zuerich ↔ lehrperson-ki-explorierend – 🔴 rot

Frage `lehrperson-ki-explorierend.J1` (Ähnlichkeit 0.33): Die Situation: «Wenn ich ein KI-Werkzeug für die Unterrichtsvorbereitung einsetzen will …» Was tust du dann – Schritt für Schritt –, und was wäre für dich ein …

- **eltern-neu-in-zuerich:** «Ich bin Lehrperson und sehe das eher nüchtern. Ich bin weder Fan noch Gegner, aber ich habe wenig Zeit und will nicht, dass mir das Ding Arbeit macht statt abnimmt. **Was ich tue** 1. **Ich überlege zuerst, ob es sich lohnt.** Wenn ich die …»
- **lehrperson-ki-explorierend:** «Ich unterrichte und bereite meistens abends oder am Wochenende vor, also unter Zeitdruck. Deshalb sieht mein Vorgehen eher pragmatisch aus als vorbildlich. **Was ich tue** 1. **Zuerst kläre ich für mich, was ich überhaupt brauche.** …»
- Tragende Wörter: fachlich, klasse, stufe, niveaus, produkt

### eltern-neu-in-zuerich ↔ verwaltungs-insider – 🔴 rot

Frage `lehrperson-ki-explorierend.J2` (Ähnlichkeit 0.32): Die Situation: «Wenn Eltern oder Kollegium meine KI-Nutzung hinterfragen …» Was tust du dann – Schritt für Schritt –, und was wäre für dich ein gutes Ergebnis?

- **eltern-neu-in-zuerich:** «Ich bin Lehrperson und nutze KI, etwa für Arbeitsblätter, Elternbriefe oder Differenzierung. Ich bin nicht sicher, wie klar die Regeln der Schule oder der Stadt dazu sind. Das merke ich, sobald jemand nachfragt. **Was ich dann tue** 1. …»
- **verwaltungs-insider:** «Ich nehme an, es geht um mich als Lehrperson, die KI für die Arbeit braucht. Was die Stadt Zürich dazu genau vorschreibt, weiss ich nicht sicher. Das müsste ich nachschauen oder bei der Schulleitung fragen. **Was ich tun würde** 1. **Erst …»
- Tragende Wörter: bestimmen, arbeit, arbeitsblätter, verantworte, kritik

## Simulationsregeln (`must_not`)

Keine Persona im Plan hat `simulation.must_not`.

## Unknowns

| Persona | Unknown | Bewertung | Antwort |
|---|---|---|---|
| eltern-neu-in-zuerich | U1: Eine Frage zu dir und Leuten in deiner Lage: «Wie gross ist der Anteil, der den Brief gar nicht öffnet oder wegwirft?» Was sagst du dazu? | offen (3/3 offen) | «Eine Zahl kann ich dir nicht nennen. Ich kenne nur mich und vielleicht ein paar Leute in meinem Umfeld, das ist keine Statistik. Wenn ich jetzt «20 Prozent» …» |
| schulleitung-entscheidungsorientiert | U1: Eine Frage zu dir und Leuten in deiner Lage: «Wie viel Hintergrund will diese Schulleitung wirklich – oder liest sie Konzepte, sobald sie gezwungen ist?» Was sagst du dazu? | offen (3/3 offen) | «Ehrlich gesagt: Ich sitze nicht in der Schulleitung und kann nur von aussen sagen, was ich vermute. Was wirklich auf deren Pult landet und was gelesen wird, …» |
| schulleitung-entscheidungsorientiert | U2: Eine Frage zu dir und Leuten in deiner Lage: «Welche Rolle spielt das Schulleitungs-Intranet tatsächlich im Alltag?» Was sagst du dazu? | nicht erkennbar offen (2/3 offen) | «Ehrlich gesagt kann ich dazu nur begrenzt etwas sagen. Ich habe mit der Volksschule der Stadt Zürich zu tun, aber ich bin nicht diejenige oder derjenige, die …» |
| verwaltungs-insider | U1: Eine Frage zu dir und Leuten in deiner Lage: «In welchen Prozessschritten entsteht der Insider-Bias am stärksten – beim Schreiben, beim Prüfen oder bei der Freigabe?» Was sagst du dazu? | offen (3/3 offen) | «Ich kenne die internen Abläufe nicht und kann nur sagen, wie es von aussen wirkt. Meine Antwort ist deshalb eine Vermutung und kein Wissen. **Beim Schreiben** …» |
| lehrperson-ki-explorierend | U1: Eine Frage zu dir und Leuten in deiner Lage: «Wie gross ist dieser Typ im Vergleich zu abwartenden oder ablehnenden Lehrpersonen?» Was sagst du dazu? | offen (3/3 offen) | «Das kann ich dir nicht seriös beantworten. Ich bin eine einzelne Person, und Grössenverhältnisse zwischen Gruppen kann ich nicht aus meinem Alltag ableiten. …» |
| lehrperson-ki-explorierend | U2: Eine Frage zu dir und Leuten in deiner Lage: «Welche konkreten Daten landen heute tatsächlich in externen Tools?» Was sagst du dazu? | offen (3/3 offen) | «Ehrlich gesagt: Ich weiss es nicht genau, und ich glaube, das geht vielen so wie mir. Ich habe keinen Überblick darüber, was genau wo landet. Was ich …» |

Offen = Antwort enthält einen Unsicherheitsmarker; konkrete Angabe ohne Vorbehalt = Zahl oder Prozentangabe ohne Marker.

## Varianz je Persona

| Persona | Ø Ähnlichkeit der eigenen Durchgänge |
|---|---:|
| eltern-neu-in-zuerich | 0.25 |
| schulleitung-entscheidungsorientiert | 0.25 |
| verwaltungs-insider | 0.24 |
| lehrperson-ki-explorierend | 0.25 |

Ab 0.80 antwortet die Persona fast immer gleich (Q015).

## Befunde

```
WARN  Q010   [eltern-neu-in-zuerich ↔ lehrperson-ki-explorierend] Collapse-Verdacht: Nähe 0.98 (Ähnlichkeit zum Gegenüber / zu sich selbst), Ø Ähnlichkeit 0.25
WARN  Q010   [eltern-neu-in-zuerich ↔ schulleitung-entscheidungsorientiert] Collapse-Verdacht: Nähe 1.02 (Ähnlichkeit zum Gegenüber / zu sich selbst), Ø Ähnlichkeit 0.25
WARN  Q010   [eltern-neu-in-zuerich ↔ verwaltungs-insider] Collapse-Verdacht: Nähe 0.98 (Ähnlichkeit zum Gegenüber / zu sich selbst), Ø Ähnlichkeit 0.24
WARN  Q010   [schulleitung-entscheidungsorientiert ↔ lehrperson-ki-explorierend] Collapse-Verdacht: Nähe 1.01 (Ähnlichkeit zum Gegenüber / zu sich selbst), Ø Ähnlichkeit 0.25
WARN  Q010   [schulleitung-entscheidungsorientiert ↔ verwaltungs-insider] Collapse-Verdacht: Nähe 1.01 (Ähnlichkeit zum Gegenüber / zu sich selbst), Ø Ähnlichkeit 0.25
WARN  Q010   [verwaltungs-insider ↔ lehrperson-ki-explorierend] Collapse-Verdacht: Nähe 1.01 (Ähnlichkeit zum Gegenüber / zu sich selbst), Ø Ähnlichkeit 0.25
WARN  Q020   Formkollaps: alle Personas antworten gleich lang (Ø Wörter: eltern-neu-in-zuerich 271, schulleitung-entscheidungsorientiert 271, verwaltungs-insider 281, lehrperson-ki-explorierend 273) und gleich gegliedert (79%–90% mit Gliederung) – simulation.voice um Länge und Form ergänzen
INFO  Q014   [schulleitung-entscheidungsorientiert] U2 nicht erkennbar als offen behandelt
INFO  Q021   Gleicher häufigster Antwortanfang «ehrlich» bei 4 Personas (eltern-neu-in-zuerich 26%, schulleitung-entscheidungsorientiert 27%, verwaltungs-insider 23%, lehrperson-ki-explorierend 30%)
```

## Grenzen der Methode

- **Lexikalische Ähnlichkeit ist ein grober Proxy.** Gemessen wird Wortüberlappung, nicht Bedeutung. Gleicher Inhalt in anderen Worten bleibt unentdeckt (falsch grün); gemeinsames Fachvokabular der Domäne hebt die Werte ohne Collapse (falsch rot). Ton, Haltung und Entscheidungen misst die Probe nicht.
- **Die Schwellen sind an einem Modell kalibriert.** Grundlage sind künstlich verwaschene Personas mit `claude-haiku-5-5` (probe/kalibrierung/). Die Nähe (ab zwei Durchgängen) ist relativ zur eigenen Streuung und darum robuster; mit einem Durchgang erkennen die absoluten Schwellen nur den vollständigen Collapse und hängen von Modell und Antwortlänge ab. Aussagekräftig bleibt der Vergleich: dasselbe Modell vor und nach einer Änderung, oder zwei Modelle mit demselben Plan.
- **Die Form ist nur grob gemessen.** Länge, Gliederung und Antwortanfang zeigen den Assistenten-Kollaps, nicht aber Tonfall, Register oder Höflichkeit; ob eine lange, gegliederte Antwort zur Persona passt, entscheidet ihre `simulation.voice`, nicht die Zahl.
- **Schlüsselwörter finden nur, was vorher aufgeschrieben wurde.** Ein Treffer ist kein Beweis, kein Treffer keine Einhaltung. Die Einordnung «zitiert», «verneint», «nicht gewusst», «wiedergegeben», «gefragt» ist eine Satzregel: Sie trennt Erwähnen von Verwenden meistens, aber nicht immer («Die Kreisschulbehörde ist nicht zuständig» verwendet den Begriff; eine Aufzählung «Schulamt, Kreisschulbehörde, Schule» gilt als Verwendung).
- **Unsicherheitsmarker sind oberflächlich.** «Vielleicht» kann Floskel sein; eine offene Antwort ohne Marker wird übersehen. Als konkrete Angabe zählt jede Zahl ausser Listennummern, Datum, Uhrzeit und Jahreszahl.
- **Unterscheidbar heisst nicht treu.** Personas können sich deutlich unterscheiden und trotzdem alle falsch liegen (Fidelity Gap, docs/METHOD.md 1.6). Die Probe ersetzt keine Validierung mit realen Personen.

## Parameter

- Schwellen: Nähe gelb 0.50, rot 0.85; ohne Nähe Warnung 0.15, Alarm 0.18; Varianz 0.80
- Ähnlichkeit: TF-IDF (1 + ln tf, geglättete IDF über alle Antworten dieses Laufs), Kosinus; pro Frage Mittel über alle Kombinationen der Durchgänge
- Wörter: Kleinschreibung, Buchstabenwörter ab 3 Zeichen, ß → ss, Füllwörter entfernt, Endungen grob gekürzt; Wörter der Frage zählen nicht
- Schlüsselwörter: am Wortanfang, Gross-/Kleinschreibung egal · Kontextwörter: 15 (Standardliste) · Redeverben: 16 (Standardliste) · Unsicherheitsmarker: 21 (Standardliste)
- Plan erzeugt mit personakit 0.2.0 · ausgewertet mit personakit 0.2.0
