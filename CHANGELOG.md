# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- journeykit coupling (P6): `personakit lint <paths> --journeys <path>` (repeatable; file or folder of journeykit `*.json`, `*.schema.json` skipped) checks references in both directions – K000 unreadable journey or missing `meta.id`/`persona.id` (ERROR), K001 `relations.journeys` names an unknown journey, K002 a journey's `persona.id` names an unknown persona, K003 a persona points to a journey that names another persona (WARN), K004 a journey names the persona but `relations.journeys` does not (INFO). personakit reads only `meta.id` and `persona.id` and does not import or validate journeykit; neither schema changes. Without `--journeys` nothing changes
- `personakit.api.lint_workspace(paths, journeys=…)` and `LintReport.journeys`; new module `personakit.journeys`
- Decision note `docs/JOURNEYKIT.md` (which journey fields name actors, why personakit owns the cross-lint, why evidence is joined by a naming convention instead of a shared file) and `docs/METHOD.md` 1.9; journeykit example journeys as test fixtures under `tests/fixtures/journeykit/`
- Notion export (P7): `personakit render <paths> -f notion [--target api|mcp]` writes JSON for a database «Personas» without network calls – one page per persona `id` (the upsert key) with the properties Name, ID, Archetyp, Set, Priorität, Status, Evidenz, Version, Review bis and Tags, plus the database definition. `api` (default) gives page bodies for `POST /v1/pages` (headings, bulleted lists, quotes, a table for the behaviour variables, toggles for evidence and assumptions); `mcp` gives the same pages as flat property values and Notion-flavored Markdown for the Notion MCP tools. API limits are kept: text split at 2000 UTF-16 units, at most 100 blocks per children array (overflow in `append` batches), two nesting levels; `mcp` escapes Notion Markdown. `Priorität` is the persona's default priority, the priority per set is listed on the page. New module `personakit.notion`; the persona format is unchanged
- Skill `persona-kit`: step «Nach Notion publizieren» – export, check the database, look up existing pages by `ID` and update them instead of creating duplicates; `docs/FORMAT.md` documents the database and both targets

### Fixed
- Notion export, checked against a real Notion database through the Notion MCP tools: the source file name in the page footer is now inline code, because Notion turned `….persona.md` into a link (`.md` is a top-level domain); `` `code` `` in body sections becomes code instead of escaped backticks; `--target mcp` lists the select and multi-select options in `database.options`, because the MCP tools reject a page whose value is not yet an option (the skill step «Nach Notion publizieren» now adds missing options first, and `docs/FORMAT.md` no longer claims Notion creates them)

## [0.2.0] - 2026-10-07

### Added
- `personakit.api` for tools that embed personakit (groundwork for `personakit-mcp`): `load_workspace_tolerant(paths)` returns valid personas, sets and groups and reports unreadable files (`P000`), schema violations (`SCHEMA`) and broken `set.yml` (`X000`) as `problems` with their path instead of stopping at the first one; `lint_workspace(paths)` returns a `LintReport` (findings, linted personas and sets) with exactly the checks of `personakit lint`
- Factoid format `factoids/<study>/<source_id>.factoids.md`: frontmatter (`source_id`, `type`, `date`, `n`, `consent_note`, optional `title`, `ref`, `note`) validated against the new `schema/factoids.schema.json`, and one Markdown table row per factoid (`id`, `participant`, `observation`, `variable`, `value` 1–5, `quote`); optional `variables.yml` per study with scales and anchors (`schema/variables.schema.json`). The persona format stays at `1.0`
- `personakit factoids <folder>`: checks a study folder (F000–F009) and reports sources, a participant × variable matrix (median per participant), the distribution per scale step, thin variables (F010) and participants ≥ 2 points apart from all others on at least two variables (F011); `--json`, `--strict`
- `personakit skeleton <folder> --participants … --id … -a …`: persona skeleton from chosen participants with `behaviour.variables` (medians, anchors), `evidence` per source, `quotes` from factoids marked as quote, `evidence_level` by number of interviews/observations (≥ 5 → `qualitative`, else `proto`), unplaced variables as `unknowns` and a `## Herleitung` section with factoid IDs; hints for thin variables and Frankenstein selections
- Data protection: participant codes only (F006 rejects anything else without echoing it), `consent_note` required, `.gitignore` excludes `factoids/*` except the synthetic `factoids/beispiel/`
- Skill `persona-kit` uses `factoids` and `skeleton` for the counting and keeps the interpretation (archetype, goals, jobs, simulation rules) with references to factoid IDs; `docs/FORMAT.md` and `docs/METHOD.md` (1.8) document format, rules and rationale
- Sets per solution: `personas/<set-id>/set.yml` (`id`, `title`, `solution`, `scope`, `status`, `owner`, `personas: [{id, priority}]`), validated against the new `schema/set.schema.json`. Membership is declared only in `set.yml`, so one persona file can belong to several sets; the priority applies per set and overrides the persona's `priority`, which becomes the default. Personas listed by no set form a loose set. The persona format stays at `1.0`, no migration needed
- Set lint: X002–X004 run per set with the effective priority (retired sets are skipped); E002, J001 and N001 are re-checked where a set overrides the priority; new codes X000 (broken `set.yml`), X006 (set id ≠ folder), X007 (unknown member), X008 (member listed twice), X009 (file in a set folder that no set lists), X010 (duplicate set id)
- Set members outside the given paths are resolved below the set folder's parent, so a single set folder can be linted or rendered on its own
- `list`, `render -f matrix` and `render -f html` are grouped by set (HTML: set filter, effective priority per card, «Rolle in Sets» in the detail view); the matrix shows the priority per persona; `render -f bundle` contains `sets` next to `personas`
- `Finding.set_id`; `lint --json` rows carry `set`
- `personakit lint --json`: findings as a JSON list (`level`, `code`, `persona`, `message`) on stdout for CI and other tools; exit codes unchanged
- `personakit new` asks for the archetype interactively when `--archetype` is missing and a terminal is attached
- CI job on Windows (pytest and `lint --strict` on a CRLF checkout)
- Lint codes `P000` and `SCHEMA` documented in `docs/FORMAT.md`

### Changed
- `personakit lint` runs through `personakit.api.lint_workspace`; output and exit codes unchanged
- The four example personas moved to `personas/elternkommunikation-schuleintritt/`; a second set `ki-leitplanken-lehrpersonen` shares two of them and makes `lehrperson-ki-explorierend` primary
- X001 and X005 are checked across all linted personas (sets reference personas by id; relations belong to the persona, not to a set)

### Fixed
- Persona files with CRLF line endings or a UTF-8 BOM load; the round trip (`bump`, `retire`) keeps line endings and BOM
- Files not encoded as UTF-8 stop with a clear message instead of a traceback
- `personakit new` without or with a too short `--archetype`, or with an invalid `id`, no longer writes a file that violates the schema; it exits with code 2 and says what is missing. Quotes in the archetype yield valid YAML
- Output containing `●`, `→` etc. no longer crashes on consoles and pipes with a legacy code page (cp1252 on Windows): stdout/stderr switch to UTF-8
- `render` with several personas and `--output` pointing to an existing file (or a single export pointing to a directory) stops with a clear message instead of a traceback
- Written files are identical on every OS (UTF-8, no silent LF→CRLF translation on Windows)

## [0.1.0] - 2026-10-06

### Added
- Format `personakit/1.0`: YAML frontmatter + Markdown body, JSON Schema
- CLI: `new`, `validate`, `lint`, `render`, `list`, `bump`, `retire`
- Renderers: md, card, json, yaml, prompt (simulate/audience), matrix, html, bundle
- 35 lint rules (evidence hygiene, Chekhov's gun, JTBD, simulation guardrails, lifecycle, set rules)
- Four synthetic example personas (school-administration context, German)
- Claude skill `persona-kit` with elicitation guide
- Method documentation (`docs/METHOD.md`) and format reference (`docs/FORMAT.md`)
