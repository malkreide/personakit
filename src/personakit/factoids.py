"""Factoids: single observations from research material – the deterministic bridge to a persona.

A study folder ``factoids/<study>/`` holds one ``<source_id>.factoids.md`` per source (YAML
frontmatter + one Markdown table, one factoid per row) and optionally ``variables.yml`` with
the behaviour scales and their anchors. This module parses and checks the files, places every
participant on the variables (median of their factoids), flags thin variables and outliers,
and pre-fills a persona skeleton from chosen participants.

Interpretation – which participants form a persona, archetype, goals, jobs, simulation rules –
stays with the person or model writing the persona (skills/persona-kit/SKILL.md). Participants
appear as codes only, never with names.
"""

from __future__ import annotations

import re
import statistics
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq
from ruamel.yaml.error import YAMLError
from ruamel.yaml.scalarstring import DoubleQuotedScalarString as DQ

from .lint import ERROR, INFO, WARN
from .model import _FRONTMATTER_RE, BOM, Persona, PersonaError, parse_date, to_plain
from .validate import validate_factoids, validate_variables

SUFFIX = ".factoids.md"
VARIABLES_FILE = "variables.yml"
COLUMNS = ("id", "participant", "observation", "variable", "value", "quote")
REQUIRED_COLUMNS = ("id", "participant", "observation")
# A code, not a name: up to three letters, optional separator, a number (p1, P07, ip-3, tn_12).
PARTICIPANT_RE = re.compile(r"^[A-Za-z]{1,3}[-_]?[0-9]{1,4}$")
FACTOID_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
TRUE = {"ja", "yes", "true", "x", "1", "✓", "✔"}
FALSE = {"", "nein", "no", "false", "0", "-", "–"}

MIN_PLACED = 3  # a variable needs at least this many placed participants …
MIN_SHARE = 0.5  # … and at least this share of all participants (F010)
GAP = 2  # points on the 1–5 scale that separate two personas (references/elicitation.md, D)
GAP_VARIABLES = 2  # … on at least this many variables (F011, skeleton hint)
QUALITATIVE_MIN = 5  # NN/g: qualitative personas start at 5 interviews (METHOD.md 1.3)
FIRST_HAND = ("interview", "observation")

_LEVEL_ORDER = {ERROR: 0, WARN: 1, INFO: 2}
_CELL_SPLIT = re.compile(r"(?<!\\)\|")
_SEPARATOR = re.compile(r"^\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)*\|?$")
_CODE_PARTS = re.compile(r"^([A-Za-z]*)[-_]?([0-9]+)$")
_QUOTE_MARKS = {"«": "»", "„": "“", '"': '"', "“": "”", "‹": "›", "'": "'"}


@dataclass(frozen=True)
class FactoidFinding:
    level: str
    code: str
    message: str
    source: str = ""

    def __str__(self) -> str:
        who = f"[{self.source}] " if self.source else ""
        return f"{self.level:5} {self.code:<6} {who}{self.message}"


@dataclass(frozen=True)
class Factoid:
    id: str
    participant: str
    observation: str
    variable: str = ""
    value: int | None = None
    quote: bool = False
    source: str = ""  # source_id of the file
    line: int = 0


@dataclass
class FactoidSource:
    """One ``*.factoids.md`` file: frontmatter describing the source, factoids from its table."""

    path: Path
    data: dict[str, Any]
    factoids: list[Factoid] = field(default_factory=list)
    valid: bool = True  # frontmatter passed the schema

    @property
    def source_id(self) -> str:
        return str(self.data.get("source_id") or self.path.name.removesuffix(SUFFIX))

    @property
    def type(self) -> str:
        return str(self.data.get("type", ""))

    @property
    def title(self) -> str:
        return str(self.data.get("title") or self.source_id)

    @property
    def n(self) -> int:
        return int(self.data.get("n") or 0)

    @property
    def participants(self) -> list[str]:
        return sort_codes({f.participant for f in self.factoids})


@dataclass(frozen=True)
class Scale:
    name: str
    low: str = ""
    high: str = ""


@dataclass
class Study:
    """All factoid sources of one folder plus the optional scale definitions."""

    root: Path
    sources: list[FactoidSource] = field(default_factory=list)
    scales: list[Scale] = field(default_factory=list)
    findings: list[FactoidFinding] = field(default_factory=list)  # from reading and checking the files

    @property
    def valid_sources(self) -> list[FactoidSource]:
        return [s for s in self.sources if s.valid]

    def factoids(self) -> list[Factoid]:
        return [f for s in self.valid_sources for f in s.factoids]

    def participants(self) -> list[str]:
        return sort_codes({f.participant for f in self.factoids()})

    def variables(self) -> list[str]:
        """Scales from variables.yml in their order, then further variables in order of appearance."""
        names = [s.name for s in self.scales]
        for f in self.factoids():
            if f.variable and f.variable not in names:
                names.append(f.variable)
        return names

    def scale(self, name: str) -> Scale:
        return next((s for s in self.scales if s.name == name), Scale(name))

    def positions(self) -> dict[str, dict[str, float]]:
        """``{variable: {participant: median of the participant's values}}``."""
        values: dict[str, dict[str, list[int]]] = {v: {} for v in self.variables()}
        for f in self.factoids():
            if f.variable and f.value is not None:
                values[f.variable].setdefault(f.participant, []).append(f.value)
        return {
            v: {p: float(statistics.median(vals)) for p, vals in sorted(by.items(), key=lambda x: code_key(x[0]))}
            for v, by in values.items()
        }


# ---------------------------------------------------------------- helpers
def code_key(code: str) -> tuple[str, int, str]:
    """Natural order for participant codes: p2 before p10."""
    m = _CODE_PARTS.match(code)
    return (m.group(1).lower(), int(m.group(2)), code) if m else (code.lower(), 0, code)


def sort_codes(codes) -> list[str]:
    return sorted(codes, key=code_key)


def scale_value(x: float) -> int:
    """Round a median to a scale step; exactly between two steps → the one nearer the middle (3)."""
    low = int(x // 1)
    frac = x - low
    if frac < 0.5:
        return low
    if frac > 0.5:
        return low + 1
    return low if abs(low - 3) < abs(low + 1 - 3) else low + 1


def fmt_num(x: float) -> str:
    return f"{x:g}"


def fmt_range(values) -> str:
    lo, hi = min(values), max(values)
    return fmt_num(lo) if lo == hi else f"{fmt_num(lo)}–{fmt_num(hi)}"


def _cells(line: str) -> list[str]:
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|") and not s.endswith("\\|"):
        s = s[:-1]
    return [c.strip().replace("\\|", "|") for c in _CELL_SPLIT.split(s)]


def _strip_quote_marks(text: str) -> str:
    t = text.strip()
    if len(t) >= 2 and _QUOTE_MARKS.get(t[0]) == t[-1]:
        return t[1:-1].strip()
    return t


def _read_text(path: Path) -> str:
    try:
        text = path.read_bytes().decode("utf-8")
    except UnicodeDecodeError as e:
        raise PersonaError(f"Datei ist nicht UTF-8-kodiert (Byte {e.start}); als UTF-8 speichern") from e
    if text.startswith(BOM):
        text = text[1:]
    return text.replace("\r\n", "\n")


def _yaml_mapping(text: str, what: str) -> dict[str, Any]:
    try:
        data = YAML(typ="safe", pure=True).load(text)
    except YAMLError as e:
        raise PersonaError(f"YAML nicht lesbar – {e}") from e
    if not isinstance(data, dict):
        raise PersonaError(f"{what} ist kein Mapping")
    return to_plain(data)


# ---------------------------------------------------------------- loading
def _load_source(path: Path) -> tuple[FactoidSource | None, list[FactoidFinding]]:
    name = path.name
    out: list[FactoidFinding] = []
    try:
        text = _read_text(path)
        m = _FRONTMATTER_RE.match(text)
        if not m:
            raise PersonaError("kein YAML-Frontmatter gefunden (--- … ---)")
        data = _yaml_mapping(m.group(1), "Frontmatter")
    except PersonaError as e:
        return None, [FactoidFinding(ERROR, "F000", str(e), name)]

    problems = validate_factoids(data)
    src = FactoidSource(path=path, data=data, valid=not problems)
    label = src.source_id
    out.extend(FactoidFinding(ERROR, "F001", msg, label) for msg in problems)
    if not problems and name != f"{src.source_id}{SUFFIX}":
        out.append(
            FactoidFinding(
                ERROR, "F002", f"Dateiname «{name}» passt nicht zur source_id (erwartet {src.source_id}{SUFFIX})", label
            )
        )

    first_line = text[: m.end()].count("\n") + 2  # 1-based number of the first body line
    lines = text[m.end() :].split("\n")[1:]
    start = next(
        (
            i
            for i, line in enumerate(lines[:-1])
            if line.lstrip().startswith("|") and _SEPARATOR.match(lines[i + 1].strip())
        ),
        None,
    )
    if start is None:
        out.append(FactoidFinding(ERROR, "F004", "Keine Factoid-Tabelle im Body (Kopfzeile + Trennzeile |---|)", label))
        return src, out
    header = [c.lower() for c in _cells(lines[start])]
    unknown = [c for c in header if c not in COLUMNS]
    missing = [c for c in REQUIRED_COLUMNS if c not in header]
    if unknown or missing:
        parts = []
        if missing:
            parts.append(f"Pflichtspalte fehlt: {', '.join(missing)}")
        if unknown:
            parts.append(f"unbekannte Spalte: {', '.join(unknown)}")
        out.append(FactoidFinding(ERROR, "F004", f"{'; '.join(parts)} – erlaubt: {', '.join(COLUMNS)}", label))
        return src, out

    for offset, line in enumerate(lines[start + 2 :]):
        if not line.lstrip().startswith("|"):
            break
        lineno = first_line + start + 2 + offset
        fact, finding = _parse_row(_cells(line), header, lineno, label)
        if finding:
            out.append(finding)
        elif fact:
            src.factoids.append(fact)
    if not src.factoids and not any(f.code in ("F005", "F006") for f in out):
        out.append(FactoidFinding(ERROR, "F004", "Factoid-Tabelle ohne Zeilen", label))
    return src, out


def _parse_row(
    cells: list[str], header: list[str], lineno: int, label: str
) -> tuple[Factoid | None, FactoidFinding | None]:
    def bad(code: str, msg: str) -> tuple[None, FactoidFinding]:
        return None, FactoidFinding(ERROR, code, f"Zeile {lineno}: {msg}", label)

    if len(cells) != len(header):
        return bad("F005", f"{len(cells)} Zellen, der Kopf hat {len(header)} – «|» im Text als «\\|» schreiben")
    row = dict(zip(header, cells))
    empty = [c for c in REQUIRED_COLUMNS if not row[c]]
    if empty:
        return bad("F005", f"leere Pflichtzelle: {', '.join(empty)}")
    fid = row["id"]
    if not FACTOID_ID_RE.match(fid):
        return bad("F005", f"id «{fid}» ungültig (Buchstaben, Ziffern, . _ -)")
    if not PARTICIPANT_RE.match(row["participant"]):
        # the cell is deliberately not echoed: it may hold a name
        return bad(
            "F006",
            f"Factoid {fid}: participant ist kein Teilnehmer-Code (z. B. p1, P07, ip-3) – nie Namen eintragen",
        )
    variable = row.get("variable", "")
    raw = row.get("value", "")
    value = None
    if raw:
        if not (raw.isdigit() and 1 <= int(raw) <= 5):
            return bad("F005", f"Factoid {fid}: value «{raw}» ist keine ganze Zahl 1–5")
        if not variable:
            return bad("F005", f"Factoid {fid}: value ohne variable – auf welcher Skala?")
        value = int(raw)
    quote = row.get("quote", "").lower()
    if quote not in TRUE | FALSE:
        return bad("F005", f"Factoid {fid}: quote «{row['quote']}» ist kein Wahrheitswert (ja/nein)")
    return (
        Factoid(
            id=fid,
            participant=row["participant"],
            observation=row["observation"],
            variable=variable,
            value=value,
            quote=quote in TRUE,
            source=label,
            line=lineno,
        ),
        None,
    )


def _load_scales(path: Path) -> tuple[list[Scale] | None, list[FactoidFinding]]:
    try:
        data = _yaml_mapping(_read_text(path), VARIABLES_FILE)
    except PersonaError as e:
        return None, [FactoidFinding(ERROR, "F000", str(e), VARIABLES_FILE)]
    problems = validate_variables(data)
    if problems:
        return None, [FactoidFinding(ERROR, "F001", msg, VARIABLES_FILE) for msg in problems]
    scales = [Scale(v["name"], v.get("low", ""), v.get("high", "")) for v in data["variables"]]
    names = [s.name for s in scales]
    dupes = sorted({n for n in names if names.count(n) > 1})
    if dupes:
        return None, [FactoidFinding(ERROR, "F001", f"Variable mehrfach definiert: {', '.join(dupes)}", VARIABLES_FILE)]
    return scales, []


def load_study(path: str | Path) -> Study:
    """Read and check a study folder (or a single factoid file); problems become findings."""
    p = Path(path)
    if p.is_dir():
        root, files = p, sorted(p.glob(f"*{SUFFIX}"))
    elif p.is_file():
        root, files = p.parent, [p]
    else:
        raise PersonaError(f"Pfad nicht gefunden: {p}")
    if not files:
        nested = sorted({f.parent.name for f in p.rglob(f"*{SUFFIX}")})
        hint = f"; Studienordner angeben, z. B. {p / nested[0]}" if nested else ""
        raise PersonaError(f"Keine *{SUFFIX}-Dateien in {p}{hint}")

    study = Study(root=root)
    scale_file = root / VARIABLES_FILE
    scales: list[Scale] | None = None
    if scale_file.is_file():
        scales, problems = _load_scales(scale_file)
        study.findings.extend(problems)
        study.scales = scales or []

    for f in files:
        src, problems = _load_source(f)
        study.findings.extend(problems)
        if src is not None:
            study.sources.append(src)

    ids = Counter(s.source_id for s in study.valid_sources)
    for sid in sorted(i for i, c in ids.items() if c > 1):
        where = ", ".join(s.path.name for s in study.valid_sources if s.source_id == sid)
        study.findings.append(FactoidFinding(ERROR, "F003", f"source_id «{sid}» mehrfach vorhanden ({where})", sid))

    seen: dict[str, Factoid] = {}
    for s in study.sources:
        for fact in s.factoids:
            first = seen.setdefault(fact.id, fact)
            if first is not fact:
                study.findings.append(
                    FactoidFinding(
                        ERROR,
                        "F007",
                        f"Factoid-id «{fact.id}» mehrfach vorhanden (zuerst {first.source}, Zeile {first.line};"
                        f" erneut Zeile {fact.line}) – IDs gelten im ganzen Studienordner",
                        fact.source,
                    )
                )
            if scales is not None and fact.variable and fact.variable not in {x.name for x in scales}:
                study.findings.append(
                    FactoidFinding(
                        ERROR,
                        "F008",
                        f"Zeile {fact.line}: Variable «{fact.variable}» steht nicht in {VARIABLES_FILE}",
                        fact.source,
                    )
                )
    return study


# ---------------------------------------------------------------- analysis
def analyse_study(study: Study) -> list[FactoidFinding]:
    """Coverage of the variables (F010), sources with more codes than n (F009), outliers (F011)."""
    out: list[FactoidFinding] = []
    for s in study.valid_sources:
        k = len(s.participants)
        if s.n and k > s.n:
            out.append(
                FactoidFinding(WARN, "F009", f"{k} Teilnehmer-Codes, aber n = {s.n} – n oder Codes prüfen", s.source_id)
            )

    participants = study.participants()
    total = len(participants)
    positions = study.positions()
    for v in study.variables():
        placed = len(positions[v])
        if placed < MIN_PLACED or placed < MIN_SHARE * total:
            out.append(
                FactoidFinding(
                    WARN,
                    "F010",
                    f"Variable «{v}» nur bei {placed} von {total} Teilnehmenden verortet – zu dünn für Häufungen:"
                    " nachkodieren, Material ergänzen oder Variable streichen",
                )
            )

    for p in participants:
        apart = []
        for v, pos in positions.items():
            others = [x for q, x in pos.items() if q != p]
            if p in pos and others and all(abs(pos[p] - x) >= GAP for x in others):
                apart.append(f"{v}: {fmt_num(pos[p])} vs. {fmt_range(others)}")
        if len(apart) >= GAP_VARIABLES:
            out.append(
                FactoidFinding(
                    INFO,
                    "F011",
                    f"{p} weicht auf {len(apart)} Variablen um ≥ {GAP} Punkte von allen anderen ab ({'; '.join(apart)})"
                    " – Kandidat für eine eigene Persona oder für simulation.variance",
                )
            )
    return out


def sort_findings(findings) -> list[FactoidFinding]:
    return sorted(findings, key=lambda f: (_LEVEL_ORDER[f.level], f.source, f.code))


# ---------------------------------------------------------------- report
def render_report(study: Study, findings: list[FactoidFinding]) -> str:
    participants = study.participants()
    positions = study.positions()
    o = [f"# Factoids – {study.root.name}", "", "## Quellen", ""]
    o += ["| Quelle | Typ | Datum | n | Teilnehmende | Factoids | Zitate |", "|---|---|---|---:|---|---:|---:|"]
    for s in study.sources:
        sid = s.source_id if s.valid else f"{s.source_id} (ungültig)"
        o.append(
            f"| {sid} | {s.type} | {s.data.get('date', '')} | {s.n or ''} | {', '.join(s.participants)} "
            f"| {len(s.factoids)} | {sum(f.quote for f in s.factoids)} |"
        )

    o += ["", "## Verortung", "", "Median der Factoid-Werte je Teilnehmer und Variable; · = nicht verortet.", ""]
    o.append("| Variable | " + " | ".join(participants) + " | verortet |")
    o.append("|---|" + "---:|" * len(participants) + "---:|")
    for v in study.variables():
        pos = positions[v]
        cells = [fmt_num(pos[p]) if p in pos else "·" for p in participants]
        o.append(f"| {v} | " + " | ".join(cells) + f" | {len(pos)}/{len(participants)} |")

    o += ["", "## Verteilung", "", "Teilnehmende je Skalenstufe; * = Median zwischen zwei Stufen.", ""]
    o += ["| Variable | 1 | 2 | 3 | 4 | 5 |", "|---|---|---|---|---|---|"]
    for v in study.variables():
        steps: dict[int, list[str]] = {i: [] for i in range(1, 6)}
        for p, x in positions[v].items():
            steps[scale_value(x)].append(p + ("" if float(x).is_integer() else "*"))
        o.append(f"| {v} | " + " | ".join(" ".join(steps[i]) for i in range(1, 6)) + " |")

    o += ["", "## Befunde", ""]
    o += [f"    {f}" for f in sort_findings(findings)] or ["Keine."]
    return "\n".join(o) + "\n"


def report_json(study: Study, findings: list[FactoidFinding]) -> dict[str, Any]:
    positions = study.positions()
    return {
        "study": study.root.name,
        "sources": [
            {
                "source_id": s.source_id,
                "type": s.type,
                "date": s.data.get("date"),
                "n": s.n or None,
                "valid": s.valid,
                "participants": s.participants,
                "factoids": len(s.factoids),
                "quotes": sum(f.quote for f in s.factoids),
                "path": s.path.as_posix(),
            }
            for s in study.sources
        ],
        "participants": study.participants(),
        "variables": [
            {"name": v, "low": study.scale(v).low, "high": study.scale(v).high, "placed": len(positions[v])}
            for v in study.variables()
        ],
        "positions": positions,
        "findings": [
            {"level": f.level, "code": f.code, "source": f.source, "message": f.message}
            for f in sort_findings(findings)
        ],
    }


# ---------------------------------------------------------------- skeleton
@dataclass
class Skeleton:
    persona: Persona
    evidence_level: str
    first_hand: int  # participants with factoids from interviews or observations
    hints: list[str] = field(default_factory=list)


def build_skeleton(study: Study, participants: list[str], persona: Persona, label: str) -> Skeleton:
    """Fill behaviour.variables, evidence, quotes and evidence_level of a fresh template persona.

    Values are medians over the chosen participants (each participant first reduced to the
    median of their factoids). Everything that needs interpretation stays empty; a
    ``## Herleitung`` section lists which factoids back which value.
    """
    known = set(study.participants())
    missing = [p for p in participants if p not in known]
    if missing:
        raise PersonaError(
            f"Unbekannte Teilnehmer-Codes: {', '.join(missing)} – vorhanden: {', '.join(study.participants())}"
        )
    chosen = sort_codes(dict.fromkeys(participants))
    facts = [f for f in study.factoids() if f.participant in chosen]
    used = sorted(
        (s for s in study.valid_sources if any(f.source == s.source_id for f in facts)),
        key=lambda s: (FIRST_HAND.index(s.type) if s.type in FIRST_HAND else len(FIRST_HAND), str(s.data.get("date"))),
    )
    ev = {s.source_id: f"E{i}" for i, s in enumerate(used, 1)}
    types = {s.source_id: s.type for s in used}
    first_hand = len({f.participant for f in facts if types[f.source] in FIRST_HAND})
    level = "qualitative" if first_hand >= QUALITATIVE_MIN else "proto"
    hints: list[str] = []
    if level == "proto":
        hints.append(
            f"evidence_level proto: {first_hand} Interviews/Beobachtungen (< {QUALITATIVE_MIN}) – assumptions füllen (E001)"
        )

    positions = study.positions()
    variables = CommentedSeq()
    rows: list[str] = []
    uncovered: list[str] = []
    thin: list[str] = []
    for v in study.variables():
        pos = {p: x for p, x in positions[v].items() if p in chosen}
        if not pos:
            uncovered.append(v)
            continue
        med = statistics.median(pos.values())
        value = scale_value(med)
        backing = [f for f in facts if f.variable == v and f.value is not None]
        top = Counter(f.source for f in backing).most_common(1)[0][0]
        scale = study.scale(v)
        item = CommentedMap()
        item["name"] = DQ(v)
        item["low"] = DQ(scale.low)
        item["high"] = DQ(scale.high)
        item["value"] = value
        item["evidence"] = ev[top]
        variables.append(item)
        spread = fmt_range(pos.values())
        placed = " · ".join(f"{p} {fmt_num(x)}" for p, x in pos.items())
        ids = ", ".join(f.id for f in backing)
        rows.append(f"| {v} | {value} | {fmt_num(med)} | {spread} | {placed} | {ids} |")
        if len(pos) < MIN_SHARE * len(chosen):
            thin.append(f"{v} ({len(pos)} von {len(chosen)})")
    if thin:
        hints.append("Bei weniger als der Hälfte der Gewählten verortet – Wert vorläufig: " + ", ".join(thin))
    if uncovered:
        hints.append("Ohne Verortung bei den gewählten Teilnehmenden (→ unknowns): " + ", ".join(uncovered))

    # two chosen participants this far apart are two personas by the rule in references/elicitation.md
    for i, a in enumerate(chosen):
        for b in chosen[i + 1 :]:
            far = [v for v, pos in positions.items() if a in pos and b in pos and abs(pos[a] - pos[b]) >= GAP]
            if len(far) >= GAP_VARIABLES:
                hints.append(
                    f"{a} und {b} liegen auf {len(far)} Variablen ≥ {GAP} Punkte auseinander ({', '.join(far)})"
                    " – Frankenstein-Gefahr: Auswahl prüfen oder in simulation.variance festhalten"
                )

    evidence = CommentedSeq()
    for s in used:
        who = sort_codes({f.participant for f in facts if f.source == s.source_id})
        e = CommentedMap()
        e["id"] = ev[s.source_id]
        e["type"] = s.type
        e["source"] = DQ(s.title)
        date = parse_date(s.data.get("date"))
        if date:
            e["date"] = date
        e["n"] = len(who)
        total = f" von n = {s.n}" if s.n else ""
        e["note"] = DQ(f"Factoids {s.source_id}: Teilnehmende {', '.join(who)}{total}")
        e["ref"] = DQ(s.path.as_posix())
        evidence.append(e)

    quotes = CommentedSeq()
    for f in facts:
        if f.quote:
            q = CommentedMap()
            q["text"] = DQ(_strip_quote_marks(f.observation))
            q["evidence"] = ev[f.source]
            quotes.append(q)

    d = persona.data
    d["evidence_level"] = level
    d["behaviour"]["variables"] = variables
    d["quotes"] = quotes
    d["evidence"] = evidence
    if uncovered:
        d["unknowns"] = CommentedSeq(
            DQ(f"Verortung auf «{v}» bei den Teilnehmenden {', '.join(chosen)} nicht belegt") for v in uncovered
        )
    log = d.get("changelog") or []
    if log:
        log[0]["note"] = DQ(f"Skelett aus Factoids {label} ({', '.join(chosen)})")

    quoted = [f"{f.id} ({f.participant})" for f in facts if f.quote]
    h = [
        "",
        "## Herleitung",
        "",
        "<!-- Erzeugt von «personakit skeleton» (deterministischer Teil). Interpretation ergänzen und jede"
        " Aussage mit Factoid-IDs belegen, z. B. «Archetyp ← I02, I05» oder «J1 ← I07, B01». -->",
        "",
        f"Factoids aus `{label}`, Teilnehmende {', '.join(chosen)}: {first_hand} mit Interview oder Beobachtung"
        f" → evidence_level {level}.",
        "",
        "| Variable | Wert | Median | Spanne | Teilnehmende | Factoids |",
        "|---|---:|---:|---|---|---|",
        *rows,
        "",
        "Wert = Median über die Teilnehmenden (je Teilnehmer zuerst der Median seiner Factoids);"
        " liegt er zwischen zwei Stufen, gilt die Stufe näher bei 3.",
    ]
    if quoted:
        h += ["", f"Zitate: {', '.join(quoted)}."]
    if hints:
        h += [""] + [f"- Hinweis: {x}" for x in hints]
    persona.body = persona.body.rstrip("\n") + "\n" + "\n".join(h) + "\n"
    return Skeleton(persona=persona, evidence_level=level, first_hand=first_hand, hints=hints)
