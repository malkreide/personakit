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
- **Basis (ab zwei Durchgängen):** Ø-Ähnlichkeit der Durchgänge einer Persona untereinander. **Nähe** = Ähnlichkeit zum Gegenüber geteilt durch diese Basis (Mittel beider Personas, über die Fragen mit mindestens zwei Durchgängen je Persona). Bei 1 sind zwei Personas einander so ähnlich wie sich selbst. Liegt die eigene Ähnlichkeit sehr hoch, ist die Varianz kollabiert (Q015).

**Ampel pro Paar**, kalibriert an künstlich verwaschenen Personas ([`probe/kalibrierung/`](../probe/kalibrierung/), siehe unten):

| | Ab zwei Durchgängen (Nähe) | Mit einem Durchgang (absolut) |
|---|---|---|
| 🔴 rot – Collapse-Verdacht | Nähe ≥ 0.85 (`--ratio-alarm`) | Ø ≥ 0.18 (`--alarm`) · mindestens die Hälfte der Fragen ≥ 0.18 |
| 🟡 gelb – prüfen | Nähe ≥ 0.50 (`--ratio-warn`) | Ø ≥ 0.15 (`--warn`) · mindestens ein Viertel der Fragen ≥ 0.18 |
| 🟢 grün | sonst | sonst |

Fällt die Basis unter 0.05, ist die Nähe instabil, und es gelten die absoluten Schwellen. Mit nur einem Durchgang erkennt die Ampel nur den vollständigen Collapse; der Bericht sagt das (Q018).

**`must_not` über Schlüsselwörter.** Eine Datei `probe-keywords.yml` (Vorlage mit `--keywords-template`) ordnet jeder Regel `N1…` einer Persona Schlüsselwörter zu. Treffer: Gross-/Kleinschreibung egal, am Wortanfang (`Kreisschulbehörde` trifft `Kreisschulbehörden`). Jeder Treffer mit Frage, Wort und Ausschnitt; steht das Wort schon in der Frage, wird das vermerkt (die Persona kann es übernommen haben). Regeln ohne Schlüsselwörter heissen «nicht geprüft», nie «eingehalten».

**Unknowns als offen.** Die Antwort auf eine Unknown-Frage gilt als *offen*, wenn sie einen Unsicherheitsmarker enthält («weiss … nicht», «keine Ahnung», «vielleicht», «kann … nicht … sagen» …, `…` für bis zu vier Wörter, Liste in `probe-keywords.yml` ersetzbar). Ohne Marker: *nicht erkennbar offen*; ohne Marker, aber mit Zahl oder Prozentangabe: *konkrete Angabe ohne Vorbehalt* – der typische erfundene Fakt. Listennummern, Datum, Uhrzeit und Jahreszahl zählen nicht als Zahl (ergänzt nach Lauf 2).

**Form der Antworten (ergänzt nach Lauf 1).** Länge pro Antwort, Wörter pro Satz, Anteil gegliederter Antworten und häufigstes erstes Inhaltswort, je Persona. Gleiche Form zweier Personas: Länge innerhalb 80 %, Gliederung innerhalb 20 Prozentpunkten. Formkollaps (Q020), wenn das für alle Paare gilt und alle in Assistentenform antworten (gegliedert oder lang); gleicher häufigster Antwortanfang bei mehreren Personas (Q021). Deterministisch, ohne Modell, und bewusst getrennt von der Ampel: Die Ampel misst *was*, diese Kennzahlen *wie* geantwortet wird.

**Treffer im Kontext (ergänzt nach Lauf 1).** Ein Schlüsselwort in Anführungszeichen, in einer Frage oder mit einer Verneinung höchstens vier Wörter daneben gilt als erwähnt, nicht verwendet (Q017 statt Q012). Das Fenster ist eng, weil ein «keine» im Nebensatz («…, dass ich keine Frist verpasse») die Verwendung davor nicht aufhebt. Nach Lauf 2 ergänzt: «weiss/verstehe/kenne … nicht» vor dem Wort (*nicht gewusst*) und ein Redeverb wie «sagt», «steht» vor dem Wort (*wiedergegeben*). Aufzählungen bleiben bewusst Verwendungen: Der einzige echte Rollenbruch aus Lauf 2 war selbst eine Aufzählung.

### Erfahrung aus Lauf 1

Erster Lauf am 9.10.2026: vier Beispiel-Personas, 32 Fragen, je 3 Durchgänge, 330 Antworten von `claude-sonnet-5-5` über die Claude-Code-CLI. Ergebnis:

- **Inhalt unterscheidbar:** Ø Ähnlichkeit zwischen Personas 0.08–0.11, Trennung 0.19–0.27, alle Paare grün. Auch bei fremden Szenarien blieben die Personas in ihrer Perspektive.
- **Form kollabiert:** Jede Persona antwortete im Schnitt mit rund 300 Wörtern, 85–94 % der Antworten gegliedert, «Ehrlich:» als häufigster Anfang bei allen vier – auch die Persona mit «kurzen Sätzen» (8.5 Wörter pro Satz, aber 300 Wörter pro Antwort). Die Ampel sah das nicht. Daraus: Formkennzahlen, Q020, Q021.
- **`must_not` nur Fehlalarme:** 30 Schlüsselwort-Treffer, alle Erwähnungen («Bei Wörtern wie «Kreisschulbehörde» kommt Unsinn heraus», «bin ich nicht begeistert»). Mit der Kontextregel: 30 von 30 als erwähnt eingeordnet (28 zitiert, 2 verneint), kein Q012 mehr.
- **Schwellen:** Lange echte Antworten liegen bei etwa 0.1 – weit unter Warnung (0.30) und Alarm (0.50). Absolute Schwellen sind bei langen Antworten stumpf; die Trennung (ab zwei Durchgängen) ist das belastbarere Signal. Die Schwellen bleiben vorerst, bis ein Lauf mit echtem inhaltlichem Collapse vorliegt.

### Kalibrierung (Lauf 3)

Die ersten beiden Läufe enthielten keinen Collapse, die Schwellen 0.30/0.50 waren an synthetischen Texten gesetzt. Für eine bekannte Wahrheit liefen dieselben Fragen mit Haiku gegen die vier Beispiel-Personas in drei verwaschenen Stufen: ohne Stimme und Simulationsregeln, nur mit dem Archetyp, und mit einem für alle identischen generischen Prompt. Ergebnisse, Tabelle und Grenzen: [`probe/kalibrierung/README.md`](../probe/kalibrierung/README.md).

- **Die alten Schwellen erkannten selbst den vollständigen Collapse nicht.** Identische Prompts ergaben eine Ähnlichkeit von nur 0.20; die Regel «Trennung ≤ 0» kippte im Rauschen zufällig.
- **Die Nähe trennt die Stufen ohne Überlappung:** vollständig 0.31–0.40, ohne Stimme 0.38–0.44, nur Archetyp 0.53–0.61, identisch 0.97–1.03. Daraus die Schwellen gelb 0.50 und rot 0.85.
- **Ein Durchgang** trennt nur den vollständigen Collapse (0.20–0.23 gegen höchstens 0.14). Daraus die absoluten Schwellen 0.15 und 0.18.
- **Grenzen:** Die Schwellen sind an denselben Daten gewählt und geprüft. Unabhängig bestätigt ist bisher nur der Sonnet-Lauf mit vollständigen Personas (grün). Die Kalibrierung gilt für ein Modell, eine Domäne und Deutsch. `tests/test_probe_calibration.py` hält die Stufenleiter als Regressionstest fest.

### Lauf 2: Haiku statt Sonnet

Am 9.10.2026 lief derselbe Plan mit `claude-haiku-5-5`. Beide Läufe liegen mit Berichten und Vergleich unter [`probe/beispiel/`](../probe/beispiel/).

- **Inhalt:** wieder alle Paare grün; die Trennung ist mit 0.14–0.20 etwas kleiner als bei Sonnet.
- **Form:** kürzere Antworten (226–254 Wörter) und weniger gegliedert (51–75 %), knapp kein Formkollaps; «Ehrlich» ist bei allen Personas noch häufiger der Anfang.
- **`must_not`:** zunächst 6 Treffer als Verwendung. Gelesen ergab das einen echten Rollenbruch (die Elternpersona berät als Kommunikationsfachperson), einen Grenzfall und vier Erwähnungen ohne Anführungszeichen: indirekte Rede, «weiss nicht, ob …» mit weitem Abstand, eine Aufzählung. Mit den Kontexten *nicht gewusst* und *wiedergegeben* bleiben 3: Rollenbruch, Grenzfall, Aufzählung.
- **Unknowns:** zunächst ein Fehlalarm (Q013): «weiss ich das selbst nicht genau» traf den Marker «weiss nicht» nicht, und das Datum «1. November» zählte als Zahl. Mit Markern mit Lücke und ohne Datum als Zahl: 18 von 18 offen.

Beide Läufe enthalten keinen inhaltlichen Collapse; die Schwellen waren danach noch nicht kalibriert (siehe Lauf 3).

## 5. Befunde und Exit-Codes

Q-Codes stehen in `docs/FORMAT.md`. `evaluate` endet mit 0, mit `--strict` mit 1, sobald eine Warnung vorliegt (rotes Paar, Treffer in `must_not`, Unknown mit konkreter Angabe, fehlende Antworten), mit 2 bei unlesbaren Dateien.

## 6. Grenzen (stehen auch im Bericht)

- **Lexikalische Ähnlichkeit ist ein grober Proxy.** Gleicher Inhalt in anderen Worten bleibt unentdeckt (falsch grün); gemeinsames Fachvokabular einer Domäne hebt die Werte ohne Collapse (falsch rot). Ton, Haltung und Entscheidungen misst sie nicht.
- **Die Schwellen sind an einem Modell kalibriert** (Haiku, verwaschene Beispiel-Personas). Die Nähe (ab zwei Durchgängen) ist relativ und darum robuster; die absoluten Schwellen hängen an Modell und Antwortlänge. Aussagekräftig bleibt der Vergleich: dasselbe Modell vor und nach einer Änderung an den Personas, oder zwei Modelle mit demselben Plan.
- **Die Form ist nur grob gemessen.** Länge, Gliederung und Antwortanfang zeigen den Assistenten-Kollaps, nicht Tonfall, Register oder Höflichkeit.
- **Schlüsselwörter finden nur, was vorher aufgeschrieben wurde.** Ein Treffer ist kein Beweis, kein Treffer keine Einhaltung. Die Einordnung «zitiert/verneint/gefragt» ist eine Satzregel und trennt Erwähnen von Verwenden meistens, nicht immer.
- **Unsicherheitsmarker sind oberflächlich.** «Vielleicht» kann Floskel sein, eine offene Antwort ohne Marker wird übersehen.
- **Unterscheidbar heisst nicht treu.** Personas können sich deutlich unterscheiden und trotzdem alle falsch liegen (Fidelity Gap). Die Probe ersetzt keine Validierung mit realen Personen.

## 7. Bewusst nicht

- Kein eingebauter Modellaufruf: Er würde einen Anbieter festschreiben, Schlüssel verlangen und den Lauf nicht reproduzierbar machen.
- Keine Embeddings: brächten Modelle und Abhängigkeiten zurück; TF-IDF ist nachvollziehbar und zeigt, welche Wörter die Ähnlichkeit tragen.
- Keine Änderung am Persona-Format: Die Probe liest nur `simulation.must_not`, `unknowns`, `jobs`, `pains`, `goals.end` und das Szenario.
