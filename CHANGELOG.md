# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-10-06

### Added
- Format `personakit/1.0`: YAML frontmatter + Markdown body, JSON Schema
- CLI: `new`, `validate`, `lint`, `render`, `list`, `bump`, `retire`
- Renderers: md, card, json, yaml, prompt (simulate/audience), matrix, html, bundle
- 35 lint rules (evidence hygiene, Chekhov's gun, JTBD, simulation guardrails, lifecycle, set rules)
- Four synthetic example personas (school-administration context, German)
- Claude skill `persona-kit` with elicitation guide
- Method documentation (`docs/METHOD.md`) and format reference (`docs/FORMAT.md`)
