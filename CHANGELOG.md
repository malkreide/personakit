# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `personakit lint --json`: findings as a JSON list (`level`, `code`, `persona`, `message`) on stdout for CI and other tools; exit codes unchanged
- `personakit new` asks for the archetype interactively when `--archetype` is missing and a terminal is attached
- CI job on Windows (pytest and `lint --strict` on a CRLF checkout)
- Lint codes `P000` and `SCHEMA` documented in `docs/FORMAT.md`

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
