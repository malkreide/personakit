import json
import shutil
from pathlib import Path

import pytest

from personakit.cli import main
from personakit.lint import ERROR, lint_persona, lint_set
from personakit.model import Persona, load_many
from personakit.render import render, render_set
from personakit.validate import validate

ROOT = Path(__file__).resolve().parents[1]
PERSONAS = ROOT / "personas"


@pytest.fixture
def examples():
    return load_many([PERSONAS])


def test_examples_validate(examples):
    assert len(examples) == 4
    for p in examples:
        assert validate(p) == [], p.id


def test_examples_lint_clean(examples):
    findings = [f for p in examples for f in lint_persona(p)] + lint_set(examples)
    assert [f for f in findings if f.level == ERROR] == []
    assert sum(1 for p in examples if p.data["priority"] == "primary") == 1


def test_roundtrip_is_lossless():
    for path in PERSONAS.glob("*.persona.md"):
        src = path.read_text(encoding="utf-8")
        assert Persona.from_text(src, path).to_text() == src, path.name


@pytest.mark.parametrize("fmt", ["md", "card", "json", "yaml", "prompt"])
def test_single_renderers(examples, fmt):
    for p in examples:
        out = render(p, fmt, mode="audience")
        assert p.id in out or p.archetype in out
    data = json.loads(render(examples[0], "json"))
    assert data["id"] == examples[0].id
    assert "Szenario" in data["_body"]


def test_prompt_carries_guardrails(examples):
    p = next(x for x in examples if x.id == "eltern-neu-in-zuerich")
    sim = render(p, "prompt", mode="simulate")
    aud = render(p, "prompt", mode="audience")
    assert "Darf nicht:" in sim and "Unbekannt" in sim and "Erfinde keine Fakten" in sim
    assert "Zielpublikum" in aud and "Erlebnisziele" in aud


@pytest.mark.parametrize("fmt", ["matrix", "html", "bundle"])
def test_set_renderers(examples, fmt):
    out = render_set(examples, fmt, title="T")
    assert all(p.id in out for p in examples)


def test_new_validate_lint_bump(tmp_path: Path):
    d = tmp_path / "personas"
    assert main(["new", "test-typ", "-a", "Testender Archetyp", "-d", str(d)]) == 0
    f = d / "test-typ.persona.md"
    assert f.exists()
    assert main(["validate", str(d), "-q"]) == 0
    # fresh template: proto without assumptions → lint error
    assert main(["lint", str(d)]) == 1
    assert main(["bump", str(f), "-p", "minor", "-m", "Test"]) == 0
    p = Persona.load(f)
    assert p.data["version"] == "0.2.0"
    assert p.data["changelog"][-1]["note"] == "Test"
    assert main(["retire", str(f), "-m", "ersetzt"]) == 0
    assert Persona.load(f).data["status"] == "retired"


def test_filename_mismatch_is_error(tmp_path: Path):
    src = PERSONAS / "verwaltungs-insider.persona.md"
    dst = tmp_path / "anders.persona.md"
    shutil.copy(src, dst)
    codes = {f.code for f in lint_persona(Persona.load(dst))}
    assert "P001" in codes


def test_set_rules_two_primaries(examples):
    for p in examples:
        p.data["priority"] = "primary"
    codes = {f.code for f in lint_set(examples)}
    assert "X003" in codes
