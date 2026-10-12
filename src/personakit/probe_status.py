"""Status of existing collapse-probe runs against today's personas (docs/PROBE.md, «Probe-Status»).

personakit never calls a model: a run is a plan plus an answers file that someone produced earlier.
This module finds runs below a folder, pairs answers with plans by ``plan_id`` and checks, per persona,
whether the plan still carries today's simulate prompt. Only pairs of two current personas say something
about the personas as they are now.

The version alone is not enough: the calibration plans under ``probe/kalibrierung/`` carry the real ids and
versions but deliberately thinned prompts. Comparing the prompt keeps such runs from passing as findings
about the real personas.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .model import Persona, PersonaError
from .probe import (
    _LIGHT_ORDER,
    LIGHT_LABEL,
    LIMITS,
    NONE,
    WARN,
    ProbeResult,
    evaluate,
    load_answers,
    load_keywords,
    load_plan,
)
from .render import render_prompt

CURRENT, STALE, UNKNOWN = "current", "stale", "unknown"
PARTIAL = "partial"  # run state: some, but not all personas current (at least two)
STATE_LABEL = {CURRENT: "aktuell", PARTIAL: "teilweise aktuell", STALE: "veraltet", UNKNOWN: "unbekannt"}
KEYWORDS_FILE = "probe-keywords.yml"
NO_PROBE = "none"  # persona summary: no run contains this persona at all


@dataclass(frozen=True)
class StatusProblem:
    """A file below the probe folder (or a persona file) that was not used, and why."""

    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.path}: {self.message}"


@dataclass(frozen=True)
class RunPersona:
    id: str
    plan_version: str
    version: str | None  # today's version; None when the persona is not in the workspace
    state: str  # CURRENT | STALE | UNKNOWN
    reason: str = ""


@dataclass
class ProbeRun:
    plan_path: str  # relative to the probe folder, POSIX
    answers_path: str
    keywords_path: str | None
    plan: dict[str, Any]
    answers: dict[str, Any]
    personas: list[RunPersona]
    keywords: dict[str, Any] | None = field(default=None, repr=False)
    result: ProbeResult | None = None  # evaluated only when at least two personas are current

    @property
    def current_ids(self) -> set[str]:
        return {p.id for p in self.personas if p.state == CURRENT}

    @property
    def state(self) -> str:
        n = len(self.current_ids)
        if n == len(self.personas):
            return CURRENT
        return PARTIAL if n >= 2 else STALE

    @property
    def model(self) -> str:
        return str(self.answers.get("model") or "")

    def pairs(self, persona_id: str | None = None) -> list[Any]:
        """Evaluated pairs, optionally only those with ``persona_id``."""
        if self.result is None:
            return []
        return [p for p in self.result.pairs if persona_id is None or persona_id in (p.a, p.b)]

    def is_current_pair(self, pair: Any) -> bool:
        return pair.a in self.current_ids and pair.b in self.current_ids


@dataclass(frozen=True)
class PersonaProbe:
    """One persona in scope: the worst light of its current pairs per run, or why there is none."""

    id: str
    version: str
    runs: tuple[tuple[str, str, str, int], ...] = ()  # (answers path, model, worst light, current pairs)
    stale: tuple[tuple[str, str], ...] = ()  # (answers path, reason)

    @property
    def light(self) -> str:
        if not self.runs:
            return NONE
        return min((r[2] for r in self.runs), key=lambda x: _LIGHT_ORDER[x])


@dataclass
class ProbeStatus:
    probe_dir: Path
    runs: list[ProbeRun]
    personas: list[PersonaProbe]  # in scope: active and draft personas (filtered by set or id)
    problems: list[StatusProblem] = field(default_factory=list)
    set_id: str | None = None
    persona_id: str | None = None

    @property
    def hint(self) -> str | None:
        """A concrete next step when nothing in scope has a current probe."""
        if any(p.runs for p in self.personas):
            return None
        scope = f" für Set «{self.set_id}»" if self.set_id else ""
        scope = f" für «{self.persona_id}»" if self.persona_id else scope
        build = f"personas/{self.set_id}" if self.set_id else "<Set-Ordner>"
        if any(p.stale for p in self.personas):
            return (
                f"Probe-Läufe{scope} vorhanden, aber keiner passt zum heutigen Stand der Personas (Gründe unter "
                f"«veraltet»). Neu bauen und neu laufen lassen: personakit probe build {build} -o probe.json"
            )
        return (
            f"Keine Probe-Läufe{scope} unter {self.probe_dir}. personakit probe build {build} -o probe.json, "
            "Antworten mit einem eigenen Runner (Format: docs/FORMAT.md, Collapse-Probe), Plan und Antworten "
            f"in einen Ordner unter {self.probe_dir} legen."
        )


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _find(probe_dir: Path) -> tuple[list[tuple[Path, dict]], list[tuple[Path, dict]], list[StatusProblem]]:
    """Plans and answers below ``probe_dir``; everything else that looks like JSON is a problem."""
    root = probe_dir.resolve()
    plans: list[tuple[Path, dict]] = []
    answers: list[tuple[Path, dict]] = []
    problems: list[StatusProblem] = []
    for path in sorted(probe_dir.rglob("*.json")):
        rel = _rel(path, probe_dir)
        if not path.resolve().is_relative_to(root):
            problems.append(StatusProblem(rel, "liegt ausserhalb des Probe-Ordners (Symlink) – nicht gelesen"))
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as e:
            problems.append(StatusProblem(rel, f"nicht lesbar – {e}"))
            continue
        kind = None
        if isinstance(data, dict):
            kind = "plan" if "personakit_probe" in data else "answers" if "personakit_probe_answers" in data else None
        if kind is None:
            problems.append(StatusProblem(rel, "weder Probe-Plan noch Antwortdatei – übersprungen"))
            continue
        try:
            (plans if kind == "plan" else answers).append(
                (path, load_plan(path) if kind == "plan" else load_answers(path))
            )
        except PersonaError as e:
            problems.append(StatusProblem(rel, str(e).removeprefix(f"{path}: ")))
    return plans, answers, problems


def _freshness(plan: dict[str, Any], by_id: dict[str, list[Persona]]) -> list[RunPersona]:
    out: list[RunPersona] = []
    for entry in plan["personas"]:
        pid, plan_version = entry["id"], str(entry.get("version", ""))
        found = by_id.get(pid, [])
        if not found:
            out.append(RunPersona(pid, plan_version, None, UNKNOWN, "nicht im Workspace"))
            continue
        if len(found) > 1:
            out.append(RunPersona(pid, plan_version, None, UNKNOWN, "ID mehrfach im Workspace (X001)"))
            continue
        p = found[0]
        version = str(p.data.get("version", ""))
        if render_prompt(p, mode="simulate") == entry["prompt"]:
            out.append(RunPersona(pid, plan_version, version, CURRENT))
        elif plan_version != version:
            out.append(
                RunPersona(pid, plan_version, version, STALE, f"Plan mit Version {plan_version}, heute {version}")
            )
        else:
            out.append(
                RunPersona(
                    pid,
                    plan_version,
                    version,
                    STALE,
                    f"Prompt weicht ab bei gleicher Version {version} (Persona ohne Versionssprung geändert, "
                    "anderer Renderer oder absichtlich veränderter Plan)",
                )
            )
    return out


def probe_status(
    personas: list[Persona],
    probe_dir: str | Path,
    set_members: dict[str, list[str]] | None = None,
    set_id: str | None = None,
    persona_id: str | None = None,
) -> ProbeStatus:
    """Runs below ``probe_dir`` checked against ``personas``.

    ``set_members`` maps set ids to their member ids (``personakit.api.probe_status`` passes the workspace's).
    ``set_id`` keeps runs whose plan names that set and the set's personas; ``persona_id`` keeps runs with that
    persona and only its pairs. A missing folder, an unknown set or an unknown id raise ``PersonaError``.
    """
    probe_dir = Path(probe_dir)
    if not probe_dir.is_dir():
        raise PersonaError(f"Probe-Ordner nicht gefunden: {probe_dir}")
    set_members = set_members or {}
    by_id: dict[str, list[Persona]] = {}
    for p in personas:
        by_id.setdefault(p.id, []).append(p)
    if set_id is not None and set_id not in set_members:
        known = ", ".join(sorted(set_members)) or "keine"
        raise PersonaError(f"Unbekanntes Set «{set_id}» (vorhanden: {known})")
    if persona_id is not None and persona_id not in by_id:
        raise PersonaError(f"Unbekannte Persona «{persona_id}» (personakit list zeigt alle IDs)")

    plans, answers, problems = _find(probe_dir)
    plans_by_id: dict[str, list[tuple[Path, dict]]] = {}
    for path, plan in plans:
        plans_by_id.setdefault(plan["plan_id"], []).append((path, plan))
    used: set[Path] = set()
    runs: list[ProbeRun] = []
    for a_path, ans in answers:
        rel = _rel(a_path, probe_dir)
        candidates = plans_by_id.get(ans["plan_id"], [])
        same_dir = [c for c in candidates if c[0].parent == a_path.parent]
        chosen = same_dir[0] if same_dir else candidates[0] if len(candidates) == 1 else None
        if chosen is None:
            why = "mehrere Pläne, keiner im selben Ordner" if candidates else "kein Plan gefunden"
            problems.append(StatusProblem(rel, f"Antworten zu plan_id {ans['plan_id']}: {why} – nicht ausgewertet"))
            continue
        p_path, plan = chosen
        used.add(p_path)
        k_path = p_path.parent / KEYWORDS_FILE
        keywords = None
        if k_path.is_file():
            try:
                keywords = load_keywords(k_path)
            except PersonaError as e:
                problems.append(
                    StatusProblem(
                        _rel(k_path, probe_dir),
                        f"{str(e).removeprefix(f'{k_path}: ')} – ohne Schlüsselwörter ausgewertet",
                    )
                )
        run = ProbeRun(
            plan_path=_rel(p_path, probe_dir),
            answers_path=rel,
            keywords_path=_rel(k_path, probe_dir) if keywords is not None else None,
            plan=plan,
            answers=ans,
            personas=_freshness(plan, by_id),
            keywords=keywords,
        )
        runs.append(run)
    problems.extend(
        StatusProblem(_rel(path, probe_dir), f"Plan {plan['plan_id']} ohne Antwortdatei – nichts auszuwerten")
        for path, plan in plans
        if path not in used
    )

    # filters (weglassen = kein Filter)
    scope_ids = [p.id for p in personas if p.data.get("status") != "retired"]
    if set_id is not None:
        members = set(set_members[set_id])
        scope_ids = [i for i in scope_ids if i in members]
        runs = [r for r in runs if set_id in (r.plan.get("sets") or [])]
    if persona_id is not None:
        scope_ids = [persona_id]
        runs = [r for r in runs if persona_id in {x.id for x in r.personas}]
    scope_ids = list(dict.fromkeys(scope_ids))

    for run in runs:
        if run.state != STALE:  # stale runs need no evaluation: the plan alone says so
            run.result = evaluate(run.plan, run.answers, run.keywords)
    evaluated = sorted(runs, key=lambda r: (r.state != CURRENT, r.state != PARTIAL, r.answers_path))

    summary: list[PersonaProbe] = []
    for pid in scope_ids:
        p = by_id[pid][0]
        entries: list[tuple[str, str, str, int]] = []
        stale: list[tuple[str, str]] = []
        for run in evaluated:
            rp = next((x for x in run.personas if x.id == pid), None)
            if rp is None:
                continue
            if rp.state != CURRENT or run.result is None:
                stale.append((run.answers_path, rp.reason or "zu wenige aktuelle Personas im Lauf"))
                continue
            current = [x for x in run.pairs(pid) if run.is_current_pair(x)]
            if not current:
                stale.append((run.answers_path, "kein Paar mit einer anderen aktuellen Persona"))
                continue
            worst = min((x.light for x in current), key=lambda x: _LIGHT_ORDER[x])
            entries.append((run.answers_path, run.model, worst, len(current)))
        summary.append(PersonaProbe(pid, str(p.data.get("version", "")), tuple(entries), tuple(stale)))
    return ProbeStatus(probe_dir, evaluated, summary, problems, set_id, persona_id)


# ================================================================== output
def _cell(text: str) -> str:
    return " ".join(str(text).split()).replace("|", "\\|")


def _model(m: str) -> str:
    """Short model label for a table cell: up to the first comma, at most 60 characters."""
    m = " ".join(m.split())
    short = m.split(",")[0] if len(m) > 40 else m
    return _cell(short if len(short) <= 60 else short[:59] + "…") or "–"


def render_status(st: ProbeStatus) -> str:
    """Markdown overview; ``personakit probe status`` prints it."""
    counts = {s: sum(1 for r in st.runs if r.state == s) for s in (CURRENT, PARTIAL, STALE)}
    scope = f" · Set «{st.set_id}»" if st.set_id else ""
    scope += f" · Persona «{st.persona_id}»" if st.persona_id else ""
    o = [
        "# Probe-Status",
        "",
        f"Probe-Ordner `{st.probe_dir.as_posix()}`{scope} · {len(st.runs)} Läufe: "
        f"{counts[CURRENT]} aktuell, {counts[PARTIAL]} teilweise aktuell, {counts[STALE]} veraltet",
        "",
        "> Grün heisst: Die Antworten der Personas unterscheiden sich in der Wortwahl. Es heisst nicht, dass eine "
        "Persona ihre Stimme hält oder richtig liegt. Nur Paare zweier aktueller Personas zählen; die Grenzen der "
        "Methode stehen am Schluss.",
        "",
    ]
    if st.hint:
        o += [f"**Hinweis:** {st.hint}", ""]
    o += [
        "## Personas",
        "",
        "| Persona | Version | Probe | Lauf | Modell | aktuelle Paare |",
        "|---|---|---|---|---|---|",
    ]
    for p in st.personas:
        if p.runs:
            for path, model, light, n in p.runs:
                o.append(f"| {p.id} | {p.version} | {LIGHT_LABEL[light]} | `{path}` | {_model(model)} | {n} |")
        elif p.stale:
            o.append(f"| {p.id} | {p.version} | veraltet | {', '.join(f'`{x[0]}`' for x in p.stale)} | – | 0 |")
        else:
            o.append(f"| {p.id} | {p.version} | keine Probe | – | – | 0 |")
    o.append("")
    if st.runs:
        o += ["## Läufe", ""]
    for r in st.runs:
        o += [
            f"### `{r.answers_path}` – {STATE_LABEL[r.state]}",
            "",
            f"- Plan `{r.plan_path}` ({r.plan['plan_id']}, {r.plan.get('generator') or 'unbekannt'}), "
            f"{r.plan.get('samples', 1)} Durchgänge, Sets: {', '.join(r.plan.get('sets') or []) or '–'}",
            f"- Modell: {_cell(r.model) or '–'}",
            f"- Schlüsselwörter: `{r.keywords_path}`" if r.keywords_path else "- Schlüsselwörter: keine",
            "",
            "| Persona | im Plan | heute | Stand |",
            "|---|---|---|---|",
        ]
        for x in r.personas:
            state = STATE_LABEL[x.state] + (f" – {x.reason}" if x.reason else "")
            o.append(f"| {x.id} | {x.plan_version or '–'} | {x.version or '–'} | {_cell(state)} |")
        o.append("")
        pairs = r.pairs(st.persona_id)
        if pairs:
            o += ["| Paar | Ampel | Nähe | Ø Ähnlichkeit | zählt |", "|---|---|---|---|---|"]
            for x in pairs:
                near = "–" if x.nearness is None else f"{x.nearness:.2f}"
                mean = "–" if x.mean is None else f"{x.mean:.2f}"
                counts_ = "ja" if r.is_current_pair(x) else "nein (Persona veraltet)"
                o.append(f"| {x.a} ↔ {x.b} | {LIGHT_LABEL[x.light]} | {near} | {mean} | {counts_} |")
            o.append("")
            warns = [f for f in r.result.findings if f.level == WARN] if r.result else []
            if warns:
                o += ["Warnungen:", ""]
                o += [f"- `{f.code}` {_cell((f'[{f.subject}] ' if f.subject else '') + f.message)}" for f in warns]
                o.append("")
    if st.problems:
        o += ["## Nicht ausgewertet", ""] + [f"- `{x.path}`: {_cell(x.message)}" for x in st.problems] + [""]
    o += ["## Grenzen", ""] + [f"- {x}" for x in LIMITS] + [""]
    return "\n".join(o)


def status_json(st: ProbeStatus) -> dict[str, Any]:
    """Structured status; ``personakit probe status --json`` prints it, ``personakit-mcp`` serves it."""
    from . import __version__

    def pair(r: ProbeRun, x: Any) -> dict[str, Any]:
        return {
            "a": x.a,
            "b": x.b,
            "light": x.light,
            "nearness": x.nearness,
            "mean": x.mean,
            "current": r.is_current_pair(x),
        }

    return {
        "generator": f"personakit {__version__}",
        "limits": [re.sub(r"\*\*", "", x) for x in LIMITS],
        "probe_dir": st.probe_dir.as_posix(),
        "filters": {"set": st.set_id, "id": st.persona_id},
        "hint": st.hint,
        "personas": [
            {
                "id": p.id,
                "version": p.version,
                "light": p.light if p.runs else None,
                "runs": [{"answers": a, "model": m, "light": lt, "current_pairs": n} for a, m, lt, n in p.runs],
                "stale": [{"answers": a, "reason": why} for a, why in p.stale],
            }
            for p in st.personas
        ],
        "runs": [
            {
                "plan": r.plan_path,
                "answers": r.answers_path,
                "keywords": r.keywords_path,
                "plan_id": r.plan["plan_id"],
                "generator": r.plan.get("generator"),
                "model": r.model or None,
                "samples": r.plan.get("samples", 1),
                "sets": list(r.plan.get("sets") or []),
                "state": r.state,
                "personas": [
                    {
                        "id": x.id,
                        "plan_version": x.plan_version,
                        "version": x.version,
                        "state": x.state,
                        "reason": x.reason,
                    }
                    for x in r.personas
                ],
                "pairs": [pair(r, x) for x in r.pairs(st.persona_id)],
                "findings": [
                    {"level": f.level, "code": f.code, "subject": f.subject, "message": f.message}
                    for f in (r.result.findings if r.result else [])
                    if f.level == WARN
                ],
            }
            for r in st.runs
        ],
        "problems": [{"path": x.path, "message": x.message} for x in st.problems],
    }
