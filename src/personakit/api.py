"""Library entry points for tools that embed personakit (MCP server, CI scripts).

The CLI commands stop at the first unreadable file; a long-running reader such as a
server must not go blank because one draft in the folder is broken. ``load_workspace_tolerant``
keeps the valid personas and sets and reports the rest as problems, with the same codes
``personakit lint`` uses. ``lint_workspace`` is exactly what ``personakit lint`` checks, including the
journeykit cross-lint when journeys are passed (``personakit lint --journeys``).
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

from .journeys import JourneyRef, lint_journeys, load_journeys
from .lint import ERROR, Finding, lint_persona, lint_sets
from .model import Persona, PersonaError, find_persona_files
from .sets import Group, PersonaSet, build_groups, load_sets
from .validate import validate


@dataclass(frozen=True)
class Problem:
    """A file that could not be used: unreadable, schema violation or broken ``set.yml``."""

    path: Path
    finding: Finding

    def __str__(self) -> str:
        return f"{self.path}: {self.finding}"


@dataclass
class Workspace:
    """Valid personas and sets below the given paths, resolved into groups, plus what was skipped."""

    personas: list[Persona] = field(default_factory=list)
    sets: list[PersonaSet] = field(default_factory=list)
    groups: list[Group] = field(default_factory=list)
    problems: list[Problem] = field(default_factory=list)


def _load_personas(paths: list[str | Path]) -> tuple[list[Persona], list[Problem]]:
    personas: list[Persona] = []
    problems: list[Problem] = []
    for path in find_persona_files(paths):
        try:
            p = Persona.load(path)
        except PersonaError as e:
            problems.append(Problem(path, Finding(ERROR, "P000", str(e), path.name)))
            continue
        schema_errs = validate(p)
        if schema_errs:
            problems.extend(Problem(path, Finding(ERROR, "SCHEMA", e, p.id or path.name)) for e in schema_errs)
            continue
        personas.append(p)
    return personas, problems


def _load_sets(paths: list[str | Path]) -> tuple[list[PersonaSet], list[Problem]]:
    sets, errors = load_sets(paths)
    return sets, [Problem(path, Finding(ERROR, "X000", msg, set_id=path.parent.name)) for path, msg in errors]


def load_workspace_tolerant(paths: Iterable[str | Path]) -> Workspace:
    """Like ``sets.load_workspace``, but broken files become ``problems`` instead of stopping.

    A missing path still raises ``PersonaError`` – that is a configuration error, not a broken file.
    """
    paths = list(paths)
    personas, problems = _load_personas(paths)
    sets, set_problems = _load_sets(paths)
    return Workspace(
        personas=personas, sets=sets, groups=build_groups(personas, sets), problems=problems + set_problems
    )


@dataclass
class LintReport:
    """What ``personakit lint`` checked and found: findings (unsorted, unfiltered), valid personas, sets, journeys."""

    findings: list[Finding] = field(default_factory=list)
    personas: list[Persona] = field(default_factory=list)
    sets: list[PersonaSet] = field(default_factory=list)
    journeys: list[JourneyRef] = field(default_factory=list)


def lint_workspace(paths: Iterable[str | Path], journeys: Iterable[str | Path] | None = None) -> LintReport:
    """Exactly the checks of ``personakit lint <paths> [--journeys …]``: schema, persona and set rules,
    and with ``journeys`` the cross-lint against journeykit files (K000–K004).

    A missing journey path raises ``PersonaError`` like a missing persona path.
    """
    paths = list(paths)
    journeys = list(journeys or [])
    journey_refs, journey_problems = load_journeys(journeys) if journeys else ([], [])
    findings: list[Finding] = []
    personas: list[Persona] = []
    for path in find_persona_files(paths):
        loaded, problems = _load_personas([path])
        findings.extend(pr.finding for pr in problems)
        for p in loaded:
            findings.extend(lint_persona(p))
            personas.append(p)
    sets, set_problems = _load_sets(paths)
    findings.extend(pr.finding for pr in set_problems)
    if sets or len(personas) > 1 or any(Path(x).is_dir() for x in paths):
        findings.extend(lint_sets(personas, sets))
    if journeys:
        members = {m.persona.id for g in build_groups(personas, sets) for m in g.members}
        findings.extend(journey_problems)
        findings.extend(lint_journeys(personas, journey_refs, known=members))
    return LintReport(findings=findings, personas=personas, sets=sets, journeys=journey_refs)
