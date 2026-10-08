"""Collapse probe: plan from personas → answers from a model → similarity per pair, must_not, unknowns."""

import json
import shutil
from pathlib import Path

import pytest

from personakit.cli import main
from personakit.model import Persona
from personakit.probe import (
    CLAIM,
    GREEN,
    NOT_OPEN,
    OPEN,
    RED,
    YELLOW,
    build_plan,
    cosine,
    evaluate,
    keywords_template,
    load_keywords,
    render_report,
    tfidf,
    tokenize,
)
from personakit.render import render_prompt
from personakit.validate import validate_probe_answers, validate_probe_keywords, validate_probe_plan

ROOT = Path(__file__).resolve().parents[1]
SET = ROOT / "personas" / "elternkommunikation-schuleintritt"
FIXTURES = Path(__file__).parent / "fixtures" / "probe"
E, S, V = "eltern-neu-in-zuerich", "schulleitung-entscheidungsorientiert", "verwaltungs-insider"


@pytest.fixture(scope="module")
def plan(tmp_path_factory) -> dict:
    out = tmp_path_factory.mktemp("probe") / "probe.json"
    assert main(["probe", "build", str(SET), "-n", "6", "-o", str(out)]) == 0
    return json.loads(out.read_text(encoding="utf-8"))


def _answers(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def _pair(result, a: str, b: str):
    return next(p for p in result.pairs if {p.a, p.b} == {a, b})


def _codes(result) -> list[str]:
    return [f.code for f in result.findings]


# ----------------------------------------------------------------- build
def test_plan_from_set_folder_takes_set_members_and_six_questions_each(plan):
    assert validate_probe_plan(plan) == []
    assert [p["id"] for p in plan["personas"]] == [E, S, V]  # lehrperson-ki-explorierend lies there, but in no set
    assert plan["sets"] == ["elternkommunikation-schuleintritt"]
    by_origin: dict = {}
    for q in plan["questions"]:
        by_origin.setdefault(q["origin"], []).append(q["ref"])
    assert by_origin[E] == ["S1", "J1", "J2", "J3", "U1", "P1"]
    assert by_origin[S] == ["S1", "J1", "J2", "U1", "P1", "P2"]
    assert by_origin[V] == ["S1", "U1", "P1", "G1"]  # negative persona: no jobs …
    assert by_origin[None] == ["X1", "X2"]  # … filled up with generic questions, shared once


def test_plan_asks_everyone_except_unknowns_and_uses_the_simulate_prompt(plan):
    for q in plan["questions"]:
        expected = [q["origin"]] if q["kind"] == "unknown" else [E, S, V]
        assert q["ask"] == expected
    persona = Persona.load(SET / f"{E}.persona.md")
    entry = plan["personas"][0]
    assert entry["prompt"] == render_prompt(persona, mode="simulate")
    assert [r["id"] for r in entry["must_not"]] == ["N1", "N2", "N3"]
    assert entry["unknowns"][0] == {"id": "U1", "text": persona.get("unknowns")[0]}


def test_job_questions_give_the_situation_but_not_the_motivation(plan):
    job = next(q for q in plan["questions"] if q["id"] == f"{E}.J1")
    assert "Wenn ich einen Brief vom Schulamt erhalte …" in job["text"]
    assert "damit" not in job["text"] and "Frist" not in job["text"]


def test_plan_is_deterministic_and_its_id_follows_the_content():
    personas = [Persona.load(SET / f"{pid}.persona.md") for pid in (E, S, V)]
    a = build_plan(personas, questions=8)
    assert a == build_plan(personas, questions=8)
    assert a["plan_id"] != build_plan(personas, questions=7)["plan_id"]
    assert a["plan_id"] != build_plan(personas[:2], questions=8)["plan_id"]
    for n in (6, 10):
        mine = [q for q in build_plan(personas, questions=n)["questions"] if q["origin"] == E]
        assert len(mine) <= n
    with pytest.raises(ValueError):
        build_plan(personas, questions=11)


def test_question_count_outside_6_to_10_is_rejected_by_the_cli():
    with pytest.raises(SystemExit):
        main(["probe", "build", str(SET), "-n", "5"])


def test_build_needs_two_personas_and_skips_retired(tmp_path, capsys):
    assert main(["probe", "build", str(SET / f"{E}.persona.md")]) == 2
    assert "mindestens zwei" in capsys.readouterr().err
    folder = tmp_path / "set"
    shutil.copytree(SET, folder)
    assert main(["retire", str(folder / f"{V}.persona.md"), "-m", "Test"]) == 0
    out = tmp_path / "probe.json"
    assert main(["probe", "build", str(folder), "-o", str(out)]) == 0
    err = capsys.readouterr().err
    assert "im Ruhestand" in err and V in err
    assert [p["id"] for p in json.loads(out.read_text(encoding="utf-8"))["personas"]] == [E, S]


def test_loose_persona_joins_when_its_file_is_named(tmp_path):
    out = tmp_path / "probe.json"
    lehrperson = SET / "lehrperson-ki-explorierend.persona.md"

    def ids(*paths) -> list[str]:
        assert main(["probe", "build", *map(str, paths), "-o", str(out)]) == 0
        return [p["id"] for p in json.loads(out.read_text(encoding="utf-8"))["personas"]]

    assert ids(SET, lehrperson) == [E, S, V, "lehrperson-ki-explorierend"]  # the set, plus the file named outright
    assert ids(SET / f"{E}.persona.md", lehrperson) == [E, "lehrperson-ki-explorierend"]  # files only: no set


def test_templates_are_valid_and_never_overwritten(tmp_path, capsys):
    answers, kw, out = tmp_path / "answers.json", tmp_path / "kw.yml", tmp_path / "probe.json"
    args = ["probe", "build", str(SET), "-n", "6", "-o", str(out), "--answers-template", str(answers)]
    assert main(args + ["--keywords-template", str(kw)]) == 0
    template = json.loads(answers.read_text(encoding="utf-8"))
    plan = json.loads(out.read_text(encoding="utf-8"))
    assert validate_probe_answers(template) == []
    assert template["plan_id"] == plan["plan_id"]
    assert sum(len(v) for v in template["answers"].values()) == 48  # 15 shared × 3 + 3 unknowns
    data = load_keywords(kw)
    assert validate_probe_keywords(data) == []
    assert data["must_not"][E] == {"N1": [], "N2": [], "N3": []}
    assert "# Keine Kenntnis von Zuständigkeiten" in kw.read_text(encoding="utf-8")
    answers.write_text("gefüllt", encoding="utf-8")
    assert main(args) == 2
    assert "existiert bereits" in capsys.readouterr().err
    assert answers.read_text(encoding="utf-8") == "gefüllt"
    assert main(args + ["--force"]) == 0


def test_build_with_samples_writes_lists(tmp_path):
    answers = tmp_path / "answers.json"
    assert (
        main(
            [
                "probe",
                "build",
                str(SET),
                "--samples",
                "3",
                "-o",
                str(tmp_path / "p.json"),
                "--answers-template",
                str(answers),
            ]
        )
        == 0
    )
    first = next(iter(json.loads(answers.read_text(encoding="utf-8"))["answers"][E].values()))
    assert first == ["", "", ""]


# ------------------------------------------------------------- similarity
def test_tokenize_drops_stop_words_and_trims_endings():
    assert tokenize("Ich frage in der Gruppe nach, die Gruppen fragen zurück.") == [
        "frag",
        "grupp",
        "grupp",
        "frag",
        "zurück",
    ]
    assert tokenize("Straße") == tokenize("Strasse")


def test_tfidf_cosine_identical_and_disjoint():
    a, b, c = tfidf([["brief", "frist"], ["brief", "frist"], ["konto", "login"]])
    assert cosine(a, b) == pytest.approx(1.0)
    assert cosine(a, c) == 0.0


# ---------------------------------------------------------------- evaluate
def test_collapse_is_flagged_red_and_distinct_personas_stay_green(plan):
    keywords = load_keywords(FIXTURES / "keywords.yml")
    collapse = evaluate(plan, _answers("answers-collapse.json"), keywords)
    pair = _pair(collapse, E, S)
    assert pair.light == RED
    assert pair.shared == 15 and pair.mean >= 0.5
    assert collapse.pairs[0] is pair  # red first
    assert _pair(collapse, E, V).light == GREEN and _pair(collapse, S, V).light == GREEN
    assert "Q010" in _codes(collapse)
    top = pair.top_question
    both = (collapse.texts[(E, top)][0] + " " + collapse.texts[(S, top)][0]).lower()
    assert pair.top_terms and all(t in both for t in pair.top_terms)

    distinct = evaluate(plan, _answers("answers-distinct.json"), keywords)
    assert {p.light for p in distinct.pairs} == {GREEN}
    assert all(p.mean < 0.3 for p in distinct.pairs)
    assert "Q010" not in _codes(distinct) and "Q011" not in _codes(distinct)


def test_paraphrased_collapse_scores_lower_than_copied_collapse(plan):
    """The lexical proxy in numbers: same stance in other words is barely seen."""
    pair = _pair(evaluate(plan, _answers("answers-collapse.json")), E, S)
    copied = pair.similarity[f"{S}.J1"]
    paraphrased = pair.similarity[f"{E}.S1"]
    assert copied > 0.9 and paraphrased < 0.5


def test_must_not_hits_with_keywords_and_unchecked_rules(plan):
    keywords = load_keywords(FIXTURES / "keywords.yml")
    collapse = evaluate(plan, _answers("answers-collapse.json"), keywords)
    n1 = next(c for c in collapse.rules if c.persona == E and c.id == "N1")
    assert [(h.question, h.keyword, h.in_question) for h in n1.hits] == [(f"{E}.S1", "Kreisschulbehörde", True)]
    distinct = evaluate(plan, _answers("answers-distinct.json"), keywords)
    n2 = next(c for c in distinct.rules if c.persona == E and c.id == "N2")
    assert {h.keyword for h in n2.hits} == {"Tagesstruktur", "Einschulung"}  # named as not understood: a hit, not proof
    unchecked = {(c.persona, c.id) for c in distinct.rules if not c.checked}
    assert unchecked == {(E, "N3"), (V, "N1")}
    q005 = [f.subject for f in distinct.findings if f.code == "Q005"]
    assert sorted(q005) == sorted([E, V])
    without = evaluate(plan, _answers("answers-distinct.json"))
    assert all(not c.checked for c in without.rules) and "Q012" not in _codes(without)


def test_unknowns_open_not_open_and_claim(plan):
    distinct = {u.persona: u.status for u in evaluate(plan, _answers("answers-distinct.json")).unknowns}
    assert distinct == {E: OPEN, S: OPEN, V: CLAIM}
    collapse = {u.persona: u.status for u in evaluate(plan, _answers("answers-collapse.json")).unknowns}
    assert collapse == {E: CLAIM, S: NOT_OPEN, V: CLAIM}
    custom = evaluate(
        plan, _answers("answers-collapse.json"), {"personakit_probe_keywords": "1.0", "open_markers": ["in der regel"]}
    )
    assert {u.persona: u.status for u in custom.unknowns}[S] == OPEN


def test_sharp_s_matches_swiss_spelling_in_markers_and_keywords(plan):
    answers = _answers("answers-distinct.json")
    answers["answers"][V][f"{V}.U1"] = "Ich weiß es nicht genau."
    answers["answers"][E][f"{E}.J1"] = "Ich frage bei der Strasse nach."
    keywords = {"personakit_probe_keywords": "1.0", "must_not": {E: {"N1": ["Straße"]}}}
    result = evaluate(plan, answers, keywords)
    assert {u.persona: u.status for u in result.unknowns}[V] == OPEN
    assert [h.question for c in result.rules for h in c.hits] == [f"{E}.J1"]


def test_samples_measure_separation_and_variance(plan):
    """Two personas drawing from the same pool are as close to each other as to themselves."""
    base = _answers("answers-collapse.json")["answers"]
    pool = [base[E], base[S], base[V]]
    answers: dict = {E: {}, S: {}, V: {}}
    for q in plan["questions"]:
        variants = [p.get(q["id"]) for p in pool if p.get(q["id"])]
        for pid in q["ask"]:
            if pid == V:
                answers[pid][q["id"]] = [base[V][q["id"]]] * 3  # always the same words
            else:
                answers[pid][q["id"]] = variants[:3]
    result = evaluate(plan, {"personakit_probe_answers": "1.0", "answers": answers})
    pair = _pair(result, E, S)
    assert pair.separation is not None and pair.separation <= 0
    assert pair.light == RED
    assert result.variance[V] == pytest.approx(1.0)
    assert [f.subject for f in result.findings if f.code == "Q015"] == [V]


def test_missing_extra_empty_and_stale_answers_are_reported(plan):
    answers = _answers("answers-distinct.json")
    answers["plan_id"] = "veraltet"
    del answers["answers"][S][f"{E}.J1"]
    answers["answers"][E][f"{E}.J2"] = "   "
    answers["answers"][E]["X1"] = "Wem vertraust du?"  # only words of the question
    answers["answers"]["unbekannt"] = {"X1": "…"}
    answers["answers"][V][f"{E}.U1"] = "nicht gefragt"
    result = evaluate(plan, answers)
    by_code = {}
    for f in result.findings:
        by_code.setdefault(f.code, []).append(f)
    assert "Q001" in by_code
    assert [f.subject for f in by_code["Q002"]] == [S] and f"{E}.J1" in by_code["Q002"][0].message
    assert "unbekannt" in by_code["Q003"][0].message and f"{V}/{E}.U1" in by_code["Q003"][0].message
    q004 = " ".join(f.message for f in by_code["Q004"])
    assert f"{E}.J2" in q004 and "X1" in q004
    assert _pair(result, E, S).shared == 12  # J1 missing for S, J2 empty and X1 hollow for E


def test_keywords_for_unknown_persona_or_rule_are_reported(plan):
    keywords = {"personakit_probe_keywords": "1.0", "must_not": {"niemand": {"N1": ["x"]}, E: {"N9": ["x"]}}}
    result = evaluate(plan, _answers("answers-distinct.json"), keywords)
    messages = [f.message for f in result.findings if f.code == "Q006"]
    assert len(messages) == 2 and any("niemand" in m for m in messages) and any("N9" in m for m in messages)


def test_report_has_light_table_examples_and_limits(plan):
    result = evaluate(plan, _answers("answers-collapse.json"), load_keywords(FIXTURES / "keywords.yml"))
    md = render_report(result, "probe.json", "answers.json")
    assert "| eltern-neu-in-zuerich ↔ schulleitung-entscheidungsorientiert | 🔴 rot |" in md
    assert "## Ähnlichste Antworten" in md and "Tragende Wörter" in md
    assert "## Grenzen der Methode" in md and "grober Proxy" in md and "Fidelity Gap" in md
    assert "Wort steht auch in der Frage" in md
    assert "konkrete Angabe ohne Vorbehalt" in md
    assert md.index("## Ampel pro Persona-Paar") < md.index("## Grenzen der Methode")


def test_keywords_template_lists_every_rule(plan):
    text = keywords_template(plan)
    assert text.count(": []") == sum(len(p["must_not"]) for p in plan["personas"])


# --------------------------------------------------------------------- cli
def test_cli_evaluate_markdown_json_and_exit_codes(plan, tmp_path, capsys):
    plan_file = tmp_path / "probe.json"
    plan_file.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
    collapse, distinct = FIXTURES / "answers-collapse.json", FIXTURES / "answers-distinct.json"
    kw = FIXTURES / "keywords.yml"

    assert main(["probe", "evaluate", str(plan_file), str(collapse), "-k", str(kw)]) == 0
    captured = capsys.readouterr()
    assert "# Collapse-Probe – elternkommunikation-schuleintritt" in captured.out
    assert "1 rot, 0 gelb, 2 grün" in captured.err
    assert main(["probe", "evaluate", str(plan_file), str(collapse), "--strict"]) == 1
    capsys.readouterr()

    report = tmp_path / "bericht.md"
    assert main(["probe", "evaluate", str(plan_file), str(distinct), "-o", str(report)]) == 0
    assert "🟢 grün" in report.read_text(encoding="utf-8")
    capsys.readouterr()

    assert main(["probe", "evaluate", str(plan_file), str(collapse), "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["pairs"][0]["light"] == RED and data["pairs"][0]["shared"] == 15
    assert data["limits"] and data["unknowns"][0]["status"] == CLAIM

    # a lower alarm threshold turns the distinct set's closest pair at least yellow
    assert main(["probe", "evaluate", str(plan_file), str(distinct), "--warn", "0.03", "--alarm", "0.1", "--json"]) == 0
    lights = {p["light"] for p in json.loads(capsys.readouterr().out)["pairs"]}
    assert lights & {RED, YELLOW}


def test_cli_evaluate_rejects_bad_input(plan, tmp_path, capsys):
    plan_file = tmp_path / "probe.json"
    plan_file.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
    bad = tmp_path / "answers.json"
    bad.write_text('{"answers": {}}', encoding="utf-8")
    assert main(["probe", "evaluate", str(plan_file), str(bad)]) == 2
    assert "personakit_probe_answers" in capsys.readouterr().err
    bad.write_text("{kein json", encoding="utf-8")
    assert main(["probe", "evaluate", str(plan_file), str(bad)]) == 2
    assert "kein gültiges JSON" in capsys.readouterr().err
    answers = FIXTURES / "answers-distinct.json"
    assert main(["probe", "evaluate", str(plan_file), str(answers), "--warn", "0.6", "--alarm", "0.5"]) == 2
    assert main(["probe", "evaluate", str(tmp_path / "fehlt.json"), str(answers)]) == 2
    assert "Pfad nicht gefunden" in capsys.readouterr().err


def test_answers_file_with_bom_and_umlaut_path(plan, tmp_path):
    folder = tmp_path / "Prüfung Lauf 1"
    folder.mkdir()
    plan_file = folder / "probe.json"
    plan_file.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
    answers = folder / "antworten.json"
    answers.write_bytes(b"\xef\xbb\xbf" + (FIXTURES / "answers-distinct.json").read_bytes())
    assert main(["probe", "evaluate", str(plan_file), str(answers)]) == 0
