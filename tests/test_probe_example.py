"""The example runs under probe/beispiel/: valid files, and reports that match the current evaluation."""

from pathlib import Path

import pytest

from personakit.probe import evaluate, load_answers, load_keywords, load_plan, render_report

EXAMPLE = Path(__file__).resolve().parents[1] / "probe" / "beispiel"
RUNS = ("sonnet", "haiku")


@pytest.mark.parametrize("run", RUNS)
def test_example_files_are_valid_and_complete(run):
    plan = load_plan(EXAMPLE / "probe.json")
    answers = load_answers(EXAMPLE / f"answers-{run}.json")
    assert answers["plan_id"] == plan["plan_id"]
    assert run in answers["model"]
    expected = sum(len(q["ask"]) for q in plan["questions"]) * plan["samples"]
    given = sum(1 for by_q in answers["answers"].values() for v in by_q.values() for s in v if s.strip())
    assert given == expected


@pytest.mark.parametrize("run", RUNS)
def test_example_reports_are_current(run):
    """Regenerate with: personakit probe evaluate probe.json answers-<run>.json -k probe-keywords.yml -o bericht-<run>.md"""
    result = evaluate(
        load_plan(EXAMPLE / "probe.json"),
        load_answers(EXAMPLE / f"answers-{run}.json"),
        load_keywords(EXAMPLE / "probe-keywords.yml"),
    )
    report = render_report(result, "probe.json", f"answers-{run}.json")
    assert (EXAMPLE / f"bericht-{run}.md").read_text(encoding="utf-8") == report
