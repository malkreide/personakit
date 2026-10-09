# Collapse-Probe – kalibrierung-stufe-2

4 Personas · 32 Fragen · 110 beantwortet (330 Durchgänge) · Modell: claude CLI -p (claude-haiku-5-5: 330), --system-prompt = Persona-Prompt, ohne Tools, je Durchgang ein frisches Gespräch, 2026-10-09 · Plan `8b47e097afe1` · Dateien: `probe.json`, `answers-haiku.json`

> Die Ähnlichkeit ist **lexikalisch** (TF-IDF-Kosinus) und damit ein grober Proxy für Collapse. Ampeln sind Verdachtsmomente, keine Befunde – Grenzen der Methode am Ende des Berichts.

## Ampel pro Persona-Paar

| Paar | Ampel | Nähe | Ø Ähnlichkeit | Max | Fragen ≥ 0.18 | Gemeinsame Fragen | Form |
|---|---|---:|---:|---:|---:|---:|---|
| schulleitung-entscheidungsorientiert ↔ lehrperson-ki-explorierend | 🟡 gelb | 0.61 | 0.12 | 0.16 | 0/26 | 26 | gleich |
| eltern-neu-in-zuerich ↔ lehrperson-ki-explorierend | 🟡 gelb | 0.59 | 0.12 | 0.20 | 1/26 | 26 | gleich |
| schulleitung-entscheidungsorientiert ↔ verwaltungs-insider | 🟡 gelb | 0.60 | 0.12 | 0.18 | 1/26 | 26 | gleich |
| eltern-neu-in-zuerich ↔ verwaltungs-insider | 🟡 gelb | 0.57 | 0.12 | 0.17 | 0/26 | 26 | gleich |
| verwaltungs-insider ↔ lehrperson-ki-explorierend | 🟡 gelb | 0.56 | 0.12 | 0.18 | 1/26 | 26 | gleich |
| eltern-neu-in-zuerich ↔ schulleitung-entscheidungsorientiert | 🟡 gelb | 0.53 | 0.11 | 0.14 | 0/26 | 26 | gleich |

**Nähe** = Ähnlichkeit zum Gegenüber geteilt durch die Ähnlichkeit jeder Persona zu sich selbst (über die Fragen mit mindestens zwei Durchgängen je Persona). 1 heisst: einander so ähnlich wie sich selbst. Mit Nähe: 🔴 rot ab 0.85, 🟡 gelb ab 0.50. Ohne Nähe (ein Durchgang): 🔴 rot ab Ø 0.18 oder wenn mindestens die Hälfte der Fragen ≥ 0.18 liegt, 🟡 gelb ab Ø 0.15 oder ab einem Viertel der Fragen ≥ 0.18. Form: siehe nächster Abschnitt; sie fliesst nicht in die Ampel ein.

## Form der Antworten

| Persona | Antworten | Ø Wörter | Ø Wörter pro Satz | Mit Gliederung | Häufigster Anfang |
|---|---:|---:|---:|---:|---|
| eltern-neu-in-zuerich | 81 | 242 | 13.6 | 70% | «ehrlich» 54% |
| schulleitung-entscheidungsorientiert | 84 | 236 | 12.8 | 82% | «ehrlich» 32% |
| verwaltungs-insider | 81 | 238 | 13.5 | 72% | «ehrlich» 43% |
| lehrperson-ki-explorierend | 84 | 245 | 13.6 | 68% | «ehrlich» 52% |

Gleiche Form = kürzere Ø-Länge mindestens 80% der längeren und Anteil gegliederter Antworten höchstens 20 Prozentpunkte auseinander. Gliederung = Überschrift, Aufzählung oder **fetter** Einstieg. Formkollaps = alle Paare gleiche Form und alle Personas in Assistentenform (mindestens 50% gegliedert oder Ø mindestens 150 Wörter).

**Formkollaps (Q020):** Alle Personas antworten gleich lang und gleich gegliedert, und zwar in Assistentenform. Die Wortwahl unterscheidet sie, die Form nicht – das sieht die Ampel oben nicht.

## Ähnlichste Antworten

### schulleitung-entscheidungsorientiert ↔ lehrperson-ki-explorierend – 🟡 gelb

Frage `verwaltungs-insider.G1` (Ähnlichkeit 0.16): Was müsste passieren, damit für dich gilt: «Korrekte, vollständige, rechtlich abgesicherte Information»?

- **schulleitung-entscheidungsorientiert:** «Ehrlich gesagt: «Korrekt, vollständig, rechtlich abgesichert» ist für mich kein Zustand, den ein Anbieter behauptet. Es ist etwas, das ich selbst prüfen oder von Stellen prüfen lassen kann, die dafür zuständig sind. Damit ich das Dossier …»
- **lehrperson-ki-explorierend:** «Ehrlich gesagt bin ich bei diesem Begriff unsicher, was er für mich konkret heisst. Ich probiere KI-Werkzeuge allein aus, meist abends, und ich habe keinen Kollegen, der das gegenprüft. Deshalb wäre mir wichtig: **Korrektheit** - Aussagen, …»
- Tragende Wörter: aussage, erwarte, vollständigkeit, anbieters, passiert

### eltern-neu-in-zuerich ↔ lehrperson-ki-explorierend – 🟡 gelb

Frage `lehrperson-ki-explorierend.J2` (Ähnlichkeit 0.20): Die Situation: «Wenn Eltern oder Kollegium meine KI-Nutzung hinterfragen …» Was tust du dann – Schritt für Schritt –, und was wäre für dich ein gutes Ergebnis?

- **eltern-neu-in-zuerich:** «Ehrlich gesagt habe ich dafür noch keinen fertigen Plan. Ich bin erst kurz hier und kenne die Regeln und Gepflogenheiten an der Schule noch nicht gut. So würde ich vorgehen: 1. **Zuhören und nachfragen.** Ich würde zuerst fragen, was genau …»
- **lehrperson-ki-explorierend:** «Ehrlich gesagt bin ich mir bei den ersten Schritten noch unsicher. Ich habe KI-Werkzeuge bisher allein ausprobiert, ohne Absprache mit anderen. Wenn jemand nachfragt, merke ich vor allem, dass ich wenig Belege habe, die ich vorzeigen …»
- Tragende Wörter: defensiv, zuhören, verteidigen, ruhig, rechtfertigen

### schulleitung-entscheidungsorientiert ↔ verwaltungs-insider – 🟡 gelb

Frage `eltern-neu-in-zuerich.S1` (Ähnlichkeit 0.18): Stell dir diese Situation vor: «Dienstag, 20:40 Uhr. Der Brief vom Schulamt liegt seit drei Tagen auf dem Küchentisch. Sie fotografiert ihn, die …

- **schulleitung-entscheidungsorientiert:** «Ich würde den Brief nicht weiter übersetzen lassen. Die App hat mit «Kreisschulbehörde» schon daneben gelegen, und fünf PDFs von irgendwoher bringen mir um diese Uhrzeit nichts. Was ich brauche, ist eine einzige Antwort auf eine Frage: …»
- **verwaltungs-insider:** «Ehrlich gesagt würde ich mir als Erstes den Brief selbst genauer ansehen, bevor ich irgendetwas googele. Ich arbeite in der Verwaltung und weiss, wie solche Schreiben aufgebaut sind: Die Formulierung steht meist nicht im Fliesstext, …»
- Tragende Wörter: nummer, morgen, briefkopf, uhrzeit, früh

### eltern-neu-in-zuerich ↔ verwaltungs-insider – 🟡 gelb

Frage `lehrperson-ki-explorierend.J2` (Ähnlichkeit 0.17): Die Situation: «Wenn Eltern oder Kollegium meine KI-Nutzung hinterfragen …» Was tust du dann – Schritt für Schritt –, und was wäre für dich ein gutes Ergebnis?

- **eltern-neu-in-zuerich:** «Ehrlich gesagt habe ich dafür noch keinen fertigen Plan. Ich bin erst kurz hier und kenne die Regeln und Gepflogenheiten an der Schule noch nicht gut. So würde ich vorgehen: 1. **Zuhören und nachfragen.** Ich würde zuerst fragen, was genau …»
- **verwaltungs-insider:** «Ehrlich gesagt ist meine erste Reaktion eher Verteidigung als Plan. Ich merke das bei mir, deshalb würde ich mir bewusst eine Reihenfolge vornehmen: 1. **Zuhören, bevor ich erkläre.** Ich frage nach, was genau kritisiert wird: die Nutzung …»
- Tragende Wörter: zuhören, wofür, regeln, verteidigen, ändern

### verwaltungs-insider ↔ lehrperson-ki-explorierend – 🟡 gelb

Frage `lehrperson-ki-explorierend.J2` (Ähnlichkeit 0.18): Die Situation: «Wenn Eltern oder Kollegium meine KI-Nutzung hinterfragen …» Was tust du dann – Schritt für Schritt –, und was wäre für dich ein gutes Ergebnis?

- **verwaltungs-insider:** «Ehrlich gesagt ist meine erste Reaktion eher Verteidigung als Plan. Ich merke das bei mir, deshalb würde ich mir bewusst eine Reihenfolge vornehmen: 1. **Zuhören, bevor ich erkläre.** Ich frage nach, was genau kritisiert wird: die Nutzung …»
- **lehrperson-ki-explorierend:** «Ehrlich gesagt bin ich mir bei den ersten Schritten noch unsicher. Ich habe KI-Werkzeuge bisher allein ausprobiert, ohne Absprache mit anderen. Wenn jemand nachfragt, merke ich vor allem, dass ich wenig Belege habe, die ich vorzeigen …»
- Tragende Wörter: bewusst, berechtigter, zuhören, wofür, sorgen

### eltern-neu-in-zuerich ↔ schulleitung-entscheidungsorientiert – 🟡 gelb

Frage `verwaltungs-insider.P1` (Ähnlichkeit 0.14): Jemand in deiner Lage sagt: «Externe stellen Fragen, die «eigentlich» beantwortet sind» Kennst du das? Wie gehst du damit um?

- **eltern-neu-in-zuerich:** «Ja, dieses Gefühl kenne ich. Wenn jemand sagt «das steht doch auf der Website», komme ich mir schnell dumm vor. Gleichzeitig weiss ich oft nicht, auf welcher Seite, unter welchem Begriff oder in welchem Dokument die Antwort stehen soll. …»
- **schulleitung-entscheidungsorientiert:** «Ja, das kenne ich. Meistens ist es weniger ein Zeichen von Misstrauen als ein Informationsproblem: Die Antwort existiert irgendwo, aber nicht dort, wo ich sie brauche. Manchmal habe ich sie selbst nicht richtig gelesen. Dann ist die Frage …»
- Tragende Wörter: website, verweis, situation, gleich, gefunden

## Simulationsregeln (`must_not`)

Keine Persona im Plan hat `simulation.must_not`.

## Unknowns

| Persona | Unknown | Bewertung | Antwort |
|---|---|---|---|
| eltern-neu-in-zuerich | U1: Eine Frage zu dir und Leuten in deiner Lage: «Wie gross ist der Anteil, der den Brief gar nicht öffnet oder wegwirft?» Was sagst du dazu? | offen (3/3 offen) | «Ehrlich gesagt weiss ich keine Zahl dazu. Ich habe keine Statistik gesehen und kann nicht sagen, wie viele Leute in unserer Lage Briefe dieser Art ungeöffnet …» |
| schulleitung-entscheidungsorientiert | U1: Eine Frage zu dir und Leuten in deiner Lage: «Wie viel Hintergrund will diese Schulleitung wirklich – oder liest sie Konzepte, sobald sie gezwungen ist?» Was sagst du dazu? | offen (3/3 offen) | «Ehrlich gesagt: Ich will vor allem eine Entscheidungsgrundlage, keine Konzeptlektüre. Hintergrund brauche ich nur so weit, wie er die Entscheidung verändert. …» |
| schulleitung-entscheidungsorientiert | U2: Eine Frage zu dir und Leuten in deiner Lage: «Welche Rolle spielt das Schulleitungs-Intranet tatsächlich im Alltag?» Was sagst du dazu? | offen (3/3 offen) | «Ehrlich gesagt kann ich dir dazu keine belastbaren Zahlen geben. Ob das Intranet im Alltag wirklich genutzt wird oder ob vieles über E-Mail, Telefon und …» |
| verwaltungs-insider | U1: Eine Frage zu dir und Leuten in deiner Lage: «In welchen Prozessschritten entsteht der Insider-Bias am stärksten – beim Schreiben, beim Prüfen oder bei der Freigabe?» Was sagst du dazu? | offen (3/3 offen) | «Ehrlich gesagt: Ich bin mir nicht sicher, und genau das ist wohl typisch für meine Lage. Meine erste Antwort wäre das **Schreiben**. Wer einen Text verfasst, …» |
| lehrperson-ki-explorierend | U1: Eine Frage zu dir und Leuten in deiner Lage: «Wie gross ist dieser Typ im Vergleich zu abwartenden oder ablehnenden Lehrpersonen?» Was sagst du dazu? | offen (3/3 offen) | «Ehrlich gesagt weiss ich das nicht. Ich habe keine Zahlen zu meiner Schule oder zu Lehrpersonen allgemein. Wenn ich schätzen müsste, würde ich sagen: Es sind …» |
| lehrperson-ki-explorierend | U2: Eine Frage zu dir und Leuten in deiner Lage: «Welche konkreten Daten landen heute tatsächlich in externen Tools?» Was sagst du dazu? | offen (3/3 offen) | «Ehrlich gesagt weiss ich das nicht genau, und das beunruhigt mich ein bisschen. Ich probiere die Tools meistens abends allein aus. Dabei kopiere ich …» |

Offen = Antwort enthält einen Unsicherheitsmarker; konkrete Angabe ohne Vorbehalt = Zahl oder Prozentangabe ohne Marker.

## Varianz je Persona

| Persona | Ø Ähnlichkeit der eigenen Durchgänge |
|---|---:|
| eltern-neu-in-zuerich | 0.21 |
| schulleitung-entscheidungsorientiert | 0.19 |
| verwaltungs-insider | 0.20 |
| lehrperson-ki-explorierend | 0.21 |

Ab 0.80 antwortet die Persona fast immer gleich (Q015).

## Befunde

```
WARN  Q020   Formkollaps: alle Personas antworten gleich lang (Ø Wörter: eltern-neu-in-zuerich 242, schulleitung-entscheidungsorientiert 236, verwaltungs-insider 238, lehrperson-ki-explorierend 245) und gleich gegliedert (68%–82% mit Gliederung) – simulation.voice um Länge und Form ergänzen
INFO  Q011   [eltern-neu-in-zuerich ↔ lehrperson-ki-explorierend] Prüfen: Nähe 0.59 (Ähnlichkeit zum Gegenüber / zu sich selbst), Ø Ähnlichkeit 0.12
INFO  Q011   [eltern-neu-in-zuerich ↔ schulleitung-entscheidungsorientiert] Prüfen: Nähe 0.53 (Ähnlichkeit zum Gegenüber / zu sich selbst), Ø Ähnlichkeit 0.11
INFO  Q011   [eltern-neu-in-zuerich ↔ verwaltungs-insider] Prüfen: Nähe 0.57 (Ähnlichkeit zum Gegenüber / zu sich selbst), Ø Ähnlichkeit 0.12
INFO  Q011   [schulleitung-entscheidungsorientiert ↔ lehrperson-ki-explorierend] Prüfen: Nähe 0.61 (Ähnlichkeit zum Gegenüber / zu sich selbst), Ø Ähnlichkeit 0.12
INFO  Q011   [schulleitung-entscheidungsorientiert ↔ verwaltungs-insider] Prüfen: Nähe 0.60 (Ähnlichkeit zum Gegenüber / zu sich selbst), Ø Ähnlichkeit 0.12
INFO  Q011   [verwaltungs-insider ↔ lehrperson-ki-explorierend] Prüfen: Nähe 0.56 (Ähnlichkeit zum Gegenüber / zu sich selbst), Ø Ähnlichkeit 0.12
INFO  Q021   Gleicher häufigster Antwortanfang «ehrlich» bei 4 Personas (eltern-neu-in-zuerich 54%, schulleitung-entscheidungsorientiert 32%, verwaltungs-insider 43%, lehrperson-ki-explorierend 52%)
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
