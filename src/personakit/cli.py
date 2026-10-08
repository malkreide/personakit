"""personakit command line interface."""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import sys
from collections import Counter
from importlib import resources
from pathlib import Path

from ruamel.yaml.scalarstring import DoubleQuotedScalarString as DQ

from . import __version__
from .api import lint_workspace
from .factoids import analyse_study, build_skeleton, load_study, render_report, report_json
from .factoids import sort_findings as sort_factoid_findings
from .lint import ERROR, WARN, Finding, sort_findings
from .model import SUFFIX, Persona, PersonaError, find_persona_files, today, write_text
from .probe import answers_template, build_plan, evaluate, keywords_template, load_answers, load_keywords, load_plan
from .probe import render_report as render_probe_report
from .probe import report_json as probe_report_json
from .probe import runs as probe_runs
from .render import SET_FORMATS, SINGLE_FORMATS, render, render_list, render_set
from .sets import Group, group_personas, load_workspace
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
def _check_id(pid: str) -> None:
    if not re.fullmatch(load_schema()["properties"]["id"]["pattern"], pid):
        raise UsageError(
            f"Ungültige id «{pid}»: nur Kleinbuchstaben, Ziffern und Bindestriche, z. B. eltern-neu-in-zuerich"
        )


def _template_text(pid: str, archetype: str, review_days: int) -> str:
    tpl = resources.files("personakit").joinpath("templates/persona.template.md").read_text(encoding="utf-8")
    t = today()
    return (
        tpl.replace("{{id}}", pid)
        # the template puts the archetype in a YAML double-quoted scalar
        .replace("{{archetype}}", archetype.replace("\\", "\\\\").replace('"', '\\"'))
        .replace("{{today}}", t.isoformat())
        .replace("{{review_by}}", (t + _dt.timedelta(days=review_days)).isoformat())
    )


def _write_persona(target: Path, text: str) -> None:
    errs = validate(Persona.from_text(text, target))
    if errs:  # safety net: never write a file that violates the schema
        raise UsageError("Vorlage ergäbe eine ungültige Persona: " + "; ".join(errs))
    target.parent.mkdir(parents=True, exist_ok=True)
    write_text(target, text)


def cmd_new(a: argparse.Namespace) -> int:
    pid = a.id
    _check_id(pid)
    target = Path(a.dir) / f"{pid}{SUFFIX}"
    if target.exists() and not a.force:
        print(f"Existiert bereits: {target} (--force zum Überschreiben)", file=sys.stderr)
        return 1
    archetype = _archetype(a.archetype)
    _write_persona(target, _template_text(pid, archetype, a.review_days))
    print(f"Angelegt: {target}", file=sys.stderr)
    return 0


def cmd_factoids(a: argparse.Namespace) -> int:
    study = load_study(a.folder)
    findings = sort_factoid_findings(study.findings + analyse_study(study))
    if a.json:
        print(json.dumps(report_json(study, findings), ensure_ascii=False, indent=2))
    else:
        sys.stdout.write(render_report(study, findings))
    n_err = sum(1 for f in findings if f.level == ERROR)
    n_warn = sum(1 for f in findings if f.level == WARN)
    print(
        f"— {len(study.sources)} Quelle(n), {len(study.participants())} Teilnehmende, "
        f"{len(study.factoids())} Factoids: {n_err} Fehler, {n_warn} Warnungen",
        file=sys.stderr,
    )
    if n_err or (a.strict and n_warn):
        return 1
    return 0


def cmd_skeleton(a: argparse.Namespace) -> int:
    pid = a.id
    _check_id(pid)
    target = Path(a.dir) / f"{pid}{SUFFIX}"
    if target.exists() and not a.force:
        print(f"Existiert bereits: {target} (--force zum Überschreiben)", file=sys.stderr)
        return 1
    participants = [x.strip() for x in a.participants.split(",") if x.strip()]
    if not participants:
        raise UsageError("--participants leer: Teilnehmer-Codes kommagetrennt angeben, z. B. p1,p3,p7")
    study = load_study(a.folder)
    errors = [f for f in study.findings if f.level == ERROR]
    if errors:
        for f in sort_factoid_findings(errors):
            print(str(f), file=sys.stderr)
        print(f"Factoids fehlerhaft – zuerst «personakit factoids {a.folder}» bereinigen", file=sys.stderr)
        return 1
    archetype = _archetype(a.archetype)
    template = Persona.from_text(_template_text(pid, archetype, a.review_days), target)
    label = Path(a.folder).as_posix()
    sk = build_skeleton(study, participants, template, label)
    _write_persona(target, sk.persona.to_text())
    for hint in sk.hints:
        print(f"Hinweis: {hint}", file=sys.stderr)
    print(
        f"Angelegt: {target} (evidence_level {sk.evidence_level}, {sk.first_hand} Interviews/Beobachtungen)"
        " – Archetyp, Ziele, Jobs und Simulationsregeln mit Factoid-IDs ergänzen, dann personakit lint",
        file=sys.stderr,
    )
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
    report = lint_workspace(a.paths, journeys=a.journeys)
    findings = report.findings
    personas, sets = report.personas, report.sets
    if a.min_level == "warn":
        findings = [f for f in findings if f.level in (ERROR, WARN)]
    elif a.min_level == "error":
        findings = [f for f in findings if f.level == ERROR]
    _print_findings(findings, as_json=a.json)
    n_err = sum(1 for f in findings if f.level == ERROR)
    n_warn = sum(1 for f in findings if f.level == WARN)
    in_sets = f" in {len(sets)} Set(s)" if sets else ""
    with_journeys = f", {len(report.journeys)} Journey(s)" if a.journeys else ""
    print(f"— {len(personas)} Persona(s){in_sets}{with_journeys}: {n_err} Fehler, {n_warn} Warnungen", file=sys.stderr)
    if n_err or (a.strict and n_warn):
        return 1
    return 0


def cmd_render(a: argparse.Namespace) -> int:
    fmt = a.format
    if fmt in SET_FORMATS:
        personas, groups = load_workspace(a.paths)
        _warn_unresolved(groups)
        _out(render_set(personas, fmt, groups=groups, title=a.title, target=a.target), a.output)
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


def _write_new(path: str, text: str, force: bool) -> None:
    """Templates the user fills in by hand: never overwrite one silently."""
    target = Path(path)
    if target.exists() and not force:
        raise UsageError(f"{target} existiert bereits – nicht überschrieben (--force zum Überschreiben)")
    target.parent.mkdir(parents=True, exist_ok=True)
    write_text(target, text)
    print(f"→ {target}", file=sys.stderr)


def cmd_probe_build(a: argparse.Namespace) -> int:
    _, groups = load_workspace(a.paths)
    _warn_unresolved(groups)
    chosen = group_personas([g for g in groups if not g.is_loose])
    # A set folder means "this set"; a persona without set joins only when its file is named explicitly
    # (or when no set is involved at all, e.g. a folder of loose personas).
    explicit = {Path(x).resolve() for x in a.paths if Path(x).is_file()}
    skipped: list[str] = []
    for g in groups:
        if not g.is_loose:
            continue
        for m in g.members:
            p = m.persona
            if len(groups) == 1 or (p.path is not None and p.path.resolve() in explicit):
                chosen.append(p)
            else:
                skipped.append(p.id)
    if skipped:
        print(
            f"Hinweis: ohne Set unter den Pfaden, nicht im Plan: {', '.join(skipped)} (Datei direkt angeben, um sie einzuschliessen)",
            file=sys.stderr,
        )
    retired = [p.id for p in chosen if p.data.get("status") == "retired"]
    if retired:
        print(f"Hinweis: im Ruhestand, nicht im Plan: {', '.join(retired)}", file=sys.stderr)
    chosen = [p for p in chosen if p.id not in retired]
    if len(chosen) < 2:
        raise UsageError(
            f"Die Probe vergleicht Personas paarweise und braucht mindestens zwei (gefunden: {len(chosen)}); "
            "ein Set oder mehrere Persona-Dateien angeben"
        )
    if a.samples < 1:
        raise UsageError("--samples muss mindestens 1 sein")
    sets = [g.id for g in groups if not g.is_loose and any(m.persona.id in {p.id for p in chosen} for m in g.members)]
    plan = build_plan(chosen, sets=sets, questions=a.questions, samples=a.samples)
    if a.answers_template:
        _write_new(a.answers_template, json.dumps(answers_template(plan), ensure_ascii=False, indent=2) + "\n", a.force)
    if a.keywords_template:
        _write_new(a.keywords_template, keywords_template(plan), a.force)
    _out(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", a.output)
    print(
        f"— {len(plan['personas'])} Personas, {len(plan['questions'])} Fragen, {probe_runs(plan)} Durchläufe "
        f"(Plan {plan['plan_id']})",
        file=sys.stderr,
    )
    return 0


def cmd_probe_evaluate(a: argparse.Namespace) -> int:
    if not 0 < a.warn <= a.alarm <= 1:
        raise UsageError(f"Schwellen ungültig: es muss 0 < --warn ({a.warn}) ≤ --alarm ({a.alarm}) ≤ 1 gelten")
    plan = load_plan(a.plan)
    answers = load_answers(a.answers)
    keywords = load_keywords(a.keywords) if a.keywords else None
    result = evaluate(plan, answers, keywords, warn=a.warn, alarm=a.alarm)
    if a.json:
        _out(json.dumps(probe_report_json(result), ensure_ascii=False, indent=2) + "\n", a.output)
    else:
        _out(render_probe_report(result, Path(a.plan).name, Path(a.answers).name), a.output)
    lights = Counter(p.light for p in result.pairs)
    n_warn = sum(1 for f in result.findings if f.level == WARN)
    print(
        f"— {len(result.pairs)} Paare: {lights['red']} rot, {lights['yellow']} gelb, {lights['green']} grün"
        + (f", {lights['none']} ohne Daten" if lights["none"] else "")
        + f"; {n_warn} Warnungen",
        file=sys.stderr,
    )
    return 1 if a.strict and n_warn else 0


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

    s = sub.add_parser(
        "factoids", help="Factoid-Ordner prüfen: Verortung der Teilnehmenden, dünne Variablen, Ausreisser"
    )
    s.add_argument("folder", help="Studienordner mit *.factoids.md (und optional variables.yml)")
    s.add_argument("--strict", action="store_true", help="Auch bei Warnungen mit Exit-Code 1 beenden")
    s.add_argument("--json", action="store_true", help="Bericht als JSON auf stdout")
    s.set_defaults(func=cmd_factoids)

    s = sub.add_parser("skeleton", help="Persona-Skelett aus gewählten Teilnehmenden eines Factoid-Ordners")
    s.add_argument("folder", help="Studienordner mit *.factoids.md")
    s.add_argument("--participants", "-p", required=True, help="Teilnehmer-Codes, kommagetrennt, z. B. p1,p3,p7")
    s.add_argument("--id", required=True, help="Slug der neuen Persona")
    s.add_argument(
        "--archetype", "-a", default="", help="Verhaltensbasierte Bezeichnung (Pflicht; ohne Angabe wird nachgefragt)"
    )
    s.add_argument("--dir", "-d", default="personas", help="Zielordner (Default: personas)")
    s.add_argument("--review-days", type=int, default=180, help="Review-Frist in Tagen (Default: 180)")
    s.add_argument("--force", action="store_true")
    s.set_defaults(func=cmd_skeleton)

    s = sub.add_parser("validate", help="Gegen JSON-Schema prüfen")
    s.add_argument("paths", nargs="+")
    s.add_argument("--quiet", "-q", action="store_true")
    s.set_defaults(func=cmd_validate)

    s = sub.add_parser("lint", help="Schema + methodische Regeln prüfen")
    s.add_argument("paths", nargs="+")
    s.add_argument("--strict", action="store_true", help="Auch bei Warnungen mit Exit-Code 1 beenden")
    s.add_argument("--min-level", choices=["info", "warn", "error"], default="info")
    s.add_argument("--json", action="store_true", help="Findings als JSON-Liste auf stdout (für CI und Werkzeuge)")
    s.add_argument(
        "--journeys",
        action="append",
        metavar="PFAD",
        help="journeykit-Journeys (Datei oder Ordner, mehrfach möglich) gegen die Personas prüfen (K000–K004)",
    )
    s.set_defaults(func=cmd_lint)

    s = sub.add_parser(
        "render",
        help="Exportieren: md|card|json|yaml|prompt (einzeln) oder matrix|html|bundle|notion (nach Set gruppiert)",
    )
    s.add_argument("paths", nargs="+")
    s.add_argument("--format", "-f", choices=SINGLE_FORMATS + SET_FORMATS, default="md")
    s.add_argument("--mode", "-m", choices=["simulate", "audience"], default="simulate", help="Nur für prompt")
    s.add_argument("--title", default=None, help="Nur für html")
    s.add_argument(
        "--target",
        choices=["api", "mcp"],
        default="api",
        help="Nur für notion: api = Blöcke für die Notion-API, mcp = Notion-Markdown für die Notion-MCP-Tools",
    )
    s.add_argument("--output", "-o", default=None, help="Datei (einzeln/Set) oder Ordner (mehrere Einzel-Exporte)")
    s.set_defaults(func=cmd_render)

    s = sub.add_parser("list", help="Übersichtstabelle, nach Set gruppiert")
    s.add_argument("paths", nargs="+")
    s.add_argument("--output", "-o", default=None)
    s.set_defaults(func=cmd_list)

    s = sub.add_parser(
        "probe", help="Collapse-Probe: Prüffragen für simulierte Personas erzeugen und Antworten auswerten"
    )
    probe = s.add_subparsers(dest="probe_cmd", required=True)
    s = probe.add_parser(
        "build", help="Plan mit Simulate-Prompts und 6–10 Prüffragen pro Persona (deterministisch, ohne Modell)"
    )
    s.add_argument(
        "paths", nargs="+", help="Set-Ordner, personas/ oder einzelne Persona-Dateien (mindestens zwei Personas)"
    )
    s.add_argument(
        "--questions",
        "-n",
        type=int,
        default=8,
        choices=range(6, 11),
        metavar="6-10",
        help="Fragen pro Persona (Default: 8)",
    )
    s.add_argument(
        "--samples", type=int, default=1, help="Empfohlene Durchgänge pro Frage; ab 2 wird die Varianz gemessen"
    )
    s.add_argument("--output", "-o", default=None, help="Plan als Datei (sonst stdout)")
    s.add_argument("--answers-template", metavar="DATEI", help="Leere answers.json zum Füllen anlegen")
    s.add_argument(
        "--keywords-template", metavar="DATEI", help="Schlüsselwort-Vorlage für die must_not-Prüfung anlegen"
    )
    s.add_argument("--force", action="store_true", help="Bestehende Vorlagen überschreiben")
    s.set_defaults(func=cmd_probe_build)
    s = probe.add_parser("evaluate", help="Antworten auswerten: Ähnlichkeit je Persona-Paar, must_not, Unknowns")
    s.add_argument("plan", help="probe.json aus probe build")
    s.add_argument("answers", help="answers.json mit den Modellantworten")
    s.add_argument("--keywords", "-k", metavar="DATEI", help="Schlüsselwörter je must_not-Regel (YAML)")
    s.add_argument("--warn", type=float, default=0.30, help="Ø Ähnlichkeit ab der ein Paar gelb wird (Default: 0.30)")
    s.add_argument("--alarm", type=float, default=0.50, help="Ähnlichkeit ab der ein Paar rot wird (Default: 0.50)")
    s.add_argument("--json", action="store_true", help="Ergebnis als JSON statt Markdown")
    s.add_argument("--strict", action="store_true", help="Exit-Code 1 bei Warnungen (rotes Paar, must_not-Treffer …)")
    s.add_argument("--output", "-o", default=None, help="Bericht als Datei (sonst stdout)")
    s.set_defaults(func=cmd_probe_evaluate)

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
