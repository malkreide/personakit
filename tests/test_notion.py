"""render -f notion: properties for the database «Personas», blocks for the API, Notion Markdown for MCP."""

import json
import socket
from pathlib import Path

import pytest

from personakit.cli import main
from personakit.model import Persona
from personakit.notion import (
    MAX_CHILDREN,
    MAX_TEXT,
    PROPERTIES,
    md_text,
    render_notion,
    tables,
    to_markdown,
    toggles,
)
from personakit.render import render_set
from personakit.sets import build_groups, load_workspace

ROOT = Path(__file__).resolve().parents[1]
PERSONAS = ROOT / "personas"
EXAMPLE = PERSONAS / "elternkommunikation-schuleintritt" / "eltern-neu-in-zuerich.persona.md"
TRICKY = 'Stern *fett* [Link](x) <b>Tag</b> a|b \\ $5 ~x~ `c` {y} ^z «»"Zitat"'


def _api(personas=None, groups=None):
    if groups is None:
        personas, groups = load_workspace([PERSONAS])
    return json.loads(render_set(personas, "notion", groups=groups))


def _mcp(groups):
    return json.loads(render_notion(groups, target="mcp"))


def _single(p: Persona):
    return build_groups([p], [])


def _walk(blocks, depth=0):
    for b in blocks:
        yield b, depth
        yield from _walk(b[b["type"]].get("children") or [], depth + 1)


def _texts(blocks):
    for b, _ in _walk(blocks):
        body = b[b["type"]]
        if b["type"] == "table_row":
            for cell in body["cells"]:
                yield "".join(r["text"]["content"] for r in cell)
        elif "rich_text" in body:
            yield "".join(r["text"]["content"] for r in body["rich_text"])


def _text(block):
    return "".join(r["text"]["content"] for r in block[block["type"]].get("rich_text", []))


def _all_blocks(page):
    return page["children"] + [b for batch in page.get("append", []) for b in batch]


def _by_id(doc):
    return {p["properties"]["ID"]["rich_text"][0]["text"]["content"]: p for p in doc["pages"]}


@pytest.fixture
def persona() -> Persona:
    return Persona.load(EXAMPLE)


# -------------------------------------------------------------- database
def test_database_schema_matches_page_properties():
    doc = _api()
    assert doc["target"] == "api" and doc["generator"].startswith("personakit ")
    db = doc["database"]
    assert db["title"][0]["text"]["content"] == "Personas"
    assert {k: next(iter(v)) for k, v in db["properties"].items()} == PROPERTIES
    for page in doc["pages"]:
        assert set(page) <= {"properties", "children", "append"}
        assert {k: next(iter(v)) for k, v in page["properties"].items()} == PROPERTIES
        for name, kind in PROPERTIES.items():
            value = page["properties"][name][kind]
            if kind == "select" and value:
                options = [o["name"] for o in db["properties"][name][kind]["options"]]
                assert value["name"] in options, (name, value)
            if kind == "multi_select":
                options = [o["name"] for o in db["properties"][name][kind]["options"]]
                assert all(v["name"] in options for v in value), (name, value)


def test_one_page_per_persona_id_with_all_sets():
    pages = _by_id(_api())
    assert sorted(pages) == [
        "eltern-neu-in-zuerich",
        "lehrperson-ki-explorierend",
        "schulleitung-entscheidungsorientiert",
        "verwaltungs-insider",
    ]
    shared = pages["schulleitung-entscheidungsorientiert"]["properties"]
    assert [s["name"] for s in shared["Set"]["multi_select"]] == [
        "elternkommunikation-schuleintritt",
        "ki-leitplanken-lehrpersonen",
    ]


def test_priority_property_is_the_default_and_set_roles_are_in_the_page():
    page = _by_id(_api())["lehrperson-ki-explorierend"]
    assert page["properties"]["Priorität"] == {"select": {"name": "Ergänzend"}}
    texts = list(_texts(page["children"]))
    i = texts.index("Rolle in Sets")
    assert "Primär" in texts[i + 1] and "abweichend vom Default «Ergänzend»" in texts[i + 1]


def test_property_values(persona):
    props = _api([persona], _single(persona))["pages"][0]["properties"]
    assert props["Name"]["title"][0]["text"]["content"] == persona.display_name
    assert props["Archetyp"]["rich_text"][0]["text"]["content"] == persona.archetype
    assert props["Version"]["rich_text"][0]["text"]["content"] == "1.1.0"
    assert props["Status"] == {"select": {"name": "Aktiv"}}
    assert props["Evidenz"] == {"select": {"name": "Qualitativ"}}
    assert props["Review bis"] == {"date": {"start": "2027-04-06"}}
    assert props["Set"] == {"multi_select": []}  # loose persona: no set
    assert [t["name"] for t in props["Tags"]["multi_select"]] == [
        "eltern",
        "schuleintritt",
        "kindergarten",
        "mehrsprachig",
    ]


def test_missing_review_date_is_null(persona):
    del persona.data["review_by"]
    page = _api([persona], _single(persona))["pages"][0]
    assert page["properties"]["Review bis"] == {"date": None}
    props = _mcp(_single(persona))["pages"][0]["properties"]
    assert props["date:Review bis:start"] is None


# ---------------------------------------------------------------- blocks
def test_block_structure_respects_api_limits():
    for page in _api()["pages"]:
        assert 0 < len(page["children"]) <= MAX_CHILDREN
        for b, depth in _walk(_all_blocks(page)):
            assert b["object"] == "block" and b["type"] in b
            assert depth <= 2, b["type"]  # Notion accepts two levels of nesting per request
            body = b[b["type"]]
            assert len(body.get("children") or []) <= MAX_CHILDREN
            rich = body.get("rich_text") or [r for cell in body.get("cells", []) for r in cell]
            assert all(len(r["text"]["content"]) <= MAX_TEXT for r in rich)


def test_page_sections(persona):
    page = _api([persona], _single(persona))["pages"][0]
    blocks = page["children"]
    kinds = [b["type"] for b in blocks]
    headings = [_text(b) for b in blocks if b["type"] == "heading_2"]
    assert headings[:2] == ["Relevante Fakten", "Kontext"]
    for h in ("Verhalten", "Ziele", "Schmerzpunkte", "Jobs-to-be-Done", "Zitate", "Szenario", "Evidenz", "Änderungen"):
        assert h in headings
    assert "Rolle in Sets" not in headings  # loose persona
    assert kinds[0] == "quote"  # tagline
    assert sum(1 for k in kinds if k == "quote") == 3  # tagline + two quotes
    assert any(k == "bulleted_list_item" for k in kinds)


def test_behaviour_variables_as_table(persona):
    blocks = _api([persona], _single(persona))["pages"][0]["children"]
    table = next(b for b in blocks if b["type"] == "table")["table"]
    assert table["table_width"] == 4 and table["has_column_header"] is True
    rows = [[r[0]["text"]["content"] if r else "" for r in row["table_row"]["cells"]] for row in table["children"]]
    assert rows[0] == ["Variable", "1", "Ausprägung", "5"]
    assert rows[1] == [
        "Vertrautheit mit dem Schulsystem",
        "kennt weder Stufen noch Zuständigkeiten",
        "●○○○○ 1",
        "kennt Abläufe und Ansprechpersonen",
    ]
    assert len(rows) == 1 + len(persona.data["behaviour"]["variables"])


def test_evidence_and_assumptions_in_toggles(persona):
    blocks = _api([persona], _single(persona))["pages"][0]["children"]
    toggled = {_text(b): b["toggle"]["children"] for b in blocks if b["type"] == "toggle"}
    assert set(toggled) == {"Quellen (3)", "Annahmen, nicht validiert (2)"}
    first = toggled["Quellen (3)"][0]["bulleted_list_item"]["rich_text"]
    assert first[0]["text"]["content"] == "E1: " and first[0]["annotations"]["bold"] is True
    assert "n=8" in first[1]["text"]["content"]
    assert all(c["type"] == "bulleted_list_item" for c in toggled["Annahmen, nicht validiert (2)"])


def test_body_markdown_table_and_list_become_blocks(persona):
    persona.sections["Herleitung"] = (
        "| Variable | Wert |\n|---|:---:|\n| Digitale Routine | 3 |\n| Pipe a\\|b | 2 |\n\n- Archetyp ← I02, I05\n1. erstens\n\n**Fett** und `code` normal"
    )
    blocks = _api([persona], _single(persona))["pages"][0]["children"]
    start = next(n for n, b in enumerate(blocks) if b["type"] == "heading_2" and _text(b) == "Herleitung")
    section = blocks[start + 1 : start + 5]
    assert [b["type"] for b in section] == ["table", "bulleted_list_item", "numbered_list_item", "paragraph"]
    rows = section[0]["table"]["children"]
    assert len(rows) == 3  # header + 2, separator row dropped
    assert rows[2]["table_row"]["cells"][0][0]["text"]["content"] == "Pipe a|b"
    para = section[3]["paragraph"]["rich_text"]
    assert para[0]["text"]["content"] == "Fett" and para[0]["annotations"]["bold"] is True
    assert para[2]["text"]["content"] == "code" and para[2]["annotations"]["code"] is True


# -------------------------------------------------------------- escaping
def test_api_keeps_special_characters_verbatim(persona):
    persona.data["tagline"] = TRICKY + "\nzweite Zeile\x07"
    persona.data["pains"] = ["# kein Titel", "1. keine Liste", TRICKY]
    doc = json.loads(render_notion(_single(persona)))
    texts = list(_texts(_all_blocks(doc["pages"][0])))
    assert f"«{TRICKY}\nzweite Zeile»" in texts  # control character dropped, newline kept
    assert "# kein Titel" in texts and "1. keine Liste" in texts and TRICKY in texts


def test_mcp_escapes_notion_markdown(persona):
    persona.data["tagline"] = TRICKY + "\nzweite Zeile"
    persona.data["pains"] = ["# kein Titel", "1. keine Liste", "- kein Punkt", "---"]
    persona.data["behaviour"]["variables"][0]["low"] = "a|b <td>"
    content = _mcp(_single(persona))["pages"][0]["content"]
    escaped = 'Stern \\*fett\\* \\[Link\\](x) \\<b\\>Tag\\</b\\> a\\|b \\\\ \\$5 \\~x\\~ \\`c\\` \\{y\\} \\^z «»"Zitat"'
    assert f"> «{escaped}<br>zweite Zeile»" in content
    assert "- \\# kein Titel" in content
    assert "- 1\\. keine Liste" in content
    assert "- \\- kein Punkt" in content
    assert "- \\---" in content
    assert "<td>a\\|b \\<td\\></td>" in content


def test_md_text_rules():
    assert md_text("1.1.0") == "1.1.0"  # a version is not a list item
    assert md_text("#hashtag") == "#hashtag"
    assert md_text("## x") == "\\## x"
    assert md_text("2) zwei") == "2\\) zwei"
    assert md_text("a\tb\nc") == "a b<br>c"
    assert md_text("# x", line_start=False) == "# x"


def test_mcp_bold_and_italic_markers_hug_the_text():
    blocks = [
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {"type": "text", "text": {"content": "Label: "}, "annotations": {"bold": True, "italic": False}},
                    {"type": "text", "text": {"content": "Wert *x*"}},
                    {"type": "text", "text": {"content": " (E1)"}, "annotations": {"bold": False, "italic": True}},
                ]
            },
        }
    ]
    assert to_markdown(blocks) == "**Label:** Wert \\*x\\* *(E1)*"


def test_mcp_properties(persona):
    persona.data["name"] = "Ana *A*"
    persona.data["tags"] = ["a,b", "a;b", "  ", "x" * 150]
    doc = _mcp(_single(persona))
    assert doc["target"] == "mcp"
    props = doc["pages"][0]["properties"]
    assert props["userDefined:ID"] == "eltern-neu-in-zuerich" and "ID" not in props
    assert props["Name"].startswith("Ana \\*A\\* – ")
    assert props["Version"] == "1.1.0"
    assert props["Priorität"] == "Primär" and props["Set"] == []
    assert props["date:Review bis:start"] == "2027-04-06" and props["date:Review bis:is_datetime"] == 0
    assert props["Tags"] == ["a;b", "x" * 100]  # commas are not allowed in Notion options; deduplicated, trimmed
    schema = doc["database"]["schema"]
    assert schema.startswith('CREATE TABLE ("Name" TITLE, "ID" RICH_TEXT, "Archetyp" RICH_TEXT, "Set" MULTI_SELECT')
    assert "\"Priorität\" SELECT('Primär':blue, " in schema and '"Review bis" DATE' in schema


def test_mcp_database_lists_options_for_every_select(persona):
    # The MCP tools reject values the data source does not know (checked against Notion): the skill adds them first
    persona.data["tags"] = ["b", "a"]
    options = _mcp(_single(persona))["database"]["options"]
    assert options == {
        "Set": [],
        "Priorität": ["Primär", "Sekundär", "Ergänzend", "Negativ (nicht bauen für)"],
        "Status": ["Entwurf", "Aktiv", "Ruhestand"],
        "Evidenz": ["Proto (Annahmen)", "Qualitativ", "Statistisch"],
        "Tags": ["b", "a"],
    }


def test_source_file_is_code_so_notion_does_not_link_it(persona):
    # Notion turns «x.persona.md» into a link (.md is a top-level domain); a code span stays text
    api = _api([persona], _single(persona))["pages"][0]["children"][-1]["paragraph"]["rich_text"]
    assert [(r["text"]["content"], r["annotations"]["code"]) for r in api][1] == (
        "eltern-neu-in-zuerich.persona.md",
        True,
    )
    content = _mcp(_single(persona))["pages"][0]["content"]
    assert "*Erzeugt mit personakit " in content and " aus* `eltern-neu-in-zuerich.persona.md`*. Änderungen" in content


def test_code_span_with_backtick_falls_back_to_escaped_text():
    rich = [{"type": "text", "text": {"content": "a`b"}, "annotations": {"code": True}}]
    assert to_markdown([{"object": "block", "type": "paragraph", "paragraph": {"rich_text": rich}}]) == "a\\`b"


def test_ddl_quotes_single_quotes(persona):
    persona.data["tags"] = ["Eltern's"]
    assert "'Eltern''s':default" in _mcp(_single(persona))["database"]["schema"]


def test_api_tag_options_without_commas(persona):
    persona.data["tags"] = ["Schule, Kindergarten"]
    doc = _api([persona], _single(persona))
    assert doc["pages"][0]["properties"]["Tags"] == {"multi_select": [{"name": "Schule; Kindergarten"}]}
    assert doc["database"]["properties"]["Tags"]["multi_select"]["options"] == [
        {"name": "Schule; Kindergarten", "color": "default"}
    ]


# ---------------------------------------------------------------- limits
def test_long_text_is_split_at_2000_utf16_units(persona):
    text = "a" * 1999 + "😀" + "b" * 2500  # the emoji counts two units and must not be cut
    persona.data["scope"] = text
    page = _api([persona], _single(persona))["pages"][0]
    rich = next(
        b["bulleted_list_item"]["rich_text"]
        for b in page["children"]
        if b["type"] == "bulleted_list_item"
        and b["bulleted_list_item"]["rich_text"][0]["text"]["content"] == "Gilt für: "
    )
    pieces = [r["text"]["content"] for r in rich[1:]]
    assert "".join(pieces) == text
    assert pieces[0] == "a" * 1999
    assert all(len(p.encode("utf-16-le")) // 2 <= MAX_TEXT for p in pieces)
    content = _mcp(_single(persona))["pages"][0]["content"]
    assert f"- **Gilt für:** {text}\n" in content  # one run in Markdown again


def test_more_than_100_blocks_go_to_append_batches(persona):
    persona.data["pains"] = [f"Schmerz {i}" for i in range(250)]
    page = _api([persona], _single(persona))["pages"][0]
    assert len(page["children"]) == MAX_CHILDREN
    assert page["append"] and all(0 < len(batch) <= MAX_CHILDREN for batch in page["append"])
    texts = list(_texts(_all_blocks(page)))
    assert [t for t in texts if t.startswith("Schmerz ")] == [f"Schmerz {i}" for i in range(250)]
    assert texts[-1].startswith("Erzeugt mit personakit")
    small = _api()["pages"][0]
    assert "append" not in small


def test_toggle_and_table_split_beyond_100_children():
    items = [{"object": "block", "type": "paragraph", "paragraph": {"rich_text": []}}] * 150
    parts = toggles("Quellen", items)
    assert [p["toggle"]["rich_text"][0]["text"]["content"] for p in parts] == ["Quellen (1/2)", "Quellen (2/2)"]
    assert [len(p["toggle"]["children"]) for p in parts] == [100, 50]
    split = tables(["A", "B"], [[str(i), "x"] for i in range(150)])
    assert [len(t["table"]["children"]) for t in split] == [100, 52]
    assert all(t["table"]["children"][0]["table_row"]["cells"][0][0]["text"]["content"] == "A" for t in split)


# ------------------------------------------------------------------- cli
def test_cli_writes_both_targets_without_network(tmp_path: Path, monkeypatch):
    def no_network(*args, **kwargs):
        raise AssertionError("Netzwerkaufruf im Renderer")

    monkeypatch.setattr(socket, "socket", no_network)
    monkeypatch.setattr(socket, "create_connection", no_network)
    api, mcp = tmp_path / "notion.json", tmp_path / "notion-mcp.json"
    assert main(["render", str(PERSONAS), "-f", "notion", "-o", str(api)]) == 0
    assert main(["render", str(PERSONAS), "-f", "notion", "--target", "mcp", "-o", str(mcp)]) == 0
    a, m = json.loads(api.read_text(encoding="utf-8")), json.loads(mcp.read_text(encoding="utf-8"))
    assert a["target"] == "api" and m["target"] == "mcp"
    assert len(a["pages"]) == len(m["pages"]) == 4
    for page_a, page_m in zip(a["pages"], m["pages"]):
        assert page_a["properties"]["ID"]["rich_text"][0]["text"]["content"] == page_m["properties"]["userDefined:ID"]
        assert set(page_m) == {"properties", "content"}


def test_cli_single_set_folder(capsys):
    assert main(["render", str(PERSONAS / "ki-leitplanken-lehrpersonen"), "-f", "notion"]) == 0
    doc = json.loads(capsys.readouterr().out)
    assert sorted(_by_id(doc)) == [
        "lehrperson-ki-explorierend",
        "schulleitung-entscheidungsorientiert",
        "verwaltungs-insider",
    ]
    assert [o["name"] for o in doc["database"]["properties"]["Set"]["multi_select"]["options"]] == [
        "ki-leitplanken-lehrpersonen"
    ]


def test_unknown_target_is_rejected():
    with pytest.raises(ValueError, match="Notion-Ziel"):
        render_notion([], target="csv")
