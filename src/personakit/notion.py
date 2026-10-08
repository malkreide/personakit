"""Notion export: personas → JSON for a database «Personas». No network calls.

One block model, two targets:

- ``api`` – page bodies for the Notion REST API (``POST /v1/pages``): ``properties`` and
  ``children`` as block objects. The caller adds ``parent``; blocks beyond the API limit
  of 100 per request come as ``append`` batches for ``PATCH /v1/blocks/{page_id}/children``.
- ``mcp`` – the same page for the Notion MCP tools: flat property values
  (``notion-create-pages`` / ``notion-update-page``) and the content as Notion-flavored
  Markdown, rendered from the API blocks so both targets carry the same text.

The property ``ID`` is the upsert key: one page per persona, also when it belongs to
several sets. ``Priorität`` is therefore the default from the persona file; the priority
per set is listed in the page under «Rolle in Sets».
"""

from __future__ import annotations

import json
import re
from typing import Any

from . import __version__
from .model import Persona
from .render import LE, L, _bar
from .sets import Group, Member, group_personas

TARGETS = ("api", "mcp")
DATABASE_TITLE = "Personas"
MAX_TEXT = 2000  # characters (UTF-16 code units) per rich text object
MAX_CHILDREN = 100  # blocks per children array and request

PROPERTIES: dict[str, str] = {
    "Name": "title",
    "ID": "rich_text",
    "Archetyp": "rich_text",
    "Set": "multi_select",
    "Priorität": "select",
    "Status": "select",
    "Evidenz": "select",
    "Version": "rich_text",
    "Review bis": "date",
    "Tags": "multi_select",
}
_OPTIONS: dict[str, dict[str, str]] = {
    "Priorität": {"primary": "blue", "secondary": "green", "supplemental": "gray", "negative": "red"},
    "Status": {"draft": "yellow", "active": "green", "retired": "gray"},
    "Evidenz": {"proto": "orange", "qualitative": "blue", "statistical": "purple"},
}
_DDL_TYPE = {
    "title": "TITLE",
    "rich_text": "RICH_TEXT",
    "date": "DATE",
    "select": "SELECT",
    "multi_select": "MULTI_SELECT",
}

Spans = list[tuple[str, str]]  # (text, style) with style "" | "b" (bold) | "i" (italic) | "c" (code)


# ------------------------------------------------------------ rich text
_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def _clean(text: Any) -> str:
    return _CONTROL.sub("", str(text).replace("\r\n", "\n").replace("\r", "\n"))


def _units(ch: str) -> int:
    return 2 if ord(ch) > 0xFFFF else 1


def _chunks(text: str, limit: int = MAX_TEXT) -> list[str]:
    """Split into pieces of at most ``limit`` UTF-16 code units (Notion's count), never inside a character."""
    out: list[str] = []
    start = size = 0
    for i, ch in enumerate(text):
        n = _units(ch)
        if size + n > limit:
            out.append(text[start:i])
            start, size = i, 0
        size += n
    out.append(text[start:])
    return [c for c in out if c]


def rich(spans: Spans | str) -> list[dict[str, Any]]:
    """Notion rich text objects; long text is split at the 2000-character limit."""
    if isinstance(spans, str):
        spans = [(spans, "")]
    out: list[dict[str, Any]] = []
    for text, style in spans:
        for piece in _chunks(_clean(text)):
            obj: dict[str, Any] = {"type": "text", "text": {"content": piece}}
            if style:
                obj["annotations"] = {"bold": style == "b", "italic": style == "i", "code": style == "c"}
            out.append(obj)
    return out


# --------------------------------------------------------------- blocks
def _block(kind: str, spans: Spans | str, children: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    body: dict[str, Any] = {"rich_text": rich(spans)}
    if children:
        body["children"] = children
    return {"object": "block", "type": kind, kind: body}


def h2(text: str) -> dict[str, Any]:
    return _block("heading_2", text)


def h3(text: str) -> dict[str, Any]:
    return _block("heading_3", text)


def para(spans: Spans | str) -> dict[str, Any]:
    return _block("paragraph", spans)


def bullet(spans: Spans | str, children: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    return _block("bulleted_list_item", spans, children)


def numbered(spans: Spans | str) -> dict[str, Any]:
    return _block("numbered_list_item", spans)


def quote(spans: Spans | str) -> dict[str, Any]:
    return _block("quote", spans)


def toggles(title: str, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Toggle with ``items`` as children; more than 100 items are split into numbered toggles."""
    parts = [items[i : i + MAX_CHILDREN] for i in range(0, len(items), MAX_CHILDREN)] or [[]]
    if len(parts) == 1:
        return [_block("toggle", title, parts[0])]
    return [_block("toggle", f"{title} ({n}/{len(parts)})", part) for n, part in enumerate(parts, 1)]


def tables(header: list[str], rows: list[list[Spans | str]]) -> list[dict[str, Any]]:
    """Table with a header row; more than 99 data rows are split into several tables, each with the header."""
    width = max([len(header)] + [len(r) for r in rows])

    def row(cells: list[Spans | str]) -> dict[str, Any]:
        cells = list(cells) + [""] * (width - len(cells))
        return {"object": "block", "type": "table_row", "table_row": {"cells": [rich(c) for c in cells]}}

    step = MAX_CHILDREN - 1
    parts = [rows[i : i + step] for i in range(0, len(rows), step)] or [[]]
    return [
        {
            "object": "block",
            "type": "table",
            "table": {
                "table_width": width,
                "has_column_header": True,
                "has_row_header": False,
                "children": [row(list(header))] + [row(r) for r in part],
            },
        }
        for part in parts
    ]


# ------------------------------------------------------- markdown body
_TABLE_SEP = re.compile(r"^:?-{1,}:?$")
_NUMBERED = re.compile(r"^\d+[.)]\s+")
_INLINE = re.compile(r"\*\*(.+?)\*\*|`([^`\n]+)`")


def _inline(text: str) -> Spans:
    """``**bold**`` becomes bold and ```code``` code, everything else stays literal."""
    out: Spans = []
    pos = 0
    for m in _INLINE.finditer(text):
        if m.start() > pos:
            out.append((text[pos : m.start()], ""))
        out.append((m.group(1), "b") if m.group(1) is not None else (m.group(2), "c"))
        pos = m.end()
    if pos < len(text):
        out.append((text[pos:], ""))
    return out


def _cells(line: str) -> list[str]:
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|") and not line.endswith("\\|"):
        line = line[:-1]
    return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", line)]


def markdown_blocks(text: str) -> list[dict[str, Any]]:
    """Body section (Markdown) → blocks: paragraphs, ### headings, lists, quotes and pipe tables."""
    blocks: list[dict[str, Any]] = []
    paragraph: list[str] = []
    lines = _clean(text).split("\n")

    def flush() -> None:
        if paragraph:
            blocks.append(para(_inline(" ".join(paragraph))))
            paragraph.clear()

    i = 0
    while i < len(lines):
        line = lines[i]
        s = line.strip()
        if not s:
            flush()
        elif s.startswith("|"):
            flush()
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(_cells(lines[i]))
                i += 1
            rows = [r for r in rows if not all(_TABLE_SEP.match(c) for c in r if c)]
            if rows:
                blocks.extend(tables(rows[0], [[_inline(c) for c in r] for r in rows[1:]]))
            continue
        elif s.startswith("#"):
            flush()
            blocks.append(h3(s.lstrip("#").strip()))
        elif s[:2] in ("- ", "* ", "+ "):
            flush()
            blocks.append(bullet(_inline(s[2:].strip())))
        elif _NUMBERED.match(s):
            flush()
            blocks.append(numbered(_inline(_NUMBERED.sub("", s, count=1))))
        elif s.startswith(">"):
            flush()
            blocks.append(quote(_inline(s[1:].strip())))
        else:
            paragraph.append(s)
        i += 1
    flush()
    return blocks


# ------------------------------------------------------------ the page
def _labelled(label: str, value: str) -> Spans:
    return [(f"{label}: ", "b"), (value, "")]


def _items(values: list[Any] | None) -> list[str]:
    return [str(v) for v in values or [] if v]


def page_blocks(p: Persona, roles: list[tuple[Group, Member]]) -> list[dict[str, Any]]:
    """All blocks of a persona page, in reading order (the same sections as ``render -f md``)."""
    d = p.plain()
    o: list[dict[str, Any]] = []
    if d.get("tagline"):
        o.append(quote(f"«{d['tagline']}»"))
    for key, label in (("domain", "Bereich"), ("scope", "Gilt für"), ("owner", "Pflege")):
        if d.get(key):
            o.append(bullet(_labelled(label, str(d[key]))))

    if roles:
        o.append(h2("Rolle in Sets"))
        for g, m in roles:
            spans: Spans = [(g.title, "b"), (f" ({g.id}): {L(m.priority)}", "")]
            if m.overridden:
                spans.append((f" – abweichend vom Default «{L(m.default)}»", "i"))
            o.append(bullet(spans))

    facts = [f for f in d.get("profile") or [] if f.get("fact")]
    if facts:
        o.append(h2("Relevante Fakten"))
        for f in facts:
            spans = [(f["fact"], "b")]
            if f.get("relevance"):
                spans += [(" — ", ""), (f["relevance"], "i")]
            o.append(bullet(spans))

    ctx = d.get("context") or {}
    if any(ctx.values()):
        o.append(h2("Kontext"))
        for key, label in (("role", "Rolle"), ("situation", "Situation"), ("environment", "Umgebung")):
            if ctx.get(key):
                o.append(bullet(_labelled(label, ctx[key])))
        if _items(ctx.get("channels")):
            o.append(bullet(_labelled("Kanäle", ", ".join(_items(ctx["channels"])))))
        if _items(ctx.get("constraints")):
            o.append(bullet([("Restriktionen", "b")], [bullet(c) for c in _items(ctx["constraints"])]))

    beh = d.get("behaviour") or {}
    variables = [v for v in beh.get("variables") or [] if v.get("name")]
    if variables or _items(beh.get("patterns")):
        o.append(h2("Verhalten"))
        if variables:
            rows: list[list[Spans | str]] = [
                [
                    v["name"],
                    str(v.get("low") or ""),
                    f"{_bar(v.get('value', 3))} {v.get('value', '')}".rstrip(),
                    str(v.get("high") or ""),
                ]
                for v in variables
            ]
            o.extend(tables(["Variable", "1", "Ausprägung", "5"], rows))
        if _items(beh.get("patterns")):
            o.append(h3("Muster"))
            o.extend(bullet(x) for x in _items(beh["patterns"]))

    g = d.get("goals") or {}
    if any(_items(g.get(k)) for k in ("experience", "end", "life")):
        o.append(h2("Ziele"))
        for key, label in (
            ("experience", "Erlebnisziele (nie verletzen)"),
            ("end", "Endziele"),
            ("life", "Lebensziele"),
        ):
            if _items(g.get(key)):
                o.append(h3(label))
                o.extend(bullet(x) for x in _items(g[key]))

    if _items(d.get("pains")):
        o.append(h2("Schmerzpunkte"))
        o.extend(bullet(x) for x in _items(d["pains"]))

    jobs = [j for j in d.get("jobs") or [] if j.get("statement")]
    if jobs:
        o.append(h2("Jobs-to-be-Done"))
        for j in jobs:
            o.append(h3(f"{j['id']} — {j['statement']}"))
            meta = [", ".join(L(x) for x in j.get("dimension") or [])]
            if j.get("importance") or j.get("satisfaction"):
                meta.append(
                    f"Wichtigkeit {j.get('importance', '–')}/5 · Zufriedenheit heute {j.get('satisfaction', '–')}/5"
                )
            if any(meta):
                o.append(para([(" · ".join(m for m in meta if m), "i")]))
            forces = j.get("forces") or {}
            for key, label in (
                ("push", "Push (weg vom Heute)"),
                ("pull", "Pull (hin zum Neuen)"),
                ("anxiety", "Angst"),
                ("habit", "Gewohnheit"),
            ):
                if _items(forces.get(key)):
                    o.append(bullet(_labelled(label, "; ".join(_items(forces[key])))))
            if _items(j.get("outcomes")):
                o.append(bullet([("Gewünschte Ergebnisse", "b")], [bullet(x) for x in _items(j["outcomes"])]))

    if _items(d.get("anti_patterns")):
        o.append(h2("Tut nicht / will nicht"))
        o.extend(bullet(x) for x in _items(d["anti_patterns"]))

    quotes = [q for q in d.get("quotes") or [] if q.get("text")]
    if quotes:
        o.append(h2("Zitate"))
        for q in quotes:
            spans = [(f"«{q['text']}»", "")]
            if q.get("evidence"):
                spans.append((f" ({q['evidence']})", "i"))
            o.append(quote(spans))

    for heading, text in p.sections.items():
        if heading == "_intro":
            continue
        o.append(h2(heading))
        o.extend(markdown_blocks(text))

    sim = d.get("simulation") or {}
    if any(sim.get(k) for k in ("voice", "must", "must_not", "variance")):
        o.append(h2("Einsatz als Prompt-Voreinstellung"))
        if sim.get("voice"):
            o.append(bullet(_labelled("Stimme", sim["voice"])))
        for key, label in (("must", "Muss"), ("must_not", "Darf nicht")):
            if _items(sim.get(key)):
                o.append(bullet([(label, "b")], [bullet(x) for x in _items(sim[key])]))
        if sim.get("variance"):
            o.append(bullet(_labelled("Varianz", sim["variance"])))

    o.append(h2("Evidenz"))
    evidence = d.get("evidence") or []
    if evidence:
        rows_ev = []
        for e in evidence:
            parts = [LE(e.get("type")), str(e.get("source") or "")]
            if e.get("date"):
                parts.append(str(e["date"]))
            if e.get("n"):
                parts.append(f"n={e['n']}")
            if e.get("note"):
                parts.append(str(e["note"]))
            rows_ev.append(bullet([(f"{e.get('id')}: ", "b"), (" · ".join(x for x in parts if x), "")]))
        o.extend(toggles(f"Quellen ({len(evidence)})", rows_ev))
    else:
        o.append(para([("Keine Evidenz-Einträge.", "i")]))
    if _items(d.get("assumptions")):
        assumptions = _items(d["assumptions"])
        o.extend(toggles(f"Annahmen, nicht validiert ({len(assumptions)})", [bullet(x) for x in assumptions]))
    if _items(d.get("unknowns")):
        o.append(h3("Offen"))
        o.extend(bullet(x) for x in _items(d["unknowns"]))

    rel = d.get("relations") or {}
    if any(_items(rel.get(k)) for k in ("journeys", "personas", "links")):
        o.append(h2("Verknüpfungen"))
        if _items(rel.get("journeys")):
            o.append(bullet(_labelled("Journeys", ", ".join(_items(rel["journeys"])))))
        if _items(rel.get("personas")):
            o.append(bullet(_labelled("Personas", ", ".join(_items(rel["personas"])))))
        o.extend(bullet(x) for x in _items(rel.get("links")))

    changes = [c for c in d.get("changelog") or [] if c.get("version")]
    if changes:
        o.append(h2("Änderungen"))
        o.extend(bullet(f"v{c['version']} ({c.get('date', '')}): {c.get('note', '')}") for c in reversed(changes))

    source = p.path.name if p.path else f"{p.id}.persona.md"
    o.append(
        para(
            [
                (f"Erzeugt mit personakit {__version__} aus ", "i"),
                (source, "c"),  # as code: Notion would turn «….persona.md» into a link (.md is a domain)
                (
                    ". Änderungen in der Persona-Datei vornehmen – diese Seite wird beim nächsten Export überschrieben.",
                    "i",
                ),
            ]
        )
    )
    return o


# ----------------------------------------------------------- properties
def option(name: Any) -> str:
    """Select option name: Notion rejects commas, at most 100 characters."""
    return _clean(name).replace("\n", " ").replace(",", ";").strip()[:100]


def _options(values: list[Any] | None) -> list[str]:
    out: list[str] = []
    for v in values or []:
        o = option(v)
        if o and o not in out:
            out.append(o)
    return out


def _values(p: Persona, sets: list[str]) -> dict[str, Any]:
    """Property values, target-neutral: str, list[str] or None."""
    d = p.plain()
    return {
        "Name": p.display_name,
        "ID": p.id,
        "Archetyp": p.archetype,
        "Set": _options(sets),
        "Priorität": L(d["priority"]) if d.get("priority") else None,
        "Status": L(d["status"]) if d.get("status") else None,
        "Evidenz": L(d["evidence_level"]) if d.get("evidence_level") else None,
        "Version": str(d.get("version") or ""),
        "Review bis": str(d["review_by"]) if d.get("review_by") else None,
        "Tags": _options(d.get("tags")),
    }


def api_properties(values: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for name, kind in PROPERTIES.items():
        v = values[name]
        if kind in ("title", "rich_text"):
            out[name] = {kind: rich(v or "")}
        elif kind == "select":
            out[name] = {"select": {"name": option(v)} if v else None}
        elif kind == "multi_select":
            out[name] = {"multi_select": [{"name": x} for x in v]}
        elif kind == "date":
            out[name] = {"date": {"start": v} if v else None}
    return out


def mcp_properties(values: dict[str, Any]) -> dict[str, Any]:
    """Flat values as the Notion MCP tools expect them (text as Notion Markdown, dates split, ``id`` prefixed)."""
    out: dict[str, Any] = {}
    for name, kind in PROPERTIES.items():
        v = values[name]
        key = f"userDefined:{name}" if name.lower() in ("id", "url") else name
        if kind in ("title", "rich_text"):
            out[key] = md_text(v or "")
        elif kind == "select":
            out[key] = option(v) if v else None
        elif kind == "multi_select":
            out[key] = list(v)
        elif kind == "date":
            out[f"date:{name}:start"] = v
            out[f"date:{name}:is_datetime"] = 0
    return out


def _database_options(
    personas: list[Persona], roles: dict[str, list[tuple[Group, Member]]]
) -> dict[str, list[tuple[str, str]]]:
    sets = _options([g.id for rs in roles.values() for g, _ in rs])
    tags = _options([t for p in personas for t in p.plain().get("tags") or []])
    opts = {name: [(L(k), color) for k, color in colors.items()] for name, colors in _OPTIONS.items()}
    opts["Set"] = [(s, "default") for s in sets]
    opts["Tags"] = [(t, "default") for t in tags]
    return opts


def api_database(opts: dict[str, list[tuple[str, str]]]) -> dict[str, Any]:
    props: dict[str, Any] = {}
    for name, kind in PROPERTIES.items():
        if kind in ("select", "multi_select"):
            props[name] = {kind: {"options": [{"name": n, "color": c} for n, c in opts[name]]}}
        else:
            props[name] = {kind: {}}
    return {"title": rich(DATABASE_TITLE), "properties": props}


def _sql(s: str) -> str:
    return "'" + s.replace("'", "''") + "'"


def mcp_database(opts: dict[str, list[tuple[str, str]]]) -> dict[str, Any]:
    cols = []
    for name, kind in PROPERTIES.items():
        ddl = _DDL_TYPE[kind]
        if kind in ("select", "multi_select") and opts[name]:
            ddl += "(" + ", ".join(f"{_sql(n)}:{c}" for n, c in opts[name]) + ")"
        cols.append(f'"{name}" {ddl}')
    return {
        "title": DATABASE_TITLE,
        "schema": "CREATE TABLE (" + ", ".join(cols) + ")",
        # The MCP tools reject select values the data source does not know yet: add missing ones first
        "options": {name: [n for n, _ in opts[name]] for name, kind in PROPERTIES.items() if "select" in kind},
    }


# ------------------------------------------------- Notion-flavored Markdown
_MD_SPECIAL = set("\\*~`$[]<>{}|^")
_LINE_START = re.compile(r"^(#{1,6}(\s|$)|[-+](\s|$)|\d+[.)](\s|$)|-{3,}\s*$)")  # would start a block


def md_text(text: str, line_start: bool = True) -> str:
    """Escape for Notion-flavored Markdown; newlines become ``<br>`` so a block stays one block."""
    out = "".join("\\" + c if c in _MD_SPECIAL else c for c in _clean(text).replace("\t", " "))
    if line_start and _LINE_START.match(out):
        m = re.match(r"^(\d+)([.)])", out)
        out = f"{m.group(1)}\\{out[len(m.group(1)) :]}" if m else "\\" + out
    return out.replace("\n", "<br>")


def md_rich(rt: list[dict[str, Any]]) -> str:
    """Rich text → inline Markdown; markers stay outside surrounding spaces (``** x**`` would not render bold)."""
    runs: list[tuple[str, str]] = []  # merge pieces that were split at the length limit
    for r in rt:
        ann = r.get("annotations") or {}
        mark = "`" if ann.get("code") else "**" if ann.get("bold") else "*" if ann.get("italic") else ""
        if runs and runs[-1][0] == mark:
            runs[-1] = (mark, runs[-1][1] + r["text"]["content"])
        else:
            runs.append((mark, r["text"]["content"]))
    out: list[str] = []
    for i, (mark, text) in enumerate(runs):
        core = text.strip(" ")
        if mark == "`" and ("`" in text or "\n" in text):
            mark = ""  # cannot be a code span; plain escaped text instead
        if mark == "`" and core:
            out.append(f"`{text}`")  # code spans are literal, no escaping
            continue
        if not mark or not core:
            out.append(md_text(text, line_start=i == 0))
            continue
        lead, trail = text[: len(text) - len(text.lstrip(" "))], text[len(text.rstrip(" ")) :]
        out.append(f"{lead}{mark}{md_text(core, line_start=False)}{mark}{trail}")
    return "".join(out)


_MD_PREFIX = {
    "paragraph": "",
    "heading_2": "## ",
    "heading_3": "### ",
    "bulleted_list_item": "- ",
    "numbered_list_item": "1. ",
    "quote": "> ",
}


def to_markdown(blocks: list[dict[str, Any]], depth: int = 0) -> str:
    """API blocks → Notion-flavored Markdown (tab-indented children, toggles as ``<details>``, tables as ``<table>``)."""
    ind = "\t" * depth
    lines: list[str] = []
    for b in blocks:
        kind = b["type"]
        body = b[kind]
        if kind == "table":
            lines.append(f'{ind}<table header-row="{str(body["has_column_header"]).lower()}">')
            for row in body["children"]:
                lines.append(f"{ind}\t<tr>")
                lines.extend(f"{ind}\t\t<td>{md_rich(cell)}</td>" for cell in row["table_row"]["cells"])
                lines.append(f"{ind}\t</tr>")
            lines.append(f"{ind}</table>")
            continue
        if kind == "toggle":
            lines.append(f"{ind}<details>")
            lines.append(f"{ind}<summary>{md_rich(body['rich_text'])}</summary>")
            if body.get("children"):
                lines.append(to_markdown(body["children"], depth + 1))
            lines.append(f"{ind}</details>")
            continue
        lines.append(f"{ind}{_MD_PREFIX[kind]}{md_rich(body['rich_text'])}")
        if body.get("children"):
            lines.append(to_markdown(body["children"], depth + 1))
    return "\n".join(lines)


# ---------------------------------------------------------------- export
def _roles(groups: list[Group]) -> dict[str, list[tuple[Group, Member]]]:
    out: dict[str, list[tuple[Group, Member]]] = {}
    for g in groups:
        if g.is_loose:
            continue
        for m in g.members:
            out.setdefault(m.persona.id, []).append((g, m))
    return out


def api_page(p: Persona, roles: list[tuple[Group, Member]]) -> dict[str, Any]:
    blocks = page_blocks(p, roles)
    page: dict[str, Any] = {
        "properties": api_properties(_values(p, [g.id for g, _ in roles])),
        "children": blocks[:MAX_CHILDREN],
    }
    rest = blocks[MAX_CHILDREN:]
    if rest:
        page["append"] = [rest[i : i + MAX_CHILDREN] for i in range(0, len(rest), MAX_CHILDREN)]
    return page


def mcp_page(p: Persona, roles: list[tuple[Group, Member]]) -> dict[str, Any]:
    return {
        "properties": mcp_properties(_values(p, [g.id for g, _ in roles])),
        "content": to_markdown(page_blocks(p, roles)) + "\n",
    }


def render_notion(groups: list[Group], target: str = "api") -> str:
    if target not in TARGETS:
        raise ValueError(f"Unbekanntes Notion-Ziel: {target} (erlaubt: {', '.join(TARGETS)})")
    personas = group_personas(groups)
    roles = _roles(groups)
    opts = _database_options(personas, roles)
    if target == "api":
        database, pages = api_database(opts), [api_page(p, roles.get(p.id, [])) for p in personas]
    else:
        database, pages = mcp_database(opts), [mcp_page(p, roles.get(p.id, [])) for p in personas]
    doc = {"generator": f"personakit {__version__}", "target": target, "database": database, "pages": pages}
    return json.dumps(doc, ensure_ascii=False, indent=2) + "\n"
