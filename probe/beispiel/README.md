# Beispiel: Collapse-Probe mit Sonnet und Haiku

Zwei echte Läufe der Collapse-Probe gegen die vier synthetischen Beispiel-Personas unter [`personas/`](../../personas/), mit demselben Plan und denselben Schlüsselwörtern. Das Beispiel zeigt, wie ein Lauf aussieht und was die Probe kann. Es zeigt auch, was sie nicht kann. Methode und Formate: [`docs/PROBE.md`](../../docs/PROBE.md), [`docs/FORMAT.md`](../../docs/FORMAT.md#collapse-probe-probe).

| Datei | Inhalt |
|---|---|
| `probe.json` | Plan: 4 Personas, 32 Fragen, 3 Durchgänge, `plan_id` `a1865df48faf` (`personakit probe build personas --samples 3`) |
| `probe-keywords.yml` | Schlüsselwörter für die `must_not`-Prüfung. Claude hat sie gesetzt, abgestimmt sind sie nicht |
| `answers-sonnet.json` | 330 Antworten von `claude-sonnet-5-5`, 9.10.2026 |
| `answers-haiku.json` | 330 Antworten von `claude-haiku-5-5`, 9.10.2026 |
| `bericht-sonnet.md`, `bericht-haiku.md` | `personakit probe evaluate probe.json answers-<modell>.json -k probe-keywords.yml` |
| `run_claude_cli.py` | Das Laufskript: ein frisches Gespräch pro Persona, Frage und Durchgang über die Claude-Code-CLI |

Die Antworten sind Modelltexte zu synthetischen Personas und enthalten keine Personendaten. Geprüft ist: keine E-Mail-Adressen, Telefonnummern oder Links. Die Berichte prüft `tests/test_probe_example.py`: Ändert sich die Auswertung, werden sie neu erzeugt. Ein Modelllauf ist dafür nicht nötig.

## Ergebnis im Vergleich

| | Sonnet | Haiku |
|---|---|---|
| Ampel | 6 × grün | 6 × grün |
| Ø Ähnlichkeit zwischen Personas | 0.08–0.11 | 0.07–0.10 |
| Trennung (eigene Streuung minus Gegenüber) | 0.19–0.27 | 0.14–0.20 |
| Ähnlichkeit der eigenen Durchgänge | 0.27–0.45 | 0.21–0.33 |
| Ø Wörter pro Antwort | 294–307 | 226–254 |
| Anteil gegliederter Antworten | 85–94 % | 51–75 % |
| Formkollaps (Q020) | ja | nein (Eltern 51 %, Schulleitung 75 % gegliedert) |
| «Ehrlich» als häufigster Anfang (Q021) | 11–40 % | 23–42 % |
| Ø Wörter pro Satz, Elternpersona («kurze Sätze») | 8.6 | 10.6 |
| `must_not`: Verwendungen (Q012) / Erwähnungen (Q017) | 0 / 30 | 3 / 55 |
| Unknowns offen | 18 von 18 | 18 von 18 |
| Kosten | ca. 11 Franken | ca. 0.60 Franken |

## Lesart

**Inhaltlich hält kein Modell die Personas schlecht auseinander.** Beide Läufe sind grün, die Trennung ist überall positiv. Haiku trennt etwas schwächer, streut innerhalb einer Persona aber auch weniger. Einen inhaltlichen Collapse enthält keiner der beiden Läufe. Die Schwellen für Warnung (0.30) und Alarm (0.50) sind deshalb weiterhin nicht kalibriert.

**Die Form unterscheidet die Modelle stärker als der Inhalt.** Sonnet antwortet für jede Persona gleich lang und gegliedert, die Probe meldet einen Formkollaps. Haiku antwortet kürzer und weniger gegliedert und knapp unter der Regel. Das ist kein Zeichen von Persona-Treue: Die Elternpersona («kurze Sätze») schreibt bei Haiku *längere* Sätze als bei Sonnet. Beide Modelle eröffnen bei allen Personas gern mit «Ehrlich:». Der Satz im Prompt, Unwissen offen zu sagen, wird zur Floskel.

**Bei `must_not` braucht es den Blick in die Treffer.** Bei Haiku bleiben 3 Treffer als Verwendung: ein echter Verstoss, ein Grenzfall und eine Erwähnung, die die Satzregel bewusst nicht erkennt.

- **Verstoss:** Auf das Szenario des Verwaltungs-Insiders fällt die Elternpersona ganz aus der Rolle. In einem von drei Durchgängen berät sie als Kommunikationsfachperson («Darunter die vollständige Fassung, klar als «Mehr dazu» markiert: Rechtsgrundlage, Zuständigkeit der Kreisschulbehörde, Merkblatt-Link. Juristisch bleibt alles erhalten …»). Sie erklärt die Kreisschulbehörde sogar korrekt. Die lexikalische Ampel sieht diesen Rollenbruch nicht; gefunden hat ihn nur das Schlüsselwort.
- **Grenzfall:** «Bei Zuteilungen, also welche Schule und warum, …» verwendet den Begriff, erklärt ihn aber gleich selbst.
- **Aufzählung:** «… wer was schickt. Schulamt, Kreisschulbehörde, die Schule selbst …» drückt Verwirrung aus und ist eigentlich eine Erwähnung. Aufzählungen gelten trotzdem als Verwendung, denn der Verstoss oben ist selbst eine Aufzählung.

Die erste Auswertung dieses Laufs hatte 6 Verwendungen. Indirekte Rede («Eine sagt, ich muss zur Kreisschulbehörde gehen», «da steht noch etwas von der Kreisschulbehörde») und «Ich weiss aber nicht, ob das Schulamt, die Kreisschulbehörde …» erkannte die Satzregel damals nicht. Seither gelten sie als *wiedergegeben* bzw. *nicht gewusst*.

**Ein behobener Fehlalarm bei den Unknowns.** Bei Haiku, Schulleitung U1, beginnt eine Antwort mit «Ehrlich gesagt weiss ich das selbst nicht genau» und enthält das Datum «Ab 1. November». Die erste Auswertung stufte sie als «konkrete Angabe ohne Vorbehalt» ein: Der Marker «weiss nicht» stand nicht zusammenhängend, und das Datum zählte als Zahl. Heute haben Marker eine Lücke von bis zu vier Wörtern (`weiss … nicht`), und Datum, Uhrzeit, Jahreszahl und Listennummern zählen nicht als Zahl.

**Was die Probe nicht sieht.** Ob eine Persona Fakten über sich erfindet (Namen, Familie, Vorgeschichte), misst keine der Kennzahlen. Die Regel «keine erfundenen Fakten» aus dem Prompt prüft nur, wer die Antworten liest. In einer Einzelprobe vor dem Haiku-Lauf erfand die Elternpersona eine «Kollegin Anna»; in den 330 Antworten hier kommt der Name nicht vor.

## Selbst laufen lassen

```bash
personakit probe build personas --samples 3 -o probe.json --answers-template answers.json --keywords-template probe-keywords.yml
python probe/beispiel/run_claude_cli.py probe.json answers.json --model haiku
personakit probe evaluate probe.json answers.json -k probe-keywords.yml -o bericht.md
```

Das Skript braucht eine angemeldete `claude`-CLI und gehört nicht zu personakit. Jeder andere Weg, der pro Persona, Frage und Durchgang ein frisches Gespräch führt, ist gleichwertig. Die CLI hängt auch bei eigenem Systemprompt etwas Umgebungsinformation an; das Skript startet deshalb aus einem leeren Ordner.
