# Format-Referenz `*.persona.md`

Eine Persona ist eine Markdown-Datei `<id>.persona.md` mit YAML-Frontmatter (strukturiert, gegen `schema/persona.schema.json` validiert) und einem Markdown-Body (Szenario, Narrativ). Alle anderen Formate werden daraus gerendert.

Kodierung UTF-8. Dateien mit Windows-Zeilenenden (CRLF) und mit UTF-8-BOM werden gelesen; `bump` und `retire` schreiben sie mit denselben Zeilenenden und demselben BOM zurück. Massgebend ist das Zeilenende der ersten Zeile, gemischte Dateien werden beim Schreiben vereinheitlicht. Exporte (`render`, `list`, `new`) schreiben UTF-8 mit LF, auf jedem Betriebssystem gleich.

## Kopf

| Feld | Pflicht | Bedeutung |
|---|:---:|---|
| `personakit` | ✔ | Format-Version, aktuell `"1.0"` |
| `id` | ✔ | Slug, muss dem Dateinamen entsprechen |
| `archetype` | ✔ | Verhaltensbasierte Bezeichnung («Schulleitung, die Entscheidungsgrundlagen will, nicht Optionen») |
| `name` | | Optionaler Vorname für narrative Ansprache |
| `tagline` | | Ein Satz in den Worten der Persona |
| `kind` | | `user` · `buyer` · `stakeholder` · `partner` · `operator` |
| `priority` | ✔ | `primary` · `secondary` · `supplemental` · `negative` – Default; ein Set kann sie überschreiben (siehe [Sets](#sets-setyml)) |
| `domain` | | Fachlicher Bereich |
| `scope` | | Für welche Lösungen die Persona gilt – und für welche nicht |
| `language` | | BCP-47, Default `de-CH` |
| `version` | ✔ | SemVer: major = Verhalten/Jobs geändert, minor = ergänzt, patch = korrigiert |
| `status` | ✔ | `draft` · `active` · `retired` |
| `evidence_level` | ✔ | `proto` · `qualitative` · `statistical` |
| `owner` | | Verantwortlich für Pflege |
| `created` / `updated` / `review_by` | | ISO-Daten; `review_by` begrenzt die Halbwertszeit |
| `tags` | | Freie Schlagworte |

## Inhalt

| Block | Inhalt |
|---|---|
| `profile[]` | `fact` + `relevance` – biografische Fakten nur mit Begründung |
| `context` | `role`, `situation`, `environment`, `channels[]`, `constraints[]` |
| `behaviour.variables[]` | `name`, `low`, `high`, `value` (1–5), `evidence` – 3–7 Skalen |
| `behaviour.patterns[]` | Beobachtete Muster («macht X, wenn Y») |
| `goals` | `experience[]` (nie verletzen), `end[]`, `life[]` |
| `pains[]` | Validierte Hürden im heutigen Prozess |
| `jobs[]` | `id` (J1…), `statement` (Job Story), `dimension[]`, `forces{push,pull,anxiety,habit}`, `outcomes[]`, `importance`, `satisfaction`, `evidence` |
| `quotes[]` | `text` + `evidence` |
| `anti_patterns[]` | Was die Persona nicht tut / nicht will; bei negativen Personas: wofür nicht gebaut wird |
| `simulation` | `voice`, `must[]`, `must_not[]`, `variance` – Regeln für den Prompt-Einsatz |
| `evidence[]` | `id` (E1…), `type`, `source`, `date`, `n`, `note`, `ref` |
| `assumptions[]` | Nicht validierte Annahmen (Pflicht bei `proto`) |
| `unknowns[]` | Offene Fragen – bleiben im Prompt als «unbekannt» |
| `relations` | `journeys[]` (journeykit-`meta.id`, prüfbar mit `lint --journeys`), `personas[]`, `links[]` |
| `changelog[]` | `version`, `date`, `note` |

Evidenz-Typen: `interview` · `observation` · `survey` · `analytics` · `support-log` · `workshop` · `secondary` · `assumption`.

## Body

```markdown
## Szenario
Eine konkrete Situation mit der Lösung. Pflicht-nah (Lint L005).

## Narrativ
Optional, max. ~10 Sätze, führt keine neuen Fakten ein.
```

Weitere `##`-Abschnitte sind erlaubt und werden in md/json/html mit exportiert.

## Sets (`set.yml`)

Ein Set fasst die Personas **einer Lösung** zusammen: `personas/<set-id>/set.yml`, validiert gegen `schema/set.schema.json`. Dieselbe Persona darf in mehreren Sets vorkommen, jeweils mit eigener Priorität.

```yaml
personakit: "1.0"
id: elternkommunikation-schuleintritt      # = Ordnername
title: "Elternkommunikation Schuleintritt"
solution: "Information und Anmeldung rund um Kindergarten- und Schuleintritt"
scope: "Gilt für … Gilt nicht für …"
status: active                             # draft · active · retired
owner: "Marketing und Kommunikation"       # optional
personas:
  - id: eltern-neu-in-zuerich
    priority: primary                      # überschreibt priority aus der Persona-Datei
  - id: verwaltungs-insider                # ohne priority: Default aus der Persona-Datei
```

| Feld | Pflicht | Bedeutung |
|---|:---:|---|
| `personakit` | ✔ | Format-Version des Sets, aktuell `"1.0"` |
| `id` | ✔ | Slug, muss dem Ordnernamen entsprechen |
| `title` | ✔ | Lesbarer Name |
| `solution` | | Die Lösung, für die das Set gilt |
| `scope` | | Wofür das Set gilt – und wofür nicht |
| `status` | ✔ | `draft` · `active` · `retired`; ein Set im Ruhestand wird von X002–X004 übersprungen |
| `owner` | | Verantwortlich für die Pflege |
| `personas[]` | ✔ | `id` (Pflicht) und `priority` (optional) |

Regeln:

- **Mitgliedschaft steht nur in `set.yml`.** Der Ordner ist der Ablageort der Datei. Eine geteilte Persona existiert einmal – im Ordner ihres ersten Sets oder direkt unter `personas/` – und andere Sets verweisen über die `id` auf sie.
- **Wirksame Priorität** = `priority` in `set.yml`, sonst `priority` der Persona-Datei.
- **Loses Set:** Personas, die keine `set.yml` nennt, bilden ein loses Set. Ein Repo ohne `set.yml` verhält sich wie vor der Einführung von Sets.
- **Auflösung:** Mitglieder, die nicht unter den übergebenen Pfaden liegen, werden unter dem Elternordner des Set-Ordners gesucht (`<id>.persona.md`). Ein Set-Ordner lässt sich deshalb auch allein linten oder rendern.
- `list`, `render -f matrix|html` gruppieren nach Set; `render -f bundle` enthält `sets` (Metadaten und `personas: [{id, priority}]` mit wirksamer Priorität) und `personas` (jede Persona einmal, mit ihrem Default).

Die Persona-Datei bleibt unverändert bei `personakit: "1.0"`; Sets sind eine reine Ergänzung, eine Migration ist nicht nötig. Wer Sets einführen will, legt einen Unterordner mit `set.yml` an und verschiebt die Dateien dorthin (Git: `git mv`).

## Lint-Regeln

| Code | Stufe | Regel |
|---|---|---|
| P000 | ERROR | Datei nicht lesbar (kein Frontmatter, kein Mapping, nicht UTF-8) |
| SCHEMA | ERROR | Verstoss gegen das JSON-Schema; methodische Regeln laufen erst danach |
| P001 | ERROR | Dateiname ≠ `<id>.persona.md` |
| P002 | WARN | Archetyp klingt demografisch |
| P003 | WARN | `scope` fehlt |
| E001 | ERROR | `proto` ohne `assumptions` |
| E002 | WARN | `proto` und `active` (ausser negative) |
| E003 | ERROR | `qualitative`/`statistical` ohne echte Evidenz |
| E004 | WARN | < 5 Interviews/Beobachtungen bei `qualitative` |
| E005 | WARN | `statistical` ohne Survey n ≥ 100 |
| E006 | WARN | Zitat ohne Evidenz-Verweis |
| E007 | ERROR | Verweis auf unbekannte Evidenz-ID |
| E008 | WARN | `unknowns` leer |
| C001 | WARN | Profil-Fakt ohne `relevance` |
| B001 | WARN | Keine Verhaltensvariablen |
| B002 | INFO | > 7 Verhaltensvariablen |
| B003 | INFO | Variable ohne Skalen-Anker |
| G001 | WARN | `goals.end` leer |
| G002 | INFO | `goals.experience` leer |
| G003 | WARN | `pains` leer |
| J001 | WARN | Kein Job (ausser negative) |
| J002 | INFO | Job nicht als Job Story formuliert |
| J003 | INFO | Job wichtig und bereits gut bedient |
| S001 | WARN | `active` ohne `simulation.must_not` |
| S002 | WARN | `active` ohne `simulation.variance` |
| S003 | INFO | `active` ohne `simulation.voice` |
| L001 | WARN | `review_by` fehlt |
| L002 | WARN | Review überfällig |
| L003 | INFO | Review in ≤ 30 Tagen |
| L004 | INFO | `changelog` leer |
| L005 | WARN | Kein `## Szenario` |
| N001 | WARN | Negative Persona ohne `anti_patterns` |
| X000 | ERROR | `set.yml` nicht lesbar oder Verstoss gegen das Set-Schema |
| X001 | ERROR | Persona-`id` mehrfach vorhanden (repo-weit: Sets verweisen über die `id`) |
| X002 | WARN | Keine primäre Persona im Set (pro Set, wirksame Priorität) |
| X003 | WARN | Mehr als eine primäre Persona im Set |
| X004 | INFO | Mehr als 5 aktive Personas im Set |
| X005 | WARN | `relations.personas` verweist auf unbekannte ID (repo-weit: Relationen gehören zur Persona, nicht zum Set) |
| X006 | ERROR | Set-`id` ≠ Ordnername |
| X007 | ERROR | `set.yml` nennt eine unbekannte oder ungültige Persona |
| X008 | ERROR | Persona im selben Set mehrfach aufgeführt |
| X009 | WARN | Persona-Datei liegt in einem Set-Ordner, gehört aber zu keinem Set |
| X010 | ERROR | Set-`id` mehrfach vorhanden |
| K000 | ERROR | Journey-Datei nicht lesbar, oder `meta.id` bzw. `persona.id` fehlt (nur mit `--journeys`) |
| K001 | WARN | `relations.journeys` nennt eine Journey, die unter `--journeys` nicht vorkommt |
| K002 | WARN | Journey nennt in `persona.id` eine unbekannte Persona |
| K003 | WARN | Persona verweist auf eine Journey, die eine andere Persona führt |
| K004 | INFO | Journey führt die Persona, `relations.journeys` nennt sie nicht |

X002–X004 laufen pro Set und für das lose Set; ein Set mit `status: retired` wird übersprungen. Überschreibt ein Set die Priorität einer Persona, prüft der Linter die prioritätsabhängigen Regeln E002, J001 und N001 im Set erneut und meldet nur, was mit der wirksamen Priorität zusätzlich anfällt.

### Kopplung mit journeykit (`--journeys`)

`personakit lint personas --journeys <pfad>` prüft die Verweise zwischen Personas und [journeykit](https://github.com/malkreide/journeykit)-Journeys in beide Richtungen. Begründung und Abgrenzung: [`JOURNEYKIT.md`](JOURNEYKIT.md).

- Eine Journey nennt ihre Persona in `persona.id`; diese ID ist die personakit-`id`. Die Persona nennt ihre Journeys in `relations.journeys` mit der `meta.id` der Journey.
- `<pfad>` ist eine Journey-Datei oder ein Ordner (rekursiv `*.json`, ohne `*.schema.json`); `--journeys` darf mehrfach stehen. Jede übergebene Journey gehört zum geprüften Bestand, ihre `persona.id` gilt also als Verweis.
- personakit liest von einer Journey nur `meta.id` und `persona.id`. Ob die Journey sonst gültig ist, prüft `journeykit lint`.
- Mehrere Dateien mit derselben `meta.id` (z. B. Hypothese und Synthese) zählen als eine Journey. K003 meldet nur, wenn keine davon die Persona führt.
- Personas, die ein Set ausserhalb der übergebenen Pfade auflöst, gelten für K002 als bekannt.
- Ohne `--journeys` läuft keine K-Regel. In `personakit.api` entspricht das `lint_workspace(paths, journeys=[…])`.

### Maschinenlesbare Ausgabe

`personakit lint <pfade> --json` schreibt die Findings als JSON-Liste auf stdout (`set` ist die Set-`id` oder leer für Personas ohne Set und für Persona-Regeln), sortiert wie die Textausgabe; die Zusammenfassung bleibt auf stderr. `--min-level` filtert auch hier, die Exit-Codes sind dieselben (0 sauber, 1 Fehler bzw. mit `--strict` auch Warnungen, 2 Aufruf- oder Pfadfehler).

```json
[
  {"level": "ERROR", "code": "E001", "set": "", "persona": "eltern-neu-in-zuerich", "message": "…"},
  {"level": "WARN", "code": "X003", "set": "elternkommunikation-schuleintritt", "persona": "", "message": "…"}
]
```

## Factoids (`*.factoids.md`)

Factoids sind die Brücke vom Material zur Persona: je eine beobachtbare Aussage aus einem Interview, einer Beobachtung, einem Log oder einer Umfrage, mit Quelle und Teilnehmer-Code, ohne Interpretation. Eine Studie ist ein Ordner `factoids/<studie>/` mit einer Datei pro Quelle und optional `variables.yml`. `personakit factoids` prüft den Ordner und verortet die Teilnehmenden auf den Verhaltensvariablen; `personakit skeleton` legt aus gewählten Teilnehmenden ein Persona-Skelett an. Was eine Persona *bedeutet* – Archetyp, Ziele, Jobs, Simulationsregeln –, bleibt Interpretation (Mensch oder Modell, siehe Skill `persona-kit`).

```
factoids/<studie>/
├── variables.yml                      # optional: Skalen mit Ankern
├── interviews-schuleintritt.factoids.md
└── beobachtung-website.factoids.md
```

Synthetisches Beispiel: [`factoids/beispiel/`](../factoids/beispiel/).

### Datei `<source_id>.factoids.md`

Frontmatter, validiert gegen `schema/factoids.schema.json`:

| Feld | Pflicht | Bedeutung |
|---|:---:|---|
| `personakit` | ✔ | Format-Version, aktuell `"1.0"` |
| `source_id` | ✔ | Slug, muss dem Dateinamen entsprechen |
| `title` | | Lesbarer Name; wird im Skelett zu `evidence[].source` (sonst `source_id`) |
| `type` | ✔ | Evidenz-Typ wie in der Persona (`interview` · `observation` · `survey` · …) |
| `date` | ✔ | Datum der Erhebung (bei Serien: Abschluss) |
| `n` | ✔ | Anzahl Teilnehmende bzw. Fälle der Quelle |
| `consent_note` | ✔ | Wie die Einwilligung eingeholt wurde und wo der Schlüssel Code → Person liegt (nicht im Repo) |
| `ref` | | Ablageort des Rohmaterials – ein Verweis, nicht das Material |
| `note` | | Freitext |

Im Body steht **eine** Markdown-Tabelle (die erste Tabelle zählt), eine Zeile pro Factoid:

| Spalte | Pflicht | Inhalt |
|---|:---:|---|
| `id` | ✔ | Eindeutig im ganzen Studienordner, z. B. `I01` (Interviews), `B01` (Beobachtung) |
| `participant` | ✔ | Teilnehmer-Code: bis drei Buchstaben, optional `-`/`_`, eine Nummer (`p1`, `P07`, `ip-3`, `tn_12`). **Nie Namen.** Derselbe Code meint in allen Dateien des Ordners dieselbe Person |
| `observation` | ✔ | Wörtlich (dann `quote: ja`) oder als Beobachtung ohne Deutung. `\|` im Text als `\\|` schreiben |
| `variable` | | Name der Verhaltensvariable, auf die das Factoid einzahlt |
| `value` | | 1–5 auf dieser Variable; nur zusammen mit `variable` |
| `quote` | | `ja`/`nein` (auch `yes`/`no`, `true`/`false`, `x`, leer = nein) |

```markdown
| id | participant | observation | variable | value | quote |
|---|---|---|---|---|---|
| I09 | p3 | «Ich habe den Brief dreimal übersetzt …» | Deutsch (Behördensprache) | 2 | ja |
| I16 | p4 | Betreuung ist die dringendste Frage. | | | nein |
```

Dateien mit CRLF und UTF-8-BOM werden gelesen.

### `variables.yml` (optional)

```yaml
personakit: "1.0"
variables:
  - name: "Digitale Routine"
    low: "nutzt nur Messenger"                          # Anker für 1
    high: "erledigt Behördliches selbstverständlich online"  # Anker für 5
```

Validiert gegen `schema/variables.schema.json`. Ist die Datei vorhanden, sind nur diese Variablen erlaubt (Tippfehler werden zu F008), die Reihenfolge gilt für Matrix und Skelett, und die Anker gehen nach `behaviour.variables[].low/high`. Ohne Datei gilt jede Variable, die in einer Tabelle vorkommt, und die Anker bleiben leer (Lint B003).

### `personakit factoids <ordner>`

Liest alle `*.factoids.md` direkt im Ordner (nicht rekursiv: ein Ordner = eine Studie, Codes sind nur innerhalb einer Studie eindeutig) und schreibt einen Markdown-Bericht auf stdout:

- **Quellen** – Typ, Datum, n, Teilnehmer-Codes, Anzahl Factoids und Zitate.
- **Verortung** – Matrix Variable × Teilnehmer. Ein Teilnehmer mit mehreren Factoids auf derselben Variable steht beim Median seiner Werte (z. B. `2.5`).
- **Verteilung** – je Variable, welche Teilnehmenden auf welcher Stufe liegen. Hier werden Häufungen sichtbar.
- **Befunde** – siehe Codes unten.

`--json` liefert dasselbe maschinenlesbar (`sources`, `participants`, `variables`, `positions`, `findings`). Exit-Code 0 ohne Fehler, 1 bei Fehlern (mit `--strict` auch bei Warnungen), 2 bei Pfadfehlern.

### `personakit skeleton <ordner> --participants p1,p3,p7 --id <persona-id> -a "<Archetyp>"`

Legt `personas/<persona-id>.persona.md` (`--dir` ändert den Ordner) aus der Vorlage an und füllt nur, was sich aus den Factoids der gewählten Teilnehmenden ableiten lässt:

| Feld | Herkunft |
|---|---|
| `behaviour.variables` | Je Variable der Median über die Gewählten (je Teilnehmer zuerst der Median seiner Factoids); liegt er genau zwischen zwei Stufen, gilt die Stufe näher bei 3. Anker aus `variables.yml`; `evidence` = Quelle mit den meisten Factoids auf dieser Variable |
| `evidence[]` | Eine Quelle pro Datei, die Factoids der Gewählten enthält (Interviews und Beobachtungen zuerst). `n` = Anzahl gewählter Teilnehmender in dieser Quelle, `note` nennt Codes und das `n` der Quelle, `ref` den Pfad der Factoid-Datei |
| `quotes[]` | Alle Factoids der Gewählten mit `quote: ja`, äussere Anführungszeichen entfernt, mit Evidenz-ID |
| `evidence_level` | `qualitative` ab 5 Gewählten mit Interview oder Beobachtung, sonst `proto` (dann verlangt Lint E001 `assumptions`) |
| `unknowns` | Variablen, auf denen keiner der Gewählten verortet ist |
| `## Herleitung` | Tabelle Variable · Wert · Median · Spanne · Teilnehmende · Factoid-IDs, die Zitat-IDs und Hinweise. Hier belegt die Interpretation später jede Aussage mit Factoid-IDs |

Alles andere – Archetyp-Formulierung, `context`, `goals`, `pains`, `jobs`, `anti_patterns`, `simulation`, Szenario – bleibt leer bzw. Vorlage. Das Skelett hat `status: draft` und `version: 0.1.0`. Der Archetyp ist wie bei `new` Pflicht (fehlt er, wird im Terminal nachgefragt).

`skeleton` bricht ab, wenn der Ordner Fehler hat (Exit 1) oder ein Code unbekannt ist (Exit 2). Hinweise auf stderr (und im Abschnitt `## Herleitung`): weniger als 5 Interviews, Variablen, die bei weniger als der Hälfte der Gewählten belegt sind, und **Frankenstein-Gefahr** – zwei Gewählte, die auf mindestens zwei Variablen ≥ 2 Punkte auseinanderliegen (nach der Abgrenzungsregel in `skills/persona-kit/references/elicitation.md` eher zwei Personas).

### Datenschutz

- Factoid-Dateien enthalten nur Teilnehmer-Codes. Der Schlüssel Code → Person liegt ausserhalb des Repos; `consent_note` sagt wo. F006 weist alles zurück, was nicht wie ein Code aussieht, und gibt den Zelleninhalt dabei nicht aus.
- Reale Studienordner werden nicht eingecheckt: `.gitignore` schliesst `factoids/*` aus und lässt nur `factoids/beispiel/` zu. Wer reale Factoids teilen muss, tut das über die Ablage der Erhebung, nicht über Git.
- Auch `observation` kann identifizieren (Beruf, Ort, seltene Umstände). Beim Extrahieren so formulieren, dass die Aussage ohne diese Details trägt.

### Factoid-Befunde

| Code | Stufe | Regel |
|---|---|---|
| F000 | ERROR | Datei nicht lesbar (kein Frontmatter, kein Mapping, nicht UTF-8; auch `variables.yml`) |
| F001 | ERROR | Verstoss gegen `factoids.schema.json` bzw. `variables.schema.json` (oder Variable doppelt definiert) |
| F002 | ERROR | Dateiname ≠ `<source_id>.factoids.md` |
| F003 | ERROR | `source_id` mehrfach im Ordner |
| F004 | ERROR | Keine Factoid-Tabelle, Pflichtspalte fehlt, unbekannte Spalte oder Tabelle ohne Zeilen |
| F005 | ERROR | Zeile ungültig: Zellenzahl, leere Pflichtzelle, ungültige `id`, `value` nicht 1–5 oder ohne `variable`, `quote` kein Wahrheitswert |
| F006 | ERROR | `participant` ist kein Teilnehmer-Code (Datenschutz: nie Namen) |
| F007 | ERROR | Factoid-`id` mehrfach im Studienordner |
| F008 | ERROR | Variable steht nicht in `variables.yml` (nur wenn die Datei existiert) |
| F009 | WARN | Mehr Teilnehmer-Codes in einer Quelle als ihr `n` |
| F010 | WARN | Variable bei weniger als 3 oder weniger als der Hälfte der Teilnehmenden verortet – zu dünn für Häufungen |
| F011 | INFO | Teilnehmer liegt auf mindestens zwei Variablen ≥ 2 Punkte von **allen** anderen entfernt – Kandidat für eine eigene Persona oder für `simulation.variance` |

F011 prüft wörtlich «von allen anderen»: Zwei Teilnehmende, die gemeinsam abseits liegen, bilden eine Häufung, keinen Ausreisser – sie zeigt die Verteilung, nicht dieser Befund. Die Schwellen (≥ 2 Punkte auf ≥ 2 Variablen) sind dieselben wie die Abgrenzungsregel für Personas im Erhebungsleitfaden; die 5 für `qualitative` folgt NN/g (`docs/METHOD.md`, 1.3).
