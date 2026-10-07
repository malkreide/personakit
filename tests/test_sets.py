"""Sets per solution: personas/<set-id>/set.yml, per-set priority, per-set lint, grouped exports."""

import json
import shutil
from pathlib import Path

import pytest

from personakit.cli import main
from personakit.lint import ERROR, WARN, lint_persona, lint_set, lint_sets
from personakit.model import Persona, find_persona_files, load_many
from personakit.render import render_list, render_set
from personakit.sets import build_groups, load_sets, load_workspace

ROOT = Path(__file__).resolve().parents[1]
PERSONAS = ROOT / "personas"
ELTERN = "elternkommunikation-schuleintritt"
KI = "ki-leitplanken-lehrpersonen"


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A writable copy of the example personas with both sets."""
    dst = tmp_path / "personas"
    shutil.copytree(PERSONAS, dst)
    return dst


def _lint(root: Path):
    personas = load_many([root])
    sets, errors = load_sets([root])
    assert errors == []
    return [f for p in personas for f in lint_persona(p)] + lint_sets(personas, sets)


def _codes(findings, set_id=None):
    return {f.code for f in findings if set_id is None or f.set_id == set_id}


def _write_set(folder: Path, sid: str, members: list[str], status: str = "active") -> None:
    folder.mkdir(parents=True, exist_ok=True)
    lines = ['personakit: "1.0"', f"id: {sid}", 'title: "Testset"', f"status: {status}", "personas:"]
    for m in members:
        pid, _, prio = m.partition(":")
        lines.append(f"  - id: {pid}")
        if prio:
            lines.append(f"    priority: {prio}")
    (folder / "set.yml").write_text("\n".join(lines) + "\n", encoding="utf-8")


# ------------------------------------------------------------- examples
def test_examples_form_two_sets_without_loose_personas():
    personas, groups = load_workspace([PERSONAS])
    assert [g.id for g in groups] == [ELTERN, KI]
    eltern, ki = groups
    assert {m.persona.id: m.priority for m in eltern.members} == {
        "eltern-neu-in-zuerich": "primary",
        "schulleitung-entscheidungsorientiert": "secondary",
        "verwaltungs-insider": "negative",
    }
    lehrperson = next(m for m in ki.members if m.persona.id == "lehrperson-ki-explorierend")
    assert (lehrperson.priority, lehrperson.default, lehrperson.overridden) == ("primary", "supplemental", True)
    insider = next(m for m in ki.members if m.persona.id == "verwaltungs-insider")
    assert insider.priority == "negative" and not insider.overridden  # no priority in set.yml → default


def test_examples_lint_clean_per_set():
    findings = _lint(PERSONAS)
    assert [f for f in findings if f.level in (ERROR, WARN)] == []


def test_single_set_folder_resolves_members_stored_elsewhere(capsys):
    # the ki set folder holds only set.yml; its personas live in the eltern folder
    assert main(["lint", str(PERSONAS / KI), "--strict"]) == 0
    assert "0 Fehler, 0 Warnungen" in capsys.readouterr().err


def test_set_file_is_not_a_persona_path():
    assert find_persona_files([PERSONAS / ELTERN / "set.yml"]) == []


# ------------------------------------------------------------ priority
def test_primary_rule_runs_per_set(repo: Path):
    # same persona primary in two sets is fine; two primaries in one set is not
    _write_set(repo / "zweites-set", "zweites-set", ["eltern-neu-in-zuerich:primary"])
    assert not {"X002", "X003"} & _codes(_lint(repo))
    _write_set(repo / "zweites-set", "zweites-set", ["eltern-neu-in-zuerich:primary", "verwaltungs-insider:primary"])
    findings = _lint(repo)
    assert _codes(findings, "zweites-set") >= {"X003"}
    assert "X003" not in _codes(findings, ELTERN)


def test_set_without_primary_warns(repo: Path):
    _write_set(repo / "ohne-primaer", "ohne-primaer", ["eltern-neu-in-zuerich:secondary"])
    assert "X002" in _codes(_lint(repo), "ohne-primaer")


def test_retired_set_skips_focus_rules(repo: Path):
    _write_set(repo / "alt", "alt", ["eltern-neu-in-zuerich:secondary"], status="retired")
    assert "X002" not in _codes(_lint(repo), "alt")


def test_override_rechecks_priority_dependent_rules(repo: Path):
    # eltern has no anti_patterns: as negative persona in a set → N001 in that set only
    p = Persona.load(repo / ELTERN / "eltern-neu-in-zuerich.persona.md")
    p.data.pop("anti_patterns", None)
    p.save()
    _write_set(repo / "kontrast", "kontrast", ["verwaltungs-insider:primary", "eltern-neu-in-zuerich:negative"])
    findings = _lint(repo)
    n001 = [f for f in findings if f.code == "N001"]
    assert [(f.set_id, f.persona) for f in n001] == [("kontrast", "eltern-neu-in-zuerich")]
    assert "in diesem Set negative" in n001[0].message


def test_override_to_non_negative_rechecks_proto_active(repo: Path):
    # verwaltungs-insider (default negative, active, proto) as primary → E002 in that set
    _write_set(repo / "umgekehrt", "umgekehrt", ["verwaltungs-insider:primary"])
    assert "E002" in _codes(_lint(repo), "umgekehrt")
    assert "E002" not in _codes([f for f in _lint(repo) if not f.set_id])


# ----------------------------------------------------------- loose set
def test_personas_without_set_form_the_loose_set(repo: Path):
    loose = repo / "lose"
    loose.mkdir()
    src = repo / ELTERN / "verwaltungs-insider.persona.md"
    text = src.read_text(encoding="utf-8").replace("id: verwaltungs-insider", "id: lose-persona")
    (loose / "lose-persona.persona.md").write_text(text, encoding="utf-8")
    _, groups = load_workspace([repo])
    assert groups[-1].is_loose and [m.persona.id for m in groups[-1].members] == ["lose-persona"]
    x002 = [f for f in _lint(repo) if f.code == "X002"]
    assert len(x002) == 1 and x002[0].set_id == "" and "ohne Set" in x002[0].message


def test_repo_without_sets_behaves_as_before(tmp_path: Path):
    for f in PERSONAS.rglob("*.persona.md"):
        shutil.copy(f, tmp_path / f.name)
    personas = load_many([tmp_path])
    groups = build_groups(personas, [])
    assert len(groups) == 1 and groups[0].is_loose
    assert {f.code for f in lint_set(personas)} == set()  # one primary among the four defaults
    assert render_list(personas).startswith("| ID |")


# --------------------------------------------------------- set.yml rules
def test_set_id_must_match_folder(repo: Path):
    _write_set(repo / "ordner", "anderer-name", ["eltern-neu-in-zuerich:primary"])
    assert "X006" in _codes(_lint(repo), "anderer-name")


def test_unknown_and_duplicate_members(repo: Path):
    _write_set(repo / "kaputt", "kaputt", ["eltern-neu-in-zuerich:primary", "gibt-es-nicht", "eltern-neu-in-zuerich"])
    codes = _codes(_lint(repo), "kaputt")
    assert {"X007", "X008"} <= codes


def test_unlisted_file_in_set_folder_warns(repo: Path):
    src = repo / ELTERN / "verwaltungs-insider.persona.md"
    text = src.read_text(encoding="utf-8").replace("id: verwaltungs-insider", "id: vergessen")
    (repo / ELTERN / "vergessen.persona.md").write_text(text, encoding="utf-8")
    x009 = [f for f in _lint(repo) if f.code == "X009"]
    assert [(f.set_id, f.persona) for f in x009] == [(ELTERN, "vergessen")]


def test_file_stored_in_other_sets_folder_is_fine():
    # lehrperson-ki-explorierend lives in the eltern folder but belongs to the ki set only
    assert "X009" not in _codes(_lint(PERSONAS))


def test_duplicate_set_id_across_roots(repo: Path, tmp_path: Path):
    other = tmp_path / "andere"
    _write_set(other / ELTERN, ELTERN, ["eltern-neu-in-zuerich:primary"])
    personas = load_many([repo])
    sets, _ = load_sets([repo, other])
    assert "X010" in {f.code for f in lint_sets(personas, sets)}


def test_broken_set_file_is_x000(repo: Path, capsys):
    (repo / KI / "set.yml").write_text('personakit: "1.0"\nid: ki-leitplanken-lehrpersonen\n', encoding="utf-8")
    assert main(["lint", str(repo), "--json"]) == 1
    rows = json.loads(capsys.readouterr().out)
    assert any(r["code"] == "X000" and r["set"] == KI for r in rows)
    # exports stop with a clear message instead of silently dropping the set
    assert main(["list", str(repo)]) == 2
    assert "set.yml" in capsys.readouterr().err


def test_finding_shows_set_and_persona():
    from personakit.lint import Finding

    assert "[s › p]" in str(Finding(WARN, "X009", "m", "p", "s"))
    assert "[s]" in str(Finding(WARN, "X002", "m", set_id="s"))


# -------------------------------------------------------------- exports
def test_list_and_matrix_are_grouped_by_set():
    personas, groups = load_workspace([PERSONAS])
    out = render_list(personas, groups)
    assert out.index("## Elternkommunikation Schuleintritt") < out.index("## KI-Leitplanken für Lehrpersonen")
    assert out.count("`schulleitung-entscheidungsorientiert`") == 2  # shared persona appears in both sets
    assert "Primär\\*" in out  # lehrperson: priority overridden in the ki set
    matrix = render_set(personas, "matrix", groups=groups)
    assert matrix.count("### Verhaltensmatrix") == 2 and "_Priorität_" in matrix


def test_bundle_contains_set_structure():
    personas, groups = load_workspace([PERSONAS])
    data = json.loads(render_set(personas, "bundle", groups=groups))
    assert [s["id"] for s in data["sets"]] == [ELTERN, KI]
    ki = data["sets"][1]
    assert ki["title"] == "KI-Leitplanken für Lehrpersonen" and ki["status"] == "draft"
    assert {"id": "lehrperson-ki-explorierend", "priority": "primary"} in ki["personas"]
    assert len(data["personas"]) == 4  # every persona once, with its default priority
    lehrperson = next(p for p in data["personas"] if p["id"] == "lehrperson-ki-explorierend")
    assert lehrperson["priority"] == "supplemental"


def test_bundle_without_sets_has_one_loose_group(tmp_path: Path):
    for f in PERSONAS.rglob("*.persona.md"):
        shutil.copy(f, tmp_path / f.name)
    personas = load_many([tmp_path])
    data = json.loads(render_set(personas, "bundle"))
    assert len(data["sets"]) == 1 and data["sets"][0]["id"] is None
    assert len(data["sets"][0]["personas"]) == 4


def test_html_carries_sets(tmp_path: Path):
    out = tmp_path / "personas.html"
    assert main(["render", str(PERSONAS), "-f", "html", "-o", str(out)]) == 0
    html = out.read_text(encoding="utf-8")
    assert "const SETS=" in html and "{{SETS}}" not in html
    assert '"id": "ki-leitplanken-lehrpersonen"' in html and "Rolle in Sets" in html
