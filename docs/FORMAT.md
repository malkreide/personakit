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
- `list`, `render -f matrix|html` gruppieren nach Set; `render -f notion` schreibt eine Seite pro Persona mit allen ihren Sets (siehe [Notion-Export](#notion-export-render--f-notion)); `render -f bundle` enthält `sets` (Metadaten und `personas: [{id, priority}]` mit wirksamer Priorität) und `personas` (jede Persona einmal, mit ihrem Default).

Die Persona-Datei bleibt unverändert bei `personakit: "1.0"`; Sets sind eine reine Ergänzung, eine Migration ist nicht nötig. Wer Sets einführen will, legt einen Unterordner mit `set.yml` an und verschiebt die Dateien dorthin (Git: `git mv`).

## Notion-Export (`render -f notion`)

`personakit render <pfade> -f notion [--target api|mcp] [-o datei.json]` schreibt JSON für eine Notion-Datenbank «Personas». Der Renderer macht keine Netzwerkaufrufe; das Schreiben nach Notion übernimmt ein Skript (REST-API) oder die Skill `persona-kit` (Notion-MCP-Tools, Schritt «Nach Notion publizieren»).

```json
{
  "generator": "personakit 0.2.0",
  "target": "api",
  "database": { "title": […], "properties": {…} },
  "pages": [ { "properties": {…}, "children": […] } ]
}
```

- **Eine Seite pro Persona-`id`**, auch wenn die Persona in mehreren Sets steht. `ID` ist der Schlüssel zum Aktualisieren: Gibt es in der Datenbank schon eine Seite mit derselben `ID`, wird sie überschrieben, nicht dupliziert.
- **Die Datei bleibt die Quelle.** Die Seite endet mit dem Hinweis, aus welcher Datei sie erzeugt wurde; Änderungen in Notion gehen beim nächsten Export verloren.
- Exportiert werden die Personas der übergebenen Pfade, gruppiert nach Set wie bei `bundle`. Ein einzelner Set-Ordner lässt sich allein exportieren.

### Datenbank «Personas»

Die Datenbank muss diese Properties mit genau diesen Namen und Typen haben (weitere Properties stören nicht):

| Property | Typ | Inhalt |
|---|---|---|
| `Name` | Title | `name – archetype`, ohne `name` nur der Archetyp |
| `ID` | Text (`rich_text`) | Persona-`id`, Schlüssel für das Aktualisieren |
| `Archetyp` | Text | `archetype` |
| `Set` | Multi-select | Set-`id`s, in denen die Persona steht; leer für Personas ohne Set |
| `Priorität` | Select | `Primär` · `Sekundär` · `Ergänzend` · `Negativ (nicht bauen für)` – der Default aus der Persona-Datei |
| `Status` | Select | `Entwurf` · `Aktiv` · `Ruhestand` |
| `Evidenz` | Select | `Proto (Annahmen)` · `Qualitativ` · `Statistisch` |
| `Version` | Text | SemVer als Text, z. B. `1.1.0` (kein Number: `1.10.0` wäre sonst `1.1`) |
| `Review bis` | Date | `review_by`; leer, wenn nicht gesetzt |
| `Tags` | Multi-select | `tags` |

Select statt Notions Typ «Status», weil sich dessen Optionen über die API nicht anlegen lassen. `Priorität` ist bewusst der Default aus der Persona-Datei: Eine Seite pro Persona kann nur eine Priorität tragen, und eine Priorität, die davon abhängt, welches Set zuletzt exportiert wurde, würde bei jedem Export kippen. Die Priorität pro Set steht auf der Seite unter «Rolle in Sets», mit Hinweis, wo sie vom Default abweicht. Notion lehnt Kommas in Select-Optionen ab; der Export ersetzt sie durch `;` und kürzt Optionen auf 100 Zeichen.

`database` im Export beschreibt diese Datenbank zum Anlegen: bei `api` als `title` und `properties` mit den Select-Optionen und Farben (API-Version `2022-06-28`; ab `2025-09-03` gehören die `properties` unter `initial_data_source`), bei `mcp` als `schema` (`CREATE TABLE …`) für das MCP-Tool `notion-create-database` und als `options` (je Select- und Multi-select-Property die Optionen, die der Export verwendet). Die Optionen von `Set` und `Tags` sind die des Exports. **Über die Notion-MCP-Tools legt Notion fehlende Optionen beim Schreiben einer Seite nicht an**, sondern lehnt die Seite ab (geprüft am 8.10.2026); fehlende Optionen müssen vorher an der Datenquelle ergänzt werden (Skill `persona-kit`, Schritt «Nach Notion publizieren»). Ob die REST-API sie selbst anlegt, ist nicht geprüft – im Zweifel ebenso vorher ergänzen.

### Seiteninhalt

Dieselben Abschnitte wie `render -f md`, leere fallen weg: Tagline als Zitat, Bereich/Gilt für/Pflege, «Rolle in Sets», Relevante Fakten, Kontext, Verhalten (Verhaltensvariablen als Tabelle `Variable | 1 | Ausprägung | 5`, Muster als Aufzählung), Ziele, Schmerzpunkte, Jobs-to-be-Done (je Job eine Überschrift, Kräfte und Ergebnisse als Aufzählung), Tut nicht, Zitate als Zitat-Blöcke, die Body-Abschnitte (Absätze, Listen, `###`-Überschriften und Pipe-Tabellen werden zu Blöcken, `**fett**` bleibt fett, `` `code` `` wird Code, übriges Markdown bleibt Text), Prompt-Einsatz, Evidenz (Quellen und Annahmen je in einem Toggle, «Offen» sichtbar), Verknüpfungen, Änderungen.

### Ziele `api` und `mcp`

| | `--target api` (Default) | `--target mcp` |
|---|---|---|
| Für | Notion-REST-API, `POST /v1/pages` | Notion-MCP-Tools `notion-create-pages`, `notion-update-page` |
| `pages[]` | `properties` (Property-Objekte) und `children` (Block-Objekte) | `properties` (flache Werte) und `content` (Notion-Markdown) |
| `parent` | ergänzt der Aufrufer: `{"database_id": …}` bzw. `{"data_source_id": …}` | im Tool-Aufruf: `parent: {"data_source_id": …}` |
| `ID` | `"ID": {"rich_text": […]}` | `"userDefined:ID": "…"` (das MCP-Tool verlangt das Präfix für Properties namens `id`) |
| `Review bis` | `{"date": {"start": "2027-04-06"}}` oder `{"date": null}` | `"date:Review bis:start"`, `"date:Review bis:is_datetime": 0` |
| Select, Multi-select | `{"select": {"name": …}}`, `{"multi_select": [{"name": …}]}` | Text bzw. Liste von Texten |

Beide Ziele kommen aus denselben Blöcken; `content` ist die Markdown-Fassung von `children`.

**Grenzen der Notion-API**, die der Export einhält: Text wird nach 2000 Zeichen (UTF-16-Einheiten, wie Notion zählt) auf mehrere Rich-Text-Objekte verteilt, nie mitten in einem Zeichen. Ein `children`-Array hat höchstens 100 Blöcke: Toggles und Tabellen mit mehr Einträgen werden geteilt («Quellen (1/2)», Tabellen mit wiederholter Kopfzeile). Hat eine Seite mehr als 100 Blöcke, stehen die ersten 100 in `children`, der Rest in `append` – Stapel zu höchstens 100 für `PATCH /v1/blocks/{page_id}/children` nach dem Anlegen; `append` fehlt, wenn alles in `children` passt, und gehört nicht in den Body von `POST /v1/pages`. Verschachtelt wird höchstens zwei Ebenen tief, wie es die API pro Anfrage erlaubt.

**Escaping.** `api`: Text steht unverändert im JSON (JSON-Escaping genügt), Steuerzeichen ausser Zeilenumbruch und Tab werden entfernt, `\r\n` wird zu `\n`. `mcp`: in Text und Text-Properties wird jedes der Zeichen `` \ * ~ ` $ [ ] < > { } | ^ `` mit `\` maskiert, wie es die Notion-Markdown-Spezifikation verlangt; ein Zeilenumbruch wird zu `<br>`, damit ein Block ein Block bleibt; Text, der am Zeilenanfang als Block gelesen würde (`# `, `- `, `1. `, `---`), bekommt ein `\` davor. Select-Werte werden nicht maskiert. Code (aus `` `…` `` im Body und der Dateiname in der Fusszeile) bleibt unmaskiert, weil Notion Code wörtlich nimmt; enthält er selbst einen Backtick, wird er als maskierter Text ausgegeben. Der Dateiname steht als Code, weil Notion `….persona.md` sonst in einen Link verwandelt (`.md` ist eine Top-Level-Domain); andere Domains im Text (z. B. `stadt-zuerich.ch`) verlinkt Notion beim Schreiben über MCP ebenfalls automatisch.

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

## Collapse-Probe (`probe`)

Die Probe misst, ob simulierte Personas unterscheidbar bleiben (Persona Collapse, `docs/METHOD.md` 1.6). personakit erzeugt Fragen und wertet Antworten aus; das Modell, das antwortet, wählt und betreibt der Mensch. Begründung und Abwägungen: [`PROBE.md`](PROBE.md). Zwei echte Läufe (Sonnet und Haiku gegen die Beispiel-Personas) mit Berichten: [`probe/beispiel/`](../probe/beispiel/).

```bash
personakit probe build personas/<set> -o probe.json --answers-template answers.json --keywords-template probe-keywords.yml
#   … Plan gegen ein Modell laufen lassen, answers.json füllen …
personakit probe evaluate probe.json answers.json -k probe-keywords.yml -o bericht.md
```

### `probe build <pfade>`

| Option | Bedeutung |
|---|---|
| `-n`, `--questions` | Fragen pro Persona, 6–10 (Default 8) |
| `--samples` | Empfohlene Durchgänge pro Frage (Default 1); ab 2 misst `evaluate` Trennung und Varianz |
| `-o` | Plan als Datei, sonst stdout |
| `--answers-template` | Leere `answers.json` mit allen Persona-/Fragen-Kombinationen |
| `--keywords-template` | `probe-keywords.yml` mit einer leeren Liste pro `must_not`-Regel, Regeltext als Kommentar |
| `--force` | Bestehende Vorlagen überschreiben (sonst Abbruch mit Exit 2, damit eine gefüllte Datei nie verloren geht) |

Personas: bei einem Set-Ordner die Set-Mitglieder; Personas ohne Set nur, wenn ihre Datei ausdrücklich genannt ist (oder kein Set beteiligt ist). `retired` wird übersprungen, mindestens zwei Personas sind nötig.

Fragen pro Persona, in dieser Reihenfolge bis zur gewünschten Zahl:

| Ref | Quelle | Frage (gekürzt) | An |
|---|---|---|---|
| `S1` | erster Absatz von `## Szenario`, ganze Sätze bis 360 Zeichen | «Stell dir diese Situation vor: «…» Was tust du jetzt – und warum?» | alle |
| `J…` | `jobs[]` (höchstens 3): nur der «Wenn …»-Teil der Job Story | «Die Situation: «Wenn … …» Was tust du dann …?» | alle |
| `U1` | erstes `unknowns[]` | «Eine Frage zu dir und Leuten in deiner Lage: «…» Was sagst du dazu?» | nur die eigene Persona |
| `P1`–`P3` | `pains[]` | «Jemand in deiner Lage sagt: «…» Kennst du das? Wie gehst du damit um?» | alle |
| `U2…` | weitere `unknowns[]` | wie `U1` | nur die eigene Persona |
| `G…` | `goals.end[]` | «Was müsste passieren, damit für dich gilt: «…»?» | alle |
| `X1`–`X4` | allgemein, für alle gleich | z. B. «Wem vertraust du bei solchen Fragen am meisten – und wem nicht?» | alle, einmal im Plan |

Fragen-ID: `<persona-id>.<Ref>`, allgemeine Fragen `X1`–`X4`. Der Plan (`probe.json`, Schema `schema/probe.schema.json`) enthält `plan_id` (Hash über Personas und Fragen), `samples`, `sets`, `instructions`, `personas[]` (`id`, `version`, `archetype`, `priority`, `evidence_level`, `prompt` = `render -f prompt -m simulate`, `must_not[]` mit `N1…`, `unknowns[]` mit `U1…`) und `questions[]` (`id`, `origin`, `kind`, `ref`, `text`, `ask`).

**Ausführen:** pro Persona, Frage und Durchgang ein neues Gespräch ohne Vorgeschichte, Systemprompt = `personas[].prompt`, Nutzernachricht = `questions[].text`, nur für die Personas in `ask`.

### `answers.json`

```json
{
  "personakit_probe_answers": "1.0",
  "plan_id": "3f9a1c0b7e21",
  "model": "Modell, Temperatur, Datum",
  "answers": {
    "eltern-neu-in-zuerich": {
      "eltern-neu-in-zuerich.J1": "Antwort",
      "X1": ["Durchgang 1", "Durchgang 2"]
    }
  }
}
```

Schema `schema/probe-answers.schema.json`. `plan_id` und `model` sind optional, aber empfohlen. Pro Persona und Frage ein String oder eine Liste von Durchgängen; leere Strings zählen als fehlend.

### `probe-keywords.yml` (optional)

```yaml
personakit_probe_keywords: "1.0"
must_not:
  eltern-neu-in-zuerich:
    N1: [Kreisschulbehörde, Schulpflege]   # Regel N1 aus probe.json
    N2: [Tagesstruktur, Einschulung]
open_markers: [weiss nicht, keine ahnung, vielleicht]   # optional: ersetzt die Standardliste
context_markers: [nicht, kein, keine, nie]               # optional: ersetzt die Standardliste der Verneinungen
```

Schema `schema/probe-keywords.schema.json`. Schlüsselwörter treffen am Wortanfang, Gross-/Kleinschreibung egal (`Kreisschulbehörde` trifft `Kreisschulbehörden`). Kontextwörter (Verneinungen) treffen nur ganze Wörter (`nie` trifft nicht `niedrig`); Standardliste: nicht, nichts, kein, keine, keinen, keinem, keiner, keines, nie, niemals, weder, ohne, unklar, unbekannt, unverständlich.

### `probe evaluate <plan> <answers>`

| Option | Bedeutung |
|---|---|
| `-k`, `--keywords` | Schlüsselwort-Datei; ohne sie gelten alle `must_not`-Regeln als «nicht geprüft» |
| `--warn`, `--alarm` | Schwellen für die Ampel (Default 0.30 und 0.50; `0 < warn ≤ alarm ≤ 1`) |
| `--json` | Ergebnis als JSON (`pairs` mit `same_form`, `variance`, `form`, `form_collapse`, `must_not` mit `context` je Treffer, `unknowns`, `findings`, `limits`) |
| `--strict` | Exit 1 bei jeder Warnung |
| `-o` | Bericht als Datei, sonst stdout |

Der Markdown-Bericht enthält: Ampel pro Persona-Paar (Ø und maximale Ähnlichkeit, Anteil der Fragen ≥ Alarm, gemeinsame Fragen, Trennung, Form gleich oder verschieden), die **Form der Antworten** je Persona, die ähnlichsten Antworten der auffälligen Paare mit den Wörtern, die die Ähnlichkeit tragen, die `must_not`-Prüfung pro Regel mit Treffern (Verwendungen und Erwähnungen getrennt), die Unknown-Prüfung, bei mehreren Durchgängen die Varianz je Persona, die Befunde, die **Grenzen der Methode** und die Parameter.

**Ähnlichkeit:** TF-IDF-Kosinus (`1 + ln tf`, geglättete IDF über alle Antworten des Laufs) auf Buchstabenwörtern ab drei Zeichen, Füllwörter entfernt, Endungen grob gekürzt, ohne die Wörter der Frage. Pro Frage und Paar das Mittel über alle Kombinationen der Durchgänge; **Trennung** = Ø(Ähnlichkeit der eigenen Durchgänge beider Personas) − Ähnlichkeit zwischen ihnen, nur über Fragen mit mindestens zwei Durchgängen je Persona.

| Ampel | Bedingung (eine genügt) |
|---|---|
| 🔴 rot | Ø ≥ Alarm · mindestens die Hälfte der gemeinsamen Fragen ≥ Alarm · Trennung ≤ 0 und Ø ≥ Warnung |
| 🟡 gelb | Ø ≥ Warnung · mindestens ein Viertel der gemeinsamen Fragen ≥ Alarm · Trennung ≤ 0 |
| 🟢 grün | sonst |
| ⚪ keine Daten | keine gemeinsam beantwortete Frage |

**Form der Antworten:** Die Ampel vergleicht Wörter; den Assistenten-Kollaps – alle Personas antworten gleich lang, gegliedert und mit denselben Floskeln, nur mit anderem Vokabular – sieht sie nicht. Deshalb misst `evaluate` je Persona über alle ihre Antworten:

| Kennzahl | Messung |
|---|---|
| Ø Wörter | Wörter pro Antwort, ohne Markdown und Aufzählungszeichen |
| Ø Wörter pro Satz | Sätze an `.`, `!`, `?`, `…` und Zeilenumbrüchen getrennt (ein Listenpunkt ist ein Satz) |
| Mit Gliederung | Anteil der Antworten mit Überschrift (`#`), Aufzählung (`-`, `*`, `•`, `1.`) oder **fettem** Einstieg |
| Häufigster Anfang | erstes Inhaltswort (ohne Füllwörter, ab 3 Zeichen) und sein Anteil, z. B. «ehrlich» bei «Ehrlich:», «Ehrlich gesagt» |

Zwei Personas haben **gleiche Form**, wenn die kürzere Ø-Länge mindestens 80 % der längeren beträgt und der Anteil gegliederter Antworten höchstens 20 Prozentpunkte auseinanderliegt (Spalte «Form» in der Ampeltabelle; fliesst nicht in die Ampel ein). **Formkollaps** (Q020): alle Paare gleiche Form, und alle Personas antworten in Assistentenform (mindestens 50 % gegliedert oder Ø mindestens 150 Wörter). Kurze, ungegliederte Antworten gleicher Länge sind kein Formkollaps: So sprechen Menschen. Ob eine lange Antwort zur Persona passt, sagt ihre `simulation.voice`.

**Treffer im Kontext:** Ein Schlüsselwort ist *erwähnt*, nicht *verwendet*, wenn es in Anführungszeichen steht (`«…»`, `„…“`, `“…”`, `"…"`, `‹…›` – *zitiert*), wenn höchstens vier Wörter davor oder danach im selben Satz ein Kontextwort steht (*verneint*: «Ich weiss nicht, was die Kreisschulbehörde ist») oder wenn der Satz mit `?` endet (*gefragt*). Erwähnungen zählen nicht als möglicher Verstoss (Q012), sondern als Q017, und stehen im Bericht mit `[zitiert]`, `[verneint]` oder `[gefragt]` zum Lesen. Grenze der Satzregel: «Die Kreisschulbehörde ist nicht zuständig» verwendet den Begriff und gilt trotzdem als verneint.

**Unknowns:** Eine Antwort auf eine Unknown-Frage ist *offen*, wenn sie einen Unsicherheitsmarker enthält; ohne Marker *nicht erkennbar offen*; ohne Marker, aber mit Zahl oder «Prozent» eine *konkrete Angabe ohne Vorbehalt*. Bei mehreren Durchgängen zählt der ungünstigste.

Exit-Codes: 0 nach der Auswertung, mit `--strict` 1 bei mindestens einer Warnung, 2 bei unlesbaren oder ungültigen Dateien, fehlenden Pfaden und ungültigen Schwellen.

### Probe-Befunde

| Code | Stufe | Regel |
|---|---|---|
| Q001 | WARN | `plan_id` der Antworten ≠ `plan_id` des Plans (Personas oder Fragen seit dem Lauf geändert) |
| Q002 | WARN | Antworten fehlen (pro Persona, mit Fragen-IDs) |
| Q003 | INFO | Antworten zu Personas oder Fragen, die der Plan nicht kennt oder der Persona nicht stellt – ignoriert |
| Q004 | WARN | Leere Antwort, oder Antwort ohne eigene Wörter (nur Füllwörter und Wörter der Frage) – nicht verglichen |
| Q005 | INFO | `must_not`-Regel ohne Schlüsselwörter – nicht geprüft |
| Q006 | WARN | Schlüsselwörter für eine unbekannte Persona oder Regel – nicht geprüft |
| Q010 | WARN | Persona-Paar rot: Collapse-Verdacht |
| Q011 | INFO | Persona-Paar gelb: prüfen |
| Q012 | WARN | Schlüsselwort einer `must_not`-Regel in einer Antwort der Persona verwendet (nicht nur erwähnt, siehe Q017) |
| Q013 | WARN | Unknown mit konkreter Angabe ohne Vorbehalt beantwortet |
| Q014 | INFO | Unknown nicht erkennbar als offen behandelt |
| Q015 | INFO | Durchgänge einer Persona fast gleich (Ø ≥ 0.80): Varianz kollabiert |
| Q016 | INFO | Weniger als 3 gemeinsame Fragen – Ampel wenig belastbar |
| Q017 | INFO | Treffer einer `must_not`-Regel nur im Kontext (zitiert, verneint, gefragt) – lesen, nicht zählen |
| Q020 | WARN | Formkollaps: alle Personas gleich lang und gleich gegliedert, in Assistentenform |
| Q021 | INFO | Dasselbe Wort ist bei mindestens zwei Personas der häufigste Antwortanfang (je mindestens 10 %) |

Alle Q-Befunde gehen auf `docs/METHOD.md` 1.6 zurück: Collapse (Q010/Q011), Collapse der Form – «zu rational», Assistentenregister (Q020/Q021), kollabierte Varianz (Q015), erfundene Fakten statt offener Fragen (Q013/Q014), Verletzung der Simulationsregeln (Q012). Q001–Q006 und Q016 sichern ab, dass fehlende oder unpassende Daten nicht still als Ergebnis zählen.
