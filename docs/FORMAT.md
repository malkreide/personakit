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
| `relations` | `journeys[]` (journeykit-IDs), `personas[]`, `links[]` |
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

X002–X004 laufen pro Set und für das lose Set; ein Set mit `status: retired` wird übersprungen. Überschreibt ein Set die Priorität einer Persona, prüft der Linter die prioritätsabhängigen Regeln E002, J001 und N001 im Set erneut und meldet nur, was mit der wirksamen Priorität zusätzlich anfällt.

### Maschinenlesbare Ausgabe

`personakit lint <pfade> --json` schreibt die Findings als JSON-Liste auf stdout (`set` ist die Set-`id` oder leer für Personas ohne Set und für Persona-Regeln), sortiert wie die Textausgabe; die Zusammenfassung bleibt auf stderr. `--min-level` filtert auch hier, die Exit-Codes sind dieselben (0 sauber, 1 Fehler bzw. mit `--strict` auch Warnungen, 2 Aufruf- oder Pfadfehler).

```json
[
  {"level": "ERROR", "code": "E001", "set": "", "persona": "eltern-neu-in-zuerich", "message": "…"},
  {"level": "WARN", "code": "X003", "set": "elternkommunikation-schuleintritt", "persona": "", "message": "…"}
]
```
