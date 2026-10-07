# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
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
