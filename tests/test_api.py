"""Library entry points: tolerant workspace loading and lint_workspace (parity with the CLI)."""

import json
import shutil
from pathlib import Path

import pytest

from personakit.api import lint_workspace, load_workspace_tolerant
from personakit.cli import main
from personakit.lint import sort_findings
from personakit.model import PersonaError
from personakit.sets import load_workspace

ROOT = Path(__file__).resolve().parents[1]
PERSONAS = ROOT / "personas"
ELTERN = "elternkommunikation-schuleintritt"


@pytest.fixture
def broken(tmp_path: Path) -> Path:
    """Example personas plus one unreadable file, one schema violation, one broken set.yml and a fresh draft."""
    dst = tmp_path / "personas"
    shutil.copytree(PERSONAS, dst)
    (dst / ELTERN / "kaputt.persona.md").write_text("kein frontmatter\n", encoding="utf-8")
    (dst / ELTERN / "ohne-ziele.persona.md").write_text(
        '---\npersonakit: "1.0"\nid: ohne-ziele\n---\n\n## Szenario\n', encoding="utf-8"
    )
    (dst / "defektes-set").mkdir()
    (dst / "defektes-set" / "set.yml").write_text("- keine\n- mapping\n", encoding="utf-8")
    assert main(["new", "frischer-entwurf", "-a", "Frischer Entwurf ohne Inhalt", "-d", str(dst)]) == 0
    return dst


def _rows(findings):
    return [
        {"level": f.level, "code": f.code, "set": f.set_id, "persona": f.persona, "message": f.message}
        for f in sort_findings(findings)
    ]


# ---------------------------------------------------------------- tolerant loading
def test_tolerant_load_matches_strict_load_on_clean_repo():
    personas, groups = load_workspace([PERSONAS])
    ws = load_workspace_tolerant([PERSONAS])
    assert ws.problems == []
    assert [p.id for p in ws.personas] == [p.id for p in personas]
    assert [g.export() for g in ws.groups] == [g.export() for g in groups]
    assert sorted(s.id for s in ws.sets) == ["elternkommunikation-schuleintritt", "ki-leitplanken-lehrpersonen"]


def test_tolerant_load_keeps_valid_personas_and_reports_the_rest(broken: Path):
    with pytest.raises(PersonaError):
        load_workspace([broken])  # strict: one broken file stops everything
    ws = load_workspace_tolerant([broken])
    ids = {p.id for p in ws.personas}
    assert {"eltern-neu-in-zuerich", "verwaltungs-insider", "frischer-entwurf"} <= ids
    assert "ohne-ziele" not in ids
    by_code = {pr.finding.code: pr for pr in ws.problems}
    assert set(by_code) == {"P000", "SCHEMA", "X000"}
    assert by_code["P000"].path.name == "kaputt.persona.md"
    assert by_code["SCHEMA"].path.name == "ohne-ziele.persona.md"
    assert by_code["SCHEMA"].finding.persona == "ohne-ziele"
    assert by_code["X000"].path.parent.name == "defektes-set"
    assert "kaputt.persona.md" in str(by_code["P000"])
    assert [g.id for g in ws.groups if not g.is_loose] == [ELTERN, "ki-leitplanken-lehrpersonen"]


def test_tolerant_load_missing_path_is_an_error(tmp_path: Path):
    with pytest.raises(PersonaError, match="Pfad nicht gefunden"):
        load_workspace_tolerant([tmp_path / "gibt-es-nicht"])


# ---------------------------------------------------------------- lint parity
@pytest.mark.parametrize("which", ["clean", "broken"])
def test_lint_workspace_equals_cli_lint_json(which: str, broken: Path, capsys):
    root = PERSONAS if which == "clean" else broken
    capsys.readouterr()
    main(["lint", str(root), "--json"])
    cli_rows = json.loads(capsys.readouterr().out)
    assert _rows(lint_workspace([root]).findings) == cli_rows
    if which == "broken":
        assert {"P000", "SCHEMA", "X000"} <= {r["code"] for r in cli_rows}


def test_lint_workspace_reports_scope(broken: Path):
    report = lint_workspace([broken])
    assert len(report.personas) == len(load_workspace_tolerant([broken]).personas)
    assert len(report.sets) == 2  # the broken set.yml is a finding, not a set


def test_lint_workspace_single_file_skips_set_rules():
    one = next((PERSONAS / ELTERN).glob("*.persona.md"))
    report = lint_workspace([one])
    assert report.sets == [] and len(report.personas) == 1
    assert not any(f.code.startswith("X") for f in report.findings)
