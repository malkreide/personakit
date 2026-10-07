"""Methodological lint rules – what the JSON schema cannot express.

The rules encode the method decisions documented in docs/METHOD.md:
behaviour before demographics (Cooper), Chekhov's gun for profile facts,
explicit evidence level (NN/g), JTBD as job stories, guardrails for synthetic
use, and a bounded half-life (review_by). Set rules run per set (personas/<set>/set.yml)
with the priority the set assigns; personas without a set form the loose set.
"""

from __future__ import annotations

import datetime as _dt
import re
from collections.abc import Iterable
from dataclasses import dataclass, replace

from .model import Persona, parse_date, today
from .sets import Group, PersonaSet, build_groups

ERROR, WARN, INFO = "ERROR", "WARN", "INFO"
_LEVEL_ORDER = {ERROR: 0, WARN: 1, INFO: 2}

JOB_STORY_RE = re.compile(
    r"^\s*(wenn|when|als|if)\b.*\b(möchte|will|want|need|brauche)\b.*\b(damit|so that|so dass|sodass|um)\b",
    re.IGNORECASE,
)
DEMOGRAPHIC_HINTS = re.compile(
    r"\b(\d{2}\s*(jahre|j\.|years)|jährig|verheiratet|ledig|single|hund|katze|hobby|hobbys|wohnt in|lebt in)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Finding:
    level: str
    code: str
    message: str
    persona: str = ""
    set_id: str = ""

    def __str__(self) -> str:
        ctx = " › ".join(x for x in (self.set_id, self.persona) if x)
        who = f"[{ctx}] " if ctx else ""
        return f"{self.level:5} {self.code:<6} {who}{self.message}"


def _f(level: str, code: str, msg: str, p: Persona) -> Finding:
    return Finding(level, code, msg, p.id or (p.path.name if p.path else "?"))


def _nonempty(x) -> bool:
    return bool(x) and (not isinstance(x, (list, dict)) or len(x) > 0)


# ------------------------------------------------------------------ single
def lint_persona(p: Persona) -> list[Finding]:  # noqa: C901 – rule table, intentionally flat
    out: list[Finding] = []
    d = p.data
    level = d.get("evidence_level")
    status = d.get("status")

    # --- identity --------------------------------------------------------
    if p.path and p.path.name != f"{p.id}.persona.md":
        out.append(
            _f(ERROR, "P001", f"Dateiname «{p.path.name}» passt nicht zur id «{p.id}» (erwartet {p.id}.persona.md)", p)
        )
    if DEMOGRAPHIC_HINTS.search(p.archetype or ""):
        out.append(
            _f(
                WARN,
                "P002",
                "Archetyp klingt demografisch – verhaltensbasiert formulieren (was tut die Person, nicht wer sie ist)",
                p,
            )
        )
    if not d.get("scope"):
        out.append(_f(WARN, "P003", "scope fehlt – für welche Lösungen gilt die Persona, für welche nicht?", p))

    # --- evidence hygiene ------------------------------------------------
    evidence = d.get("evidence") or []
    real_evidence = [e for e in evidence if e.get("type") != "assumption"]
    assumptions = d.get("assumptions") or []
    if level == "proto":
        if not _nonempty(assumptions):
            out.append(
                _f(
                    ERROR,
                    "E001",
                    "evidence_level=proto, aber keine assumptions – Proto-Personas müssen ihre Annahmen offenlegen",
                    p,
                )
            )
    elif level in ("qualitative", "statistical"):
        if not real_evidence:
            out.append(_f(ERROR, "E003", f"evidence_level={level}, aber kein Evidenz-Eintrag ausser assumption", p))
        if level == "qualitative":
            n = sum(int(e.get("n") or 0) for e in real_evidence if e.get("type") in ("interview", "observation"))
            if 0 < n < 5:
                out.append(
                    _f(WARN, "E004", f"Nur {n} Interviews/Beobachtungen – NN/g empfiehlt 5–30 bis zur Sättigung", p)
                )
        if level == "statistical" and not any(
            e.get("type") == "survey" and (e.get("n") or 0) >= 100 for e in real_evidence
        ):
            out.append(_f(WARN, "E005", "evidence_level=statistical ohne Survey mit n≥100 – Härtegrad prüfen", p))
    ev_ids = {e.get("id") for e in evidence}
    for q in d.get("quotes") or []:
        ref = q.get("evidence")
        if not ref:
            out.append(_f(WARN, "E006", f"Zitat ohne Evidenz-Verweis: «{str(q.get('text'))[:50]}…»", p))
        elif ref not in ev_ids:
            out.append(_f(ERROR, "E007", f"Zitat verweist auf unbekannte Evidenz «{ref}»", p))
    for v in (d.get("behaviour") or {}).get("variables") or []:
        ref = v.get("evidence")
        if ref and ref not in ev_ids:
            out.append(
                _f(ERROR, "E007", f"Verhaltensvariable «{v.get('name')}» verweist auf unbekannte Evidenz «{ref}»", p)
            )
    for j in d.get("jobs") or []:
        ref = j.get("evidence")
        if ref and ref not in ev_ids:
            out.append(_f(ERROR, "E007", f"Job {j.get('id')} verweist auf unbekannte Evidenz «{ref}»", p))
    if not _nonempty(d.get("unknowns")):
        out.append(_f(WARN, "E008", "unknowns leer – eine Persona ohne offene Fragen ist verdächtig vollständig", p))

    # --- Chekhov's gun ---------------------------------------------------
    for fact in d.get("profile") or []:
        if fact.get("fact") and not fact.get("relevance"):
            out.append(
                _f(WARN, "C001", f"Profil-Fakt ohne relevance: «{fact.get('fact')}» – streichen oder begründen", p)
            )

    # --- behaviour & goals -----------------------------------------------
    variables = (d.get("behaviour") or {}).get("variables") or []
    variables = [v for v in variables if v.get("name")]
    if not variables:
        out.append(_f(WARN, "B001", "Keine Verhaltensvariablen – Verhalten ist der Kern einer Design-Persona", p))
    elif len(variables) > 7:
        out.append(_f(INFO, "B002", f"{len(variables)} Verhaltensvariablen – mehr als 7 verwässern die Persona", p))
    for v in variables:
        if not (v.get("low") and v.get("high")):
            out.append(_f(INFO, "B003", f"Variable «{v.get('name')}» ohne Skalen-Anker (low/high)", p))
    goals = d.get("goals") or {}
    if not _nonempty(goals.get("end")):
        out.append(_f(WARN, "G001", "goals.end leer – ohne Endziele keine Priorisierung", p))
    if not _nonempty(goals.get("experience")):
        out.append(_f(INFO, "G002", "goals.experience leer – wie darf sich die Persona nie fühlen?", p))
    if not _nonempty(d.get("pains")):
        out.append(_f(WARN, "G003", "pains leer – welche Hürden soll die Lösung beseitigen?", p))

    # --- JTBD ------------------------------------------------------------
    jobs = [j for j in d.get("jobs") or [] if j.get("statement")]
    for j in jobs:
        if not JOB_STORY_RE.search(j["statement"]):
            out.append(
                _f(
                    INFO,
                    "J002",
                    f"Job {j.get('id')} nicht als Job Story formuliert («Wenn …, möchte ich …, damit …»)",
                    p,
                )
            )
        if j.get("importance") and j.get("satisfaction") and j["importance"] >= 4 and j["satisfaction"] >= 4:
            out.append(
                _f(INFO, "J003", f"Job {j.get('id')}: wichtig und bereits gut bedient – Innovationschance gering", p)
            )

    # --- simulation guardrails -------------------------------------------
    sim = d.get("simulation") or {}
    if status == "active":
        if not _nonempty(sim.get("must_not")):
            out.append(
                _f(WARN, "S001", "simulation.must_not leer – ohne Grenzen driftet ein LLM in den Durchschnitt", p)
            )
        if not sim.get("variance"):
            out.append(
                _f(WARN, "S002", "simulation.variance fehlt – wo weichen reale Personen dieses Typs voneinander ab?", p)
            )
        if not sim.get("voice"):
            out.append(_f(INFO, "S003", "simulation.voice fehlt – Register/Sprache für Prompt-Einsatz", p))

    # --- lifecycle -------------------------------------------------------
    rb = parse_date(d.get("review_by"))
    if status != "retired":
        if rb is None:
            out.append(_f(WARN, "L001", "review_by fehlt – Personas haben eine begrenzte Halbwertszeit", p))
        elif rb < today():
            out.append(_f(WARN, "L002", f"Review überfällig seit {rb.isoformat()}", p))
        elif rb <= today() + _dt.timedelta(days=30):
            out.append(_f(INFO, "L003", f"Review fällig am {rb.isoformat()}", p))
    if not _nonempty(d.get("changelog")):
        out.append(_f(INFO, "L004", "changelog leer", p))
    if not p.sections.get("Szenario"):
        out.append(
            _f(WARN, "L005", "Kein «## Szenario» im Body – erst mit Szenario wird die Persona zum Testinstrument", p)
        )

    # --- priority-dependent rules, here with the default from the file ----
    out.extend(_priority_rules(p, d.get("priority")))
    return out


def _priority_rules(p: Persona, priority: str | None) -> list[Finding]:
    """Rules whose outcome depends on the priority – re-run by lint_sets when a set overrides it."""
    out: list[Finding] = []
    d = p.data
    if d.get("evidence_level") == "proto" and d.get("status") == "active" and priority != "negative":
        out.append(
            _f(WARN, "E002", "Proto-Persona ist «active» – nur als Hypothese einsetzen oder Evidenz nachliefern", p)
        )
    if priority != "negative" and not any(j.get("statement") for j in d.get("jobs") or []):
        out.append(_f(WARN, "J001", "Kein Job-to-be-Done – was «stellt» die Persona die Lösung ein zu tun?", p))
    if priority == "negative" and not _nonempty(d.get("anti_patterns")):
        out.append(_f(WARN, "N001", "Negative Persona ohne anti_patterns – wofür genau wird nicht gebaut?", p))
    return out


# --------------------------------------------------------------------- set
def lint_set(personas: Iterable[Persona]) -> list[Finding]:
    """Cross-persona rules for personas without set.yml – one loose set (one solution scope)."""
    return lint_sets(personas, [])


def lint_sets(personas: Iterable[Persona], sets: Iterable[PersonaSet]) -> list[Finding]:
    """Cross-persona rules: ids and references repo-wide, focus rules (X002–X004) per set."""
    ps = list(personas)
    sets = list(sets)
    groups = build_groups(ps, sets)
    out: list[Finding] = []

    # --- repo-wide: sets reference personas by id, so ids must be unique everywhere
    ids = [p.id for p in ps]
    for dup in sorted({i for i in ids if ids.count(i) > 1}):
        out.append(Finding(ERROR, "X001", f"id «{dup}» mehrfach vorhanden", dup))
    set_ids = [s.id for s in sets]
    for dup in sorted({i for i in set_ids if set_ids.count(i) > 1}):
        where = ", ".join(str(s.path) for s in sets if s.id == dup)
        out.append(Finding(ERROR, "X010", f"Set-id «{dup}» mehrfach vorhanden ({where})", set_id=dup))

    # --- per set
    named = any(not g.is_loose for g in groups)
    for g in groups:
        out.extend(_lint_group(g, named))

    # --- files stored in a set folder that no set lists
    set_dirs = {s.dir.resolve(): s.id for s in sets}
    loose = {m.persona.id for g in groups if g.is_loose for m in g.members}
    for p in ps:
        if p.id not in loose or p.path is None:
            continue
        home = next((set_dirs[d] for d in p.path.resolve().parents if d in set_dirs), None)
        if home:
            out.append(
                Finding(
                    WARN,
                    "X009",
                    "Datei liegt in einem Set-Ordner, gehört aber zu keinem Set – in set.yml aufnehmen oder verschieben",
                    p.id,
                    home,
                )
            )

    # --- relations are part of the persona, not of a set → resolved repo-wide
    known = set(ids) | {m.persona.id for g in groups for m in g.members}
    for p in ps:
        for ref in (p.data.get("relations") or {}).get("personas") or []:
            if ref not in known:
                out.append(Finding(WARN, "X005", f"relations.personas verweist auf unbekannte Persona «{ref}»", p.id))
    return out


def _lint_group(g: Group, named: bool) -> list[Finding]:
    out: list[Finding] = []
    sid = g.id
    s = g.set
    if s is not None:
        if s.dir.name != s.id:
            out.append(
                Finding(
                    ERROR,
                    "X006",
                    f"Set-id «{s.id}» passt nicht zum Ordner «{s.dir.name}» (erwartet {s.id}/set.yml)",
                    set_id=sid,
                )
            )
        for pid in g.unknown:
            out.append(Finding(ERROR, "X007", f"set.yml nennt unbekannte oder ungültige Persona «{pid}»", set_id=sid))
        for pid in g.duplicates:
            out.append(Finding(ERROR, "X008", f"Persona «{pid}» mehrfach in set.yml aufgeführt", set_id=sid))
        if s.status == "retired":
            return out

    where = " unter den Personas ohne Set" if g.is_loose and named else ""
    live = [m for m in g.members if m.persona.data.get("status") != "retired"]
    primaries = [m for m in live if m.priority == "primary"]
    if live and not primaries:
        out.append(
            Finding(WARN, "X002", f"Keine primäre Persona{where} – wer muss zwingend zufrieden sein?", set_id=sid)
        )
    if len(primaries) > 1:
        out.append(
            Finding(
                WARN,
                "X003",
                f"{len(primaries)} primäre Personas{where} ({', '.join(m.persona.id for m in primaries)})"
                " – Cooper: genau eine pro Lösung",
                set_id=sid,
            )
        )
    if len(live) > 5:
        out.append(
            Finding(
                INFO,
                "X004",
                f"{len(live)} aktive Personas{where} – mehr als 3–5 lassen sich kaum im Kopf behalten",
                set_id=sid,
            )
        )

    # --- the set gives a persona another priority: re-check what depends on it
    for m in g.members:
        if not m.overridden:
            continue
        before = {(f.code, f.message) for f in _priority_rules(m.persona, m.default)}
        for f in _priority_rules(m.persona, m.priority):
            if (f.code, f.message) not in before:
                out.append(replace(f, message=f"{f.message} (in diesem Set {m.priority})", set_id=sid))
    return out


def sort_findings(findings: Iterable[Finding]) -> list[Finding]:
    return sorted(findings, key=lambda f: (_LEVEL_ORDER[f.level], f.set_id, f.persona, f.code))
