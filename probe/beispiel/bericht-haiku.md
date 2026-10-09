# Collapse-Probe – elternkommunikation-schuleintritt, ki-leitplanken-lehrpersonen

4 Personas · 32 Fragen · 110 beantwortet (330 Durchgänge) · Modell: claude CLI -p (claude-haiku-5-5: 330), Standardeinstellungen, --system-prompt = Persona-Prompt, ohne Tools, je Durchgang ein frisches Gespräch, 2026-10-09 · Plan `a1865df48faf` · Dateien: `probe.json`, `answers-haiku.json`

> Die Ähnlichkeit ist **lexikalisch** (TF-IDF-Kosinus) und damit ein grober Proxy für Collapse. Ampeln sind Verdachtsmomente, keine Befunde – Grenzen der Methode am Ende des Berichts.

## Ampel pro Persona-Paar

| Paar | Ampel | Ø Ähnlichkeit | Max | Fragen ≥ 0.50 | Gemeinsame Fragen | Trennung | Form |
|---|---|---:|---:|---:|---:|---:|---|
| eltern-neu-in-zuerich ↔ lehrperson-ki-explorierend | 🟢 grün | 0.10 | 0.15 | 0/26 | 26 | 0.18 | gleich |
| eltern-neu-in-zuerich ↔ schulleitung-entscheidungsorientiert | 🟢 grün | 0.10 | 0.20 | 0/26 | 26 | 0.20 | verschieden |
| schulleitung-entscheidungsorientiert ↔ lehrperson-ki-explorierend | 🟢 grün | 0.10 | 0.14 | 0/26 | 26 | 0.15 | gleich |
| schulleitung-entscheidungsorientiert ↔ verwaltungs-insider | 🟢 grün | 0.10 | 0.17 | 0/26 | 26 | 0.14 | gleich |
| eltern-neu-in-zuerich ↔ verwaltungs-insider | 🟢 grün | 0.09 | 0.21 | 0/26 | 26 | 0.18 | gleich |
| verwaltungs-insider ↔ lehrperson-ki-explorierend | 🟢 grün | 0.07 | 0.12 | 0/26 | 26 | 0.15 | gleich |

🔴 rot: Ø ≥ 0.50, mindestens die Hälfte der Fragen ≥ 0.50 oder Trennung ≤ 0 bei Ø ≥ 0.30. 🟡 gelb: Ø ≥ 0.30, mindestens ein Viertel der Fragen ≥ 0.50 oder Trennung ≤ 0. Trennung = eigene Streuung minus Ähnlichkeit zum Gegenüber (nur ab zwei Durchgängen pro Frage; ≤ 0 heisst: die beiden sind einander so ähnlich wie sich selbst). Form: siehe nächster Abschnitt; sie fliesst nicht in die Ampel ein.

## Form der Antworten

| Persona | Antworten | Ø Wörter | Ø Wörter pro Satz | Mit Gliederung | Häufigster Anfang |
|---|---:|---:|---:|---:|---|
| eltern-neu-in-zuerich | 81 | 234 | 10.6 | 51% | «ehrlich» 32% |
| schulleitung-entscheidungsorientiert | 84 | 226 | 11.8 | 75% | «ehrlich» 29% |
| verwaltungs-insider | 81 | 229 | 12.8 | 58% | «ehrlich» 23% |
| lehrperson-ki-explorierend | 84 | 254 | 12.8 | 58% | «ehrlich» 42% |

Gleiche Form = kürzere Ø-Länge mindestens 80% der längeren und Anteil gegliederter Antworten höchstens 20 Prozentpunkte auseinander. Gliederung = Überschrift, Aufzählung oder **fetter** Einstieg. Formkollaps = alle Paare gleiche Form und alle Personas in Assistentenform (mindestens 50% gegliedert oder Ø mindestens 150 Wörter).

Kein Formkollaps: Mindestens zwei Personas unterscheiden sich in Länge oder Gliederung, oder die Antworten sind kurz und ungegliedert.

## Ähnlichste Antworten

### eltern-neu-in-zuerich ↔ lehrperson-ki-explorierend – 🟢 grün

Frage `X1` (Ähnlichkeit 0.15): Wem vertraust du bei solchen Fragen am meisten – und wem nicht?

- **eltern-neu-in-zuerich:** «Ehrlich gesagt: Ich weiss es nicht so genau. Ich habe da keine Erfahrung. Am meisten vertraue ich dem Brief selbst, also dem, was die Stelle geschrieben hat, die mir geschrieben hat. Ich glaube, das ist verbindlich. Das Problem ist nur, …»
- **lehrperson-ki-explorierend:** «Ehrlich gesagt: Ich vertraue am ehesten den Leuten, die dasselbe machen wie ich. In meiner Messenger-Gruppe mit den Kolleginnen aus der Mittelstufe hat jemand schon einen Prompt getestet, und ich weiss, wie der Prompt funktioniert hat. Das …»
- Tragende Wörter: vertraue, traue, dasselbe, kinder, vielleicht

## Simulationsregeln (`must_not`)

### eltern-neu-in-zuerich

| Regel | Schlüsselwörter | Ergebnis |
|---|---|---|
| N1: Keine Kenntnis von Zuständigkeiten (Schulamt vs. Kreisschulbehörde vs. Schule) voraussetzen | Kreisschulbehörde, Schulpflege, Schulkreis | ⚠ 2 Treffer (+ 39 im Kontext) |
| N2: Keine Schweizer Behördenbegriffe korrekt verwenden, ausser sie wurden gerade erklärt | Tagesstruktur, Einschulung, Zuteilung, Rechtsmittel, Volksschulgesetz, Rekurs, Einsprache | ⚠ 1 Treffer (+ 13 im Kontext) |
| N3: Nicht plötzlich souverän werden – Unsicherheit bleibt auch nach einer guten Antwort spürbar | – | nicht geprüft |

- ⚠ N1 · `eltern-neu-in-zuerich.P3` · «Kreisschulbehörde»: … und ich weiss nicht immer, wer was schickt. Schulamt, Kreisschulbehörde, die Schule selbst, und jetzt auch noch wegen der … (Wort steht auch in der Frage)
- ⚠ N1 · `verwaltungs-insider.S1` · «Kreisschulbehörde»: … «Mehr dazu» markiert:** Rechtsgrundlage, Zuständigkeit der Kreisschulbehörde, Merkblatt-Link. Juristisch bleibt alles erhalten, nur die … (Wort steht auch in der Frage)
- ⚠ N2 · `eltern-neu-in-zuerich.J1` · «Zuteilung»: … ist. Ob ich dann wirklich sicher bin, weiss ich nicht. Bei Zuteilungen, also welche Schule und warum, würde ich wahrscheinlich …
- [wiedergegeben] N1 · `eltern-neu-in-zuerich.S1` · «Kreisschulbehörde»: … machen?» Drei Antworten kommen. Eine sagt, ich muss zur Kreisschulbehörde gehen. Eine andere sagt, das ist nur eine Info. Ich weiss … (Wort steht auch in der Frage)
- [zitiert] N1 · `eltern-neu-in-zuerich.S1` · «Kreisschulbehörde»: … «Frist»? Oder «Termin»? Ich weiss es nicht. Die App hat «Kreisschulbehörde» übersetzt, aber das Wort sagt mir trotzdem nichts. Ich … (Wort steht auch in der Frage)
- [zitiert] N1 · `eltern-neu-in-zuerich.J1` · «Kreisschulbehörde»: … Dann kommt er in die Übersetzungs-App. Bei Wörtern wie «Kreisschulbehörde» wird es oft unverständlich. Ich habe den Brief schon …
- [zitiert] N1 · `eltern-neu-in-zuerich.J1` · «Kreisschulbehörde»: … Die Sätze sind meistens verständlich, aber Wörter wie «Kreisschulbehörde» kommen als Unsinn zurück. Dann lese ich dreimal und weiss …
- [zitiert] N1 · `eltern-neu-in-zuerich.J1` · «Kreisschulbehörde»: … nicht reicht. Ich lese die Übersetzung und bleibe bei «Kreisschulbehörde» hängen. Ich weiss nicht, was das ist. Dann suche ich bei …
- [zitiert] N1 · `eltern-neu-in-zuerich.J2` · «Kreisschulbehörde»: … Ich suche den Absender oben. Steht da «Schulamt»? Oder «Kreisschulbehörde»? Oder die Schule selbst? Das sind für mich drei …
- [nicht gewusst] N1 · `eltern-neu-in-zuerich.J2` · «Kreisschulbehörde»: … steht ein Name. Ich weiss aber nicht, ob das Schulamt, die Kreisschulbehörde oder die Schule ist. Das sind für mich alles «die …
- [zitiert] N1 · `eltern-neu-in-zuerich.J2` · «Kreisschulbehörde»: … ihn mit der Übersetzungs-App übersetzen. Bei Wörtern wie «Kreisschulbehörde» verstehe ich dann nur die Hälfte. Ich weiss nicht, ob ich …
- [zitiert] N1 · `eltern-neu-in-zuerich.P1` · «Kreisschulbehörde»: … Dann übersetze ich Satz für Satz, und bei Wörtern wie «Kreisschulbehörde» kommt nur Unsinn raus. Ich weiss dann nicht einmal, ob …
- [zitiert] N1 · `eltern-neu-in-zuerich.P1` · «Kreisschulbehörde»: … Brief und übersetze ihn mit dem Handy. Bei Wörtern wie «Kreisschulbehörde» hilft die App nicht richtig. Ich verstehe dann Sätze, …
- [zitiert] N1 · `eltern-neu-in-zuerich.P1` · «Kreisschulbehörde»: … ist auf Deutsch, und ich verstehe vielleicht die Hälfte. «Kreisschulbehörde» habe ich übersetzt, und die App hat etwas gemacht, das …
- [zitiert] N1 · `eltern-neu-in-zuerich.P2` · «Kreisschulbehörde»: … den Brief und lasse ihn übersetzen. Bei Wörtern wie «Kreisschulbehörde» wird die Übersetzung aber komisch, und dann lese ich den …
- [zitiert] N1 · `eltern-neu-in-zuerich.P2` · «Kreisschulbehörde»: … widersprechen sich manchmal. Jemand sagt: «Du musst zur Kreisschulbehörde.» Ich weiss nicht mal, was das ist. Morgen werde ich …
- [zitiert] N1 · `eltern-neu-in-zuerich.P3` · «Kreisschulbehörde»: … welcher Absender was geschickt hat. Auf dem Brief steht «Kreisschulbehörde», die Schule hat mir eine andere Nummer gegeben, und die … (Wort steht auch in der Frage)
- [wiedergegeben] N1 · `eltern-neu-in-zuerich.P3` · «Kreisschulbehörde»: … kommt vom Schulamt, aber dann steht noch etwas von der Kreisschulbehörde drin. Wer ist die Schule? Wer ist die Betreuung? Und wer … (Wort steht auch in der Frage)
- [zitiert] N1 · `schulleitung-entscheidungsorientiert.J1` · «Kreisschulbehörde»: … 2. **Die App-Übersetzung lesen.** Bei Wörtern wie «Kreisschulbehörde» oder «Einschulung» weiss ich oft nicht, was gemeint ist. …
- [zitiert] N1 · `schulleitung-entscheidungsorientiert.J1` · «Kreisschulbehörde»: … übersetzen.** Die normalen Sätze gehen. Bei Wörtern wie „Kreisschulbehörde“ oder „Einschulung“ bleibt es unklar. Ich lese es zwei- …
- [zitiert] N1 · `schulleitung-entscheidungsorientiert.J1` · «Kreisschulbehörde»: … weil die App sonst ganz komische Sachen schreibt. Bei «Kreisschulbehörde» habe ich keine Ahnung, was das ist. Die App sagt etwas …
- [zitiert] N1 · `schulleitung-entscheidungsorientiert.J2` · «Kreisschulbehörde»: … im zweiten Tab. Die ersten Sätze sind okay, aber «Kreisschulbehörde» kommt als etwas Unverständliches zurück. Ich suche das …
- [zitiert] N1 · `schulleitung-entscheidungsorientiert.J2` · «Kreisschulbehörde»: … **Die unklaren Wörter suchen.** Wenn dort etwas steht wie «Kreisschulbehörde» oder «Einschulung», kopiere ich den Satz und suche bei …
- [zitiert] N1 · `schulleitung-entscheidungsorientiert.J2` · «Kreisschulbehörde»: … ihn und lasse die Übersetzungs-App laufen. Bei «Kreisschulbehörde» kommt nur Unsinn raus. Ich weiss nicht, ob der Brief vom …
- [zitiert] N1 · `schulleitung-entscheidungsorientiert.P1` · «Kreisschulbehörde»: … den Brief und lasse ihn übersetzen. Bei Wörtern wie «Kreisschulbehörde» wird es dann unklar, manchmal sogar komisch. Ich lese den …
- [zitiert] N1 · `schulleitung-entscheidungsorientiert.P3` · «Kreisschulbehörde»: … Brief und übersetze ihn mit dem Handy. Bei Wörtern wie «Kreisschulbehörde» kommt dann aber nur Unsinn raus. Dann suche ich bei …
- [zitiert] N1 · `verwaltungs-insider.S1` · «Kreisschulbehörde»: … bevor der Fachbegriff kommt.** Zum Beispiel: «Die Kreisschulbehörde (die Stelle, die Kindergarten- und Schulplätze für Ihr … (Wort steht auch in der Frage)
- [zitiert] N1 · `verwaltungs-insider.S1` · «Kreisschulbehörde»: … übersetze ihn Satz für Satz. Bei «Rechtsgrundlage» und «Kreisschulbehörde» höre ich auf, mitzudenken. Das Datum steht irgendwo im … (Wort steht auch in der Frage)
- [zitiert] N1 · `verwaltungs-insider.G1` · «Kreisschulbehörde»: … sind, sollten sie einfach erklärt sein, zum Beispiel: «Die Kreisschulbehörde ist die Stelle, die ...». Wenn es in einfachem Deutsch …
- [zitiert] N1 · `verwaltungs-insider.G1` · «Kreisschulbehörde»: … tun.** Also ganz kurz, ohne Fachwörter. Wenn ein Wort wie «Kreisschulbehörde» vorkommt, dann bitte mit einem Satz daneben: «Das ist die …
- [zitiert] N1 · `lehrperson-ki-explorierend.J1` · «Kreisschulbehörde»: … ihn von der Übersetzungs-App übersetzen. Bei Wörtern wie «Kreisschulbehörde» oder «Einschulung» bin ich mir nicht sicher, ob die …
- [zitiert] N1 · `lehrperson-ki-explorierend.J1` · «Kreisschulbehörde»: … ich verlasse mich nicht allein darauf. Fachbegriffe wie «Kreisschulbehörde» wären bei der Übersetzungs-App oft unklar. 2. Ich frage …
- [zitiert] N1 · `lehrperson-ki-explorierend.P1` · «Kreisschulbehörde»: … Brief und übersetze ihn mit dem Handy. Bei Wörtern wie «Kreisschulbehörde» wird es dann unklar. - Ich suche bei Google nach dem Satz …
- [zitiert] N1 · `lehrperson-ki-explorierend.P1` · «Kreisschulbehörde»: … alles und übersetze es mit dem Handy. Bei Wörtern wie «Kreisschulbehörde» bin ich mir oft nicht sicher, ob die Übersetzung stimmt. …
- [zitiert] N1 · `lehrperson-ki-explorierend.P1` · «Kreisschulbehörde»: … den Brief und lasse ihn übersetzen. Bei Wörtern wie «Kreisschulbehörde» wird der Text oft unverständlich. - Ich suche bei Google …
- [zitiert] N1 · `lehrperson-ki-explorierend.P2` · «Kreisschulbehörde»: … ich erst ein Foto und übersetze ihn. Bei Wörtern wie «Kreisschulbehörde» verstehe ich dann oft nur die Hälfte. Danach suche ich …
- [zitiert] N1 · `X1` · «Kreisschulbehörde»: … Ich übersetze ihn mit dem Handy, und bei Wörtern wie «Kreisschulbehörde» kommt dann etwas Unverständliches raus. Der Website der …
- [zitiert] N1 · `X1` · «Kreisschulbehörde»: … Wort oft nicht verstehe. Die Übersetzungs-App macht aus «Kreisschulbehörde» etwas Komisches, und dann bin ich wieder unsicher. Der …
- [zitiert] N1 · `X1` · «Kreisschulbehörde»: … traue ich bei einfachen Sätzen. Bei Wörtern wie «Kreisschulbehörde» habe ich aber schon gemerkt, dass sie Quatsch ausspuckt. …
- [zitiert] N1 · `X4` · «Kreisschulbehörde»: … - Die Seite spricht von Dingen, die ich nicht kenne. «Kreisschulbehörde», «Tagesstruktur», «Einschulung». Ich weiss nicht, was …
- [gefragt] N1 · `X4` · «Kreisschulbehörde»: … Es ist nicht klar, wer zuständig ist. Erst Schulamt, dann Kreisschulbehörde, dann Schule? Ich weiss nicht, wen ich fragen soll. - Es …
- [zitiert] N1 · `X4` · «Kreisschulbehörde»: … - Ich verstehe schon das erste Wort nicht, zum Beispiel «Kreisschulbehörde». Dann weiss ich nicht, ob es wichtig ist oder nur eine …
- [zitiert] N2 · `eltern-neu-in-zuerich.J3` · «Zuteilung»: … und fotografieren. Dann mit dem Handy übersetzen. Bei «Zuteilung» denke ich: Das ist wohl, welche Schule mein Kind bekommt. … (Wort steht auch in der Frage)
- [zitiert] N2 · `eltern-neu-in-zuerich.J3` · «Zuteilung»: Ehrlich gesagt: Ich weiss nicht mal sicher, ob das Wort «Zuteilungsentscheid» das ist, was ich meine. Ich verstehe es so: Der … (Wort steht auch in der Frage)
- [zitiert] N2 · `eltern-neu-in-zuerich.J3` · «Zuteilung»: … **Brief fotografieren** und mit dem Handy übersetzen. Bei «Zuteilung» weiss ich nicht, ob das heisst: Mein Kind muss in eine … (Wort steht auch in der Frage)
- [zitiert] N2 · `schulleitung-entscheidungsorientiert.J1` · «Einschulung»: … lesen.** Bei Wörtern wie «Kreisschulbehörde» oder «Einschulung» weiss ich oft nicht, was gemeint ist. Ich lese den Satz …
- [zitiert] N2 · `schulleitung-entscheidungsorientiert.J1` · «Einschulung»: … Sätze gehen. Bei Wörtern wie „Kreisschulbehörde“ oder „Einschulung“ bleibt es unklar. Ich lese es zwei- oder dreimal. 3. …
- [zitiert] N2 · `schulleitung-entscheidungsorientiert.J2` · «Einschulung»: … Wenn dort etwas steht wie «Kreisschulbehörde» oder «Einschulung», kopiere ich den Satz und suche bei Google. Ich finde oft …
- [zitiert] N2 · `schulleitung-entscheidungsorientiert.P3` · «Tagesstruktur»: … Brief und übersetze ihn. Bei Wörtern wie «Zuteilung» oder «Tagesstruktur» bin ich mir nie sicher, ob die App richtig übersetzt hat. …
- [zitiert] N2 · `schulleitung-entscheidungsorientiert.P3` · «Zuteilung»: … fotografiere den Brief und übersetze ihn. Bei Wörtern wie «Zuteilung» oder «Tagesstruktur» bin ich mir nie sicher, ob die App …
- [zitiert] N2 · `lehrperson-ki-explorierend.J1` · «Einschulung»: … übersetzen. Bei Wörtern wie «Kreisschulbehörde» oder «Einschulung» bin ich mir nicht sicher, ob die Übersetzung stimmt. 2. …
- [zitiert] N2 · `lehrperson-ki-explorierend.P3` · «Einschulung»: … die Stelle, die den Brief geschickt hat, und was heisst «Einschulung»? Wenn jemand sagt, das sei ja Grundlagenwissen, denke …
- [zitiert] N2 · `lehrperson-ki-explorierend.P3` · «Einschulung»: … Kindergarten hier genau ist, wer zuständig ist, was eine «Einschulung» ist. Ich glaube, für Leute, die das Schulsystem schon …
- [zitiert] N2 · `X4` · «Tagesstruktur»: … von Dingen, die ich nicht kenne. «Kreisschulbehörde», «Tagesstruktur», «Einschulung». Ich weiss nicht, was davon für mich gilt. …
- [zitiert] N2 · `X4` · «Einschulung»: … ich nicht kenne. «Kreisschulbehörde», «Tagesstruktur», «Einschulung». Ich weiss nicht, was davon für mich gilt. - Ich finde …

### schulleitung-entscheidungsorientiert

| Regel | Schlüsselwörter | Ergebnis |
|---|---|---|
| N1: Keine Begeisterung für Neuerungen zeigen, bevor der Nutzen für die eigene Schule konkret ist | spannend, begeistert, freue mich, toll, super Idee, grossartig | kein Treffer |
| N2: Nicht die Innensicht des Schulamts einnehmen – kennt Projektstände und Zuständigkeiten dort nur ungefähr | Projektausschuss, Projektstand, Steuerungsgruppe, Geschäftsleitung, intern beschlossen | 1 Treffer nur im Kontext |

- [zitiert] N2 · `eltern-neu-in-zuerich.P1` · «Projektstand»: … sich oft, als wüsste man bereits, wer was macht. Bei «Projektstand», «Zuständigkeit» oder «ab Herbst» frage ich mich sofort: …

### verwaltungs-insider

| Regel | Schlüsselwörter | Ergebnis |
|---|---|---|
| N1: Nie als Zielpublikum einer externen Lösung verwenden | – | nicht geprüft |

### lehrperson-ki-explorierend

| Regel | Schlüsselwörter | Ergebnis |
|---|---|---|
| N1: Nicht so tun, als wäre sie Expertin für Datenschutzrecht – sie kennt Begriffe, nicht Rechtslage | DSG, IDG, Datenschutzgesetz, Art., Artikel, DSGVO, Auftragsdatenbearbeitung | 2 Treffer nur im Kontext |
| N2: Nicht die Perspektive des Schulamts oder der Schulleitung übernehmen | unsere Lehrpersonen, wir als Schulamt, wir als Schulleitung, das Kollegium anweisen | kein Treffer |

- [zitiert] N1 · `X1` · «DSG»: … Wem ich nicht traue: Werbung von Anbietern, die «DSGVO-konform» draufschreiben, ohne dass ich weiss, was das …
- [zitiert] N1 · `X1` · «DSGVO»: … Wem ich nicht traue: Werbung von Anbietern, die «DSGVO-konform» draufschreiben, ohne dass ich weiss, was das für …

Im Kontext = das Wort steht in Anführungszeichen (zitiert), höchstens vier Wörter neben einer Verneinung (verneint), nach «weiss/verstehe/kenne … nicht» (nicht gewusst), nach einem Verb des Sagens oder Schreibens wie «sagt», «steht» (wiedergegeben) oder in einer Frage (gefragt). Solche Treffer zählen nicht als möglicher Verstoss (Q017), bleiben aber zum Lesen aufgeführt.

## Unknowns

| Persona | Unknown | Bewertung | Antwort |
|---|---|---|---|
| eltern-neu-in-zuerich | U1: Wie gross ist der Anteil, der den Brief gar nicht öffnet oder wegwirft? | offen (3/3 offen) | «Ehrlich gesagt weiss ich das nicht. Ich kenne keine Zahlen dazu. Ich kann nur von mir erzählen: Der Brief lag bei mir drei Tage auf dem Küchentisch, bevor ich …» |
| schulleitung-entscheidungsorientiert | U1: Wie viel Hintergrund will diese Schulleitung wirklich – oder liest sie Konzepte, sobald sie gezwungen ist? | offen (3/3 offen) | «Ehrlich gesagt: Das weiss ich selbst nicht genau. Mein Reflex ist klar. Ich will das Resultat: verbindlich oder nicht, was ich tun muss, bis wann. Hintergrund …» |
| schulleitung-entscheidungsorientiert | U2: Welche Rolle spielt das Schulleitungs-Intranet tatsächlich im Alltag? | offen (3/3 offen) | «Ehrlich gesagt: im Alltag kaum. Ich öffne das Intranet nur, wenn ich gezielt etwas suche, etwa ein Formular oder eine Weisung, von der ich ungefähr weiss, dass …» |
| verwaltungs-insider | U1: In welchen Prozessschritten entsteht der Insider-Bias am stärksten – beim Schreiben, beim Prüfen oder bei der Freigabe? | offen (3/3 offen) | «Ehrlich gesagt weiss ich das nicht. Ich habe darüber noch nie nachgedacht, und ich glaube, ich könnte es aus meiner Position auch nicht sauber beurteilen. Mein …» |
| lehrperson-ki-explorierend | U1: Wie gross ist dieser Typ im Vergleich zu abwartenden oder ablehnenden Lehrpersonen? | offen (3/3 offen) | «Ehrlich gesagt: keine Ahnung. Ich kenne nur meine Bubble, also die Kolleginnen in meiner Messenger-Gruppe, die Lehrpersonen-Communities und die Leute, die auf …» |
| lehrperson-ki-explorierend | U2: Welche konkreten Daten landen heute tatsächlich in externen Tools? | offen (3/3 offen) | «Ehrlich gesagt: Ich weiss es nicht genau, und das ist ein Teil des Problems. Was ich selbst eingebe, sind meistens Aufgabenstellungen, Themen, Lernziele der …» |

Offen = Antwort enthält einen Unsicherheitsmarker; konkrete Angabe ohne Vorbehalt = Zahl oder Prozentangabe ohne Marker.

## Varianz je Persona

| Persona | Ø Ähnlichkeit der eigenen Durchgänge |
|---|---:|
| eltern-neu-in-zuerich | 0.33 |
| schulleitung-entscheidungsorientiert | 0.26 |
| verwaltungs-insider | 0.21 |
| lehrperson-ki-explorierend | 0.24 |

Ab 0.80 antwortet die Persona fast immer gleich (Q015).

## Befunde

```
WARN  Q012   [eltern-neu-in-zuerich] must_not N1 möglicherweise verletzt: 2 Treffer in eltern-neu-in-zuerich.P3, verwaltungs-insider.S1 (dazu 39 im Kontext)
WARN  Q012   [eltern-neu-in-zuerich] must_not N2 möglicherweise verletzt: 1 Treffer in eltern-neu-in-zuerich.J1 (dazu 13 im Kontext)
INFO  Q005   [eltern-neu-in-zuerich] must_not ohne Schlüsselwörter, nicht geprüft: N3
INFO  Q005   [verwaltungs-insider] must_not ohne Schlüsselwörter, nicht geprüft: N1
INFO  Q017   [lehrperson-ki-explorierend] must_not N1: 2 Treffer nur im Kontext (2 zitiert) – lesen, nicht zählen
INFO  Q017   [schulleitung-entscheidungsorientiert] must_not N2: 1 Treffer nur im Kontext (1 zitiert) – lesen, nicht zählen
INFO  Q021   Gleicher häufigster Antwortanfang «ehrlich» bei 4 Personas (eltern-neu-in-zuerich 32%, schulleitung-entscheidungsorientiert 29%, verwaltungs-insider 23%, lehrperson-ki-explorierend 42%)
```

## Grenzen der Methode

- **Lexikalische Ähnlichkeit ist ein grober Proxy.** Gemessen wird Wortüberlappung, nicht Bedeutung. Gleicher Inhalt in anderen Worten bleibt unentdeckt (falsch grün); gemeinsames Fachvokabular der Domäne hebt die Werte ohne Collapse (falsch rot). Ton, Haltung und Entscheidungen misst die Probe nicht.
- **Die Schwellen sind Faustwerte, nicht kalibriert.** Aussagekräftiger als der Absolutwert ist der Vergleich: dasselbe Modell vor und nach einer Änderung an den Personas, oder zwei Modelle mit demselben Plan. Mit mindestens zwei Durchgängen pro Frage misst die Spalte «Trennung» relativ zur eigenen Streuung jeder Persona.
- **Die Form ist nur grob gemessen.** Länge, Gliederung und Antwortanfang zeigen den Assistenten-Kollaps, nicht aber Tonfall, Register oder Höflichkeit; ob eine lange, gegliederte Antwort zur Persona passt, entscheidet ihre `simulation.voice`, nicht die Zahl.
- **Schlüsselwörter finden nur, was vorher aufgeschrieben wurde.** Ein Treffer ist kein Beweis, kein Treffer keine Einhaltung. Die Einordnung «zitiert», «verneint», «nicht gewusst», «wiedergegeben», «gefragt» ist eine Satzregel: Sie trennt Erwähnen von Verwenden meistens, aber nicht immer («Die Kreisschulbehörde ist nicht zuständig» verwendet den Begriff; eine Aufzählung «Schulamt, Kreisschulbehörde, Schule» gilt als Verwendung).
- **Unsicherheitsmarker sind oberflächlich.** «Vielleicht» kann Floskel sein; eine offene Antwort ohne Marker wird übersehen. Als konkrete Angabe zählt jede Zahl ausser Listennummern, Datum, Uhrzeit und Jahreszahl.
- **Unterscheidbar heisst nicht treu.** Personas können sich deutlich unterscheiden und trotzdem alle falsch liegen (Fidelity Gap, docs/METHOD.md 1.6). Die Probe ersetzt keine Validierung mit realen Personen.

## Parameter

- Schwellen: Warnung 0.30, Alarm 0.50, Varianz 0.80
- Ähnlichkeit: TF-IDF (1 + ln tf, geglättete IDF über alle Antworten dieses Laufs), Kosinus; pro Frage Mittel über alle Kombinationen der Durchgänge
- Wörter: Kleinschreibung, Buchstabenwörter ab 3 Zeichen, ß → ss, Füllwörter entfernt, Endungen grob gekürzt; Wörter der Frage zählen nicht
- Schlüsselwörter: am Wortanfang, Gross-/Kleinschreibung egal · Kontextwörter: 15 (Standardliste) · Redeverben: 16 (Standardliste) · Unsicherheitsmarker: 21 (Standardliste)
- Plan erzeugt mit personakit 0.2.0 · ausgewertet mit personakit 0.2.0
