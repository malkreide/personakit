"""Factoid pipeline: factoids/<study>/*.factoids.md → matrix and findings → persona skeleton."""

import json
from pathlib import Path

import pytest

from personakit.cli import main
from personakit.factoids import analyse_study, load_study, scale_value
from personakit.lint import ERROR, lint_persona
from personakit.model import Persona
from personakit.validate import validate

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "factoids" / "beispiel"
ARCHETYPE = "Neu zugezogene Eltern, die das Schulsystem von null kennenlernen"
HEAD = "| id | participant | observation | variable | value | quote |\n|---|---|---|---|---|---|\n"


def _source(folder: Path, sid: str, rows: str, n: int = 5, kind: str = "interview", extra: str = "") -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    f = folder / f"{sid}.factoids.md"
    f.write_text(
        f'---\npersonakit: "1.0"\nsource_id: {sid}\ntype: {kind}\ndate: 2026-09-01\nn: {n}\n'
        f'consent_note: "synthetisch"\n{extra}---\n\n{HEAD}{rows}',
        encoding="utf-8",
    )
    return f


def _codes(study):
    return [f.code for f in study.findings + analyse_study(study)]


# ------------------------------------------------------------- example
def test_example_study_is_valid_and_flags_thin_variable_and_outlier():
    study = load_study(EXAMPLE)
    assert [f for f in study.findings if f.level == ERROR] == []
    assert [s.source_id for s in study.sources] == ["beobachtung-website", "interviews-schuleintritt"]
    assert study.participants() == ["p1", "p2", "p3", "p4", "p5", "p6", "p7", "p8", "p9"]
    pos = study.positions()
    assert pos["Digitale Routine"]["p6"] == 4  # interview and observation combined
    assert pos["Vertrauen in offizielle Kanäle"] == {"p3": 3, "p6": 3, "p7": 1}
    findings = analyse_study(study)
    assert [(f.code, f.message.split(" ")[0]) for f in findings if f.code == "F011"] == [("F011", "p7")]
    thin = [f.message for f in findings if f.code == "F010"]
    assert len(thin) == 1 and "Vertrauen in offizielle Kanäle" in thin[0]


def test_factoids_cli_report_and_json(capsys):
    assert main(["factoids", str(EXAMPLE)]) == 0
    out = capsys.readouterr().out
    assert "## Verortung" in out and "| Digitale Routine | 3 | 5 | 3 |" in out
    assert "F010" in out and "F011" in out
    assert main(["factoids", str(EXAMPLE), "--strict"]) == 1  # F010 is a warning
    capsys.readouterr()
    assert main(["factoids", str(EXAMPLE), "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["positions"]["Deutsch (Behördensprache)"]["p2"] == 5
    assert data["variables"][0]["low"] == "kennt weder Stufen noch Zuständigkeiten"
    assert {f["code"] for f in data["findings"]} == {"F010", "F011"}


def test_no_factoid_files_is_a_usage_error(tmp_path: Path, capsys):
    _source(tmp_path / "studie", "a", "| A1 | p1 | x | | | |\n")
    assert main(["factoids", str(tmp_path)]) == 2
    assert "studie" in capsys.readouterr().err  # points to the study folder below


# ---------------------------------------------------------- parsing
def test_table_cells_escaped_pipe_and_quote_variants(tmp_path: Path):
    _source(
        tmp_path,
        "a",
        "| A1 | p1 | «Entweder \\| oder» | V | 2 | ja |\n"
        "| A2 | P-02 | Notiz | | | |\n"
        "| A3 | tn_3 | Notiz | V | 5 | x |\n"
        "| A4 | p4 | Notiz | V | 4 | nein |\n",
    )
    study = load_study(tmp_path)
    assert study.findings == []
    facts = {f.id: f for f in study.factoids()}
    assert facts["A1"].observation == "«Entweder | oder»" and facts["A1"].quote
    assert facts["A2"].participant == "P-02" and facts["A2"].value is None and not facts["A2"].quote
    assert facts["A3"].quote and facts["A3"].value == 5


@pytest.mark.parametrize(
    ("row", "code"),
    [
        ("| A1 | p1 | x | V | 7 | |\n", "F005"),  # value outside 1–5
        ("| A1 | p1 | x | | 3 | |\n", "F005"),  # value without variable
        ("| A1 | p1 | x | V | 3 | vielleicht |\n", "F005"),  # quote not a boolean
        ("| A1 | p1 | x | V | 3 |\n", "F005"),  # cell count ≠ header
        ("| A1 | | x | | | |\n", "F005"),  # empty required cell
        ("| A1 | Anna Muster | x | | | |\n", "F006"),  # a name, not a code
    ],
)
def test_invalid_rows(tmp_path: Path, row: str, code: str):
    _source(tmp_path, "a", row)
    assert code in _codes(load_study(tmp_path))


def test_name_is_not_echoed(tmp_path: Path):
    _source(tmp_path, "a", "| A1 | Anna Muster | x | | | |\n")
    msgs = " ".join(f.message for f in load_study(tmp_path).findings)
    assert "Anna" not in msgs


def test_file_level_errors(tmp_path: Path):
    _source(tmp_path / "s1", "a", "| A1 | p1 | x | | | |\n").rename(tmp_path / "s1" / "b.factoids.md")
    assert "F002" in _codes(load_study(tmp_path / "s1"))

    f = _source(tmp_path / "s2", "a", "")
    f.write_text(f.read_text(encoding="utf-8").replace('consent_note: "synthetisch"\n', ""), encoding="utf-8")
    assert "F001" in _codes(load_study(tmp_path / "s2"))

    (tmp_path / "s3").mkdir()
    (tmp_path / "s3" / "a.factoids.md").write_text("keine Datei mit Frontmatter\n", encoding="utf-8")
    assert _codes(load_study(tmp_path / "s3")) == ["F000"]

    f = _source(tmp_path / "s4", "a", "")
    f.write_text(f.read_text(encoding="utf-8").replace(HEAD, "Nur Text.\n"), encoding="utf-8")
    assert "F004" in _codes(load_study(tmp_path / "s4"))

    f = _source(tmp_path / "s5", "a", "| A1 | p1 | x | | | |\n")
    f.write_text(f.read_text(encoding="utf-8").replace("| participant |", "| teilnehmer |"), encoding="utf-8")
    assert "F004" in _codes(load_study(tmp_path / "s5"))


def test_cross_file_rules(tmp_path: Path):
    _source(tmp_path, "a", "| X1 | p1 | x | Vx | 2 | |\n| X2 | p2 | x | Vx | 2 | |\n", n=1)
    _source(tmp_path, "b", "| X1 | p3 | x | Wx | 2 | |\n")
    (tmp_path / "variables.yml").write_text('personakit: "1.0"\nvariables:\n  - name: Vx\n', encoding="utf-8")
    codes = _codes(load_study(tmp_path))
    assert "F007" in codes  # X1 twice in the study
    assert "F008" in codes  # Wx not in variables.yml
    assert "F009" in codes  # two codes, n = 1


def test_crlf_and_bom(tmp_path: Path):
    f = _source(tmp_path, "a", "| A1 | p1 | x | V | 2 | ja |\n")
    f.write_bytes(("﻿" + f.read_text(encoding="utf-8")).replace("\n", "\r\n").encode("utf-8"))
    study = load_study(tmp_path)
    assert study.findings == []
    assert study.factoids()[0].line == 12  # line in the file, frontmatter counted


def test_outlier_means_apart_from_all_others(tmp_path: Path):
    rows = "".join(
        f"| {p}{v} | {p} | x | {v} | {val} | |\n"
        for p, vals in {"p1": (1, 1), "p2": (2, 2), "p3": (5, 5), "p4": (5, 5)}.items()
        for v, val in zip(("V", "W"), vals)
    )
    _source(tmp_path, "a", rows)
    # p3 and p4 are far from p1/p2 but not from each other: a cluster, not an outlier
    assert "F011" not in _codes(load_study(tmp_path))


@pytest.mark.parametrize(("x", "want"), [(1.0, 1), (1.5, 2), (2.5, 3), (3.5, 3), (4.5, 4), (2.25, 2), (3.75, 4)])
def test_scale_value_rounds_half_towards_middle(x, want):
    assert scale_value(x) == want


# ---------------------------------------------------------- skeleton
def test_skeleton_from_example(tmp_path: Path, capsys):
    args = ["skeleton", str(EXAMPLE), "-p", "p1,p3,p4,p6,p8", "--id", "eltern-entwurf", "-a", ARCHETYPE]
    assert main([*args, "-d", str(tmp_path)]) == 0
    f = tmp_path / "eltern-entwurf.persona.md"
    p = Persona.load(f)
    assert validate(p) == []
    assert p.data["evidence_level"] == "qualitative"  # 5 participants interviewed
    assert p.data["status"] == "draft"
    values = {v["name"]: v["value"] for v in p.data["behaviour"]["variables"]}
    assert values == {
        "Vertrautheit mit dem Schulsystem": 1,
        "Digitale Routine": 3,
        "Deutsch (Behördensprache)": 2,
        "Fehlervermeidung vs. Ausprobieren": 1,
        "Vertrauen in offizielle Kanäle": 3,
    }
    assert p.data["behaviour"]["variables"][0]["low"] == "kennt weder Stufen noch Zuständigkeiten"
    ev = {e["id"]: e for e in p.data["evidence"]}
    assert (ev["E1"]["type"], ev["E1"]["n"]) == ("interview", 5)
    assert (ev["E2"]["type"], ev["E2"]["n"]) == ("observation", 2)
    assert ev["E1"]["ref"].endswith("interviews-schuleintritt.factoids.md")
    quotes = [q["text"] for q in p.data["quotes"]]
    assert len(quotes) == 3 and quotes[0] == "Ich fülle lieber nichts aus als etwas Falsches."  # outer «» removed
    assert all(q["evidence"] in ev for q in p.data["quotes"])
    # interpretation stays empty
    assert p.data["goals"]["end"] == [] and p.data["jobs"][0]["statement"] == "" and p.data["simulation"]["must"] == []
    assert "| Digitale Routine | 3 | 3 | 3–4 |" in p.body and "Zitate: I04 (p1), I09 (p3), I21 (p6)." in p.body
    assert [f for f in lint_persona(p) if f.level == ERROR] == []
    text = f.read_text(encoding="utf-8")
    assert Persona.from_text(text, f).to_text() == text  # lossless round trip
    assert "Vertrauen in offizielle Kanäle (2 von 5)" in capsys.readouterr().err

    assert main([*args, "-d", str(tmp_path)]) == 1  # exists, no --force


def test_skeleton_proto_below_five_interviews_and_frankenstein_hint(tmp_path: Path, capsys):
    args = ["skeleton", str(EXAMPLE), "-p", "p2,p5,p7", "--id", "gemischt", "-a", "Gemischte Auswahl zum Test"]
    assert main([*args, "-d", str(tmp_path)]) == 0
    p = Persona.load(tmp_path / "gemischt.persona.md")
    assert p.data["evidence_level"] == "proto"
    assert "E001" in {f.code for f in lint_persona(p)}  # proto needs assumptions – that is interpretation
    err = capsys.readouterr().err
    assert "p2 und p7" in err and "Frankenstein" in err


def test_skeleton_lists_uncovered_variables_as_unknowns(tmp_path: Path):
    study = tmp_path / "s"
    _source(study, "a", "| A1 | p1 | x | V | 2 | |\n| A2 | p2 | x | W | 4 | |\n")
    assert main(["skeleton", str(study), "-p", "p1", "--id", "x-typ", "-a", "Testtyp", "-d", str(tmp_path)]) == 0
    p = Persona.load(tmp_path / "x-typ.persona.md")
    assert [v["name"] for v in p.data["behaviour"]["variables"]] == ["V"]
    assert any("«W»" in u for u in p.data["unknowns"])


def test_skeleton_refuses_unknown_participants_and_broken_study(tmp_path: Path, capsys):
    base = ["--id", "x-typ", "-a", "Testtyp", "-d", str(tmp_path / "out")]
    assert main(["skeleton", str(EXAMPLE), "-p", "p1,p99", *base]) == 2
    assert "p99" in capsys.readouterr().err
    broken = tmp_path / "broken"
    _source(broken, "a", "| A1 | p1 | x | V | 9 | |\n")
    assert main(["skeleton", str(broken), "-p", "p1", *base]) == 1
    assert "F005" in capsys.readouterr().err
    assert not (tmp_path / "out").exists()


def test_example_folder_is_synthetic_and_whitelisted():
    for f in EXAMPLE.glob("*.factoids.md"):
        assert "BEISPIEL" in f.read_text(encoding="utf-8"), f.name
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert "factoids/*" in gitignore and "!factoids/beispiel/" in gitignore
