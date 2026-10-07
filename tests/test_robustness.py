"""Robustness for everyday use on Windows and in CI (line endings, BOM, paths, CLI edge cases)."""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from personakit.cli import main
from personakit.model import Persona, PersonaError
from personakit.validate import validate

ROOT = Path(__file__).resolve().parents[1]
PERSONAS = ROOT / "personas"
EXAMPLE = PERSONAS / "elternkommunikation-schuleintritt" / "verwaltungs-insider.persona.md"


def _lf_text() -> str:
    # bytes → str without newline translation, independent of git's autocrlf on checkout
    return EXAMPLE.read_bytes().decode("utf-8").replace("\r\n", "\n")


# ----------------------------------------------------------- 1. CRLF and BOM
@pytest.mark.parametrize(
    ("newline", "bom"),
    [("\r\n", False), ("\n", True), ("\r\n", True)],
    ids=["crlf", "bom", "crlf+bom"],
)
def test_crlf_and_bom_load_and_roundtrip(tmp_path: Path, newline: str, bom: bool):
    raw = ("﻿" if bom else "") + _lf_text().replace("\n", newline)
    f = tmp_path / EXAMPLE.name
    f.write_bytes(raw.encode("utf-8"))

    p = Persona.load(f)
    assert p.id == "verwaltungs-insider"
    assert validate(p) == []
    assert "Szenario" in p.sections
    assert not any("\r" in v for v in p.sections.values())
    assert p.to_text() == raw

    p.save()
    assert f.read_bytes() == raw.encode("utf-8")


def test_crlf_survives_bump(tmp_path: Path):
    f = tmp_path / EXAMPLE.name
    f.write_bytes(_lf_text().replace("\n", "\r\n").encode("utf-8"))
    assert main(["bump", str(f), "-m", "CRLF-Test"]) == 0
    raw = f.read_bytes()
    assert b"CRLF-Test" in raw
    assert raw.count(b"\n") == raw.count(b"\r\n")


def test_lf_file_is_saved_with_lf(tmp_path: Path):
    f = tmp_path / EXAMPLE.name
    f.write_bytes(_lf_text().encode("utf-8"))
    Persona.load(f).save()
    assert b"\r\n" not in f.read_bytes()


def test_non_utf8_file_gives_clear_error(tmp_path: Path):
    f = tmp_path / EXAMPLE.name
    f.write_bytes(_lf_text().encode("cp1252"))
    with pytest.raises(PersonaError, match="UTF-8"):
        Persona.load(f)


# ------------------------------------------------------- 2. new needs archetype
def test_new_without_archetype_fails_with_hint(tmp_path: Path, capsys, monkeypatch):
    monkeypatch.setattr(sys, "stdin", _FakeStdin(tty=False))
    assert main(["new", "ohne-archetyp", "-d", str(tmp_path)]) == 2
    err = capsys.readouterr().err
    assert "--archetype" in err and "Archetyp" in err
    assert not (tmp_path / "ohne-archetyp.persona.md").exists()


def test_new_with_too_short_archetype_fails(tmp_path: Path, capsys, monkeypatch):
    monkeypatch.setattr(sys, "stdin", _FakeStdin(tty=False))
    assert main(["new", "kurz", "-a", "ab", "-d", str(tmp_path)]) == 2
    assert "mindestens 3 Zeichen" in capsys.readouterr().err
    assert not (tmp_path / "kurz.persona.md").exists()


def test_new_asks_for_archetype_interactively(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(sys, "stdin", _FakeStdin(tty=True))
    monkeypatch.setattr("builtins.input", lambda _prompt="": "Interaktiv erfasster Archetyp")
    assert main(["new", "interaktiv", "-d", str(tmp_path)]) == 0
    p = Persona.load(tmp_path / "interaktiv.persona.md")
    assert p.archetype == "Interaktiv erfasster Archetyp"
    assert validate(p) == []


def test_new_with_quotes_in_archetype_stays_valid(tmp_path: Path):
    archetype = 'Eltern mit «wenig» "Deutsch" \\ Zeit'
    assert main(["new", "zitat", "-a", archetype, "-d", str(tmp_path)]) == 0
    p = Persona.load(tmp_path / "zitat.persona.md")
    assert p.archetype == archetype
    assert validate(p) == []


def test_new_with_invalid_id_fails(tmp_path: Path, capsys):
    assert main(["new", "Keine Slug-ID", "-a", "Gültiger Archetyp", "-d", str(tmp_path)]) == 2
    assert "id" in capsys.readouterr().err
    assert list(tmp_path.iterdir()) == []


class _FakeStdin:
    def __init__(self, tty: bool):
        self._tty = tty

    def isatty(self) -> bool:
        return self._tty


# --------------------------------------------------------------- 3. lint --json
def test_lint_json_output(tmp_path: Path, capsys):
    d = tmp_path / "personas"
    assert main(["new", "json-typ", "-a", "Testender Archetyp", "-d", str(d)]) == 0
    capsys.readouterr()
    assert main(["lint", str(d), "--json"]) == 1  # fresh template has errors → exit code unchanged
    out = capsys.readouterr().out
    findings = json.loads(out)
    assert isinstance(findings, list) and findings
    for f in findings:
        assert set(f) == {"level", "code", "set", "persona", "message"}
    assert any(f["level"] == "ERROR" and f["persona"] == "json-typ" for f in findings)


def test_lint_json_clean_examples(capsys):
    assert main(["lint", str(PERSONAS), "--json", "--strict"]) == 0
    assert json.loads(capsys.readouterr().out) == []


def test_lint_json_reports_unparsable_file(tmp_path: Path, capsys):
    (tmp_path / "kaputt.persona.md").write_text("kein frontmatter\n", encoding="utf-8")
    assert main(["lint", str(tmp_path), "--json"]) == 1
    findings = json.loads(capsys.readouterr().out)
    assert [f["code"] for f in findings] == ["P000"]


# ------------------------------------------------- 4. umlauts and spaces in paths
def test_all_commands_with_umlauts_and_spaces(tmp_path: Path, capsys):
    base = tmp_path / "Ordner mit Ümläuten" / "Persönliche Personas"
    assert main(["new", "test-typ", "-a", "Testender Archetyp", "-d", str(base)]) == 0
    f = base / "test-typ.persona.md"
    assert f.exists()
    shutil.copy(EXAMPLE, base / EXAMPLE.name)
    assert main(["validate", str(base), "-q"]) == 0
    assert main(["lint", str(base)]) == 1
    assert main(["lint", str(base / EXAMPLE.name), "--strict"]) == 0
    out = tmp_path / "Ausgabe für Grüezi"
    assert main(["render", str(base), "-f", "card", "-o", str(out)]) == 0
    assert (out / "test-typ.card.md").exists()
    assert main(["render", str(base / EXAMPLE.name), "-f", "md", "-o", str(out / "Einzel Datei.md")]) == 0
    assert main(["render", str(base), "-f", "html", "-o", str(out / "Übersicht.html")]) == 0
    assert main(["list", str(base), "-o", str(out / "Liste ä.md")]) == 0
    assert main(["bump", str(f), "-m", "Pfad mit Ümlaut"]) == 0
    assert main(["retire", str(f), "-m", "ersetzt"]) == 0
    assert Persona.load(f).data["status"] == "retired"


def test_cli_output_survives_non_utf8_console(tmp_path: Path):
    """Windows CI pipes stdout/stderr with a legacy code page; output must not crash."""
    base = tmp_path / "Ümläute und Leerzeichen"
    base.mkdir()
    shutil.copy(EXAMPLE, base / EXAMPLE.name)
    env = {**os.environ, "PYTHONIOENCODING": "cp1252", "PYTHONUTF8": "0"}
    for args in (
        ["render", str(base), "-f", "card"],
        ["render", str(base), "-f", "md", "-o", str(base / "Ausgabe ö.md")],
        ["lint", str(base)],
        ["list", str(base)],
    ):
        r = subprocess.run([sys.executable, "-m", "personakit.cli", *args], capture_output=True, env=env, check=False)
        assert r.returncode == 0, (args, r.stderr.decode("utf-8", "replace"))
    r = subprocess.run(
        [sys.executable, "-m", "personakit.cli", "render", str(base / EXAMPLE.name), "-f", "md"],
        capture_output=True,
        env=env,
        check=True,
    )
    assert "●" in r.stdout.decode("utf-8")


# ------------------------------------------------ 5. render --output on a file
def test_render_many_to_existing_file_fails_clearly(tmp_path: Path, capsys):
    target = tmp_path / "out.md"
    target.write_text("bestehend\n", encoding="utf-8")
    assert main(["render", str(PERSONAS), "-f", "md", "-o", str(target)]) == 2
    err = capsys.readouterr().err
    assert "--output" in err and "Ordner" in err
    assert target.read_text(encoding="utf-8") == "bestehend\n"


def test_render_single_to_existing_dir_fails_clearly(tmp_path: Path, capsys):
    assert main(["render", str(EXAMPLE), "-f", "md", "-o", str(tmp_path)]) == 2
    assert "Ordner" in capsys.readouterr().err
