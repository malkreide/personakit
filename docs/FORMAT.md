# Format-Referenz `*.persona.md`

Eine Persona ist eine Markdown-Datei `<id>.persona.md` mit YAML-Frontmatter (strukturiert, gegen `schema/persona.schema.json` validiert) und einem Markdown-Body (Szenario, Narrativ). Alle anderen Formate werden daraus gerendert.

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
