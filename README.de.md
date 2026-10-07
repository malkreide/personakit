# personakit

![Version](https://img.shields.io/badge/version-0.1.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.10+-blue)

> Evidenzbasierte, verhaltensorientierte Personas als versionierte Markdown-Dateien – mit Jobs-to-be-Done-Block, Lint-Regeln und Prompt-Export für den Einsatz als Voreinstellung in KI-Lösungen.

🇬🇧 [English Version](README.md)

## Übersicht

Viele Lösungen – Content-Generatoren, Chat-Assistenten, User-Journey-Werkzeuge, Priorisierungen – brauchen eine Persona als Input. Meist liegt sie als Folie oder Poster vor: nicht maschinenlesbar, nicht versioniert, nicht überprüfbar. personakit macht aus einer Persona eine **Quelldatei**: `<id>.persona.md` mit schema-validiertem YAML-Frontmatter und Markdown-Body (Szenario, Narrativ). Alles andere – Markdown, Karte, JSON, YAML, Prompt-Block, Vergleichsmatrix, HTML-Galerie – wird daraus gerendert.

Das Format kodiert Methodik, nicht Layout: Verhalten vor Demografie (Cooper), Ziele als Erlebnis-, End- und Lebensziele, Jobs als Job Stories mit Wechselkräften, sichtbares Evidenzniveau, Lebenszyklus mit Review-Datum und Guardrails gegen den Varianz-Kollaps synthetischer Nutzer. Hintergrund und Designentscheide: [`docs/METHOD.md`](docs/METHOD.md). Feldreferenz und Lint-Codes: [`docs/FORMAT.md`](docs/FORMAT.md).

## Funktionen

- Eine Datei pro Persona: YAML-Frontmatter + Markdown-Body, gegen ein JSON-Schema validiert
- Verhaltensvariablen als Skalen 1–5 mit Ankern; demografische Fakten nur mit Relevanz-Begründung (Tschechows Gewehr)
- Jobs-to-be-Done-Block: Job Stories, Push/Pull/Angst/Gewohnheit, ODI-Ergebnisaussagen, Wichtigkeit und Zufriedenheit → Opportunity-Score
- Sichtbares Evidenzniveau (`proto` · `qualitative` · `statistical`) mit Quellen, Annahmen und offenen Fragen
- Lebenszyklus: SemVer, Status, Review-Datum, Changelog – `bump` und `retire` pflegen das mit sauberen Git-Diffs
- `simulation`-Block (Stimme, Muss, Darf nicht, Varianz), den der Prompt-Export im Modus `simulate` oder `audience` injiziert
- Exporte: Markdown, Karte, JSON, YAML, Prompt-Block, Vergleichsmatrix, HTML-Galerie als Single-File, JSON-Bundle
- 35 Lint-Regeln für Methodik (Evidenz-Hygiene, JTBD-Form, Guardrails, Lebenszyklus, genau eine primäre Persona pro Set)
- Claude-Skill `persona-kit`, der Personas aus Interviews, Support-Logs und Workshop-Notizen ableitet

### Demo

![HTML-Galerie der Beispiel-Personas mit Verhaltensskalen und Detailansicht](docs/demo.png)

## Voraussetzungen

- Python 3.10+
- `ruamel.yaml`, `jsonschema` (werden automatisch installiert)

## Installation

```bash
git clone https://github.com/malkreide/personakit
cd personakit
pip install -e ".[dev]"
personakit --version
```

## Verwendung / Schnellstart

```bash
# Vorlage anlegen (mit kommentierten Feldern)
personakit new eltern-neu-in-zuerich -a "Neu zugezogene Eltern, die das Schulsystem von null kennenlernen"

# Prüfen: Schema + Methodik
personakit lint personas

# Übersicht und Vergleich
personakit list personas
personakit render personas -f matrix

# Exportieren
personakit render personas/eltern-neu-in-zuerich.persona.md -f md
personakit render personas/eltern-neu-in-zuerich.persona.md -f prompt -m audience   # Zielpublikum-Voreinstellung
personakit render personas/eltern-neu-in-zuerich.persona.md -f prompt -m simulate   # synthetische Gegenprobe
personakit render personas -f html -o personas.html
personakit render personas -f bundle -o personas.json

# Pflegen
personakit bump personas/eltern-neu-in-zuerich.persona.md -p minor -m "J3 ergänzt" --review-days 180
personakit retire personas/alte-persona.persona.md -m "Durch neue Interviews ersetzt"
```

Die Beispiel-Personas in [`personas/`](personas/) sind **synthetisch** (Kontext Schulverwaltung) und dokumentieren keine reale Erhebung.

## Verfügbare Befehle

| Befehl | Beschreibung |
|---|---|
| `new <id> -a …` | Persona-Datei aus der kommentierten Vorlage anlegen; der Archetyp ist Pflicht (fehlt er, wird nachgefragt) |
| `validate <pfade>` | Frontmatter gegen das JSON-Schema prüfen |
| `lint <pfade>` | Schema plus 35 Methodik-Regeln; Exit-Code 1 bei Fehlern (`--strict` auch bei Warnungen), `--json` für CI und andere Werkzeuge |
| `render <pfade> -f …` | `md`, `card`, `json`, `yaml`, `prompt` (pro Persona) oder `matrix`, `html`, `bundle` (pro Set) |
| `list <pfade>` | Übersichtstabelle (Priorität, Status, Evidenz, Version, Review-Datum) |
| `bump <datei>` | Version erhöhen, Changelog-Eintrag schreiben, optional Status, Evidenzniveau und Review-Datum setzen |
| `retire <datei>` | Status auf `retired` setzen, mit Changelog-Notiz |

## Persona als Input für andere Lösungen

| Einsatz | Export |
|---|---|
| Content für ein Zielpublikum (Brief, Website, FAQ) | `render -f prompt -m audience` |
| Entwurf gegen eine Persona testen, Interview üben | `render -f prompt -m simulate` |
| User Journeys ([journeykit](https://github.com/malkreide/journeykit)) | `render -f json` / `-f bundle` |
| Priorisierung | `render -f matrix` (ODI-Opportunity-Score) |
| Notion, Wiki | `render -f md` / `-f card` |
| Team-Galerie, offline | `render -f html` |

Der Prompt-Export trägt die Guardrails der Persona mit: eine konkrete Einzelperson statt Durchschnitt, keine erfundenen Fakten, offene Fragen bleiben offen, Proto-Status wird als Hypothese markiert.

## Konfiguration

Keine Konfigurationsdateien. Das Schema liegt in `src/personakit/schema/persona.schema.json`, die Vorlage in `src/personakit/templates/persona.template.md`.

## Projektstruktur

```
personakit/
├── src/personakit/
│   ├── cli.py            # argparse-CLI
│   ├── model.py          # Frontmatter-Round-Trip (ruamel.yaml), Abschnitte
│   ├── validate.py       # JSON-Schema-Validierung
│   ├── lint.py           # 35 Methodik-Regeln
│   ├── render.py         # md, card, json, yaml, prompt, matrix, html, bundle
│   ├── schema/           # persona.schema.json
│   └── templates/        # persona.template.md
├── personas/             # vier synthetische Beispiel-Personas
├── skills/persona-kit/   # Claude-Skill + Erhebungsleitfaden
├── docs/                 # METHOD.md, FORMAT.md, demo.png
├── scripts/              # validate_repo.py (Repo-Strukturprüfung)
└── tests/
```

## Changelog

Siehe [CHANGELOG.md](CHANGELOG.md)

## Mitwirken

Beiträge sind willkommen — siehe [CONTRIBUTING.md](CONTRIBUTING.md).

## Sicherheit

Schwachstellen bitte wie in [SECURITY.md](SECURITY.md) beschrieben melden.

## Lizenz

MIT-Lizenz — siehe [LICENSE](LICENSE)

## Autor

Hayal Özkan · [malkreide](https://github.com/malkreide)
