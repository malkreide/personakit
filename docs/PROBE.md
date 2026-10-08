# Entwurfsnotiz: Collapse-Probe (P8)

Stand 2026-10-08 · Grundlage: `docs/METHOD.md` 1.6 (Persona Collapse, Fidelity Gap)

**Empfehlung in einem Satz:** personakit erzeugt die Prüffragen und wertet die Antworten aus, das Modell bleibt draussen. `probe build` schreibt einen Plan (Prompts + Fragen), den man gegen ein beliebiges Modell laufen lässt; `probe evaluate` misst mit der Standardbibliothek, ob die Antworten verschiedener Personas auf dieselbe Frage auseinanderliegen, und sagt im Bericht, was diese Messung nicht kann.

## 1. Ablauf

```
personakit probe build personas/<set> -o probe.json [--answers-template answers.json] [--keywords-template probe-keywords.yml]
   → Modell meiner Wahl: pro Persona × Frage × Durchgang ein frisches Gespräch
personakit probe evaluate probe.json answers.json [--keywords probe-keywords.yml] [-o bericht.md]
```

Kein Netzwerk, kein Modell-SDK, keine Abhängigkeit über `ruamel.yaml` und `jsonschema` hinaus. Wer den Plan ausführt, entscheidet über Modell, Temperatur und Datenschutz.

## 2. Der Plan (`probe.json`)

```json
{
  "personakit_probe": "1.0",
  "generator": "personakit 0.2.0",
  "plan_id": "3f9a1c0b7e21",
  "samples": 1,
  "sets": ["elternkommunikation-schuleintritt"],
  "instructions": "Pro Persona, Frage und Durchgang ein neues Gespräch …",
  "personas": [
    {"id": "eltern-neu-in-zuerich", "version": "1.1.0", "archetype": "…", "evidence_level": "qualitative",
     "prompt": "<persona … mode=\"simulate\"> … </persona>",
     "must_not": [{"id": "N1", "rule": "…"}], "unknowns": [{"id": "U1", "text": "…"}]}
  ],
  "questions": [
    {"id": "eltern-neu-in-zuerich.J1", "origin": "eltern-neu-in-zuerich", "kind": "job", "ref": "J1",
     "text": "Die Situation: «Wenn ich einen Brief vom Schulamt erhalte …». Was tust du dann …?",
     "ask": ["eltern-neu-in-zuerich", "schulleitung-entscheidungsorientiert", "verwaltungs-insider"]}
  ]
}
```

- **Fragen pro Persona: 6–10** (`--questions`, Default 8), deterministisch in dieser Reihenfolge, bis die Zahl erreicht ist: Szenario (`S1`), Jobs (`J…`, höchstens drei), erstes Unknown (`U1`), Schmerzpunkte (`P1`–`P3`), weitere Unknowns, Endziele (`G…`), zuletzt allgemeine Fragen (`X1`–`X4`, für alle gleich, nur einmal im Plan).
- **Jede Frage geht an alle Personas** des Plans (`ask`), damit Antworten auf denselben Reiz vergleichbar sind – genau das misst Collapse. Ausnahme: Unknown-Fragen gehen nur an ihre eigene Persona; sie prüfen, ob die Persona Offenes offen lässt, und gelten nur für sie.
- **Job-Fragen nennen nur die Situation** («Wenn …»), nicht das gewünschte Ergebnis. Sonst würde die Persona ihre eigene Motivation nachsprechen, statt sie zu zeigen.
- **Prompt** = `render -f prompt -m simulate`, unverändert. Die Probe prüft genau das, was im Einsatz verwendet wird.
- **`plan_id`** = Hash über Personas (ID, Version, Prompt) und Fragen. `evaluate` warnt, wenn die Antworten zu einem anderen Plan gehören.
- **Welche Personas:** bei einem Set-Ordner die Mitglieder des Sets (auch solche, die anderswo liegen); Personas ohne Set nur, wenn ihre Datei ausdrücklich genannt ist oder gar kein Set im Spiel ist. Personas mit `status: retired` fehlen im Plan. Mindestens zwei Personas, sonst gibt es kein Paar.

## 3. Die Antworten (`answers.json`)

```json
{
  "personakit_probe_answers": "1.0",
  "plan_id": "3f9a1c0b7e21",
  "model": "Modell, Temperatur, Datum – Freitext",
  "answers": {
    "eltern-neu-in-zuerich": {
      "eltern-neu-in-zuerich.J1": "Ich mache ein Foto vom Brief …",
      "eltern-neu-in-zuerich.S1": ["Durchgang 1 …", "Durchgang 2 …", "Durchgang 3 …"]
    }
  }
}
```

Pro Persona und Frage ein String oder eine Liste von Durchgängen. `plan_id` und `model` sind optional, aber empfohlen. Antworten zu Personas oder Fragen, die der Plan nicht kennt, werden gemeldet und ignoriert; fehlende Antworten werden gemeldet, nicht still als «ähnlich» oder «verschieden» gezählt.

## 4. Metriken

**Ähnlichkeit (Collapse-Verdacht).** Jeder Durchgang ist ein Dokument. Tokens: Kleinschreibung, nur Buchstabenwörter ab drei Zeichen, `ß` → `ss`, deutsche und englische Füllwörter entfernt, grobes Kürzen häufiger Endungen (`-ungen`, `-en`, `-er` …). **Wörter der Frage zählen nicht** – wer die Frage nachspricht, wird dadurch nicht ähnlich. Gewichtung TF-IDF (`1 + ln tf`, geglättete IDF über alle Antworten des Laufs), Vergleich mit Kosinus.

- Pro Frage und Paar: Mittel über alle Kombinationen der Durchgänge.
- Pro Paar: Ø über die gemeinsamen Fragen, Maximum, Anteil der Fragen ≥ Alarmschwelle.
- **Basis (ab zwei Durchgängen):** Ø-Ähnlichkeit der Durchgänge einer Persona untereinander. Sind zwei Personas einander so ähnlich wie sich selbst (Trennung ≤ 0), sind sie im Modell nicht unterscheidbar – unabhängig von absoluten Schwellen. Liegt die eigene Ähnlichkeit sehr hoch, ist die Varianz kollabiert (Q015).

**Ampel pro Paar** (Schwellen mit `--warn`, `--alarm` änderbar). Die Defaults sind an synthetischen Antworten geprüft (`tests/fixtures/probe/`): deutlich verschiedene Personas liegen um 0.05, wörtlich kollabierte über 0.8, sinngleich umformulierte zwischen 0.25 und 0.5 – genau dort, wo der lexikalische Proxy unsicher wird.

| Ampel | Bedingung (eine genügt) |
|---|---|
| 🔴 rot – Collapse-Verdacht | Ø ≥ Alarm (0.50) · mindestens die Hälfte der Fragen ≥ Alarm · Trennung ≤ 0 und Ø ≥ Warnung |
| 🟡 gelb – prüfen | Ø ≥ Warnung (0.30) · mindestens ein Viertel der Fragen ≥ Alarm · Trennung ≤ 0 |
| 🟢 grün | sonst |

**`must_not` über Schlüsselwörter.** Eine Datei `probe-keywords.yml` (Vorlage mit `--keywords-template`) ordnet jeder Regel `N1…` einer Persona Schlüsselwörter zu. Treffer: Gross-/Kleinschreibung egal, am Wortanfang (`Kreisschulbehörde` trifft `Kreisschulbehörden`). Jeder Treffer mit Frage, Wort und Ausschnitt; steht das Wort schon in der Frage, wird das vermerkt (die Persona kann es übernommen haben). Regeln ohne Schlüsselwörter heissen «nicht geprüft», nie «eingehalten».

**Unknowns als offen.** Die Antwort auf eine Unknown-Frage gilt als *offen*, wenn sie einen Unsicherheitsmarker enthält («weiss nicht», «keine Ahnung», «vielleicht», «kann ich nicht sagen» …, Liste in `probe-keywords.yml` ersetzbar). Ohne Marker: *nicht erkennbar offen*; ohne Marker, aber mit Zahl oder Prozentangabe: *konkrete Angabe ohne Vorbehalt* – der typische erfundene Fakt.

## 5. Befunde und Exit-Codes

Q-Codes stehen in `docs/FORMAT.md`. `evaluate` endet mit 0, mit `--strict` mit 1, sobald eine Warnung vorliegt (rotes Paar, Treffer in `must_not`, Unknown mit konkreter Angabe, fehlende Antworten), mit 2 bei unlesbaren Dateien.

## 6. Grenzen (stehen auch im Bericht)

- **Lexikalische Ähnlichkeit ist ein grober Proxy.** Gleicher Inhalt in anderen Worten bleibt unentdeckt (falsch grün); gemeinsames Fachvokabular einer Domäne hebt die Werte ohne Collapse (falsch rot). Ton, Haltung und Entscheidungen misst sie nicht.
- **Schwellen sind Faustwerte**, nicht kalibriert. Aussagekräftiger als der Absolutwert ist der Vergleich: dasselbe Modell vor und nach einer Änderung an den Personas, oder zwei Modelle mit demselben Plan. Mit mehreren Durchgängen misst die Basis relativ statt absolut.
- **Schlüsselwörter finden nur, was vorher aufgeschrieben wurde.** Ein Treffer ist kein Beweis (Verneinung, Zitat der Frage), kein Treffer keine Einhaltung.
- **Unsicherheitsmarker sind oberflächlich.** «Vielleicht» kann Floskel sein, eine offene Antwort ohne Marker wird übersehen.
- **Unterscheidbar heisst nicht treu.** Personas können sich deutlich unterscheiden und trotzdem alle falsch liegen (Fidelity Gap). Die Probe ersetzt keine Validierung mit realen Personen.

## 7. Bewusst nicht

- Kein eingebauter Modellaufruf: Er würde einen Anbieter festschreiben, Schlüssel verlangen und den Lauf nicht reproduzierbar machen.
- Keine Embeddings: brächten Modelle und Abhängigkeiten zurück; TF-IDF ist nachvollziehbar und zeigt, welche Wörter die Ähnlichkeit tragen.
- Keine Änderung am Persona-Format: Die Probe liest nur `simulation.must_not`, `unknowns`, `jobs`, `pains`, `goals.end` und das Szenario.
