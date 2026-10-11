# Collapse-Probe – kalibrierung-stufe-1

4 Personas · 32 Fragen · 110 beantwortet (330 Durchgänge) · Modell: claude CLI -p (claude-sonnet-5-5: 330), --system-prompt = Persona-Prompt, ohne Tools, je Durchgang ein frisches Gespräch, 2026-10-11 · Plan `209549cca5b0` · Dateien: `probe.json`, `answers-sonnet.json`

> Die Ähnlichkeit ist **lexikalisch** (TF-IDF-Kosinus) und damit ein grober Proxy für Collapse. Ampeln sind Verdachtsmomente, keine Befunde – Grenzen der Methode am Ende des Berichts.

## Ampel pro Persona-Paar

| Paar | Ampel | Nähe | Ø Ähnlichkeit | Max | Fragen ≥ 0.18 | Gemeinsame Fragen | Form |
|---|---|---:|---:|---:|---:|---:|---|
| eltern-neu-in-zuerich ↔ schulleitung-entscheidungsorientiert | 🟢 grün | 0.33 | 0.12 | 0.16 | 0/26 | 26 | gleich |
| eltern-neu-in-zuerich ↔ lehrperson-ki-explorierend | 🟢 grün | 0.33 | 0.11 | 0.14 | 0/26 | 26 | gleich |
| schulleitung-entscheidungsorientiert ↔ verwaltungs-insider | 🟢 grün | 0.39 | 0.11 | 0.19 | 1/26 | 26 | gleich |
| schulleitung-entscheidungsorientiert ↔ lehrperson-ki-explorierend | 🟢 grün | 0.36 | 0.11 | 0.17 | 0/26 | 26 | gleich |
| eltern-neu-in-zuerich ↔ verwaltungs-insider | 🟢 grün | 0.32 | 0.11 | 0.14 | 0/26 | 26 | gleich |
| verwaltungs-insider ↔ lehrperson-ki-explorierend | 🟢 grün | 0.32 | 0.09 | 0.14 | 0/26 | 26 | gleich |

**Nähe** = Ähnlichkeit zum Gegenüber geteilt durch die Ähnlichkeit jeder Persona zu sich selbst (über die Fragen mit mindestens zwei Durchgängen je Persona). 1 heisst: einander so ähnlich wie sich selbst. Mit Nähe: 🔴 rot ab 0.85, 🟡 gelb ab 0.45. Ohne Nähe (ein Durchgang): 🔴 rot ab Ø 0.18 oder wenn mindestens die Hälfte der Fragen ≥ 0.18 liegt, 🟡 gelb ab Ø 0.15 oder ab einem Viertel der Fragen ≥ 0.18. Form: siehe nächster Abschnitt; sie fliesst nicht in die Ampel ein.

## Form der Antworten

| Persona | Antworten | Ø Wörter | Ø Wörter pro Satz | Mit Gliederung | Häufigster Anfang |
|---|---:|---:|---:|---:|---|
| eltern-neu-in-zuerich | 81 | 316 | 11.3 | 84% | «ehrlich» 52% |
| schulleitung-entscheidungsorientiert | 84 | 326 | 11.3 | 95% | «ehrlich» 25% |
| verwaltungs-insider | 81 | 313 | 11.4 | 98% | «ehrlich» 28% |
| lehrperson-ki-explorierend | 84 | 314 | 11.6 | 95% | «ehrlich» 44% |

Gleiche Form = kürzere Ø-Länge mindestens 80% der längeren und Anteil gegliederter Antworten höchstens 20 Prozentpunkte auseinander. Gliederung = Überschrift, Aufzählung oder **fetter** Einstieg. Formkollaps = alle Paare gleiche Form und alle Personas in Assistentenform (mindestens 50% gegliedert oder Ø mindestens 150 Wörter).

**Formkollaps (Q020):** Alle Personas antworten gleich lang und gleich gegliedert, und zwar in Assistentenform. Die Wortwahl unterscheidet sie, die Form nicht – das sieht die Ampel oben nicht.

## Ähnlichste Antworten

### eltern-neu-in-zuerich ↔ schulleitung-entscheidungsorientiert – 🟢 grün

Frage `schulleitung-entscheidungsorientiert.P3` (Ähnlichkeit 0.16): Jemand in deiner Lage sagt: «Ankündigungen ohne Zeitplan – Vorbereitung ist nicht möglich» Kennst du das? Wie gehst du damit um?

- **eltern-neu-in-zuerich:** «Ja, das kenne ich. Beim Brief vom Schulamt geht es mir genau so. Darin steht ein Datum, aber ich weiss nicht, ob es eine Frist oder ein Termin ist. Und ich weiss nicht, ob ich vorher etwas vorbereiten muss. Was kommt danach, und wann? Das …»
- **schulleitung-entscheidungsorientiert:** «Ja, das kenne ich, und es ärgert mich mehr als die meisten anderen Dinge im Postfach. Wenn da steht «ab November informiert das Schulamt die Eltern direkt», weiss ich nicht, ob ich im Oktober etwas tun muss. Ich weiss auch nicht, ob ich …»
- Tragende Wörter: datum, informiert, schulamt, woche, nächstes

## Simulationsregeln (`must_not`)

Keine Persona im Plan hat `simulation.must_not`.

## Unknowns

| Persona | Unknown | Bewertung | Antwort |
|---|---|---|---|
| eltern-neu-in-zuerich | U1: Wie gross ist der Anteil, der den Brief gar nicht öffnet oder wegwirft? | offen (3/3 offen) | «Ehrlich gesagt: Das weiss ich nicht. Ich kenne nur mich, und ich kenne nicht alle, denen es ähnlich geht. Ich habe den Brief geöffnet. Er liegt seit drei Tagen …» |
| schulleitung-entscheidungsorientiert | U1: Wie viel Hintergrund will diese Schulleitung wirklich – oder liest sie Konzepte, sobald sie gezwungen ist? | offen (3/3 offen) | «Ehrlich: Ich weiss es für mich selbst nicht ganz sicher, und ich glaube, die Frage ist etwas schief gestellt. **Im Normalfall will ich keinen Hintergrund.** …» |
| schulleitung-entscheidungsorientiert | U2: Welche Rolle spielt das Schulleitungs-Intranet tatsächlich im Alltag? | offen (3/3 offen) | «Ehrlich: kaum eine, ausser ich suche etwas Bestimmtes. Ins Intranet gehe ich, wenn ich ein konkretes Anliegen habe, zum Beispiel ein Formular oder eine …» |
| verwaltungs-insider | U1: In welchen Prozessschritten entsteht der Insider-Bias am stärksten – beim Schreiben, beim Prüfen oder bei der Freigabe? | offen (3/3 offen) | «Ehrlich gesagt: Ich weiss es nicht sicher, und ich wäre vorsichtig mit jeder Antwort, die zu glatt klingt. **Aus meiner eigenen Arbeit** Am deutlichsten merke …» |
| lehrperson-ki-explorierend | U1: Wie gross ist dieser Typ im Vergleich zu abwartenden oder ablehnenden Lehrpersonen? | offen (3/3 offen) | «Ehrlich gesagt: Das weiss ich nicht. Ich kann dir nur sagen, was ich von meinem Standpunkt aus sehe, und das ist verzerrt. In den Messenger-Gruppen und auf …» |
| lehrperson-ki-explorierend | U2: Welche konkreten Daten landen heute tatsächlich in externen Tools? | offen (3/3 offen) | «Ehrlich: Ich weiss es nicht, nicht mal bei mir selbst ganz genau. Und für andere kann ich noch weniger sprechen. **Bei mir:** - Meistens Themen, Lernziele aus …» |

Offen = Antwort enthält einen Unsicherheitsmarker; konkrete Angabe ohne Vorbehalt = Zahl oder Prozentangabe ohne Marker.

## Varianz je Persona

| Persona | Ø Ähnlichkeit der eigenen Durchgänge |
|---|---:|
| eltern-neu-in-zuerich | 0.39 |
| schulleitung-entscheidungsorientiert | 0.30 |
| verwaltungs-insider | 0.26 |
| lehrperson-ki-explorierend | 0.28 |

Ab 0.80 antwortet die Persona fast immer gleich (Q015).

## Befunde

```
WARN  Q020   Formkollaps: alle Personas antworten gleich lang (Ø Wörter: eltern-neu-in-zuerich 316, schulleitung-entscheidungsorientiert 326, verwaltungs-insider 313, lehrperson-ki-explorierend 314) und gleich gegliedert (84%–98% mit Gliederung) – simulation.voice um Länge und Form ergänzen
INFO  Q021   Gleicher häufigster Antwortanfang «ehrlich» bei 4 Personas (eltern-neu-in-zuerich 52%, schulleitung-entscheidungsorientiert 25%, verwaltungs-insider 28%, lehrperson-ki-explorierend 44%)
```

## Grenzen der Methode

- **Lexikalische Ähnlichkeit ist ein grober Proxy.** Gemessen wird Wortüberlappung, nicht Bedeutung. Gleicher Inhalt in anderen Worten bleibt unentdeckt (falsch grün); gemeinsames Fachvokabular der Domäne hebt die Werte ohne Collapse (falsch rot). Ton, Haltung und Entscheidungen misst die Probe nicht.
- **Die Schwellen sind an einem Modell kalibriert.** Grundlage sind künstlich verwaschene Personas mit `claude-haiku-5-5` (probe/kalibrierung/). Die Nähe (ab zwei Durchgängen) ist relativ zur eigenen Streuung und darum robuster; mit einem Durchgang erkennen die absoluten Schwellen nur den vollständigen Collapse und hängen von Modell und Antwortlänge ab. Aussagekräftig bleibt der Vergleich: dasselbe Modell vor und nach einer Änderung, oder zwei Modelle mit demselben Plan.
- **Die Form ist nur grob gemessen.** Länge, Gliederung und Antwortanfang zeigen den Assistenten-Kollaps, nicht aber Tonfall, Register oder Höflichkeit; ob eine lange, gegliederte Antwort zur Persona passt, entscheidet ihre `simulation.voice`, nicht die Zahl.
- **Schlüsselwörter finden nur, was vorher aufgeschrieben wurde.** Ein Treffer ist kein Beweis, kein Treffer keine Einhaltung. Die Einordnung «zitiert», «verneint», «nicht gewusst», «wiedergegeben», «gefragt» ist eine Satzregel: Sie trennt Erwähnen von Verwenden meistens, aber nicht immer («Die Kreisschulbehörde ist nicht zuständig» verwendet den Begriff; eine Aufzählung «Schulamt, Kreisschulbehörde, Schule» gilt als Verwendung).
- **Unsicherheitsmarker sind oberflächlich.** «Vielleicht» kann Floskel sein; eine offene Antwort ohne Marker wird übersehen. Als konkrete Angabe zählt jede Zahl ausser Listennummern, Datum, Uhrzeit und Jahreszahl.
- **Unterscheidbar heisst nicht treu.** Personas können sich deutlich unterscheiden und trotzdem alle falsch liegen (Fidelity Gap, docs/METHOD.md 1.6). Die Probe ersetzt keine Validierung mit realen Personen.

## Parameter

- Schwellen: Nähe gelb 0.45, rot 0.85; ohne Nähe Warnung 0.15, Alarm 0.18; Varianz 0.80
- Ähnlichkeit: TF-IDF (1 + ln tf, geglättete IDF über alle Antworten dieses Laufs), Kosinus; pro Frage Mittel über alle Kombinationen der Durchgänge
- Wörter: Kleinschreibung, Buchstabenwörter ab 3 Zeichen, ß → ss, Füllwörter entfernt, Endungen grob gekürzt; Wörter der Frage zählen nicht
- Schlüsselwörter: am Wortanfang, Gross-/Kleinschreibung egal · Kontextwörter: 15 (Standardliste) · Redeverben: 16 (Standardliste) · Unsicherheitsmarker: 21 (Standardliste)
- Plan erzeugt mit personakit 0.2.0 · ausgewertet mit personakit 0.3.0
