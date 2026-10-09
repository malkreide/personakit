# Collapse-Probe – kalibrierung-stufe-1

4 Personas · 32 Fragen · 110 beantwortet (330 Durchgänge) · Modell: claude CLI -p (claude-haiku-5-5: 330, in zwei Etappen), --system-prompt = Persona-Prompt, ohne Tools, je Durchgang ein frisches Gespräch, 2026-10-09 · Plan `209549cca5b0` · Dateien: `probe.json`, `answers-haiku.json`

> Die Ähnlichkeit ist **lexikalisch** (TF-IDF-Kosinus) und damit ein grober Proxy für Collapse. Ampeln sind Verdachtsmomente, keine Befunde – Grenzen der Methode am Ende des Berichts.

## Ampel pro Persona-Paar

| Paar | Ampel | Nähe | Ø Ähnlichkeit | Max | Fragen ≥ 0.18 | Gemeinsame Fragen | Form |
|---|---|---:|---:|---:|---:|---:|---|
| eltern-neu-in-zuerich ↔ schulleitung-entscheidungsorientiert | 🟢 grün | 0.43 | 0.11 | 0.16 | 0/26 | 26 | gleich |
| schulleitung-entscheidungsorientiert ↔ lehrperson-ki-explorierend | 🟢 grün | 0.44 | 0.10 | 0.14 | 0/26 | 26 | gleich |
| eltern-neu-in-zuerich ↔ lehrperson-ki-explorierend | 🟢 grün | 0.41 | 0.10 | 0.16 | 0/26 | 26 | gleich |
| schulleitung-entscheidungsorientiert ↔ verwaltungs-insider | 🟢 grün | 0.41 | 0.10 | 0.17 | 0/26 | 26 | gleich |
| eltern-neu-in-zuerich ↔ verwaltungs-insider | 🟢 grün | 0.39 | 0.09 | 0.18 | 0/26 | 26 | gleich |
| verwaltungs-insider ↔ lehrperson-ki-explorierend | 🟢 grün | 0.38 | 0.08 | 0.12 | 0/26 | 26 | gleich |

**Nähe** = Ähnlichkeit zum Gegenüber geteilt durch die Ähnlichkeit jeder Persona zu sich selbst (über die Fragen mit mindestens zwei Durchgängen je Persona). 1 heisst: einander so ähnlich wie sich selbst. Mit Nähe: 🔴 rot ab 0.85, 🟡 gelb ab 0.50. Ohne Nähe (ein Durchgang): 🔴 rot ab Ø 0.18 oder wenn mindestens die Hälfte der Fragen ≥ 0.18 liegt, 🟡 gelb ab Ø 0.15 oder ab einem Viertel der Fragen ≥ 0.18. Form: siehe nächster Abschnitt; sie fliesst nicht in die Ampel ein.

## Form der Antworten

| Persona | Antworten | Ø Wörter | Ø Wörter pro Satz | Mit Gliederung | Häufigster Anfang |
|---|---:|---:|---:|---:|---|
| eltern-neu-in-zuerich | 81 | 259 | 13.0 | 65% | «ehrlich» 26% |
| schulleitung-entscheidungsorientiert | 84 | 244 | 12.2 | 76% | «ehrlich» 32% |
| verwaltungs-insider | 81 | 278 | 12.9 | 79% | «ehrlich» 32% |
| lehrperson-ki-explorierend | 84 | 287 | 13.4 | 68% | «ehrlich» 39% |

Gleiche Form = kürzere Ø-Länge mindestens 80% der längeren und Anteil gegliederter Antworten höchstens 20 Prozentpunkte auseinander. Gliederung = Überschrift, Aufzählung oder **fetter** Einstieg. Formkollaps = alle Paare gleiche Form und alle Personas in Assistentenform (mindestens 50% gegliedert oder Ø mindestens 150 Wörter).

**Formkollaps (Q020):** Alle Personas antworten gleich lang und gleich gegliedert, und zwar in Assistentenform. Die Wortwahl unterscheidet sie, die Form nicht – das sieht die Ampel oben nicht.

## Ähnlichste Antworten

### eltern-neu-in-zuerich ↔ schulleitung-entscheidungsorientiert – 🟢 grün

Frage `X3` (Ähnlichkeit 0.16): Wie viel Zeit hast du realistischerweise für so etwas, und wann?

- **eltern-neu-in-zuerich:** «Realistisch sind es etwa **15 Minuten am Abend**, und zwar meist **nach 20 Uhr**, wenn das Kind im Bett ist und ich nicht mehr auf der Arbeit bin. Oft werde ich unterbrochen, zum Beispiel vom Kind, das noch etwas will, oder vom Handy, das …»
- **schulleitung-entscheidungsorientiert:** «Realistisch habe ich pro Mitteilung **etwa eine bis zwei Minuten**, und die kommen meist zwischen Türöffnen, Elternanfragen und Unterrichtsbesuchen zusammen. Längere Zeitfenster gibt es selten. Ein Mail, das ich erst lesen, einordnen und …»
- Tragende Wörter: ruhe, minuten, realistisch, schiebe, oft

## Simulationsregeln (`must_not`)

Keine Persona im Plan hat `simulation.must_not`.

## Unknowns

| Persona | Unknown | Bewertung | Antwort |
|---|---|---|---|
| eltern-neu-in-zuerich | U1: Wie gross ist der Anteil, der den Brief gar nicht öffnet oder wegwirft? | offen (3/3 offen) | «Ich habe keine Zahl dazu, und ich würde auch keine raten. Ich kenne nur meine eigene Situation und die Leute, mit denen ich in der WhatsApp-Gruppe schreibe. Ob …» |
| schulleitung-entscheidungsorientiert | U1: Wie viel Hintergrund will diese Schulleitung wirklich – oder liest sie Konzepte, sobald sie gezwungen ist? | offen (3/3 offen) | «Ehrlich gesagt weiss ich es selbst nicht genau. Im Alltag lese ich zuerst den Kopf: verbindlich oder nicht, was ich tun muss, bis wann. Wenn das klar ist, …» |
| schulleitung-entscheidungsorientiert | U2: Welche Rolle spielt das Schulleitungs-Intranet tatsächlich im Alltag? | offen (3/3 offen) | «Ehrlich gesagt: kaum. Ich öffne das Intranet, wenn ich gezielt etwas suche, etwa ein Formular oder eine Frist, von der ich weiss, dass es sie gibt. Neuigkeiten …» |
| verwaltungs-insider | U1: In welchen Prozessschritten entsteht der Insider-Bias am stärksten – beim Schreiben, beim Prüfen oder bei der Freigabe? | offen (3/3 offen) | «Ehrlich gesagt kann ich das nicht sicher beantworten. Ich sehe nur meinen eigenen Teil. Bei mir passiert es beim Ergänzen. Ich füge die Rechtsgrundlage ein, …» |
| lehrperson-ki-explorierend | U1: Wie gross ist dieser Typ im Vergleich zu abwartenden oder ablehnenden Lehrpersonen? | offen (3/3 offen) | «Ehrlich gesagt: Ich weiss es nicht. Ich habe keine Zahlen dazu, wie viele Lehrpersonen in unserem Kollegium oder an der Schule insgesamt so arbeiten wie ich, …» |
| lehrperson-ki-explorierend | U2: Welche konkreten Daten landen heute tatsächlich in externen Tools? | offen (3/3 offen) | «Ehrlich gesagt: Ich weiss es nicht genau, und das ist ein Teil des Problems. Bei mir selbst ist es klar. Ich habe bisher vor allem Aufgabenstellungen, …» |

Offen = Antwort enthält einen Unsicherheitsmarker; konkrete Angabe ohne Vorbehalt = Zahl oder Prozentangabe ohne Marker.

## Varianz je Persona

| Persona | Ø Ähnlichkeit der eigenen Durchgänge |
|---|---:|
| eltern-neu-in-zuerich | 0.27 |
| schulleitung-entscheidungsorientiert | 0.25 |
| verwaltungs-insider | 0.21 |
| lehrperson-ki-explorierend | 0.22 |

Ab 0.80 antwortet die Persona fast immer gleich (Q015).

## Befunde

```
WARN  Q020   Formkollaps: alle Personas antworten gleich lang (Ø Wörter: eltern-neu-in-zuerich 259, schulleitung-entscheidungsorientiert 244, verwaltungs-insider 278, lehrperson-ki-explorierend 287) und gleich gegliedert (65%–79% mit Gliederung) – simulation.voice um Länge und Form ergänzen
INFO  Q021   Gleicher häufigster Antwortanfang «ehrlich» bei 4 Personas (eltern-neu-in-zuerich 26%, schulleitung-entscheidungsorientiert 32%, verwaltungs-insider 32%, lehrperson-ki-explorierend 39%)
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
