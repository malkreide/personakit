"""Load, save and normalise persona files (YAML frontmatter + Markdown body)."""

from __future__ import annotations

import datetime as _dt
import io
import re
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq

SUFFIX = ".persona.md"
BOM = "\ufeff"
_FRONTMATTER_RE = re.compile(r"\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?=\r?\n|\Z)", re.DOTALL)


class PersonaError(Exception):
    """Raised for malformed persona files."""


def _yaml() -> YAML:
    y = YAML(typ="rt")
    y.preserve_quotes = True
    y.width = 4096  # never re-wrap long strings → clean git diffs
    y.indent(mapping=2, sequence=4, offset=2)
    y.representer.ignore_aliases = lambda *_: True  # no &id001 anchors for repeated dates
    return y


@dataclass
class Persona:
    """A persona file: round-trip YAML frontmatter + Markdown body."""

    path: Path | None
    data: CommentedMap
    body: str = ""
    sections: dict[str, str] = field(default_factory=dict)
    newline: str = "\n"  # line ending of the source file, restored by to_text()
    bom: bool = False  # source file started with a UTF-8 BOM (e.g. Windows Notepad)

    # ------------------------------------------------------------------ access
    @property
    def id(self) -> str:
        return str(self.data.get("id", ""))

    @property
    def archetype(self) -> str:
        return str(self.data.get("archetype", ""))

    @property
    def display_name(self) -> str:
        name = self.data.get("name")
        return f"{name} – {self.archetype}" if name else self.archetype

    def get(self, dotted: str, default: Any = None) -> Any:
        """``p.get("goals.end")`` → nested lookup with a default."""
        cur: Any = self.data
        for part in dotted.split("."):
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                return default
        return cur

    def plain(self) -> dict[str, Any]:
        """Frontmatter as plain JSON-compatible dict (dates → ISO strings)."""
        return to_plain(self.data)

    # -------------------------------------------------------------------- io
    @classmethod
    def from_text(cls, text: str, path: Path | None = None) -> Persona:
        bom = text.startswith(BOM)
        if bom:
            text = text[1:]
        first_eol = re.search(r"\r?\n", text)
        newline = first_eol.group(0) if first_eol else "\n"
        text = text.replace("\r\n", "\n")  # work on LF internally; mixed files end up uniform
        m = _FRONTMATTER_RE.match(text)
        if not m:
            raise PersonaError(f"{path or '<text>'}: kein YAML-Frontmatter gefunden (--- … ---)")
        data = _yaml().load(m.group(1))
        if not isinstance(data, dict):
            raise PersonaError(f"{path or '<text>'}: Frontmatter ist kein Mapping")
        body = text[m.end() :]
        return cls(path=path, data=data, body=body, sections=split_sections(body), newline=newline, bom=bom)

    @classmethod
    def load(cls, path: str | Path) -> Persona:
        p = Path(path)
        try:
            # decode bytes ourselves: read_text() would silently translate CRLF to LF
            text = p.read_bytes().decode("utf-8")
        except UnicodeDecodeError as e:
            raise PersonaError(f"{p}: Datei ist nicht UTF-8-kodiert (Byte {e.start}); als UTF-8 speichern") from e
        return cls.from_text(text, path=p)

    def to_text(self) -> str:
        buf = io.StringIO()
        _yaml().dump(self.data, buf)
        fm = buf.getvalue().rstrip("\n")
        body = self.body if self.body.startswith("\n") else "\n" + self.body
        if not body.endswith("\n"):
            body += "\n"
        text = f"---\n{fm}\n---{body}"
        if self.newline != "\n":
            text = text.replace("\n", self.newline)
        return (BOM if self.bom else "") + text

    def add_changelog(self, version: str, date: _dt.date, note: str) -> None:
        """Append a changelog entry using quoted scalars (consistent with hand-written files)."""
        from ruamel.yaml.scalarstring import DoubleQuotedScalarString as DQ

        entry = CommentedMap()
        entry["version"] = DQ(version)
        entry["date"] = _dt.date(date.year, date.month, date.day)
        entry["note"] = DQ(note)
        log = self.data.get("changelog")
        if log is None:
            log = CommentedSeq()
            self.data["changelog"] = log
        log.append(entry)

    def save(self, path: str | Path | None = None) -> Path:
        target = Path(path) if path else self.path
        if target is None:
            raise PersonaError("Kein Zielpfad zum Speichern")
        write_text(target, self.to_text())
        self.path = target
        return target


# ---------------------------------------------------------------- helpers
def write_text(path: Path, text: str) -> None:
    """Write UTF-8 exactly as given – no newline translation, also on Windows."""
    path.write_bytes(text.encode("utf-8"))


def to_plain(obj: Any) -> Any:
    """Recursively convert ruamel containers and dates into plain Python."""
    if isinstance(obj, (CommentedMap, dict)):
        return {str(k): to_plain(v) for k, v in obj.items()}
    if isinstance(obj, (CommentedSeq, list, tuple)):
        return [to_plain(v) for v in obj]
    if isinstance(obj, _dt.datetime):
        return obj.date().isoformat()
    if isinstance(obj, _dt.date):
        return obj.isoformat()
    if isinstance(obj, bool):
        return bool(obj)
    if isinstance(obj, int):
        return int(obj)
    if isinstance(obj, float):
        return float(obj)
    if isinstance(obj, str):  # strips ruamel scalar-string subclasses
        return str(obj)
    return obj


def split_sections(body: str) -> dict[str, str]:
    """Split a Markdown body into ``{heading: text}`` on level-2 headings."""
    sections: dict[str, str] = {}
    current = "_intro"
    buf: list[str] = []
    for line in body.splitlines():
        if line.startswith("## "):
            sections[current] = "\n".join(buf).strip()
            current = line[3:].strip()
            buf = []
        else:
            buf.append(line)
    sections[current] = "\n".join(buf).strip()
    return {k: strip_html_comments(v) for k, v in sections.items() if v}


def strip_html_comments(text: str) -> str:
    return re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL).strip()


def find_persona_files(paths: Iterable[str | Path]) -> list[Path]:
    """Expand files and directories into a sorted list of ``*.persona.md`` files."""
    out: list[Path] = []
    for raw in paths:
        p = Path(raw)
        if p.is_dir():
            out.extend(sorted(p.rglob(f"*{SUFFIX}")))
        elif p.is_file():
            out.append(p)
        else:
            raise PersonaError(f"Pfad nicht gefunden: {p}")
    # de-duplicate, keep order
    seen: set[Path] = set()
    uniq = []
    for p in out:
        rp = p.resolve()
        if rp not in seen:
            seen.add(rp)
            uniq.append(p)
    return uniq


def load_many(paths: Iterable[str | Path]) -> list[Persona]:
    return [Persona.load(p) for p in find_persona_files(paths)]


def today() -> _dt.date:
    return _dt.date.today()


def parse_date(value: Any) -> _dt.date | None:
    if value is None:
        return None
    if isinstance(value, _dt.datetime):
        return value.date()
    if isinstance(value, _dt.date):
        return value
    try:
        return _dt.date.fromisoformat(str(value))
    except ValueError:
        return None
