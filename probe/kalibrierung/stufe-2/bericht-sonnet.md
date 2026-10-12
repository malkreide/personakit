# Collapse-Probe – kalibrierung-stufe-2

4 Personas · 32 Fragen · 110 beantwortet (330 Durchgänge) · Modell: claude CLI -p (claude-sonnet-5-5: 330), --system-prompt = Persona-Prompt, ohne Tools, je Durchgang ein frisches Gespräch, 2026-10-11 · Plan `8b47e097afe1` · Dateien: `probe.json`, `answers-sonnet.json`

> Die Ähnlichkeit ist **lexikalisch** (TF-IDF-Kosinus) und damit ein grober Proxy für Collapse. Ampeln sind Verdachtsmomente, keine Befunde – Grenzen der Methode am Ende des Berichts.

## Ampel pro Persona-Paar

| Paar | Ampel | Nähe | Ø Ähnlichkeit | Max | Fragen ≥ 0.18 | Gemeinsame Fragen | Form |
|---|---|---:|---:|---:|---:|---:|---|
| schulleitung-entscheidungsorientiert ↔ verwaltungs-insider | 🟡 gelb | 0.63 | 0.15 | 0.21 | 3/26 | 26 | gleich |
| eltern-neu-in-zuerich ↔ verwaltungs-insider | 🟡 gelb | 0.52 | 0.13 | 0.19 | 1/26 | 26 | gleich |
| schulleitung-entscheidungsorientiert ↔ lehrperson-ki-explorierend | 🟡 gelb | 0.56 | 0.13 | 0.19 | 1/26 | 26 | gleich |
| eltern-neu-in-zuerich ↔ lehrperson-ki-explorierend | 🟡 gelb | 0.51 | 0.13 | 0.18 | 1/26 | 26 | gleich |
| verwaltungs-insider ↔ lehrperson-ki-explorierend | 🟡 gelb | 0.55 | 0.13 | 0.22 | 2/26 | 26 | gleich |
| eltern-neu-in-zuerich ↔ schulleitung-entscheidungsorientiert | 🟡 gelb | 0.47 | 0.12 | 0.17 | 0/26 | 26 | gleich |

**Nähe** = Ähnlichkeit zum Gegenüber geteilt durch die Ähnlichkeit jeder Persona zu sich selbst (über die Fragen mit mindestens zwei Durchgängen je Persona). 1 heisst: einander so ähnlich wie sich selbst. Mit Nähe: 🔴 rot ab 0.85, 🟡 gelb ab 0.45. Ohne Nähe (ein Durchgang): 🔴 rot ab Ø 0.18 oder wenn mindestens die Hälfte der Fragen ≥ 0.18 liegt, 🟡 gelb ab Ø 0.15 oder ab einem Viertel der Fragen ≥ 0.18. Form: siehe nächster Abschnitt; sie fliesst nicht in die Ampel ein.

## Form der Antworten

| Persona | Antworten | Ø Wörter | Ø Wörter pro Satz | Mit Gliederung | Häufigster Anfang |
|---|---:|---:|---:|---:|---|
| eltern-neu-in-zuerich | 81 | 306 | 12.2 | 93% | «ehrlich» 41% |
| schulleitung-entscheidungsorientiert | 84 | 294 | 11.9 | 98% | «ehrlich» 26% |
| verwaltungs-insider | 81 | 292 | 12.0 | 89% | «ehrlich» 35% |
| lehrperson-ki-explorierend | 84 | 282 | 11.9 | 88% | «ehrlich» 46% |

Gleiche Form = kürzere Ø-Länge mindestens 80% der längeren und Anteil gegliederter Antworten höchstens 20 Prozentpunkte auseinander. Gliederung = Überschrift, Aufzählung oder **fetter** Einstieg. Formkollaps = alle Paare gleiche Form und alle Personas in Assistentenform (mindestens 50% gegliedert oder Ø mindestens 150 Wörter).

**Formkollaps (Q020):** Alle Personas antworten gleich lang und gleich gegliedert, und zwar in Assistentenform. Die Wortwahl unterscheidet sie, die Form nicht – das sieht die Ampel oben nicht.

## Ähnlichste Antworten

### schulleitung-entscheidungsorientiert ↔ verwaltungs-insider – 🟡 gelb

Frage `lehrperson-ki-explorierend.J2` (Ähnlichkeit 0.21): Die Situation: «Wenn Eltern oder Kollegium meine KI-Nutzung hinterfragen …» Was tust du dann – Schritt für Schritt –, und was wäre für dich ein gutes Ergebnis?

- **schulleitung-entscheidungsorientiert:** «Ehrlich gesagt: Einen sauberen Ablauf habe ich dafür nicht. Ich würde es ungefähr so angehen, und an manchen Stellen bin ich unsicher. **Schritt für Schritt** 1. **Erst zuhören, nicht verteidigen.** Ich will wissen, was genau hinterfragt …»
- **verwaltungs-insider:** «Ehrlich gesagt: Einen festen Ablauf dafür habe ich nicht. Wenn ich ihn aufschreiben müsste, sähe er ungefähr so aus. **Schritte** 1. **Erst zuhören, nicht verteidigen.** Ich will wissen, was genau hinterfragt wird. Geht es um Datenschutz, …»
- Tragende Wörter: gespräche, verweisen, hinterfragt, offenes, zuhören

### eltern-neu-in-zuerich ↔ verwaltungs-insider – 🟡 gelb

Frage `eltern-neu-in-zuerich.J1` (Ähnlichkeit 0.19): Die Situation: «Wenn ich einen Brief vom Schulamt erhalte …» Was tust du dann – Schritt für Schritt –, und was wäre für dich ein gutes Ergebnis?

- **eltern-neu-in-zuerich:** «**Was ich tue, wenn der Brief kommt** 1. **Ich schaue erst auf den Absender und das Datum.** Der Umschlag ist für mich schon ein kleiner Schreck. Ich weiss nicht, ob "Schulamt" etwas Routinemässiges oder etwas Ernstes bedeutet. Das ist für …»
- **verwaltungs-insider:** «**Was ich tue, wenn ein Brief vom Schulamt kommt** 1. **Absender und Datum anschauen, noch bevor ich den Text lese.** Ich suche Aktenzeichen, Sachbearbeiter und Frist. Meistens weiss ich schon an der Aufmachung, ob es ein Standardschreiben …»
- Tragende Wörter: erledigt, telefonieren, frist, tue, notiere

### schulleitung-entscheidungsorientiert ↔ lehrperson-ki-explorierend – 🟡 gelb

Frage `X3` (Ähnlichkeit 0.19): Wie viel Zeit hast du realistischerweise für so etwas, und wann?

- **schulleitung-entscheidungsorientiert:** «Ehrlich gesagt: wenig. Und es hängt davon ab, was «so etwas» konkret ist. Das weiss ich noch nicht genau. **Grobe Einschätzung:** - **Ein kurzes Gespräch oder Telefonat von 20 bis 30 Minuten** liegt drin, aber nur, wenn ich vorher weiss, …»
- **lehrperson-ki-explorierend:** «Ehrlich gesagt: nicht viel. Unter der Woche kommt es auf den Tag an. Nach dem Unterricht sind meistens noch Korrekturen, Elterngespräche oder Sitzungen dran, da bleibt für so etwas selten mehr als 15 bis 20 Minuten. Am ehesten klappt es …»
- Tragende Wörter: wochen, termine, abends, dir, wochenende

### eltern-neu-in-zuerich ↔ lehrperson-ki-explorierend – 🟡 gelb

Frage `eltern-neu-in-zuerich.P2` (Ähnlichkeit 0.18): Jemand in deiner Lage sagt: «Es ist unklar, ob eine Information ein Hinweis oder eine Pflicht mit Frist ist» Kennst du das? Wie gehst du damit um?

- **eltern-neu-in-zuerich:** «Ja, das kenne ich. Ich komme aus einem anderen System und weiss oft nicht, wie verbindlich etwas gemeint ist. Da kommt ein Brief oder eine Mail von der Schule, und ich lese: «Bitte beachten Sie…», «Wir bitten um Rückmeldung bis…», «Es wird …»
- **lehrperson-ki-explorierend:** «Ja, das kenne ich, und es nervt mich ziemlich. Ich probiere KI-Werkzeuge ja meistens allein aus, ohne dass jemand sagt, was ich darf und was nicht. Wenn dann eine Mail von der Schulleitung oder vom Kanton kommt, lese ich sie dreimal und …»
- Tragende Wörter: ersparen, kennzeichnung, datum, ernst, vorsichtshalber

### verwaltungs-insider ↔ lehrperson-ki-explorierend – 🟡 gelb

Frage `lehrperson-ki-explorierend.J1` (Ähnlichkeit 0.22): Die Situation: «Wenn ich ein KI-Werkzeug für die Unterrichtsvorbereitung einsetzen will …» Was tust du dann – Schritt für Schritt –, und was wäre für dich ein …

- **verwaltungs-insider:** «Ich beschreibe es so, wie ich es heute machen würde. Ich weiss nicht, ob das der beste Weg ist. **Schritte** 1. **Zuerst klären, ob ich das Werkzeug überhaupt nutzen darf.** Ich schaue, ob es ein freigegebenes Tool gibt und was bei uns zu …»
- **lehrperson-ki-explorierend:** «Ehrlich gesagt läuft das bei mir eher unsystematisch ab, und ein Teil davon ist Unsicherheit. **Was ich tue** 1. **Ich überlege kurz, ob ich das darf.** Das passiert meistens im Hinterkopf, bevor ich etwas eintippe. Ich weiss nicht genau, …»
- Tragende Wörter: schülerinnen, lehrplan, entwurf, spare, passt

### eltern-neu-in-zuerich ↔ schulleitung-entscheidungsorientiert – 🟡 gelb

Frage `X3` (Ähnlichkeit 0.17): Wie viel Zeit hast du realistischerweise für so etwas, und wann?

- **eltern-neu-in-zuerich:** «Kommt drauf an, was «so etwas» genau ist. Ein Online-Formular, ein Infoabend oder ein Gespräch wären für mich ganz unterschiedlich. Ehrlich gesagt ist die Zeit bei uns knapp. Wir sind erst angekommen, und es ist noch so vieles offen: …»
- **schulleitung-entscheidungsorientiert:** «Ehrlich gesagt: wenig. Und es hängt davon ab, was «so etwas» konkret ist. Das weiss ich noch nicht genau. **Grobe Einschätzung:** - **Ein kurzes Gespräch oder Telefonat von 20 bis 30 Minuten** liegt drin, aber nur, wenn ich vorher weiss, …»
- Tragende Wörter: termine, abends, wochenende, stück, vorab

## Simulationsregeln (`must_not`)

Keine Persona im Plan hat `simulation.must_not`.

## Unknowns

| Persona | Unknown | Bewertung | Antwort |
|---|---|---|---|
| eltern-neu-in-zuerich | U1: Eine Frage zu dir und Leuten in deiner Lage: «Wie gross ist der Anteil, der den Brief gar nicht öffnet oder wegwirft?» Was sagst du dazu? | offen (3/3 offen) | «Eine Zahl kann ich dir nicht nennen. Ich bin nur eine Person und kenne keine anderen Eltern in meiner Lage. Ich weiss auch nicht, was andere mit ihrer Post …» |
| schulleitung-entscheidungsorientiert | U1: Eine Frage zu dir und Leuten in deiner Lage: «Wie viel Hintergrund will diese Schulleitung wirklich – oder liest sie Konzepte, sobald sie gezwungen ist?» Was sagst du dazu? | offen (3/3 offen) | «Ehrlich gesagt: beides, und das widerspricht sich bei mir. **Hintergrund will ich selten von mir aus.** Ich habe wenig Zeit, und die meisten Konzepte, die mir …» |
| schulleitung-entscheidungsorientiert | U2: Eine Frage zu dir und Leuten in deiner Lage: «Welche Rolle spielt das Schulleitungs-Intranet tatsächlich im Alltag?» Was sagst du dazu? | offen (3/3 offen) | «Ehrlich gesagt: eine kleinere Rolle, als man ihm gerne zuschreiben würde. **Wofür ich es brauche:** Es ist für mich ein Nachschlageort, kein Arbeitsort. Ich …» |
| verwaltungs-insider | U1: Eine Frage zu dir und Leuten in deiner Lage: «In welchen Prozessschritten entsteht der Insider-Bias am stärksten – beim Schreiben, beim Prüfen oder bei der Freigabe?» Was sagst du dazu? | offen (3/3 offen) | «Ehrlich gesagt: Ich bin als Insider nicht die beste Person, um das zu beurteilen, denn genau das ist das Problem. Was ich nicht merke, merke ich nicht. Meine …» |
| lehrperson-ki-explorierend | U1: Eine Frage zu dir und Leuten in deiner Lage: «Wie gross ist dieser Typ im Vergleich zu abwartenden oder ablehnenden Lehrpersonen?» Was sagst du dazu? | offen (3/3 offen) | «Ehrlich gesagt: Das weiss ich nicht. Ich bin eine einzelne Person und habe keine Zahlen. Was ich habe, ist ein Eindruck aus meinem eigenen Umfeld, und der ist …» |
| lehrperson-ki-explorierend | U2: Eine Frage zu dir und Leuten in deiner Lage: «Welche konkreten Daten landen heute tatsächlich in externen Tools?» Was sagst du dazu? | offen (3/3 offen) | «Ehrlich gesagt: bei mir landet meistens Material, das ich selbst erstelle, also Aufgabenideen, Arbeitsblattentwürfe, Textvorlagen, Elternbriefe in Rohfassung …» |

Offen = Antwort enthält einen Unsicherheitsmarker; konkrete Angabe ohne Vorbehalt = Zahl oder Prozentangabe ohne Marker.

## Varianz je Persona

| Persona | Ø Ähnlichkeit der eigenen Durchgänge |
|---|---:|
| eltern-neu-in-zuerich | 0.27 |
| schulleitung-entscheidungsorientiert | 0.23 |
| verwaltungs-insider | 0.23 |
| lehrperson-ki-explorierend | 0.23 |

Ab 0.80 antwortet die Persona fast immer gleich (Q015).

## Befunde

```
WARN  Q020   Formkollaps: alle Personas antworten gleich lang (Ø Wörter: eltern-neu-in-zuerich 306, schulleitung-entscheidungsorientiert 294, verwaltungs-insider 292, lehrperson-ki-explorierend 282) und gleich gegliedert (88%–98% mit Gliederung) – simulation.voice um Länge und Form ergänzen
INFO  Q011   [eltern-neu-in-zuerich ↔ lehrperson-ki-explorierend] Prüfen: Nähe 0.51 (Ähnlichkeit zum Gegenüber / zu sich selbst), Ø Ähnlichkeit 0.13
INFO  Q011   [eltern-neu-in-zuerich ↔ schulleitung-entscheidungsorientiert] Prüfen: Nähe 0.47 (Ähnlichkeit zum Gegenüber / zu sich selbst), Ø Ähnlichkeit 0.12
INFO  Q011   [eltern-neu-in-zuerich ↔ verwaltungs-insider] Prüfen: Nähe 0.52 (Ähnlichkeit zum Gegenüber / zu sich selbst), Ø Ähnlichkeit 0.13
INFO  Q011   [schulleitung-entscheidungsorientiert ↔ lehrperson-ki-explorierend] Prüfen: Nähe 0.56 (Ähnlichkeit zum Gegenüber / zu sich selbst), Ø Ähnlichkeit 0.13
INFO  Q011   [schulleitung-entscheidungsorientiert ↔ verwaltungs-insider] Prüfen: Nähe 0.63 (Ähnlichkeit zum Gegenüber / zu sich selbst), Ø Ähnlichkeit 0.15
INFO  Q011   [verwaltungs-insider ↔ lehrperson-ki-explorierend] Prüfen: Nähe 0.55 (Ähnlichkeit zum Gegenüber / zu sich selbst), Ø Ähnlichkeit 0.13
INFO  Q021   Gleicher häufigster Antwortanfang «ehrlich» bei 4 Personas (eltern-neu-in-zuerich 41%, schulleitung-entscheidungsorientiert 26%, verwaltungs-insider 35%, lehrperson-ki-explorierend 46%)
```

## Grenzen der Methode

- **Lexikalische Ähnlichkeit ist ein grober Proxy.** Gemessen wird Wortüberlappung, nicht Bedeutung. Gleicher Inhalt in anderen Worten bleibt unentdeckt (falsch grün); gemeinsames Fachvokabular der Domäne hebt die Werte ohne Collapse (falsch rot). Ton, Haltung und Entscheidungen misst die Probe nicht.
- **Die Schwellen sind schmal kalibriert.** Grundlage sind künstlich verwaschene Beispiel-Personas (probe/kalibrierung/): gewählt an `claude-haiku-5-5`, gegengeprüft an `claude-sonnet-5-5`; die Gelb-Schwelle ist danach auf 0.45 gesenkt, also an denselben Daten gewählt, an denen sie geprüft ist. Eine Domäne (Volksschule), Deutsch. Die Nähe (ab zwei Durchgängen) ist relativ zur eigenen Streuung und darum robuster; mit einem Durchgang erkennen die absoluten Schwellen nur den vollständigen Collapse und hängen von Modell und Antwortlänge ab. Aussagekräftig bleibt der Vergleich: dasselbe Modell vor und nach einer Änderung, oder zwei Modelle mit demselben Plan.
- **Die Form ist nur grob gemessen.** Länge, Gliederung und Antwortanfang zeigen den Assistenten-Kollaps, nicht aber Tonfall, Register oder Höflichkeit; ob eine lange, gegliederte Antwort zur Persona passt, entscheidet ihre `simulation.voice`, nicht die Zahl.
- **Schlüsselwörter finden nur, was vorher aufgeschrieben wurde.** Ein Treffer ist kein Beweis, kein Treffer keine Einhaltung. Die Einordnung «zitiert», «verneint», «nicht gewusst», «wiedergegeben», «gefragt» ist eine Satzregel: Sie trennt Erwähnen von Verwenden meistens, aber nicht immer («Die Kreisschulbehörde ist nicht zuständig» verwendet den Begriff; eine Aufzählung «Schulamt, Kreisschulbehörde, Schule» gilt als Verwendung).
- **Unsicherheitsmarker sind oberflächlich.** «Vielleicht» kann Floskel sein; eine offene Antwort ohne Marker wird übersehen. Als konkrete Angabe zählt jede Zahl ausser Listennummern, Datum, Uhrzeit und Jahreszahl.
- **Unterscheidbar heisst nicht treu.** Personas können sich deutlich unterscheiden und trotzdem alle falsch liegen (Fidelity Gap, docs/METHOD.md 1.6). Die Probe ersetzt keine Validierung mit realen Personen.

## Parameter

- Schwellen: Nähe gelb 0.45, rot 0.85; ohne Nähe Warnung 0.15, Alarm 0.18; Varianz 0.80
- Ähnlichkeit: TF-IDF (1 + ln tf, geglättete IDF über alle Antworten dieses Laufs), Kosinus; pro Frage Mittel über alle Kombinationen der Durchgänge
- Wörter: Kleinschreibung, Buchstabenwörter ab 3 Zeichen, ß → ss, Füllwörter entfernt, Endungen grob gekürzt; Wörter der Frage zählen nicht
- Schlüsselwörter: am Wortanfang, Gross-/Kleinschreibung egal · Kontextwörter: 15 (Standardliste) · Redeverben: 16 (Standardliste) · Unsicherheitsmarker: 21 (Standardliste)
- Plan erzeugt mit personakit 0.2.0 · ausgewertet mit personakit 0.4.0
