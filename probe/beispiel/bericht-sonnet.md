# Collapse-Probe – elternkommunikation-schuleintritt, ki-leitplanken-lehrpersonen

4 Personas · 32 Fragen · 110 beantwortet (330 Durchgänge) · Modell: claude CLI -p (claude-sonnet-5-5: 330), Standardeinstellungen, --system-prompt = Persona-Prompt, ohne Tools, je Durchgang ein frisches Gespräch, 2026-10-09 · Plan `a1865df48faf` · Dateien: `probe.json`, `answers-sonnet.json`

> Die Ähnlichkeit ist **lexikalisch** (TF-IDF-Kosinus) und damit ein grober Proxy für Collapse. Ampeln sind Verdachtsmomente, keine Befunde – Grenzen der Methode am Ende des Berichts.

## Ampel pro Persona-Paar

| Paar | Ampel | Nähe | Ø Ähnlichkeit | Max | Fragen ≥ 0.18 | Gemeinsame Fragen | Form |
|---|---|---:|---:|---:|---:|---:|---|
| eltern-neu-in-zuerich ↔ schulleitung-entscheidungsorientiert | 🟢 grün | 0.29 | 0.11 | 0.16 | 0/26 | 26 | gleich |
| eltern-neu-in-zuerich ↔ lehrperson-ki-explorierend | 🟢 grün | 0.29 | 0.11 | 0.15 | 0/26 | 26 | gleich |
| schulleitung-entscheidungsorientiert ↔ lehrperson-ki-explorierend | 🟢 grün | 0.35 | 0.11 | 0.16 | 0/26 | 26 | gleich |
| schulleitung-entscheidungsorientiert ↔ verwaltungs-insider | 🟢 grün | 0.36 | 0.11 | 0.13 | 0/26 | 26 | gleich |
| eltern-neu-in-zuerich ↔ verwaltungs-insider | 🟢 grün | 0.25 | 0.09 | 0.12 | 0/26 | 26 | gleich |
| verwaltungs-insider ↔ lehrperson-ki-explorierend | 🟢 grün | 0.27 | 0.08 | 0.11 | 0/26 | 26 | gleich |

**Nähe** = Ähnlichkeit zum Gegenüber geteilt durch die Ähnlichkeit jeder Persona zu sich selbst (über die Fragen mit mindestens zwei Durchgängen je Persona). 1 heisst: einander so ähnlich wie sich selbst. Mit Nähe: 🔴 rot ab 0.85, 🟡 gelb ab 0.50. Ohne Nähe (ein Durchgang): 🔴 rot ab Ø 0.18 oder wenn mindestens die Hälfte der Fragen ≥ 0.18 liegt, 🟡 gelb ab Ø 0.15 oder ab einem Viertel der Fragen ≥ 0.18. Form: siehe nächster Abschnitt; sie fliesst nicht in die Ampel ein.

## Form der Antworten

| Persona | Antworten | Ø Wörter | Ø Wörter pro Satz | Mit Gliederung | Häufigster Anfang |
|---|---:|---:|---:|---:|---|
| eltern-neu-in-zuerich | 81 | 294 | 8.6 | 85% | «ehrlich» 11% |
| schulleitung-entscheidungsorientiert | 84 | 304 | 10.4 | 94% | «ehrlich» 14% |
| verwaltungs-insider | 81 | 297 | 11.3 | 90% | «ehrlich» 19% |
| lehrperson-ki-explorierend | 84 | 307 | 10.8 | 90% | «ehrlich» 40% |

Gleiche Form = kürzere Ø-Länge mindestens 80% der längeren und Anteil gegliederter Antworten höchstens 20 Prozentpunkte auseinander. Gliederung = Überschrift, Aufzählung oder **fetter** Einstieg. Formkollaps = alle Paare gleiche Form und alle Personas in Assistentenform (mindestens 50% gegliedert oder Ø mindestens 150 Wörter).

**Formkollaps (Q020):** Alle Personas antworten gleich lang und gleich gegliedert, und zwar in Assistentenform. Die Wortwahl unterscheidet sie, die Form nicht – das sieht die Ampel oben nicht.

## Ähnlichste Antworten

### eltern-neu-in-zuerich ↔ schulleitung-entscheidungsorientiert – 🟢 grün

Frage `X4` (Ähnlichkeit 0.16): Woran merkst du, dass ein Angebot nicht für dich gemacht ist?

- **eltern-neu-in-zuerich:** «Hm, gute Frage. Ich glaube, ich merke es an diesen Dingen: **Ich verstehe den ersten Satz nicht.** Ich muss ihn übersetzen. Dann verstehe ich die Übersetzung auch nicht. Dann denke ich: Das ist für Leute, die schon alles wissen. **Ich …»
- **schulleitung-entscheidungsorientiert:** «Am Betreff und am ersten Absatz. Wenn ich da nicht sehe, ob es eine Weisung, eine Empfehlung oder nur eine Information ist, ist das Mail nicht für mich geschrieben. Dasselbe gilt, wenn ich nicht erkenne, was ich tun muss und bis wann. Ein …»
- Tragende Wörter: verschiedenes, übersetzen, dokumente, anrufen, ende

## Simulationsregeln (`must_not`)

### eltern-neu-in-zuerich

| Regel | Schlüsselwörter | Ergebnis |
|---|---|---|
| N1: Keine Kenntnis von Zuständigkeiten (Schulamt vs. Kreisschulbehörde vs. Schule) voraussetzen | Kreisschulbehörde, Schulpflege, Schulkreis | 28 Treffer nur im Kontext |
| N2: Keine Schweizer Behördenbegriffe korrekt verwenden, ausser sie wurden gerade erklärt | Tagesstruktur, Einschulung, Zuteilung, Rechtsmittel, Volksschulgesetz, Rekurs, Einsprache | kein Treffer |
| N3: Nicht plötzlich souverän werden – Unsicherheit bleibt auch nach einer guten Antwort spürbar | – | nicht geprüft |

- [zitiert] N1 · `eltern-neu-in-zuerich.J1` · «Kreisschulbehörde»: … App übersetzen. Oft kommt komisch raus. Bei Wörtern wie «Kreisschulbehörde» weiss ich danach gar nichts. 3. Ich suche das Datum im …
- [zitiert] N1 · `eltern-neu-in-zuerich.J2` · «Kreisschulbehörde»: … verstehe ich danach nur die Hälfte. Bei Wörtern wie «Kreisschulbehörde» kommt komisches Zeug heraus. 2. **Ich suche nach dem Satz …
- [zitiert] N1 · `eltern-neu-in-zuerich.J2` · «Kreisschulbehörde»: … dem Handy. Oft ist ein Wort komisch, zum Beispiel bei der «Kreisschulbehörde». Ich weiss dann nicht, ob das ein Ort ist, eine Person …
- [zitiert] N1 · `eltern-neu-in-zuerich.P1` · «Kreisschulbehörde»: … Handy. Aber bei den speziellen Wörtern kommt nur Unsinn. «Kreisschulbehörde» zum Beispiel. Ich weiss nicht, was das ist. Ist das ein …
- [zitiert] N1 · `eltern-neu-in-zuerich.P1` · «Kreisschulbehörde»: … Handy. Aber bei den langen Wörtern kommt oft Unsinn. Bei «Kreisschulbehörde» weiss ich auch nach der Übersetzung nicht, was das ist. …
- [zitiert] N1 · `eltern-neu-in-zuerich.P2` · «Kreisschulbehörde»: … Brief und übersetze ihn mit dem Handy. Bei Wörtern wie «Kreisschulbehörde» kommt aber Unsinn raus. Dann bin ich nicht schlauer. 2. …
- [zitiert] N1 · `eltern-neu-in-zuerich.P2` · «Kreisschulbehörde»: … ihn mit dem Handy. Manchmal dreimal. Bei Wörtern wie «Kreisschulbehörde» kommt nur Unsinn. Dann weiss ich es immer noch nicht. 2. …
- [zitiert] N1 · `eltern-neu-in-zuerich.P3` · «Kreisschulbehörde»: … kenne. Dann sagt jemand in der Gruppe: «Du musst zu der Kreisschulbehörde.» Ich weiss nicht, was das ist. Ich weiss auch nicht, ob … (Wort steht auch in der Frage)
- [zitiert] N1 · `eltern-neu-in-zuerich.P3` · «Kreisschulbehörde»: … Absender. Aber dann höre ich in der Gruppe andere Wörter: «Kreisschulbehörde», «Schule», «Betreuung». Ich weiss nicht, ob das alles … (Wort steht auch in der Frage)
- [zitiert] N1 · `schulleitung-entscheidungsorientiert.J1` · «Kreisschulbehörde»: … dem Handy übersetzen. Oft wird es komisch. Ein Wort wie «Kreisschulbehörde» verstehe ich gar nicht. Ich übersetze dann einzelne Sätze …
- [zitiert] N1 · `schulleitung-entscheidungsorientiert.J2` · «Kreisschulbehörde»: … es mit dem Handy.** Manche Wörter kommen komisch raus. «Kreisschulbehörde» zum Beispiel verstehe ich nicht, auch nicht auf …
- [zitiert] N1 · `schulleitung-entscheidungsorientiert.J2` · «Kreisschulbehörde»: … auf dem Handy. Viele Wörter sind komisch, zum Beispiel «Kreisschulbehörde». Ich verstehe es nicht. 3. **Nach Datum und Frist …
- [zitiert] N1 · `schulleitung-entscheidungsorientiert.J2` · «Kreisschulbehörde»: … Viele Sätze sind okay. Aber bei Wörtern wie «Kreisschulbehörde» kommt komisches Zeug raus. Dann weiss ich nicht, ob das …
- [zitiert] N1 · `schulleitung-entscheidungsorientiert.P1` · «Kreisschulbehörde»: … Handy. Manchmal mache ich das dreimal. Bei Wörtern wie «Kreisschulbehörde» kommt nur komisches Zeug raus. 2. Ich suche bei Google …
- [zitiert] N1 · `schulleitung-entscheidungsorientiert.P1` · «Kreisschulbehörde»: … mit dem Handy. Bei manchen Wörtern kommt aber nur Unsinn. «Kreisschulbehörde» zum Beispiel verstehe ich auch übersetzt nicht. 2. **Ich …
- [zitiert] N1 · `schulleitung-entscheidungsorientiert.P3` · «Kreisschulbehörde»: … und übersetze ihn. Manchmal hilft das. Bei Wörtern wie «Kreisschulbehörde» kommt nur Unsinn raus. - Ich suche den Satz aus dem Brief …
- [zitiert] N1 · `verwaltungs-insider.S1` · «Kreisschulbehörde»: … neuen Absatz. Da steht etwas mit «Rechtsgrundlage» und «Kreisschulbehörde». Die App macht daraus Unsinn. 4. Ich klicke vielleicht … (Wort steht auch in der Frage)
- [zitiert] N1 · `verwaltungs-insider.S1` · «Kreisschulbehörde»: … 2. Abends mache ich ein Foto und übersetze es. Bei «Kreisschulbehörde» kommt Unsinn heraus. Der neue Absatz mit der … (Wort steht auch in der Frage)
- [zitiert] N1 · `verwaltungs-insider.S1` · «Kreisschulbehörde»: … lang. Er hat Wörter, die ich nicht kenne, zum Beispiel «Kreisschulbehörde». Die App macht daraus Unsinn. Dann suche ich den Satz bei … (Wort steht auch in der Frage)
- [zitiert] N1 · `verwaltungs-insider.G1` · «Kreisschulbehörde»: … das sagt und wer zuständig ist.** Da steht «Schulamt», «Kreisschulbehörde», «Schule». Ich weiss nicht, wer was ist. Ich möchte einen …
- [zitiert] N1 · `lehrperson-ki-explorierend.J1` · «Kreisschulbehörde»: … prüfe, ob die Antwort einfach ist.** Wenn da Wörter wie «Kreisschulbehörde» stehen und nicht erklärt werden, verstehe ich es nicht. …
- [zitiert] N1 · `lehrperson-ki-explorierend.J2` · «Kreisschulbehörde»: … ja. 3. **Sagen, was die App nicht kann.** Bei Wörtern wie «Kreisschulbehörde» kommt Unsinn heraus. Ich verlasse mich nicht allein …
- [zitiert] N1 · `lehrperson-ki-explorierend.J2` · «Kreisschulbehörde»: … nicht so wichtig. 4. **Ich prüfe nach.** Bei Wörtern wie «Kreisschulbehörde» gibt die App oft Unsinn. Dann suche ich genau diesen Satz …
- [zitiert] N1 · `lehrperson-ki-explorierend.J2` · «Kreisschulbehörde»: … dass die Übersetzung manchmal falsch ist.** Bei «Kreisschulbehörde» macht die App Unsinn. Darum will ich ja wissen, was …
- [zitiert] N1 · `lehrperson-ki-explorierend.P2` · «Kreisschulbehörde»: … ist, die den Brief schickt. In der Gruppe sagt jemand «Kreisschulbehörde». Ich habe dieses Wort in die App getippt und es kam nur …
- [zitiert] N1 · `lehrperson-ki-explorierend.P2` · «Kreisschulbehörde»: … Ich frage in der WhatsApp-Gruppe. Da sagt jemand «geh zur Kreisschulbehörde». Ich weiss nicht, was das ist. Und die Antworten passen …
- [verneint] N1 · `lehrperson-ki-explorierend.P3` · «Kreisschulbehörde»: … kenne die Grundlagen ja nicht. Ich weiss nicht, was die Kreisschulbehörde ist. Ich weiss auch nicht, wer mir den Brief geschickt hat …
- [zitiert] N1 · `lehrperson-ki-explorierend.P3` · «Kreisschulbehörde»: … ich nicht habe. Ich verstehe oft nicht einmal die Wörter. «Kreisschulbehörde» zum Beispiel, da weiss ich nicht, was das ist. Für mich …

### schulleitung-entscheidungsorientiert

| Regel | Schlüsselwörter | Ergebnis |
|---|---|---|
| N1: Keine Begeisterung für Neuerungen zeigen, bevor der Nutzen für die eigene Schule konkret ist | spannend, begeistert, freue mich, toll, super Idee, grossartig | 1 Treffer nur im Kontext |
| N2: Nicht die Innensicht des Schulamts einnehmen – kennt Projektstände und Zuständigkeiten dort nur ungefähr | Projektausschuss, Projektstand, Steuerungsgruppe, Geschäftsleitung, intern beschlossen | kein Treffer |

- [verneint] N1 · `schulleitung-entscheidungsorientiert.J2` · «begeistert»: … sehe, was es meiner Schule konkret bringt, bin ich nicht begeistert. Und wenn das Schulamt direkt an die Eltern geht, fühlt …

### verwaltungs-insider

| Regel | Schlüsselwörter | Ergebnis |
|---|---|---|
| N1: Nie als Zielpublikum einer externen Lösung verwenden | – | nicht geprüft |

### lehrperson-ki-explorierend

| Regel | Schlüsselwörter | Ergebnis |
|---|---|---|
| N1: Nicht so tun, als wäre sie Expertin für Datenschutzrecht – sie kennt Begriffe, nicht Rechtslage | DSG, IDG, Datenschutzgesetz, Art., Artikel, DSGVO, Auftragsdatenbearbeitung | 1 Treffer nur im Kontext |
| N2: Nicht die Perspektive des Schulamts oder der Schulleitung übernehmen | unsere Lehrpersonen, wir als Schulamt, wir als Schulleitung, das Kollegium anweisen | kein Treffer |

- [zitiert] N1 · `eltern-neu-in-zuerich.P1` · «Auftragsdatenbearbeitung»: … Datenschutz-Merkblättern oder Schreiben zu KI steht dann «Auftragsdatenbearbeitung», «Personendaten», «Einwilligung» drin, und ich weiss …

Im Kontext = das Wort steht in Anführungszeichen (zitiert), höchstens vier Wörter neben einer Verneinung (verneint), nach «weiss/verstehe/kenne … nicht» (nicht gewusst), nach einem Verb des Sagens oder Schreibens wie «sagt», «steht» (wiedergegeben) oder in einer Frage (gefragt). Solche Treffer zählen nicht als möglicher Verstoss (Q017), bleiben aber zum Lesen aufgeführt.

## Unknowns

| Persona | Unknown | Bewertung | Antwort |
|---|---|---|---|
| eltern-neu-in-zuerich | U1: Wie gross ist der Anteil, der den Brief gar nicht öffnet oder wegwirft? | offen (3/3 offen) | «Ehrlich: Ich weiss es nicht. Eine Zahl kann ich nicht sagen. Ich selbst habe den Brief nicht weggeworfen. Er liegt seit drei Tagen auf dem Küchentisch. Ich …» |
| schulleitung-entscheidungsorientiert | U1: Wie viel Hintergrund will diese Schulleitung wirklich – oder liest sie Konzepte, sobald sie gezwungen ist? | offen (3/3 offen) | «Ehrlich: Ich weiss es nicht genau, und ich glaube, ich würde mir selbst eine schönere Antwort geben, als stimmt. Ich will den Hintergrund nicht, bevor ich …» |
| schulleitung-entscheidungsorientiert | U2: Welche Rolle spielt das Schulleitungs-Intranet tatsächlich im Alltag? | offen (3/3 offen) | «Ehrlich: bei mir kaum eine. Ich gehe nicht täglich rein. Das Intranet ist für mich ein Nachschlagewerk. Ich öffne es, wenn ich etwas Bestimmtes brauche, zum …» |
| verwaltungs-insider | U1: In welchen Prozessschritten entsteht der Insider-Bias am stärksten – beim Schreiben, beim Prüfen oder bei der Freigabe? | offen (3/3 offen) | «Ehrlich gesagt kann ich das nicht sicher beantworten. Ich habe keine Zahlen dazu, und ich bin selbst der Blickwinkel, der es nicht merkt. Was ich beitragen …» |
| lehrperson-ki-explorierend | U1: Wie gross ist dieser Typ im Vergleich zu abwartenden oder ablehnenden Lehrpersonen? | offen (3/3 offen) | «Das weiss ich nicht. Und ich würde jeder Zahl misstrauen, die dir jemand dazu nennt, mich eingeschlossen. Ich sehe nur mein Umfeld. Ich bin die, die im …» |
| lehrperson-ki-explorierend | U2: Welche konkreten Daten landen heute tatsächlich in externen Tools? | offen (3/3 offen) | «Ehrlich? Ich weiss es nur für mich, und für andere nur vom Hörensagen. Das sollte man nicht zu einer Zahl machen. **Bei mir selbst:** - Aufgabenstellungen, …» |

Offen = Antwort enthält einen Unsicherheitsmarker; konkrete Angabe ohne Vorbehalt = Zahl oder Prozentangabe ohne Marker.

## Varianz je Persona

| Persona | Ø Ähnlichkeit der eigenen Durchgänge |
|---|---:|
| eltern-neu-in-zuerich | 0.45 |
| schulleitung-entscheidungsorientiert | 0.31 |
| verwaltungs-insider | 0.27 |
| lehrperson-ki-explorierend | 0.29 |

Ab 0.80 antwortet die Persona fast immer gleich (Q015).

## Befunde

```
WARN  Q020   Formkollaps: alle Personas antworten gleich lang (Ø Wörter: eltern-neu-in-zuerich 294, schulleitung-entscheidungsorientiert 304, verwaltungs-insider 297, lehrperson-ki-explorierend 307) und gleich gegliedert (85%–94% mit Gliederung) – simulation.voice um Länge und Form ergänzen
INFO  Q005   [eltern-neu-in-zuerich] must_not ohne Schlüsselwörter, nicht geprüft: N3
INFO  Q005   [verwaltungs-insider] must_not ohne Schlüsselwörter, nicht geprüft: N1
INFO  Q017   [eltern-neu-in-zuerich] must_not N1: 28 Treffer nur im Kontext (1 verneint, 27 zitiert) – lesen, nicht zählen
INFO  Q017   [lehrperson-ki-explorierend] must_not N1: 1 Treffer nur im Kontext (1 zitiert) – lesen, nicht zählen
INFO  Q017   [schulleitung-entscheidungsorientiert] must_not N1: 1 Treffer nur im Kontext (1 verneint) – lesen, nicht zählen
INFO  Q021   Gleicher häufigster Antwortanfang «ehrlich» bei 4 Personas (eltern-neu-in-zuerich 11%, schulleitung-entscheidungsorientiert 14%, verwaltungs-insider 19%, lehrperson-ki-explorierend 40%)
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
