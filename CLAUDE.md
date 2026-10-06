# personakit – Hinweise für Claude Code

## Was das ist

Evidenzbasierte Personas als versionierte Dateien `personas/<id>.persona.md` (YAML-Frontmatter + Markdown-Body). Die Datei ist die Quelle der Wahrheit; Markdown, Karte, JSON, YAML, Prompt-Block, Matrix und HTML werden daraus gerendert. Methodik und Designentscheide: `docs/METHOD.md`. Felder und Lint-Codes: `docs/FORMAT.md`. Fahrplan mit fertigen Prompts: `docs/ROADMAP.md`.

Module: `model.py` (Round-Trip, Abschnitte) → `validate.py` (JSON-Schema) → `lint.py` (Methodik-Regeln) → `render.py` (Exporte) → `cli.py`.

## Gates – vor jedem Commit alle grün

```bash
pip install -e ".[dev]"
pip install -r requirements-lint.txt
python -m ruff check .
python -m ruff format --check .
pytest -q
personakit lint personas --strict
python scripts/validate_repo.py .
```

`python -m ruff` statt `ruff`: ein älteres ruff weiter vorne im PATH hat den Pin schon einmal verdeckt.

## Konventionen

- Code, Identifier und Docstrings Englisch; CLI-Ausgaben, Lint-Meldungen und Doku Deutsch in Schweizer Rechtschreibung (kein ß).
- Jede Lint-Regel hat Code, Stufe und eine Begründung, die auf einen Befund in `docs/METHOD.md` zurückgeht. Neue Regel = Eintrag in `docs/FORMAT.md` + Test.
- Schema-Änderungen: abwärtskompatible Ergänzung → Format-Version `personakit: "1.x"` erhöhen; Bruch → `2.0`. Immer `CHANGELOG.md` unter `[Unreleased]` nachführen.
- Round-Trip bleibt verlustfrei (`test_roundtrip_is_lossless`): ruamel mit `width = 4096`, keine YAML-Anker, Strings werden nicht umgebrochen. Das hält Git-Diffs lesbar.
- Beispiel-Personas bleiben synthetisch. Keine realen Erhebungen, keine Personendaten, keine internen Dokumente.
- `README.md` (EN) und `README.de.md` (DE) synchron halten, Version-Badge in beiden.
- Conventional Commits (`feat`, `fix`, `docs`, `refactor`, `test`, `chore`).
- Unter Windows/PowerShell keine `&&`-Ketten – Befehle einzeln je Zeile.

## Offen

Siehe `.github/repo-meta.yml` → `offen` (Topics, Secret Scanning, PyPI).
