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
- 41 Lint-Regeln für Methodik (Evidenz-Hygiene, JTBD-Form, Guardrails, Lebenszyklus, genau eine primäre Persona pro Set)
- Sets pro Lösung (`personas/<set>/set.yml`): Dieselbe Persona kann in mehreren Lösungen eine andere Rolle – mit anderer Priorität – spielen; die Fokus-Regeln des Linters laufen pro Set
- Factoid-Pipeline: Erhebungsmaterial als `factoids/<studie>/*.factoids.md` (nur Teilnehmer-Codes, nie Namen); `factoids` verortet die Teilnehmenden auf den Verhaltensvariablen und meldet dünne Variablen und Ausreisser, `skeleton` füllt aus gewählten Teilnehmenden ein Persona-Skelett vor (Mediane, Evidenz, Zitate, Evidenzniveau)
- Claude-Skill `persona-kit`, der Personas aus Interviews, Support-Logs und Workshop-Notizen ableitet – zählen über `factoids`/`skeleton`, deuten mit Verweis auf Factoid-IDs

### Demo

![HTML-Galerie der Beispiel-Personas, nach Set gruppiert, mit Verhaltensskalen](docs/demo.png)

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
personakit render personas/elternkommunikation-schuleintritt/eltern-neu-in-zuerich.persona.md -f md
personakit render personas/elternkommunikation-schuleintritt/eltern-neu-in-zuerich.persona.md -f prompt -m audience   # Zielpublikum-Voreinstellung
personakit render personas/elternkommunikation-schuleintritt/eltern-neu-in-zuerich.persona.md -f prompt -m simulate   # synthetische Gegenprobe
personakit render personas -f html -o personas.html
personakit render personas -f bundle -o personas.json

# Pflegen
personakit bump personas/elternkommunikation-schuleintritt/eltern-neu-in-zuerich.persona.md -p minor -m "J3 ergänzt" --review-days 180
personakit retire personas/alte-persona.persona.md -m "Durch neue Interviews ersetzt"

# Vom Erhebungsmaterial zum Skelett
personakit factoids factoids/beispiel
personakit skeleton factoids/beispiel -p p1,p3,p4,p6,p8 --id eltern-entwurf -a "Neu zugezogene Eltern, die das Schulsystem von null kennenlernen"
```

Die Beispiel-Personas in [`personas/`](personas/) sind **synthetisch** (Kontext Schulverwaltung) und dokumentieren keine reale Erhebung.

### Sets pro Lösung

Ein Set fasst die Personas einer Lösung zusammen: `personas/<set-id>/set.yml` mit `id`, `title`, `solution`, `scope`, `status` und `personas: [{id, priority}]`. Die Mitgliedschaft steht nur dort; eine Persona-Datei kann deshalb in mehreren Sets vorkommen, jeweils mit eigener Priorität. `priority` in der Persona-Datei ist der Default. Personas, die kein Set nennt, bilden ein loses Set – ein Repo ohne `set.yml` funktioniert wie bisher. Die Beispiele zeigen beides: `elternkommunikation-schuleintritt` und `ki-leitplanken-lehrpersonen` teilen sich `schulleitung-entscheidungsorientiert` und `verwaltungs-insider`, und `lehrperson-ki-explorierend` ist nur im zweiten Set primär. Details: [`docs/FORMAT.md`](docs/FORMAT.md#sets-setyml).

### Vom Erhebungsmaterial zur Persona

Zählen ist Werkzeug, Deuten nicht. Ein Studienordner `factoids/<studie>/` enthält pro Quelle eine `<source_id>.factoids.md` – Frontmatter (`source_id`, `type`, `date`, `n`, `consent_note`) und eine Tabellenzeile pro Factoid (`id`, `participant`, `observation`, `variable`, `value`, `quote`) – sowie optional `variables.yml` mit den Skalen und ihren Ankern. `personakit factoids` verortet alle Teilnehmenden auf allen Variablen und meldet dünn belegte Variablen und Teilnehmende, die auf mindestens zwei Variablen ≥ 2 Punkte von allen anderen entfernt liegen. `personakit skeleton` macht aus den gewählten Teilnehmenden einen Persona-Entwurf; welche Teilnehmenden eine Persona bilden und was Archetyp, Ziele, Jobs und Simulationsregeln sind, entscheidet der Mensch oder die Skill `persona-kit` – belegt mit Factoid-IDs. Teilnehmende erscheinen nur als Codes; reale Studienordner schliesst `.gitignore` aus, versioniert ist nur das synthetische [`factoids/beispiel/`](factoids/beispiel/). Details: [`docs/FORMAT.md`](docs/FORMAT.md#factoids-factoidsmd).

## Verfügbare Befehle

| Befehl | Beschreibung |
|---|---|
| `new <id> -a …` | Persona-Datei aus der kommentierten Vorlage anlegen; der Archetyp ist Pflicht (fehlt er, wird nachgefragt) |
| `validate <pfade>` | Frontmatter gegen das JSON-Schema prüfen |
| `lint <pfade>` | Schema plus 41 Methodik-Regeln; Exit-Code 1 bei Fehlern (`--strict` auch bei Warnungen), `--json` für CI und andere Werkzeuge |
| `render <pfade> -f …` | `md`, `card`, `json`, `yaml`, `prompt` (pro Persona) oder `matrix`, `html`, `bundle` (nach Set gruppiert) |
| `list <pfade>` | Übersichtstabelle pro Set (Priorität im Set, Status, Evidenz, Version, Review-Datum) |
| `bump <datei>` | Version erhöhen, Changelog-Eintrag schreiben, optional Status, Evidenzniveau und Review-Datum setzen |
| `retire <datei>` | Status auf `retired` setzen, mit Changelog-Notiz |
| `factoids <ordner>` | Studienordner mit `*.factoids.md` prüfen: Matrix Teilnehmer × Variable, Verteilung, dünne Variablen (F010), Ausreisser (F011); `--json` |
| `skeleton <ordner> -p … --id … -a …` | Persona-Skelett aus gewählten Teilnehmenden: Verhaltensvariablen (Median), Evidenz, Zitate, Evidenzniveau und Abschnitt `## Herleitung` mit Factoid-IDs |

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

Keine Konfigurationsdateien ausser der optionalen `set.yml` pro Set und `variables.yml` pro Factoid-Studie. Die Schemas liegen in `src/personakit/schema/` (`persona.schema.json`, `set.schema.json`, `factoids.schema.json`, `variables.schema.json`), die Vorlage in `src/personakit/templates/persona.template.md`.

## Projektstruktur

```
personakit/
├── src/personakit/
│   ├── cli.py            # argparse-CLI
│   ├── model.py          # Frontmatter-Round-Trip (ruamel.yaml), Abschnitte
│   ├── validate.py       # JSON-Schema-Validierung
│   ├── sets.py           # set.yml, Priorität pro Set, loses Set
│   ├── factoids.py       # *.factoids.md, Teilnehmer-Matrix, Persona-Skelett
│   ├── lint.py           # 41 Methodik-Regeln
│   ├── render.py         # md, card, json, yaml, prompt, matrix, html, bundle
│   ├── schema/           # Persona, Set, Factoids, Variablen (JSON Schema)
│   └── templates/        # persona.template.md
├── personas/             # vier synthetische Beispiel-Personas in zwei Sets (set.yml)
├── factoids/beispiel/    # synthetische Beispielstudie (reale Studienordner ignoriert Git)
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
