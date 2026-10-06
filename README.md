# personakit

![Version](https://img.shields.io/badge/version-0.1.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.10+-blue)

> Evidence-based, behaviour-first personas as versioned Markdown files – with a Jobs-to-be-Done block, lint rules and a prompt export for use as a preset in AI solutions.

🇩🇪 [Deutsche Version](README.de.md)

## Overview

Many solutions – content generators, chat assistants, user-journey tools, prioritisation – need a persona as input. Usually it exists as a slide or a poster: not machine-readable, not versioned, not verifiable. personakit turns a persona into a **source file**: `<id>.persona.md` with a schema-validated YAML frontmatter and a Markdown body (scenario, narrative). Everything else – Markdown, card, JSON, YAML, prompt block, comparison matrix, HTML gallery – is rendered from it.

The format encodes method, not layout: behaviour before demographics (Cooper), goals as experience/end/life goals, jobs as job stories with forces of progress, an explicit evidence level, a lifecycle with review dates, and guardrails against the variance collapse of synthetic users. Background and design decisions: [`docs/METHOD.md`](docs/METHOD.md) (German). Field reference and lint codes: [`docs/FORMAT.md`](docs/FORMAT.md) (German).

## Features

- One file per persona: YAML frontmatter + Markdown body, validated against a JSON Schema
- Behaviour variables as 1–5 scales with anchors; demographic facts only with a stated relevance (Chekhov's gun)
- Jobs-to-be-Done block: job stories, push/pull/anxiety/habit, ODI outcome statements, importance and satisfaction → opportunity score
- Visible evidence level (`proto` · `qualitative` · `statistical`) with sources, assumptions and open questions
- Lifecycle: SemVer, status, review date, changelog – maintained by `bump` and `retire` with clean git diffs
- `simulation` block (voice, must, must_not, variance) injected into the prompt export in `simulate` or `audience` mode
- Exports: Markdown, card, JSON, YAML, prompt block, comparison matrix, single-file HTML gallery, JSON bundle
- 35 lint rules for method (evidence hygiene, JTBD form, guardrails, lifecycle, one primary persona per set)
- Claude skill `persona-kit` that derives personas from interviews, support logs and workshop notes

### Demo

![HTML gallery of the example personas with behaviour scales and detail view](docs/demo.png)

## Prerequisites

- Python 3.10+
- `ruamel.yaml`, `jsonschema` (installed automatically)

## Installation

```bash
git clone https://github.com/malkreide/personakit
cd personakit
pip install -e ".[dev]"
personakit --version
```

## Usage / Quickstart

```bash
# scaffold a persona (template with commented fields)
personakit new parents-new-in-town -a "Newly arrived parents learning the school system from scratch"

# check: schema + method rules
personakit lint personas

# overview and comparison
personakit list personas
personakit render personas -f matrix

# export
personakit render personas/eltern-neu-in-zuerich.persona.md -f md
personakit render personas/eltern-neu-in-zuerich.persona.md -f prompt -m audience   # target-audience preset
personakit render personas/eltern-neu-in-zuerich.persona.md -f prompt -m simulate   # synthetic counter-check
personakit render personas -f html -o personas.html
personakit render personas -f bundle -o personas.json

# maintain
personakit bump personas/eltern-neu-in-zuerich.persona.md -p minor -m "added J3" --review-days 180
personakit retire personas/old-persona.persona.md -m "replaced after new interviews"
```

The example personas in [`personas/`](personas/) are **synthetic** (German, school-administration context) and do not document any real research.

## Available Commands

| Command | Description |
|---|---|
| `new <id>` | Create a persona file from the commented template |
| `validate <paths>` | Validate the frontmatter against the JSON Schema |
| `lint <paths>` | Schema plus 35 method rules; exit code 1 on errors (`--strict` also on warnings) |
| `render <paths> -f …` | `md`, `card`, `json`, `yaml`, `prompt` (per persona) or `matrix`, `html`, `bundle` (per set) |
| `list <paths>` | Overview table (priority, status, evidence, version, review date) |
| `bump <file>` | Raise the version, write a changelog entry, optionally change status, evidence level and review date |
| `retire <file>` | Set status to `retired` with a changelog note |

## Persona as input for other solutions

| Use | Export |
|---|---|
| Content for a target audience (letters, web copy, FAQ) | `render -f prompt -m audience` |
| Test a draft against a persona, rehearse an interview | `render -f prompt -m simulate` |
| User journeys ([journeykit](https://github.com/malkreide/journeykit)) | `render -f json` / `-f bundle` |
| Prioritisation | `render -f matrix` (ODI opportunity score) |
| Notion, wiki | `render -f md` / `-f card` |
| Team gallery, offline | `render -f html` |

The prompt export carries the persona's guardrails: one concrete individual instead of an average, no invented facts, open questions stay open, proto status is marked as a hypothesis.

## Configuration

No configuration files. The schema lives in `src/personakit/schema/persona.schema.json`, the template in `src/personakit/templates/persona.template.md`.

## Project Structure

```
personakit/
├── src/personakit/
│   ├── cli.py            # argparse CLI
│   ├── model.py          # frontmatter round-trip (ruamel.yaml), sections
│   ├── validate.py       # JSON-Schema validation
│   ├── lint.py           # 35 method rules
│   ├── render.py         # md, card, json, yaml, prompt, matrix, html, bundle
│   ├── schema/           # persona.schema.json
│   └── templates/        # persona.template.md
├── personas/             # four synthetic example personas
├── skills/persona-kit/   # Claude skill + elicitation guide
├── docs/                 # METHOD.md, FORMAT.md, demo.png
├── scripts/              # validate_repo.py (repo structure check)
└── tests/
```

## Changelog

See [CHANGELOG.md](CHANGELOG.md)

## Contributing

Contributions are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).

## Security

Please report vulnerabilities as described in [SECURITY.md](SECURITY.md).

## License

MIT License — see [LICENSE](LICENSE)

## Author

Hayal Özkan · [malkreide](https://github.com/malkreide)
