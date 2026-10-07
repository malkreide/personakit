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
| `priority` | ✔ | `primary` · `secondary` · `supplemental` · `negative` |
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
| X001 | ERROR | `id` mehrfach im Set |
| X002 | WARN | Keine primäre Persona im Set |
| X003 | WARN | Mehr als eine primäre Persona |
| X004 | INFO | Mehr als 5 aktive Personas |
| X005 | WARN | `relations.personas` verweist auf unbekannte ID |

### Maschinenlesbare Ausgabe

`personakit lint <pfade> --json` schreibt die Findings als JSON-Liste auf stdout, sortiert wie die Textausgabe; die Zusammenfassung bleibt auf stderr. `--min-level` filtert auch hier, die Exit-Codes sind dieselben (0 sauber, 1 Fehler bzw. mit `--strict` auch Warnungen, 2 Aufruf- oder Pfadfehler).

```json
[
  {"level": "ERROR", "code": "E001", "persona": "eltern-neu-in-zuerich", "message": "…"}
]
```
