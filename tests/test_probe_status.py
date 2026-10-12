"""probe status: existing runs checked against today's personas (docs/PROBE.md, «Probe-Status»)."""

import hashlib
import json
import shutil
from pathlib import Path

import pytest

from personakit.api import probe_status
from personakit.cli import main
from personakit.model import PersonaError
from personakit.probe import GREEN, evaluate, load_answers, load_keywords, load_plan
from personakit.probe_status import CURRENT, PARTIAL, STALE, UNKNOWN, render_status, status_json

ROOT = Path(__file__).resolve().parents[1]
PERSONAS = ROOT / "personas"
PROBE = ROOT / "probe"
SET = "elternkommunikation-schuleintritt"
ELTERN = "eltern-neu-in-zuerich"


@pytest.fixture
def probe_dir(tmp_path):
    """The real example run (current) and calibration stage 3 (same ids and versions, thinned prompts)."""
    d = tmp_path / "probe"
    shutil.copytree(
        PROBE / "beispiel", d / "beispiel", ignore=shutil.ignore_patterns("*.py", "*.md", "answers-sonnet.json")
    )
    shutil.copytree(
        PROBE / "kalibrierung" / "stufe-3", d / "stufe-3", ignore=shutil.ignore_patterns("*.md", "*sonnet*")
    )
    return d


@pytest.fixture
def personas_copy(tmp_path):
    d = tmp_path / "personas"
    shutil.copytree(PERSONAS, d)
    return d


def _run(st, path):
    return next(r for r in st.runs if r.answers_path == path)


def test_example_run_is_current_and_calibration_run_is_stale(probe_dir):
    st = probe_status([PERSONAS], probe_dir)
    example, stage3 = _run(st, "beispiel/answers-haiku.json"), _run(st, "stufe-3/answers-haiku.json")
    assert example.state == CURRENT and {p.state for p in example.personas} == {CURRENT}
    assert example.keywords_path == "beispiel/probe-keywords.yml"
    # same ids, same versions – only the prompt tells the deliberately thinned plan apart
    assert stage3.state == STALE and stage3.result is None
    assert {(p.plan_version == p.version, p.state) for p in stage3.personas} == {(True, STALE)}
    assert all("gleicher Version" in p.reason for p in stage3.personas)
    assert [r.answers_path for r in st.runs][0] == "beispiel/answers-haiku.json"  # current runs first


def test_status_pairs_match_probe_evaluate(probe_dir):
    """Parity: the evaluated run is exactly what probe evaluate reports for the same files."""
    st = probe_status([PERSONAS], probe_dir)
    run = _run(st, "beispiel/answers-haiku.json")
    d = probe_dir / "beispiel"
    direct = evaluate(
        load_plan(d / "probe.json"), load_answers(d / "answers-haiku.json"), load_keywords(d / "probe-keywords.yml")
    )
    assert [(p.a, p.b, p.light, p.nearness) for p in run.result.pairs] == [
        (p.a, p.b, p.light, p.nearness) for p in direct.pairs
    ]
    assert [(f.code, f.subject) for f in run.result.findings] == [(f.code, f.subject) for f in direct.findings]


def test_persona_summary_counts_only_current_runs(probe_dir):
    st = probe_status([PERSONAS], probe_dir)
    eltern = next(p for p in st.personas if p.id == ELTERN)
    assert [(r[0], r[2], r[3]) for r in eltern.runs] == [("beispiel/answers-haiku.json", GREEN, 3)]
    assert [s[0] for s in eltern.stale] == ["stufe-3/answers-haiku.json"]
    assert eltern.light == GREEN and st.hint is None


def test_version_bump_makes_a_run_partial(probe_dir, personas_copy):
    f = personas_copy / SET / f"{ELTERN}.persona.md"
    f.write_text(f.read_text(encoding="utf-8").replace('version: "1.1.0"', 'version: "1.2.0"', 1), encoding="utf-8")
    st = probe_status([personas_copy], probe_dir)
    run = _run(st, "beispiel/answers-haiku.json")
    assert run.state == PARTIAL
    eltern = next(p for p in run.personas if p.id == ELTERN)
    assert (eltern.state, eltern.reason) == (STALE, "Plan mit Version 1.1.0, heute 1.2.0")
    counted = [p for p in run.pairs() if run.is_current_pair(p)]
    assert len(run.pairs()) == 6 and len(counted) == 3 and all(ELTERN not in (p.a, p.b) for p in counted)
    summary = next(p for p in st.personas if p.id == ELTERN)
    assert summary.runs == () and "1.2.0" in summary.stale[0][1]
    assert "| eltern-neu-in-zuerich ↔" in render_status(st) and "nein (Persona veraltet)" in render_status(st)


def test_skipped_files_are_problems(probe_dir):
    (probe_dir / "lose").mkdir()
    orphan = json.loads((probe_dir / "beispiel" / "answers-haiku.json").read_text(encoding="utf-8"))
    orphan["plan_id"] = "000000000000"
    (probe_dir / "lose" / "answers.json").write_text(json.dumps(orphan), encoding="utf-8")
    (probe_dir / "lose" / "kaputt.json").write_text("{nicht json", encoding="utf-8")
    (probe_dir / "lose" / "fremd.json").write_text('{"name": "etwas anderes"}', encoding="utf-8")
    shutil.copy(probe_dir / "stufe-3" / "probe.json", probe_dir / "lose" / "probe.json")
    (probe_dir / "stufe-3" / "answers-haiku.json").unlink()
    st = probe_status([PERSONAS], probe_dir)
    msgs = {p.path: p.message for p in st.problems}
    assert "kein Plan gefunden" in msgs["lose/answers.json"]
    assert "nicht lesbar" in msgs["lose/kaputt.json"]
    assert "weder Probe-Plan noch Antwortdatei" in msgs["lose/fremd.json"]
    assert "ohne Antwortdatei" in msgs["stufe-3/probe.json"] and "ohne Antwortdatei" in msgs["lose/probe.json"]
    assert [r.answers_path for r in st.runs] == ["beispiel/answers-haiku.json"]


def test_symlink_outside_the_probe_folder_is_not_read(probe_dir, tmp_path):
    outside = tmp_path / "draussen.json"
    shutil.copy(probe_dir / "beispiel" / "answers-haiku.json", outside)
    try:
        (probe_dir / "link.json").symlink_to(outside)
    except OSError:
        pytest.skip("symlinks not available")
    st = probe_status([PERSONAS], probe_dir)
    assert any(p.path == "link.json" and "ausserhalb" in p.message for p in st.problems)
    assert len(st.runs) == 2


def test_unknown_persona_in_plan(probe_dir, personas_copy):
    (personas_copy / SET / f"{ELTERN}.persona.md").unlink()
    st = probe_status([personas_copy], probe_dir)
    eltern = next(p for p in _run(st, "beispiel/answers-haiku.json").personas if p.id == ELTERN)
    assert (eltern.state, eltern.version) == (UNKNOWN, None)


def test_filters(probe_dir):
    by_set = probe_status([PERSONAS], probe_dir, set_id="ki-leitplanken-lehrpersonen")
    assert [r.answers_path for r in by_set.runs] == ["beispiel/answers-haiku.json"]  # stage 3 names another set
    assert {p.id for p in by_set.personas} < {p.id for p in probe_status([PERSONAS], probe_dir).personas}
    by_id = probe_status([PERSONAS], probe_dir, persona_id=ELTERN)
    assert [p.id for p in by_id.personas] == [ELTERN]
    assert all(ELTERN in (p.a, p.b) for r in by_id.runs for p in r.pairs(ELTERN))
    assert all(ELTERN in (x["a"], x["b"]) for r in status_json(by_id)["runs"] for x in r["pairs"])


def test_unknown_set_id_and_missing_folder_are_errors(probe_dir, tmp_path):
    with pytest.raises(PersonaError, match="Unbekanntes Set «gibt-es-nicht».*elternkommunikation"):
        probe_status([PERSONAS], probe_dir, set_id="gibt-es-nicht")
    with pytest.raises(PersonaError, match="Unbekannte Persona"):
        probe_status([PERSONAS], probe_dir, persona_id="gibt-es-nicht")
    with pytest.raises(PersonaError, match="Probe-Ordner nicht gefunden"):
        probe_status([PERSONAS], tmp_path / "fehlt")


def test_empty_folder_gives_a_hint(tmp_path):
    (tmp_path / "leer").mkdir()
    st = probe_status([PERSONAS], tmp_path / "leer", set_id=SET)
    assert st.runs == [] and all(p.runs == () for p in st.personas)
    assert "Keine Probe-Läufe für Set «elternkommunikation-schuleintritt»" in st.hint
    assert f"personakit probe build personas/{SET}" in st.hint
    assert status_json(st)["hint"] == st.hint and "**Hinweis:**" in render_status(st)


def test_only_stale_runs_hint_says_so(tmp_path):
    d = tmp_path / "probe"
    shutil.copytree(PROBE / "kalibrierung" / "stufe-2", d, ignore=shutil.ignore_patterns("*.md"))
    st = probe_status([PERSONAS], d)
    assert "keiner passt zum heutigen Stand" in st.hint


def test_retired_personas_are_out_of_scope(probe_dir, personas_copy):
    f = personas_copy / SET / "verwaltungs-insider.persona.md"
    f.write_text(f.read_text(encoding="utf-8").replace("status: active", "status: retired", 1), encoding="utf-8")
    st = probe_status([personas_copy], probe_dir)
    assert "verwaltungs-insider" not in {p.id for p in st.personas}


def test_json_shape_puts_limits_first(probe_dir):
    data = status_json(probe_status([PERSONAS], probe_dir))
    assert list(data)[:2] == ["generator", "limits"]
    run = data["runs"][0]
    assert run["state"] == CURRENT and run["model"].startswith("claude CLI") and len(run["pairs"]) == 6
    assert {f["level"] for f in run["findings"]} <= {"WARN"}
    assert data["runs"][-1]["state"] == STALE and data["runs"][-1]["pairs"] == []
    assert "Antwort" not in json.dumps(data["personas"])  # numbers and states only, no answer texts


def test_cli_json_equals_api_and_strict(probe_dir, tmp_path, capsys):
    out = tmp_path / "status.json"
    assert main(["probe", "status", str(PERSONAS), str(probe_dir), "--json", "-o", str(out)]) == 0
    assert json.loads(out.read_text(encoding="utf-8")) == status_json(probe_status([PERSONAS], probe_dir))
    assert "4 mit aktueller Probe" in capsys.readouterr().err
    (probe_dir / "beispiel" / "answers-haiku.json").unlink()
    assert main(["probe", "status", str(PERSONAS), str(probe_dir), "--strict"]) == 1
    assert "ohne: " in capsys.readouterr().err
    assert main(["probe", "status", str(PERSONAS), str(probe_dir), "--set", "gibt-es-nicht"]) == 2


def test_status_never_writes(probe_dir):
    def digest(root: Path) -> str:
        h = hashlib.sha256()
        for f in sorted(root.rglob("*")):
            h.update(f.as_posix().encode())
            if f.is_file():
                h.update(f.read_bytes())
        return h.hexdigest()

    before = digest(probe_dir), digest(PERSONAS)
    render_status(probe_status([PERSONAS], probe_dir))
    assert (digest(probe_dir), digest(PERSONAS)) == before
