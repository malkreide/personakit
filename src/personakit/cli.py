"""personakit command line interface."""

from __future__ import annotations

import argparse
import datetime as _dt
import sys
from importlib import resources
from pathlib import Path

from ruamel.yaml.scalarstring import DoubleQuotedScalarString as DQ

from . import __version__
from .lint import ERROR, WARN, Finding, lint_persona, lint_set, sort_findings
from .model import SUFFIX, Persona, PersonaError, find_persona_files, load_many, today
from .render import SET_FORMATS, SINGLE_FORMATS, render, render_list, render_set
from .validate import validate


def _out(text: str, target: str | None) -> None:
    if target:
        Path(target).parent.mkdir(parents=True, exist_ok=True)
        Path(target).write_text(text, encoding="utf-8")
        print(f"→ {target}", file=sys.stderr)
    else:
        sys.stdout.write(text)


def _print_findings(findings: list[Finding]) -> None:
    for f in sort_findings(findings):
        print(str(f))


# ------------------------------------------------------------------ commands
def cmd_new(a: argparse.Namespace) -> int:
    pid = a.id
    target_dir = Path(a.dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f"{pid}{SUFFIX}"
    if target.exists() and not a.force:
        print(f"Existiert bereits: {target} (--force zum Überschreiben)", file=sys.stderr)
        return 1
    tpl = resources.files("personakit").joinpath("templates/persona.template.md").read_text(encoding="utf-8")
    t = today()
    text = (
        tpl.replace("{{id}}", pid)
        .replace("{{archetype}}", a.archetype or "")
        .replace("{{today}}", t.isoformat())
        .replace("{{review_by}}", (t + _dt.timedelta(days=a.review_days)).isoformat())
    )
    target.write_text(text, encoding="utf-8")
    print(f"Angelegt: {target}", file=sys.stderr)
    return 0


def cmd_validate(a: argparse.Namespace) -> int:
    rc = 0
    for path in find_persona_files(a.paths):
        try:
            p = Persona.load(path)
        except PersonaError as e:
            print(f"ERROR {path}: {e}")
            rc = 1
            continue
        errs = validate(p)
        if errs:
            rc = 1
            for e in errs:
                print(f"ERROR [{p.id or path.name}] {e}")
        elif not a.quiet:
            print(f"OK    [{p.id}] {path}")
    return rc


def cmd_lint(a: argparse.Namespace) -> int:
    personas: list[Persona] = []
    findings: list[Finding] = []
    for path in find_persona_files(a.paths):
        try:
            p = Persona.load(path)
        except PersonaError as e:
            findings.append(Finding(ERROR, "P000", str(e), path.name))
            continue
        schema_errs = validate(p)
        findings.extend(Finding(ERROR, "SCHEMA", e, p.id or path.name) for e in schema_errs)
        if not schema_errs:
            findings.extend(lint_persona(p))
            personas.append(p)
    if len(personas) > 1 or any(Path(x).is_dir() for x in a.paths):
        findings.extend(lint_set(personas))
    if a.min_level == "warn":
        findings = [f for f in findings if f.level in (ERROR, WARN)]
    elif a.min_level == "error":
        findings = [f for f in findings if f.level == ERROR]
    _print_findings(findings)
    n_err = sum(1 for f in findings if f.level == ERROR)
    n_warn = sum(1 for f in findings if f.level == WARN)
    print(f"— {len(personas)} Persona(s): {n_err} Fehler, {n_warn} Warnungen", file=sys.stderr)
    if n_err or (a.strict and n_warn):
        return 1
    return 0


def cmd_render(a: argparse.Namespace) -> int:
    fmt = a.format
    if fmt in SET_FORMATS:
        personas = load_many(a.paths)
        _out(render_set(personas, fmt, title=a.title), a.output)
        return 0
    files = find_persona_files(a.paths)
    if len(files) == 1:
        p = Persona.load(files[0])
        _out(render(p, fmt, mode=a.mode), a.output)
        return 0
    # several personas → one file each into --output dir (or stdout concatenated)
    ext = {"md": ".md", "card": ".card.md", "json": ".json", "yaml": ".yaml", "prompt": ".prompt.md"}[fmt]
    if a.output:
        outdir = Path(a.output)
        outdir.mkdir(parents=True, exist_ok=True)
        for f in files:
            p = Persona.load(f)
            (outdir / f"{p.id}{ext}").write_text(render(p, fmt, mode=a.mode), encoding="utf-8")
        print(f"→ {len(files)} Dateien in {outdir}", file=sys.stderr)
    else:
        for f in files:
            sys.stdout.write(render(Persona.load(f), fmt, mode=a.mode) + "\n")
    return 0


def cmd_list(a: argparse.Namespace) -> int:
    personas = load_many(a.paths)
    _out(render_list(personas), a.output)
    return 0


def cmd_bump(a: argparse.Namespace) -> int:
    p = Persona.load(a.path)
    major, minor, patch = (int(x) for x in str(p.data.get("version", "0.0.0")).split("."))
    if a.part == "major":
        major, minor, patch = major + 1, 0, 0
    elif a.part == "minor":
        minor, patch = minor + 1, 0
    else:
        patch += 1
    new_v = f"{major}.{minor}.{patch}"
    t = today()
    p.data["version"] = DQ(new_v)
    p.data["updated"] = t
    if a.status:
        p.data["status"] = a.status
    if a.evidence_level:
        p.data["evidence_level"] = a.evidence_level
    if a.review_days:
        p.data["review_by"] = t + _dt.timedelta(days=a.review_days)
    p.add_changelog(new_v, t, a.message)
    p.save()
    print(f"{p.id}: v{new_v} ({a.part}) – {a.message}", file=sys.stderr)
    return 0


def cmd_retire(a: argparse.Namespace) -> int:
    p = Persona.load(a.path)
    p.data["status"] = "retired"
    p.data["updated"] = today()
    p.add_changelog(str(p.data.get("version")), today(), f"Ruhestand: {a.message}")
    p.save()
    print(f"{p.id}: retired – {a.message}", file=sys.stderr)
    return 0


# ---------------------------------------------------------------- parser
def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="personakit", description="Evidenzbasierte Personas als versionierte Markdown-Dateien."
    )
    ap.add_argument("--version", action="version", version=f"personakit {__version__}")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("new", help="Neue Persona aus Vorlage anlegen")
    s.add_argument("id", help="Slug, z. B. eltern-neu-in-zuerich")
    s.add_argument("--archetype", "-a", default="", help="Verhaltensbasierte Bezeichnung")
    s.add_argument("--dir", "-d", default="personas", help="Zielordner (Default: personas)")
    s.add_argument("--review-days", type=int, default=180, help="Review-Frist in Tagen (Default: 180)")
    s.add_argument("--force", action="store_true")
    s.set_defaults(func=cmd_new)

    s = sub.add_parser("validate", help="Gegen JSON-Schema prüfen")
    s.add_argument("paths", nargs="+")
    s.add_argument("--quiet", "-q", action="store_true")
    s.set_defaults(func=cmd_validate)

    s = sub.add_parser("lint", help="Schema + methodische Regeln prüfen")
    s.add_argument("paths", nargs="+")
    s.add_argument("--strict", action="store_true", help="Auch bei Warnungen mit Exit-Code 1 beenden")
    s.add_argument("--min-level", choices=["info", "warn", "error"], default="info")
    s.set_defaults(func=cmd_lint)

    s = sub.add_parser("render", help="Exportieren: md|card|json|yaml|prompt (einzeln) oder matrix|html|bundle (Set)")
    s.add_argument("paths", nargs="+")
    s.add_argument("--format", "-f", choices=SINGLE_FORMATS + SET_FORMATS, default="md")
    s.add_argument("--mode", "-m", choices=["simulate", "audience"], default="simulate", help="Nur für prompt")
    s.add_argument("--title", default=None, help="Nur für html")
    s.add_argument("--output", "-o", default=None, help="Datei (einzeln/Set) oder Ordner (mehrere Einzel-Exporte)")
    s.set_defaults(func=cmd_render)

    s = sub.add_parser("list", help="Übersichtstabelle")
    s.add_argument("paths", nargs="+")
    s.add_argument("--output", "-o", default=None)
    s.set_defaults(func=cmd_list)

    s = sub.add_parser("bump", help="Version erhöhen und Changelog-Eintrag schreiben")
    s.add_argument("path")
    s.add_argument("--part", "-p", choices=["major", "minor", "patch"], default="patch")
    s.add_argument("--message", "-m", required=True, help="Was hat sich geändert?")
    s.add_argument("--status", choices=["draft", "active", "retired"], default=None)
    s.add_argument("--evidence-level", choices=["proto", "qualitative", "statistical"], default=None)
    s.add_argument("--review-days", type=int, default=None, help="review_by neu setzen (Tage ab heute)")
    s.set_defaults(func=cmd_bump)

    s = sub.add_parser("retire", help="Persona in den Ruhestand versetzen")
    s.add_argument("path")
    s.add_argument("--message", "-m", required=True)
    s.set_defaults(func=cmd_retire)
    return ap


def main(argv: list[str] | None = None) -> int:
    ap = build_parser()
    a = ap.parse_args(argv)
    try:
        return int(a.func(a))
    except PersonaError as e:
        print(f"ERROR {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
