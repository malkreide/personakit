"""Calibration of the probe thresholds: washed-out personas under probe/kalibrierung/ (docs/PROBE.md, «Kalibrierung»).

Stage 0 is the full example personas, stage 3 the same generic prompt for everyone – a known, total collapse.
The ladder below is what the default thresholds were chosen for; a change to the evaluation that breaks it
needs a new calibration, not a new expectation.
"""

from collections import Counter
from pathlib import Path

import pytest

from personakit.cli import main
from personakit.probe import GREEN, RED, YELLOW, evaluate, load_answers, load_plan, render_report

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "probe" / "beispiel"
CALIBRATION = ROOT / "probe" / "kalibrierung"
STAGES = {
    0: (EXAMPLE / "probe.json", EXAMPLE / "answers-haiku.json"),
    1: (CALIBRATION / "stufe-1" / "probe.json", CALIBRATION / "stufe-1" / "answers-haiku.json"),
    2: (CALIBRATION / "stufe-2" / "probe.json", CALIBRATION / "stufe-2" / "answers-haiku.json"),
    3: (CALIBRATION / "stufe-3" / "probe.json", CALIBRATION / "stufe-3" / "answers-haiku.json"),
}


def _run(stage: int, sample: int | None = None):
    plan_path, answers_path = STAGES[stage]
    answers = load_answers(answers_path)
    if sample is not None:  # one sample per question: no nearness, absolute thresholds
        answers = {
            **answers,
            "answers": {p: {q: [v[sample]] for q, v in by.items()} for p, by in answers["answers"].items()},
        }
    return evaluate(load_plan(plan_path), answers)


@pytest.mark.parametrize("stage", [1, 2, 3])
def test_calibration_answers_are_complete_and_reports_current(stage):
    plan_path, answers_path = STAGES[stage]
    plan, answers = load_plan(plan_path), load_answers(answers_path)
    assert answers["plan_id"] == plan["plan_id"]
    given = sum(1 for by_q in answers["answers"].values() for v in by_q.values() for s in v if s.strip())
    assert given == sum(len(q["ask"]) for q in plan["questions"]) * plan["samples"]
    report = render_report(evaluate(plan, answers), "probe.json", "answers-haiku.json")
    assert (plan_path.parent / "bericht-haiku.md").read_text(encoding="utf-8") == report


@pytest.mark.parametrize(
    ("stage", "light", "low", "high"),
    [
        (0, GREEN, 0.25, 0.45),  # full personas
        (1, GREEN, 0.30, 0.48),  # without voice, quotes, patterns: lexically still apart
        (2, YELLOW, 0.50, 0.70),  # archetype only
        (3, RED, 0.90, 1.10),  # identical prompts: as close to each other as to themselves
    ],
)
def test_nearness_ladder(stage, light, low, high):
    result = _run(stage)
    assert Counter(p.light for p in result.pairs) == Counter({light: 6})
    assert all(low <= p.nearness <= high for p in result.pairs)


@pytest.mark.parametrize("sample", [0, 1, 2])
def test_one_sample_still_catches_total_collapse(sample):
    """Without a baseline only the total collapse is visible; stage 2 stays green."""
    for stage, light in ((0, GREEN), (1, GREEN), (2, GREEN), (3, RED)):
        result = _run(stage, sample)
        assert all(p.nearness is None for p in result.pairs)
        assert {p.light for p in result.pairs} == {light}, (stage, sample)
        assert "Q018" in {f.code for f in result.findings}  # says that only a total collapse is visible
    assert "Q018" not in {f.code for f in _run(2).findings}


def test_old_thresholds_missed_the_total_collapse():
    """Why the calibration was needed: with 0.30/0.50 and no nearness, identical prompts were not red."""
    result = evaluate(*(f(p) for f, p in zip((load_plan, load_answers), STAGES[3], strict=True)), warn=0.30, alarm=0.50)
    old = [p for p in result.pairs if p.mean < 0.30]
    assert len(old) == 6  # every pair below the old warning threshold


def test_sonnet_example_stays_green():
    result = evaluate(load_plan(EXAMPLE / "probe.json"), load_answers(EXAMPLE / "answers-sonnet.json"))
    assert {p.light for p in result.pairs} == {GREEN}
    assert max(p.nearness for p in result.pairs) < 0.5


def test_cli_rejects_inverted_ratio_thresholds(capsys):
    plan, answers = STAGES[3]
    assert main(["probe", "evaluate", str(plan), str(answers), "--ratio-warn", "0.9", "--ratio-alarm", "0.5"]) == 2
    assert "--ratio-warn" in capsys.readouterr().err
