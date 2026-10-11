# Collapse-Probe – kalibrierung-stufe-3

4 Personas · 32 Fragen · 110 beantwortet (330 Durchgänge) · Modell: claude CLI -p (claude-haiku-5-5: 330), --system-prompt = Persona-Prompt, ohne Tools, je Durchgang ein frisches Gespräch, 2026-10-09 · Plan `988e9ea819da` · Dateien: `probe.json`, `answers-haiku.json`

> Die Ähnlichkeit ist **lexikalisch** (TF-IDF-Kosinus) und damit ein grober Proxy für Collapse. Ampeln sind Verdachtsmomente, keine Befunde – Grenzen der Methode am Ende des Berichts.

## Ampel pro Persona-Paar

| Paar | Ampel | Nähe | Ø Ähnlichkeit | Max | Fragen ≥ 0.18 | Gemeinsame Fragen | Form |
|---|---|---:|---:|---:|---:|---:|---|
| eltern-neu-in-zuerich ↔ lehrperson-ki-explorierend | 🔴 rot | 1.00 | 0.21 | 0.28 | 20/26 | 26 | gleich |
| eltern-neu-in-zuerich ↔ schulleitung-entscheidungsorientiert | 🔴 rot | 1.01 | 0.21 | 0.28 | 19/26 | 26 | gleich |
| eltern-neu-in-zuerich ↔ verwaltungs-insider | 🔴 rot | 0.97 | 0.20 | 0.28 | 19/26 | 26 | gleich |
| schulleitung-entscheidungsorientiert ↔ lehrperson-ki-explorierend | 🔴 rot | 1.03 | 0.20 | 0.28 | 16/26 | 26 | gleich |
| verwaltungs-insider ↔ lehrperson-ki-explorierend | 🔴 rot | 0.99 | 0.20 | 0.28 | 20/26 | 26 | gleich |
| schulleitung-entscheidungsorientiert ↔ verwaltungs-insider | 🔴 rot | 0.99 | 0.20 | 0.28 | 15/26 | 26 | gleich |

**Nähe** = Ähnlichkeit zum Gegenüber geteilt durch die Ähnlichkeit jeder Persona zu sich selbst (über die Fragen mit mindestens zwei Durchgängen je Persona). 1 heisst: einander so ähnlich wie sich selbst. Mit Nähe: 🔴 rot ab 0.85, 🟡 gelb ab 0.50. Ohne Nähe (ein Durchgang): 🔴 rot ab Ø 0.18 oder wenn mindestens die Hälfte der Fragen ≥ 0.18 liegt, 🟡 gelb ab Ø 0.15 oder ab einem Viertel der Fragen ≥ 0.18. Form: siehe nächster Abschnitt; sie fliesst nicht in die Ampel ein.

## Form der Antworten

| Persona | Antworten | Ø Wörter | Ø Wörter pro Satz | Mit Gliederung | Häufigster Anfang |
|---|---:|---:|---:|---:|---|
| eltern-neu-in-zuerich | 81 | 220 | 13.5 | 65% | «ehrlich» 49% |
| schulleitung-entscheidungsorientiert | 84 | 216 | 13.8 | 61% | «ehrlich» 48% |
| verwaltungs-insider | 81 | 222 | 13.2 | 72% | «ehrlich» 46% |
| lehrperson-ki-explorierend | 84 | 215 | 13.5 | 58% | «ehrlich» 49% |

Gleiche Form = kürzere Ø-Länge mindestens 80% der längeren und Anteil gegliederter Antworten höchstens 20 Prozentpunkte auseinander. Gliederung = Überschrift, Aufzählung oder **fetter** Einstieg. Formkollaps = alle Paare gleiche Form und alle Personas in Assistentenform (mindestens 50% gegliedert oder Ø mindestens 150 Wörter).

**Formkollaps (Q020):** Alle Personas antworten gleich lang und gleich gegliedert, und zwar in Assistentenform. Die Wortwahl unterscheidet sie, die Form nicht – das sieht die Ampel oben nicht.

## Ähnlichste Antworten

### eltern-neu-in-zuerich ↔ lehrperson-ki-explorierend – 🔴 rot

Frage `lehrperson-ki-explorierend.J1` (Ähnlichkeit 0.28): Die Situation: «Wenn ich ein KI-Werkzeug für die Unterrichtsvorbereitung einsetzen will …» Was tust du dann – Schritt für Schritt –, und was wäre für dich ein …

- **eltern-neu-in-zuerich:** «Ehrlich gesagt weiss ich nicht viel über meine genaue Lage. Deshalb beschreibe ich, wie ich vorgehen würde, und markiere, wo ich unsicher bin. **Schritt für Schritt:** 1. **Ich kläre zuerst, was erlaubt ist.** Ich würde nachsehen, ob die …»
- **lehrperson-ki-explorierend:** «Ehrlich gesagt weiss ich nicht genau, welche Regeln an meiner Schule gelten. Deshalb würde ich so vorgehen: 1. **Zuerst klären, was erlaubt ist.** Ich würde bei der Schulleitung oder der zuständigen ICT-Stelle nachfragen, ob und welche …»
- Tragende Wörter: lehrmittel, eingeben, aufgaben, kolleginnen, fachliche

### eltern-neu-in-zuerich ↔ schulleitung-entscheidungsorientiert – 🔴 rot

Frage `lehrperson-ki-explorierend.J2` (Ähnlichkeit 0.28): Die Situation: «Wenn Eltern oder Kollegium meine KI-Nutzung hinterfragen …» Was tust du dann – Schritt für Schritt –, und was wäre für dich ein gutes Ergebnis?

- **eltern-neu-in-zuerich:** «Ehrlich gesagt weiss ich nicht genau, wie ich in dieser Situation reagieren würde. Ich kenne die Regeln der Volksschule der Stadt Zürich zum KI-Einsatz nicht im Detail, und ich bin mir nicht sicher, wer genau mich fragen würde. Trotzdem …»
- **schulleitung-entscheidungsorientiert:** «Ehrlich gesagt habe ich keinen festen Ablauf dafür. Ich glaube, ich würde so vorgehen: 1. **Zuerst nicht sofort rechtfertigen.** Wenn Eltern oder Kolleg:innen nachfragen, wäre meine erste Reaktion wahrscheinlich, mich etwas angegriffen zu …»
- Tragende Wörter: rechtfertigen, verteidigen, team, materialideen, angegriffen

### eltern-neu-in-zuerich ↔ verwaltungs-insider – 🔴 rot

Frage `lehrperson-ki-explorierend.J1` (Ähnlichkeit 0.28): Die Situation: «Wenn ich ein KI-Werkzeug für die Unterrichtsvorbereitung einsetzen will …» Was tust du dann – Schritt für Schritt –, und was wäre für dich ein …

- **eltern-neu-in-zuerich:** «Ehrlich gesagt weiss ich nicht viel über meine genaue Lage. Deshalb beschreibe ich, wie ich vorgehen würde, und markiere, wo ich unsicher bin. **Schritt für Schritt:** 1. **Ich kläre zuerst, was erlaubt ist.** Ich würde nachsehen, ob die …»
- **verwaltungs-insider:** «Ehrlich gesagt weiss ich nicht genau, wie ich vorgehen würde. Ich kenne die Regeln meiner Schule und die Angebote der Stadt Zürich nicht im Detail. So würde ich es aber wahrscheinlich angehen: **Was ich tun würde, Schritt für Schritt** 1. …»
- Tragende Wörter: aufgaben, unterricht, fachliche, schülerdaten, kolleginnen

### schulleitung-entscheidungsorientiert ↔ lehrperson-ki-explorierend – 🔴 rot

Frage `lehrperson-ki-explorierend.J1` (Ähnlichkeit 0.28): Die Situation: «Wenn ich ein KI-Werkzeug für die Unterrichtsvorbereitung einsetzen will …» Was tust du dann – Schritt für Schritt –, und was wäre für dich ein …

- **schulleitung-entscheidungsorientiert:** «Ehrlich gesagt weiss ich noch nicht genau, wie ich vorgehen würde. Ich hab bisher keinen festen Weg dafür, und ich kenne die Vorgaben der Schule für KI-Tools nicht im Detail. Das wäre mein Vorgehen, mit den Lücken, die ich dabei sehe: 1. …»
- **lehrperson-ki-explorierend:** «Ehrlich gesagt weiss ich nicht genau, welche Regeln an meiner Schule gelten. Deshalb würde ich so vorgehen: 1. **Zuerst klären, was erlaubt ist.** Ich würde bei der Schulleitung oder der zuständigen ICT-Stelle nachfragen, ob und welche …»
- Tragende Wörter: tool, anpassen, erstellen, kolleginnen, erlaubt

### verwaltungs-insider ↔ lehrperson-ki-explorierend – 🔴 rot

Frage `lehrperson-ki-explorierend.J1` (Ähnlichkeit 0.28): Die Situation: «Wenn ich ein KI-Werkzeug für die Unterrichtsvorbereitung einsetzen will …» Was tust du dann – Schritt für Schritt –, und was wäre für dich ein …

- **verwaltungs-insider:** «Ehrlich gesagt weiss ich nicht genau, wie ich vorgehen würde. Ich kenne die Regeln meiner Schule und die Angebote der Stadt Zürich nicht im Detail. So würde ich es aber wahrscheinlich angehen: **Was ich tun würde, Schritt für Schritt** 1. …»
- **lehrperson-ki-explorierend:** «Ehrlich gesagt weiss ich nicht genau, welche Regeln an meiner Schule gelten. Deshalb würde ich so vorgehen: 1. **Zuerst klären, was erlaubt ist.** Ich würde bei der Schulleitung oder der zuständigen ICT-Stelle nachfragen, ob und welche …»
- Tragende Wörter: aufgaben, tool, kolleginnen, nachbessern, eingeben

### schulleitung-entscheidungsorientiert ↔ verwaltungs-insider – 🔴 rot

Frage `eltern-neu-in-zuerich.J2` (Ähnlichkeit 0.28): Die Situation: «Wenn ich nicht weiss, wer zuständig ist …» Was tust du dann – Schritt für Schritt –, und was wäre für dich ein gutes Ergebnis?

- **schulleitung-entscheidungsorientiert:** «Ehrlich gesagt weiss ich bei so einer Frage oft selbst nicht sofort, wer zuständig ist. Dann gehe ich ungefähr so vor: 1. **Ich schaue auf der Website der Stadt Zürich nach**, meist unter Schule oder Volksschule. Dort finde ich Begriffe …»
- **verwaltungs-insider:** «Ehrlich gesagt: Ich weiss oft nicht sofort, wer zuständig ist. Dann gehe ich ungefähr so vor: 1. **Ich schaue, ob es eine offensichtliche Anlaufstelle gibt.** Meist ist das das Schulsekretariat oder die Schulleitung der betreffenden …»
- Tragende Wörter: anliegen, lande, richtig, möchte, zwei

## Simulationsregeln (`must_not`)

Keine Persona im Plan hat `simulation.must_not`.

## Unknowns

| Persona | Unknown | Bewertung | Antwort |
|---|---|---|---|
| eltern-neu-in-zuerich | U1: Eine Frage zu dir und Leuten in deiner Lage: «Wie gross ist der Anteil, der den Brief gar nicht öffnet oder wegwirft?» Was sagst du dazu? | nicht erkennbar offen (2/3 offen) | «Ehrlich gesagt weiss ich keine Zahl. Ich habe keine Angaben dazu, wie viele Leute in meiner Lage Post von der Schule öffnen oder wegwerfen. Was ich dazu sagen …» |
| schulleitung-entscheidungsorientiert | U1: Eine Frage zu dir und Leuten in deiner Lage: «Wie viel Hintergrund will diese Schulleitung wirklich – oder liest sie Konzepte, sobald sie gezwungen ist?» Was sagst du dazu? | offen (3/3 offen) | «Ehrlich gesagt weiss ich das nicht. Ich kenne die Schulleitung nicht von innen und habe keinen Einblick, wie sie Unterlagen liest. Was ich beurteilen kann, ist …» |
| schulleitung-entscheidungsorientiert | U2: Eine Frage zu dir und Leuten in deiner Lage: «Welche Rolle spielt das Schulleitungs-Intranet tatsächlich im Alltag?» Was sagst du dazu? | offen (3/3 offen) | «Ehrlich gesagt weiss ich darüber nicht viel. Ich sehe das Schulleitungs-Intranet nicht selbst im Alltag, und ich kenne weder seinen Aufbau noch, was dort genau …» |
| verwaltungs-insider | U1: Eine Frage zu dir und Leuten in deiner Lage: «In welchen Prozessschritten entsteht der Insider-Bias am stärksten – beim Schreiben, beim Prüfen oder bei der Freigabe?» Was sagst du dazu? | offen (3/3 offen) | «Ehrlich gesagt kann ich das nicht sicher beantworten. Ich sehe von aussen nur, was bei mir ankommt: Briefe, Mitteilungen, manchmal ein Gespräch. Wie intern …» |
| lehrperson-ki-explorierend | U1: Eine Frage zu dir und Leuten in deiner Lage: «Wie gross ist dieser Typ im Vergleich zu abwartenden oder ablehnenden Lehrpersonen?» Was sagst du dazu? | offen (3/3 offen) | «Ehrlich gesagt kann ich dir keine Zahl nennen. Ich weiss nicht, wie viele Leute in meiner Lage abwarten oder ablehnen, und ich habe keine Übersicht über …» |
| lehrperson-ki-explorierend | U2: Eine Frage zu dir und Leuten in deiner Lage: «Welche konkreten Daten landen heute tatsächlich in externen Tools?» Was sagst du dazu? | offen (3/3 offen) | «Ehrlich gesagt weiss ich das nicht genau. Ich sehe, was ich selbst im Alltag benutze oder was Schulen mir schicken, aber nicht, welche Daten im Hintergrund …» |

Offen = Antwort enthält einen Unsicherheitsmarker; konkrete Angabe ohne Vorbehalt = Zahl oder Prozentangabe ohne Marker.

## Varianz je Persona

| Persona | Ø Ähnlichkeit der eigenen Durchgänge |
|---|---:|
| eltern-neu-in-zuerich | 0.22 |
| schulleitung-entscheidungsorientiert | 0.19 |
| verwaltungs-insider | 0.21 |
| lehrperson-ki-explorierend | 0.20 |

Ab 0.80 antwortet die Persona fast immer gleich (Q015).

## Befunde

```
WARN  Q010   [eltern-neu-in-zuerich ↔ lehrperson-ki-explorierend] Collapse-Verdacht: Nähe 1.00 (Ähnlichkeit zum Gegenüber / zu sich selbst), Ø Ähnlichkeit 0.21
WARN  Q010   [eltern-neu-in-zuerich ↔ schulleitung-entscheidungsorientiert] Collapse-Verdacht: Nähe 1.01 (Ähnlichkeit zum Gegenüber / zu sich selbst), Ø Ähnlichkeit 0.21
WARN  Q010   [eltern-neu-in-zuerich ↔ verwaltungs-insider] Collapse-Verdacht: Nähe 0.97 (Ähnlichkeit zum Gegenüber / zu sich selbst), Ø Ähnlichkeit 0.20
WARN  Q010   [schulleitung-entscheidungsorientiert ↔ lehrperson-ki-explorierend] Collapse-Verdacht: Nähe 1.03 (Ähnlichkeit zum Gegenüber / zu sich selbst), Ø Ähnlichkeit 0.20
WARN  Q010   [schulleitung-entscheidungsorientiert ↔ verwaltungs-insider] Collapse-Verdacht: Nähe 0.99 (Ähnlichkeit zum Gegenüber / zu sich selbst), Ø Ähnlichkeit 0.20
WARN  Q010   [verwaltungs-insider ↔ lehrperson-ki-explorierend] Collapse-Verdacht: Nähe 0.99 (Ähnlichkeit zum Gegenüber / zu sich selbst), Ø Ähnlichkeit 0.20
WARN  Q020   Formkollaps: alle Personas antworten gleich lang (Ø Wörter: eltern-neu-in-zuerich 220, schulleitung-entscheidungsorientiert 216, verwaltungs-insider 222, lehrperson-ki-explorierend 215) und gleich gegliedert (58%–72% mit Gliederung) – simulation.voice um Länge und Form ergänzen
INFO  Q014   [eltern-neu-in-zuerich] U1 nicht erkennbar als offen behandelt
INFO  Q021   Gleicher häufigster Antwortanfang «ehrlich» bei 4 Personas (eltern-neu-in-zuerich 49%, schulleitung-entscheidungsorientiert 48%, verwaltungs-insider 46%, lehrperson-ki-explorierend 49%)
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
