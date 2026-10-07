"""Sets: the personas of one solution, declared in ``personas/<set-id>/set.yml``.

Membership lives only in ``set.yml``; the folder is just where files are stored. A
persona file exists once and may be listed by several sets, each with its own
priority (the ``priority`` in the persona file is the default). Personas that no
set lists form the loose set (``Group.set is None``) – a repository without any
``set.yml`` behaves as before.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError

from .model import BOM, SET_FILE, SUFFIX, Persona, PersonaError, load_many, to_plain
from .validate import validate, validate_set

LOOSE_TITLE = "Ohne Set"


@dataclass
class PersonaSet:
    """A ``set.yml``: id, title, solution, scope, status and the member list."""

    path: Path
    data: dict[str, Any]

    @property
    def id(self) -> str:
        return str(self.data.get("id", ""))

    @property
    def title(self) -> str:
        return str(self.data.get("title") or self.id)

    @property
    def status(self) -> str:
        return str(self.data.get("status", ""))

    @property
    def dir(self) -> Path:
        return self.path.parent

    @property
    def entries(self) -> list[dict[str, Any]]:
        return list(self.data.get("personas") or [])

    @classmethod
    def load(cls, path: str | Path) -> PersonaSet:
        p = Path(path)
        try:
            text = p.read_bytes().decode("utf-8")
        except UnicodeDecodeError as e:
            raise PersonaError(f"{p}: Datei ist nicht UTF-8-kodiert (Byte {e.start}); als UTF-8 speichern") from e
        if text.startswith(BOM):
            text = text[1:]
        try:
            data = YAML(typ="safe", pure=True).load(text)
        except YAMLError as e:
            raise PersonaError(f"{p}: YAML nicht lesbar – {e}") from e
        if not isinstance(data, dict):
            raise PersonaError(f"{p}: set.yml ist kein Mapping")
        return cls(path=p, data=to_plain(data))

    def export(self) -> dict[str, Any]:
        """Set metadata for exports, without format version and raw member list."""
        return {k: v for k, v in self.data.items() if k not in ("personakit", "personas")}


@dataclass(frozen=True)
class Member:
    """A persona in a group with its effective priority there."""

    persona: Persona
    priority: str

    @property
    def default(self) -> str:
        return str(self.persona.data.get("priority", ""))

    @property
    def overridden(self) -> bool:
        return self.priority != self.default


@dataclass
class Group:
    """Resolved set (or the loose set) – what lint and the grouped exports work on."""

    set: PersonaSet | None
    members: list[Member] = field(default_factory=list)
    unknown: list[str] = field(default_factory=list)  # ids listed in set.yml but not found or invalid
    duplicates: list[str] = field(default_factory=list)  # ids listed more than once

    @property
    def id(self) -> str:
        return self.set.id if self.set else ""

    @property
    def title(self) -> str:
        return self.set.title if self.set else LOOSE_TITLE

    @property
    def is_loose(self) -> bool:
        return self.set is None

    def export(self) -> dict[str, Any]:
        head: dict[str, Any] = self.set.export() if self.set else {"id": None, "title": LOOSE_TITLE}
        head["personas"] = [{"id": m.persona.id, "priority": m.priority} for m in self.members]
        return head


# ---------------------------------------------------------------- loading
def find_set_files(paths: Iterable[str | Path]) -> list[Path]:
    """All ``set.yml`` below the given directories, plus ``set.yml`` files given directly."""
    out: list[Path] = []
    seen: set[Path] = set()
    for raw in paths:
        p = Path(raw)
        found = sorted(p.rglob(SET_FILE)) if p.is_dir() else [p] if p.name == SET_FILE and p.is_file() else []
        for f in found:
            if f.resolve() not in seen:
                seen.add(f.resolve())
                out.append(f)
    return out


def load_sets(paths: Iterable[str | Path]) -> tuple[list[PersonaSet], list[tuple[Path, str]]]:
    """Load and schema-check every ``set.yml``; broken files come back as ``(path, message)``."""
    sets: list[PersonaSet] = []
    errors: list[tuple[Path, str]] = []
    for f in find_set_files(paths):
        try:
            s = PersonaSet.load(f)
        except PersonaError as e:
            errors.append((f, str(e)))
            continue
        problems = validate_set(s.data)
        if problems:
            errors.extend((f, f"{f}: {msg}") for msg in problems)
            continue
        sets.append(s)
    return sets, errors


def _from_context(s: PersonaSet, pid: str) -> Persona | None:
    """Find a member outside the given paths: ``<id>.persona.md`` anywhere below the set's parent folder."""
    root = s.dir.parent
    for f in sorted(root.rglob(f"{pid}{SUFFIX}")):
        try:
            p = Persona.load(f)
        except PersonaError:
            continue
        if p.id == pid and not validate(p):
            return p
    return None


def build_groups(personas: Iterable[Persona], sets: Iterable[PersonaSet]) -> list[Group]:
    """Resolve set members (effective priority = set.yml, else persona default) and collect the loose set.

    Members not among ``personas`` are looked up below the set's parent folder, so a single
    set folder can be linted or rendered on its own even if its personas live elsewhere.
    """
    ps = list(personas)
    index: dict[str, Persona] = {}
    for p in ps:
        index.setdefault(p.id, p)
    groups: list[Group] = []
    listed: set[str] = set()
    for s in sorted(sets, key=lambda x: (x.id, str(x.path))):
        g = Group(set=s)
        seen: set[str] = set()
        for entry in s.entries:
            pid = str(entry.get("id", ""))
            if pid in seen:
                g.duplicates.append(pid)
                continue
            seen.add(pid)
            p = index.get(pid) or _from_context(s, pid)
            if p is None:
                g.unknown.append(pid)
                continue
            index.setdefault(pid, p)
            g.members.append(Member(p, str(entry.get("priority") or p.data.get("priority", ""))))
            listed.add(pid)
        groups.append(g)
    loose = [p for p in ps if p.id not in listed]
    if loose or not groups:
        groups.append(Group(set=None, members=[Member(p, str(p.data.get("priority", ""))) for p in loose]))
    return groups


def load_workspace(paths: Iterable[str | Path]) -> tuple[list[Persona], list[Group]]:
    """Personas and resolved groups for list/render; a broken ``set.yml`` stops with PersonaError."""
    paths = list(paths)
    personas = load_many(paths)
    sets, errors = load_sets(paths)
    if errors:
        raise PersonaError("; ".join(msg for _, msg in errors) + " (Details: personakit lint)")
    return personas, build_groups(personas, sets)


def group_personas(groups: Iterable[Group]) -> list[Persona]:
    """Every persona that appears in a group, once, in group order."""
    out: list[Persona] = []
    seen: set[str] = set()
    for g in groups:
        for m in g.members:
            if m.persona.id not in seen:
                seen.add(m.persona.id)
                out.append(m.persona)
    return out
