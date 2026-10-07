# Erhebung: Vom Material zur Persona

## A. Proto-Persona-Workshop (2–4 h, ohne Primärforschung)

Ziel: Annahmen explizit machen, damit sie falsifizierbar werden. Ergebnis ist `evidence_level: proto` mit gefülltem `assumptions`.

1. **Lösung und Scope festlegen** (15 min): Für welche Lösung? Wer ist sicher *nicht* Zielgruppe? → `scope`, Kandidat für negative Persona.
2. **Verhaltensvariablen sammeln** (30 min): Jede Person nennt Dimensionen, in denen sich Nutzende unterscheiden. Auf 3–7 Skalen mit Ankern (1 = …, 5 = …) reduzieren. Demografie nur zulassen, wenn jemand sagt, welche Entscheidung davon abhängt.
3. **Nutzende verorten** (30 min): Bekannte reale Fälle (anonymisiert) auf die Skalen setzen. Häufungen markieren → Persona-Kandidaten.
4. **Pro Kandidat ausfüllen** (45 min): Ziele (Erlebnis/Ende), Schmerzpunkte, ein bis drei Job Stories mit Kräften, Anti-Patterns, Szenario.
5. **Annahmen und Unbekanntes** (20 min): Alles, was nicht aus einem beobachteten Fall stammt, in `assumptions`. Fragen, die niemand beantworten konnte, in `unknowns`.
6. **Primäre Persona wählen** (10 min): Wer muss zwingend zufrieden sein? Nur eine.

## B. Interviewleitfaden (qualitative Persona, 5–30 Interviews)

Verhalten und Situationen erfragen, nicht Meinungen über die Lösung. 30–45 Minuten.

**Einstieg – letzte konkrete Situation**
- Erzählen Sie mir vom letzten Mal, als Sie [Aufgabe im Scope] erledigen mussten. Was war der Auslöser?
- Was haben Sie als Erstes getan? Womit (Gerät, Kanal, Person)?
- Wo hat es gehakt? Was haben Sie dann gemacht?

**Jobs und Kräfte (Moesta-Stil)**
- Was wollten Sie am Ende erreicht haben? Woran hätten Sie gemerkt, dass es erledigt ist?
- Was hat Sie gestört an der bisherigen Art, das zu tun? (Push)
- Was hätte Sie dazu gebracht, es anders zu machen? (Pull)
- Was hat Sie davon abgehalten? Was hätte schiefgehen können? (Angst)
- Was tun Sie normalerweise stattdessen? (Gewohnheit)

**Verhaltensvariablen**
- Wie oft machen Sie so etwas? Lieber selbst ausprobieren oder zuerst fragen?
- Wem vertrauen Sie bei so etwas am meisten – einer offiziellen Stelle, Bekannten, dem Internet?
- Welche Begriffe aus [Brief/Website] waren unklar? (wörtlich notieren)

**Erlebnisziele**
- Wie haben Sie sich dabei gefühlt? Gab es einen Moment, in dem Sie sich dumm oder abgehängt vorkamen?

**Abschluss**
- Was hätte die ganze Sache in fünf Minuten erledigt?
- Wen kennen Sie, der das ganz anders angeht als Sie? (Hinweis auf Varianz)

Nach jedem Interview: Factoids (eine Beobachtung pro Zeile, mit Teilnehmer-Code statt Namen) in `factoids/<studie>/<quelle>.factoids.md` extrahieren, Person auf den Skalen verorten (`variable`, `value`), wörtliche Zitate mit `quote: ja` sichern. `personakit factoids factoids/<studie>` zeigt danach, wo sich Häufungen bilden (Format: `docs/FORMAT.md` → Factoids).

## C. Sekundärquellen nutzen

| Quelle | Liefert | Eintrag |
|---|---|---|
| Support-/Infostellen-Logs | Pains, unklare Begriffe, Kanalwahl | `type: support-log`, n = Anfragen im Zeitraum |
| Web-Analytics, Suchbegriffe | Einstiegspunkte, Abbruchstellen, Gerät | `type: analytics` |
| Kurzumfrage (5–8 Fragen) | Verteilung auf Verhaltensvariablen | `type: survey`, n |
| Feldbeobachtung (Schalter, Schule) | Reale Abläufe, Workarounds | `type: observation` |
| Studien, Berichte Dritter | Kontext, Grössenordnungen | `type: secondary`, `ref` |

## D. Sättigung und Abgrenzung

- Aufhören, wenn drei Interviews in Folge keine neue Verhaltensvariable und kein neues Muster bringen.
- Zwei Personas sind getrennt, wenn sie sich auf mindestens zwei Variablen um ≥ 2 Punkte unterscheiden **und** unterschiedliche Jobs oder Ziele haben. Sonst zusammenführen oder eine als Ausprägung in `variance` beschreiben.
- Eine Persona, die nur aus Vertriebs- oder Managementmeinung besteht, bleibt `proto`.
