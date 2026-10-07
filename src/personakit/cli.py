"""personakit command line interface."""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import sys
from importlib import resources
from pathlib import Path

from ruamel.yaml.scalarstring import DoubleQuotedScalarString as DQ

from . import __version__
from .lint import ERROR, WARN, Finding, lint_persona, lint_sets, sort_findings
from .model import SUFFIX, Persona, PersonaError, find_persona_files, today, write_text
from .render import SET_FORMATS, SINGLE_FORMATS, render, render_list, render_set
from .sets import Group, load_sets, load_workspace
from .validate import load_schema, validate


class UsageError(Exception):
    """Wrong or incomplete CLI arguments; reported without traceback, exit code 2."""


def _out(text: str, target: str | None) -> None:
    if target:
        path = Path(target)
        if path.is_dir():
            raise UsageError(f"--output {path} ist ein Ordner; für diesen Export einen Dateinamen angeben")
        path.parent.mkdir(parents=True, exist_ok=True)
        write_text(path, text)
        print(f"→ {target}", file=sys.stderr)
    else:
        sys.stdout.write(text)


def _print_findings(findings: list[Finding], as_json: bool = False) -> None:
    if as_json:
        rows = [
            {"level": f.level, "code": f.code, "set": f.set_id, "persona": f.persona, "message": f.message}
            for f in sort_findings(findings)
        ]
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return
    for f in sort_findings(findings):
        print(str(f))


def _warn_unresolved(groups: list[Group]) -> None:
    """Exports skip set members that cannot be resolved – say so instead of dropping them silently."""
    for g in groups:
        for pid in g.unknown:
            print(
                f"Hinweis: Set «{g.id}» nennt unbekannte oder ungültige Persona «{pid}» (Details: personakit lint)",
                file=sys.stderr,
            )


def _utf8_streams() -> None:
    """Legacy code pages (cp1252 in Windows pipes and CI logs) cannot encode ●, → or ○ – switch to UTF-8."""
    for stream in (sys.stdout, sys.stderr):
        enc = (getattr(stream, "encoding", None) or "").lower().replace("-", "").replace("_", "")
        if enc != "utf8" and hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")


def _archetype(given: str) -> str:
    """Archetype from --archetype, else asked interactively; must satisfy the schema's minLength."""
    min_len = load_schema()["properties"]["archetype"]["minLength"]
    archetype = given.strip()
    if not archetype and sys.stdin is not None and sys.stdin.isatty():
        try:
            archetype = input("Archetyp (verhaltensbasiert, z. B. «Neu zugezogene Eltern mit wenig Deutsch»): ").strip()
        except (EOFError, KeyboardInterrupt):
            archetype = ""
    if not archetype:
        raise UsageError(
            "Archetyp fehlt: --archetype/-a angeben, z. B. "
            '-a "Neu zugezogene Eltern mit wenig Deutsch" '
            f"(verhaltensbasiert, nicht demografisch; mindestens {min_len} Zeichen)"
        )
    if len(archetype) < min_len:
        raise UsageError(f"Archetyp «{archetype}» ist zu kurz: mindestens {min_len} Zeichen (--archetype/-a)")
    return archetype


# ------------------------------------------------------------------ commands
def cmd_new(a: argparse.Namespace) -> int:
    pid = a.id
    if not re.fullmatch(load_schema()["properties"]["id"]["pattern"], pid):
        raise UsageError(
            f"Ungültige id «{pid}»: nur Kleinbuchstaben, Ziffern und Bindestriche, z. B. eltern-neu-in-zuerich"
        )
    target_dir = Path(a.dir)
    target = target_dir / f"{pid}{SUFFIX}"
    if target.exists() and not a.force:
        print(f"Existiert bereits: {target} (--force zum Überschreiben)", file=sys.stderr)
        return 1
    archetype = _archetype(a.archetype)
    tpl = resources.files("personakit").joinpath("templates/persona.template.md").read_text(encoding="utf-8")
    t = today()
    text = (
        tpl.replace("{{id}}", pid)
        # the template puts the archetype in a YAML double-quoted scalar
        .replace("{{archetype}}", archetype.replace("\\", "\\\\").replace('"', '\\"'))
        .replace("{{today}}", t.isoformat())
        .replace("{{review_by}}", (t + _dt.timedelta(days=a.review_days)).isoformat())
    )
    errs = validate(Persona.from_text(text, target))
    if errs:  # safety net: never write a file that violates the schema
        raise UsageError("Vorlage ergäbe eine ungültige Persona: " + "; ".join(errs))
    target_dir.mkdir(parents=True, exist_ok=True)
    write_text(target, text)
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
    sets, set_errors = load_sets(a.paths)
    findings.extend(Finding(ERROR, "X000", msg, set_id=path.parent.name) for path, msg in set_errors)
    if sets or len(personas) > 1 or any(Path(x).is_dir() for x in a.paths):
        findings.extend(lint_sets(personas, sets))
    if a.min_level == "warn":
        findings = [f for f in findings if f.level in (ERROR, WARN)]
    elif a.min_level == "error":
        findings = [f for f in findings if f.level == ERROR]
    _print_findings(findings, as_json=a.json)
    n_err = sum(1 for f in findings if f.level == ERROR)
    n_warn = sum(1 for f in findings if f.level == WARN)
    in_sets = f" in {len(sets)} Set(s)" if sets else ""
    print(f"— {len(personas)} Persona(s){in_sets}: {n_err} Fehler, {n_warn} Warnungen", file=sys.stderr)
    if n_err or (a.strict and n_warn):
        return 1
    return 0


def cmd_render(a: argparse.Namespace) -> int:
    fmt = a.format
    if fmt in SET_FORMATS:
        personas, groups = load_workspace(a.paths)
        _warn_unresolved(groups)
        _out(render_set(personas, fmt, groups=groups, title=a.title), a.output)
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
        if outdir.exists() and not outdir.is_dir():
            raise UsageError(
                f"--output {outdir} ist eine bestehende Datei; bei {len(files)} Personas erwartet "
                f"-f {fmt} einen Ordner (je Persona eine Datei). Für eine Sammeldatei -f matrix, html oder bundle"
            )
        outdir.mkdir(parents=True, exist_ok=True)
        for f in files:
            p = Persona.load(f)
            write_text(outdir / f"{p.id}{ext}", render(p, fmt, mode=a.mode))
        print(f"→ {len(files)} Dateien in {outdir}", file=sys.stderr)
    else:
        for f in files:
            sys.stdout.write(render(Persona.load(f), fmt, mode=a.mode) + "\n")
    return 0


def cmd_list(a: argparse.Namespace) -> int:
    personas, groups = load_workspace(a.paths)
    _warn_unresolved(groups)
    _out(render_list(personas, groups), a.output)
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
    s.add_argument(
        "--archetype", "-a", default="", help="Verhaltensbasierte Bezeichnung (Pflicht; ohne Angabe wird nachgefragt)"
    )
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
    s.add_argument("--json", action="store_true", help="Findings als JSON-Liste auf stdout (für CI und Werkzeuge)")
    s.set_defaults(func=cmd_lint)

    s = sub.add_parser(
        "render", help="Exportieren: md|card|json|yaml|prompt (einzeln) oder matrix|html|bundle (nach Set gruppiert)"
    )
    s.add_argument("paths", nargs="+")
    s.add_argument("--format", "-f", choices=SINGLE_FORMATS + SET_FORMATS, default="md")
    s.add_argument("--mode", "-m", choices=["simulate", "audience"], default="simulate", help="Nur für prompt")
    s.add_argument("--title", default=None, help="Nur für html")
    s.add_argument("--output", "-o", default=None, help="Datei (einzeln/Set) oder Ordner (mehrere Einzel-Exporte)")
    s.set_defaults(func=cmd_render)

    s = sub.add_parser("list", help="Übersichtstabelle, nach Set gruppiert")
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
    _utf8_streams()
    ap = build_parser()
    a = ap.parse_args(argv)
    try:
        return int(a.func(a))
    except (PersonaError, UsageError) as e:
        print(f"ERROR {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
