"""journeykit cross-lint (K000–K004) against the examples of both repos."""

import json
import shutil
from pathlib import Path

import pytest

from personakit.api import lint_workspace
from personakit.cli import main
from personakit.lint import ERROR, INFO, WARN, sort_findings

ROOT = Path(__file__).resolve().parents[1]
PERSONAS = ROOT / "personas"
JOURNEYS = ROOT / "tests" / "fixtures" / "journeykit"
KIGA = "kindergarteneintritt"
ELTERN_SET = PERSONAS / "elternkommunikation-schuleintritt"
KI_SET = PERSONAS / "ki-leitplanken-lehrpersonen"


def _k(findings):
    return [(f.level, f.code, f.persona, f.message) for f in sort_findings(findings) if f.code.startswith("K")]


def _journey(dst: Path, name: str, jid: str, pid: str) -> Path:
    dst.mkdir(parents=True, exist_ok=True)
    path = dst / name
    path.write_text(
        json.dumps({"schema_version": "1.0", "meta": {"id": jid}, "persona": {"id": pid}}), encoding="utf-8"
    )
    return path


@pytest.fixture
def kiga(tmp_path: Path) -> Path:
    dst = tmp_path / KIGA
    shutil.copytree(JOURNEYS / KIGA, dst)
    return dst


def _set_persona(path: Path, pid: str) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    data["persona"]["id"] = pid
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def test_examples_of_both_repos():
    """Today the coupling is one-sided: the persona points to the journey, the journey names another persona."""
    report = lint_workspace([PERSONAS], journeys=[JOURNEYS])
    assert {j.id for j in report.journeys} == {
        "kindergarteneintritt-eltern",
        "kindergarteneintritt-eltern-berufstaetig",
        "baubewilligung-waermepumpe-bauherrschaft",
        "baubewilligung-waermepumpe-nachbarschaft",
    }
    assert len(report.journeys) == 5  # hypothesis and synthesis share one meta.id
    assert _k(report.findings) == [
        (
            WARN,
            "K002",
            "",
            "Journey «baubewilligung-waermepumpe-nachbarschaft» (baubewilligung/journey-nachbarschaft.json)"
            " nennt unbekannte Persona «nachbarschaft»",
        ),
        (
            WARN,
            "K002",
            "",
            "Journey «baubewilligung-waermepumpe-bauherrschaft» (baubewilligung/journey.json)"
            " nennt unbekannte Persona «erstbauherrschaft»",
        ),
        (
            WARN,
            "K002",
            "",
            "Journey «kindergarteneintritt-eltern-berufstaetig» (kindergarteneintritt/journey-berufstaetig.json)"
            " nennt unbekannte Persona «eltern-berufstaetig»",
        ),
        (
            WARN,
            "K002",
            "",
            "Journey «kindergarteneintritt-eltern» (kindergarteneintritt/journey.json)"
            " nennt unbekannte Persona «eltern-zugezogen»",
        ),
        (
            WARN,
            "K002",
            "",
            "Journey «kindergarteneintritt-eltern» (kindergarteneintritt/workshop-hypothese.json)"
            " nennt unbekannte Persona «eltern-zugezogen»",
        ),
        (
            WARN,
            "K003",
            "eltern-neu-in-zuerich",
            "Journey «kindergarteneintritt-eltern» führt Persona «eltern-zugezogen», nicht diese"
            " – persona.id der Journey oder relations.journeys korrigieren",
        ),
    ]
    # the cross-lint adds findings, it does not change the persona and set rules
    assert [f for f in report.findings if not f.code.startswith("K")] == lint_workspace([PERSONAS]).findings


def test_aligned_examples_are_clean(kiga: Path):
    """After renaming persona.id in journeykit, the persona and its journey agree in both directions."""
    for name in ("journey.json", "workshop-hypothese.json"):
        _set_persona(kiga / name, "eltern-neu-in-zuerich")
    (kiga / "journey-berufstaetig.json").unlink()  # no persona for it in personakit's examples
    assert _k(lint_workspace([PERSONAS], journeys=[kiga]).findings) == []


def test_unknown_journey():
    findings = lint_workspace([PERSONAS], journeys=[JOURNEYS / "baubewilligung"]).findings
    assert (
        WARN,
        "K001",
        "eltern-neu-in-zuerich",
        "relations.journeys verweist auf unbekannte Journey «kindergarteneintritt-eltern»",
    ) in _k(findings)


def test_missing_backlink_is_info(tmp_path: Path):
    _journey(tmp_path, "j.json", "insider-anfrage", "verwaltungs-insider")
    assert _k(lint_workspace([PERSONAS], journeys=[tmp_path]).findings) == [
        (
            WARN,
            "K001",
            "eltern-neu-in-zuerich",
            "relations.journeys verweist auf unbekannte Journey «kindergarteneintritt-eltern»",
        ),
        (
            INFO,
            "K004",
            "verwaltungs-insider",
            "Journey «insider-anfrage» führt diese Persona – in relations.journeys nachtragen",
        ),
    ]


def test_set_members_stored_elsewhere_are_known(tmp_path: Path):
    """A set folder linted alone resolves its members from the parent folder – journeys may name them."""
    _journey(tmp_path, "j.json", "ki-im-unterricht", "lehrperson-ki-explorierend")
    report = lint_workspace([KI_SET], journeys=[tmp_path])
    assert report.personas == []
    assert _k(report.findings) == []


def test_unreadable_journeys(tmp_path: Path):
    (tmp_path / "kaputt.json").write_text("{nicht json", encoding="utf-8")
    (tmp_path / "liste.json").write_text("[1, 2]", encoding="utf-8")
    (tmp_path / "ohne-persona.json").write_text('{"meta": {"id": "x"}}', encoding="utf-8")
    (tmp_path / "latin1.json").write_bytes('{"meta": {"id": "zürich"}}'.encode("latin-1"))
    (tmp_path / "journey.schema.json").write_text('{"title": "Schema"}', encoding="utf-8")  # skipped
    _journey(tmp_path / "unter ordner", "gut.json", "kindergarteneintritt-eltern", "eltern-neu-in-zuerich")
    report = lint_workspace([ELTERN_SET], journeys=[tmp_path])
    assert [j.label for j in report.journeys] == ["unter ordner/gut.json"]
    assert _k(report.findings) == [
        (ERROR, "K000", "", "Journey kaputt.json nicht lesbar: kein gültiges JSON (Zeile 1)"),
        (ERROR, "K000", "", "Journey latin1.json nicht lesbar: nicht UTF-8"),
        (ERROR, "K000", "", "Journey liste.json: meta.id oder persona.id fehlt – keine journeykit-Journey?"),
        (ERROR, "K000", "", "Journey ohne-persona.json: meta.id oder persona.id fehlt – keine journeykit-Journey?"),
    ]


def test_without_journeys_no_cross_lint():
    report = lint_workspace([PERSONAS])
    assert report.journeys == []
    assert _k(report.findings) == []


def test_cli_lint_journeys(capsys):
    args = ["lint", str(PERSONAS), "--journeys", str(JOURNEYS / KIGA), "--journeys", str(JOURNEYS / "baubewilligung")]
    assert main([*args, "--json"]) == 0
    out, err = capsys.readouterr()
    rows = json.loads(out)
    report = lint_workspace([PERSONAS], journeys=[JOURNEYS / KIGA, JOURNEYS / "baubewilligung"])
    assert rows == [
        {"level": f.level, "code": f.code, "set": f.set_id, "persona": f.persona, "message": f.message}
        for f in sort_findings(report.findings)
    ]
    assert "5 Journey(s): 0 Fehler, 6 Warnungen" in err
    assert main([*args, "--strict"]) == 1
    capsys.readouterr()
    assert main(["lint", str(PERSONAS), "--journeys", str(JOURNEYS / "fehlt")]) == 2
    assert "Pfad nicht gefunden" in capsys.readouterr().err
