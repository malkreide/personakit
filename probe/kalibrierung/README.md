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
| 1 ohne Stimme (Sonnet, zur Kontrolle) | 0.32–0.39 | 0.09–0.12 | 0.09–0.13 | 0–12 % | – | 6 × grün |
| 2 nur Archetyp | 0.53–0.61 | 0.11–0.12 | 0.11–0.14 | 0–19 % | 6 × grün | 6 × gelb |
| 2 nur Archetyp (Sonnet, zur Kontrolle) | 0.48–0.63 | 0.12–0.15 | 0.12–0.16 | 4–42 % | – | 6 × gelb (mit 0.50: 5 × gelb, 1 × grün) |
| 3 identisch | 0.97–1.03 | 0.20–0.21 | 0.20–0.23 | 54–85 % | 3 × grün, 3 × gelb | 6 × rot |
| 3 identisch (Sonnet, zur Kontrolle) | 0.98–1.02 | 0.24–0.25 | 0.24–0.28 | 81–96 % | – | 6 × rot |

Die Werte für einen Durchgang umfassen alle drei Durchgänge je einzeln ausgewertet. Die Berichte liegen in `stufe-*/bericht-haiku.md`.

## Was daraus folgt

1. **Die alten Schwellen hätten nicht einmal den vollständigen Collapse erkannt.** Identische Prompts ergeben bei Antworten von rund 230 Wörtern nur eine Ähnlichkeit von 0.20. Die bisherige Zusatzregel «Trennung ≤ 0» kippte bei identischen Prompts zufällig nach beiden Seiten (Trennung −0.006 bis +0.005).
2. **Die Nähe trennt die Stufen sauber und ohne Überlappung.** Sie ist relativ zur eigenen Streuung jeder Persona und hängt deshalb weniger an Modell und Antwortlänge als die absolute Ähnlichkeit. Regel ab zwei Durchgängen, an Haiku gewählt: gelb ab 0.50, rot ab 0.85; nach der Gegenprobe mit Sonnet **gelb ab 0.45, rot ab 0.85** (siehe unten).
3. **Mit einem Durchgang bleibt nur die absolute Ähnlichkeit.** Sie trennt Stufe 3 von allen anderen, Stufe 2 aber nicht von Stufe 0. Neue Schwellen: **Warnung 0.15, Alarm 0.18** (statt 0.30 und 0.50). Der Bericht sagt in diesem Fall, dass nur ein vollständiger Collapse sichtbar ist (Q018).
4. **Stufe 1 bleibt grün, und das ist richtig gemessen.** Ohne Stimme und Simulationsregeln unterscheiden sich die Personas weiter über Kontext, Ziele und Jobs. Was verloren geht, ist Ton und Haltung. Das misst die Wortähnlichkeit nicht; die Form der Antworten zeigt es teilweise (bei Haiku meldet Stufe 1 einen Formkollaps, Stufe 0 nicht; bei Sonnet melden ihn beide).

## Gegenprobe mit Sonnet

Gewählt wurden die Schwellen an Haiku; danach liefen die Stufen 2 und 3 mit `claude-sonnet-5-5` (je 330 Antworten, 11.10.2026, rund 22 Franken) als Prüfung an einem zweiten Modell, ohne die Schwellen anzupassen. Nach dem Senken der Gelb-Schwelle lief auch Stufe 1 mit Sonnet (330 Antworten, 11.10.2026), um zu prüfen, ob «ohne Stimme» unter 0.45 bleibt.

- **Rot hält.** Identische Prompts ergeben auch bei Sonnet eine Nähe von 0.98–1.02; alle sechs Paare sind rot, mit drei Durchgängen und mit jedem einzelnen.
- **Gelb hält knapp.** Fünf von sechs Paaren der Stufe «nur Archetyp» sind gelb, eines bleibt grün: Eltern ↔ Schulleitung mit einer Nähe von 0.475. Dasselbe Paar ist auch bei Haiku das am wenigsten nahe (0.533). Die beiden Archetypen liegen inhaltlich am weitesten auseinander; mehr als das Etikett unterscheidet sie in dieser Stufe nicht. Stufe 2 ist deshalb keine harte Wahrheit wie Stufe 3, aber das grüne Paar zeigte, dass die Gelb-Schwelle von 0.50 an einem zweiten Modell nicht alle geschrumpften Personas erfasst.
- **Gelb deshalb ab 0.45.** Damit sind alle Paare der Stufe 2 mit beiden Modellen gelb (Abstand zur Schwelle bei Sonnet 0.025), vollständige Personas bleiben grün (höchstens 0.40). Auch 0.45 ist allerdings an denselben Daten gewählt, an denen die Schwelle jetzt geprüft wird; eine echte Prüfung bringt erst ein drittes Modell oder eine andere Domäne.
- **Stufe 1 bleibt grün, mit Abstand.** Ohne Stimme liegt Sonnet bei einer Nähe von 0.32–0.39: 0.06 unter der Gelb-Schwelle und deutlich unter dem am wenigsten nahen Paar der Stufe 2 (0.475). Knapp ist die Schwelle nur bei Haiku (bis 0.44). Bei Sonnet liegt Stufe 1 kaum über Stufe 0 (0.25–0.36): Ohne Stimme verlieren die Personas Ton und Haltung, aber kaum Inhalt. Die Wortähnlichkeit misst diesen Verlust nicht, und die Form zeigt ihn bei Sonnet auch nicht, weil schon die vollständigen Personas einen Formkollaps melden.
- **Absolut, mit einem Durchgang,** liegt Sonnet etwas höher als Haiku (Stufe 2 bis 0.16, Stufe 3 ab 0.24): Stufe 3 bleibt rot, in Stufe 2 wird in zwei von drei Durchgängen ein Paar gelb.

## Grenzen dieser Kalibrierung

- **Gewählt an Haiku, geprüft an Sonnet.** Die Schwellen liegen in der Lücke zwischen zwei Haiku-Stufen. Sonnet bestätigt Grün für vollständige Personas (0.25–0.36) und Rot für identische Prompts (0.98–1.02); bei «nur Archetyp» blieb mit 0.50 ein Paar von sechs grün, darum gilt jetzt 0.45 (siehe oben). Stufe 1 bleibt auch mit Sonnet grün (0.32–0.39).
- **Ein Modell, eine Domäne, Deutsch.** Andere Modelle, kürzere Antworten oder ein anderes Fachgebiet können die Werte verschieben. Das gilt vor allem für die absoluten Schwellen; die Nähe ist robuster, aber auch nicht modellfrei.
- **Die Lücke zwischen Stufe 1 und 2 ist schmal** (Haiku 0.44 gegen 0.53; Sonnet 0.39 gegen 0.48). Die Gelb-Schwelle 0.45 liegt bei Haiku nur 0.01 über Stufe 1: Ein Paar ohne Stimme kann gelb werden, ein Paar knapp darunter ist nicht sicher unverdächtig. Das ist gewollt: Gelb heisst prüfen, nicht verwerfen.
- **Stufe 3 ist ein künstlicher Extremfall.** Realer Collapse ist meist partiell: Personas, die sich nur noch im Etikett unterscheiden (Stufe 2), sind das realistischere Warnsignal. Gelb heisst deshalb: Antworten lesen.

## Neu erzeugen

```bash
python probe/kalibrierung/make_plans.py
python probe/beispiel/run_claude_cli.py probe/kalibrierung/stufe-2/probe.json answers.json --model haiku
personakit probe evaluate probe/kalibrierung/stufe-2/probe.json answers.json
```

`tests/test_probe_calibration.py` prüft die Stufenleiter: Stufe 0 und 1 grün, Stufe 2 gelb, Stufe 3 rot, und mit einem Durchgang nur Stufe 3 rot. Wer die Auswertung ändert und die Leiter bricht, braucht eine neue Kalibrierung, nicht eine neue Erwartung im Test.
