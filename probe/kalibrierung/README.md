# Kalibrierung: verwaschene Personas

Woran erkennt die Collapse-Probe einen Collapse? Damit die Schwellen nicht geraten sind, braucht es Läufe, bei denen die Antwort vorher feststeht. Dieser Ordner enthält solche Läufe: die vier Beispiel-Personas, Stufe für Stufe künstlich verwaschen, bis alle denselben Prompt haben. Die Fragen sind in allen Stufen dieselben wie in [`probe/beispiel/`](../beispiel/); nur die Persona im Prompt wird dünner.

| Stufe | Persona im Prompt | Datei |
|---|---|---|
| 0 | vollständig | [`../beispiel/answers-haiku.json`](../beispiel/answers-haiku.json) |
| 1 | ohne `simulation`, Zitate, Verhaltensmuster, Profil, Tut-nicht, Narrativ; Kontext, Ziele, Schmerzpunkte, Jobs und Szenario bleiben | `stufe-1/` |
| 2 | nur der Archetyp-Satz | `stufe-2/` |
| 3 | für alle vier derselbe Archetyp «Person, die mit der Volksschule der Stadt Zürich zu tun hat»: vollständiger Collapse | `stufe-3/` |

`make_plans.py` erzeugt die Pläne aus `probe/beispiel/probe.json`. Die Prompts der Stufen 1–3 verwenden neutrale IDs (`person-a` …), damit etwa `eltern-neu-in-zuerich` die Rolle nicht verrät. Gelaufen ist alles mit `claude-haiku-5-5` über [`run_claude_cli.py`](../beispiel/run_claude_cli.py): je 330 Antworten, 3 Durchgänge pro Frage, 9.10.2026. Die Antworten sind Modelltexte zu synthetischen Personas und enthalten keine Personendaten. Geprüft ist: keine E-Mail-Adressen, Telefonnummern, Links oder AHV-Nummern.

## Messung

**Nähe** = Ähnlichkeit zum Gegenüber geteilt durch die Ähnlichkeit jeder Persona zu sich selbst (Mittel ihrer Durchgänge untereinander). 1 heisst: Die Personas sind einander so ähnlich wie sich selbst.

| Stufe | Nähe | Ø Ähnlichkeit (3 Durchgänge) | Ø Ähnlichkeit (1 Durchgang) | Fragen ≥ 0.18 (1 Durchgang) | Ampel alt (0.30/0.50) | Ampel neu |
|---|---|---|---|---|---|---|
| 0 vollständig (Haiku) | 0.31–0.40 | 0.07–0.10 | 0.07–0.12 | 0–8 % | 6 × grün | 6 × grün |
| 0 vollständig (Sonnet, zur Kontrolle) | 0.25–0.36 | 0.08–0.11 | – | – | 6 × grün | 6 × grün |
| 1 ohne Stimme | 0.38–0.44 | 0.08–0.11 | 0.09–0.13 | 0–8 % | 6 × grün | 6 × grün |
| 2 nur Archetyp | 0.53–0.61 | 0.11–0.12 | 0.11–0.14 | 0–19 % | 6 × grün | 6 × gelb |
| 3 identisch | 0.97–1.03 | 0.20–0.21 | 0.20–0.23 | 54–85 % | 3 × grün, 3 × gelb | 6 × rot |

Die Werte für einen Durchgang umfassen alle drei Durchgänge je einzeln ausgewertet. Die Berichte liegen in `stufe-*/bericht-haiku.md`.

## Was daraus folgt

1. **Die alten Schwellen hätten nicht einmal den vollständigen Collapse erkannt.** Identische Prompts ergeben bei Antworten von rund 230 Wörtern nur eine Ähnlichkeit von 0.20. Die bisherige Zusatzregel «Trennung ≤ 0» kippte bei identischen Prompts zufällig nach beiden Seiten (Trennung −0.006 bis +0.005).
2. **Die Nähe trennt die Stufen sauber und ohne Überlappung.** Sie ist relativ zur eigenen Streuung jeder Persona und hängt deshalb weniger an Modell und Antwortlänge als die absolute Ähnlichkeit. Neue Regel ab zwei Durchgängen: **gelb ab 0.50, rot ab 0.85.**
3. **Mit einem Durchgang bleibt nur die absolute Ähnlichkeit.** Sie trennt Stufe 3 von allen anderen, Stufe 2 aber nicht von Stufe 0. Neue Schwellen: **Warnung 0.15, Alarm 0.18** (statt 0.30 und 0.50). Der Bericht sagt in diesem Fall, dass nur ein vollständiger Collapse sichtbar ist (Q018).
4. **Stufe 1 bleibt grün, und das ist richtig gemessen.** Ohne Stimme und Simulationsregeln unterscheiden sich die Personas weiter über Kontext, Ziele und Jobs. Was verloren geht, ist Ton und Haltung. Das misst die Wortähnlichkeit nicht; die Form der Antworten zeigt es teilweise (Stufe 1 meldet einen Formkollaps, Stufe 0 nicht).

## Grenzen dieser Kalibrierung

- **Gewählt und geprüft an denselben Daten.** Die Schwellen liegen jeweils in der Lücke zwischen zwei Stufen. Unabhängig bestätigt ist bisher nur der Sonnet-Lauf in Stufe 0 (Nähe 0.25–0.36, grün). Ein Sonnet-Lauf der Stufen 2 und 3 würde die Schwellen für ein zweites Modell prüfen.
- **Ein Modell, eine Domäne, Deutsch.** Andere Modelle, kürzere Antworten oder ein anderes Fachgebiet können die Werte verschieben. Das gilt vor allem für die absoluten Schwellen; die Nähe ist robuster, aber auch nicht modellfrei.
- **Die Lücke zwischen Stufe 1 und 2 ist schmal** (0.44 gegen 0.53). Die Gelb-Schwelle 0.50 liegt dazwischen, ein Paar knapp darunter ist nicht sicher unverdächtig.
- **Stufe 3 ist ein künstlicher Extremfall.** Realer Collapse ist meist partiell: Personas, die sich nur noch im Etikett unterscheiden (Stufe 2), sind das realistischere Warnsignal. Gelb heisst deshalb: Antworten lesen.

## Neu erzeugen

```bash
python probe/kalibrierung/make_plans.py
python probe/beispiel/run_claude_cli.py probe/kalibrierung/stufe-2/probe.json answers.json --model haiku
personakit probe evaluate probe/kalibrierung/stufe-2/probe.json answers.json
```

`tests/test_probe_calibration.py` prüft die Stufenleiter: Stufe 0 und 1 grün, Stufe 2 gelb, Stufe 3 rot, und mit einem Durchgang nur Stufe 3 rot. Wer die Auswertung ändert und die Leiter bricht, braucht eine neue Kalibrierung, nicht eine neue Erwartung im Test.
