"""journeykit coupling: check references between personas and journeys in both directions.

A journey names its persona in ``persona.id``; a persona names its journeys in ``relations.journeys``
(journey ``meta.id``). personakit reads only these two IDs from a journey – it neither imports nor
validates journeykit (that is ``journeykit lint``), so neither format depends on the other.
Decision and rule rationale: docs/JOURNEYKIT.md, docs/METHOD.md 1.9.
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from .lint import ERROR, INFO, WARN, Finding
from .model import Persona, PersonaError

SCHEMA_SUFFIX = (
    ".schema.json"  # journeykit ships its schema as JSON; pointing --journeys at the repo must not trip on it
)


@dataclass(frozen=True)
class JourneyRef:
    """The two IDs personakit needs from a journey file, plus where it came from."""

    id: str
    persona: str
    path: Path
    label: str


def find_journey_files(paths: Iterable[str | Path]) -> list[tuple[Path, str]]:
    """Expand files and directories into ``(path, label)`` pairs; the label is relative to the given folder."""
    out: list[tuple[Path, str]] = []
    seen: set[Path] = set()
    for raw in paths:
        root = Path(raw)
        if root.is_dir():
            found = [(f, f.relative_to(root).as_posix()) for f in sorted(root.rglob("*.json"))]
            found = [(f, label) for f, label in found if not f.name.endswith(SCHEMA_SUFFIX)]
        elif root.is_file():
            found = [(root, root.name)]
        else:
            raise PersonaError(f"Pfad nicht gefunden: {root}")
        for f, label in found:
            if f.resolve() not in seen:
                seen.add(f.resolve())
                out.append((f, label))
    return out


def _id_at(data: dict, key: str) -> str:
    block = data.get(key)
    value = block.get("id") if isinstance(block, dict) else None
    return value if isinstance(value, str) else ""


def load_journeys(paths: Iterable[str | Path]) -> tuple[list[JourneyRef], list[Finding]]:
    """Read ``meta.id`` and ``persona.id`` of every journey file; unreadable files become K000."""
    journeys: list[JourneyRef] = []
    problems: list[Finding] = []
    for path, label in find_journey_files(paths):
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
        except UnicodeDecodeError:
            problems.append(Finding(ERROR, "K000", f"Journey {label} nicht lesbar: nicht UTF-8"))
            continue
        except json.JSONDecodeError as e:
            problems.append(
                Finding(ERROR, "K000", f"Journey {label} nicht lesbar: kein gültiges JSON (Zeile {e.lineno})")
            )
            continue
        jid = _id_at(data, "meta") if isinstance(data, dict) else ""
        pid = _id_at(data, "persona") if isinstance(data, dict) else ""
        if not jid or not pid:
            problems.append(
                Finding(ERROR, "K000", f"Journey {label}: meta.id oder persona.id fehlt – keine journeykit-Journey?")
            )
            continue
        journeys.append(JourneyRef(jid, pid, path, label))
    return journeys, problems


def lint_journeys(personas: list[Persona], journeys: list[JourneyRef], known: Iterable[str] = ()) -> list[Finding]:
    """K001–K004: ``relations.journeys`` against journey IDs, journey ``persona.id`` against persona IDs.

    ``personas`` are the personas being linted; ``known`` adds IDs that resolve elsewhere (set members
    stored outside the given paths), so a journey naming them is not reported as unknown.
    """
    by_id: dict[str, list[JourneyRef]] = {}
    for j in journeys:
        by_id.setdefault(j.id, []).append(j)  # hypothesis and synthesis may share one meta.id
    known_ids = {p.id for p in personas} | set(known)
    out: list[Finding] = []
    for p in personas:
        linked = (p.data.get("relations") or {}).get("journeys") or []
        for jid in linked:
            files = by_id.get(jid)
            if not files:
                out.append(Finding(WARN, "K001", f"relations.journeys verweist auf unbekannte Journey «{jid}»", p.id))
            elif all(j.persona != p.id for j in files):
                others = ", ".join(f"«{x}»" for x in sorted({j.persona for j in files}))
                out.append(
                    Finding(
                        WARN,
                        "K003",
                        f"Journey «{jid}» führt Persona {others}, nicht diese"
                        " – persona.id der Journey oder relations.journeys korrigieren",
                        p.id,
                    )
                )
        for jid in sorted({j.id for j in journeys if j.persona == p.id} - set(linked)):
            out.append(
                Finding(INFO, "K004", f"Journey «{jid}» führt diese Persona – in relations.journeys nachtragen", p.id)
            )
    for j in journeys:
        if j.persona not in known_ids:
            out.append(Finding(WARN, "K002", f"Journey «{j.id}» ({j.label}) nennt unbekannte Persona «{j.persona}»"))
    return out
