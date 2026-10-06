"""Renderers: one persona → md | card | json | yaml | prompt; a set → matrix | html | bundle."""

from __future__ import annotations

import html as _html
import io
import json
from collections.abc import Iterable
from typing import Any

from ruamel.yaml import YAML

from . import __version__
from .model import Persona

SINGLE_FORMATS = ("md", "card", "json", "yaml", "prompt")
SET_FORMATS = ("matrix", "html", "bundle")

_LABEL = {
    "primary": "Primär",
    "secondary": "Sekundär",
    "supplemental": "Ergänzend",
    "negative": "Negativ (nicht bauen für)",
    "draft": "Entwurf",
    "active": "Aktiv",
    "retired": "Ruhestand",
    "proto": "Proto (Annahmen)",
    "qualitative": "Qualitativ",
    "statistical": "Statistisch",
    "user": "Anwender·in",
    "buyer": "Entscheider·in",
    "stakeholder": "Stakeholder",
    "partner": "Partner",
    "operator": "Betreiber·in",
    "functional": "funktional",
    "emotional": "emotional",
    "social": "sozial",
}
_EVIDENCE_LABEL = {
    "interview": "Interview",
    "observation": "Beobachtung",
    "survey": "Umfrage",
    "analytics": "Analytics",
    "support-log": "Support-Log",
    "workshop": "Workshop",
    "secondary": "Sekundärquelle",
    "assumption": "Annahme",
}


def L(key: Any) -> str:
    return _LABEL.get(str(key), str(key))


def LE(key: Any) -> str:
    return _EVIDENCE_LABEL.get(str(key), str(key))


def _bar(value: int, width: int = 5) -> str:
    v = max(1, min(width, int(value or 0)))
    return "●" * v + "○" * (width - v)


def _bullets(items: Iterable[Any] | None, prefix: str = "- ") -> str:
    items = [str(i) for i in (items or []) if i]
    return "\n".join(f"{prefix}{i}" for i in items) if items else "_–_"


def _nonempty(x: Any) -> bool:
    return bool(x) and (not isinstance(x, (list, dict)) or len(x) > 0)


# ================================================================== single
def render(persona: Persona, fmt: str, **opts: Any) -> str:
    if fmt == "md":
        return render_md(persona)
    if fmt == "card":
        return render_card(persona)
    if fmt == "json":
        return json.dumps(_export_dict(persona), ensure_ascii=False, indent=2) + "\n"
    if fmt == "yaml":
        y = YAML(typ="safe")
        y.default_flow_style = False
        y.allow_unicode = True
        y.width = 4096
        y.sort_base_mapping_type_on_output = False  # keep schema order, not alphabetical
        buf = io.StringIO()
        y.dump(_export_dict(persona), buf)
        return buf.getvalue()
    if fmt == "prompt":
        return render_prompt(persona, mode=opts.get("mode", "simulate"))
    raise ValueError(f"Unbekanntes Format: {fmt}")


def _export_dict(p: Persona) -> dict[str, Any]:
    d = p.plain()
    d["_body"] = {k: v for k, v in p.sections.items()}
    d["_meta"] = {"generator": f"personakit {__version__}", "source": p.path.name if p.path else None}
    return d


# ----------------------------------------------------------------- md
def render_md(p: Persona) -> str:
    d = p.plain()
    o: list[str] = []
    o.append(f"# {p.display_name}")
    if d.get("tagline"):
        o.append(f"> «{d['tagline']}»")
    o.append("")
    o.append("| | |\n|---|---|")
    o.append(f"| ID | `{p.id}` v{d.get('version')} |")
    o.append(f"| Priorität | {L(d.get('priority'))} · {L(d.get('kind'))} |")
    o.append(f"| Status | {L(d.get('status'))} · Evidenz: {L(d.get('evidence_level'))} |")
    if d.get("domain"):
        o.append(f"| Bereich | {d['domain']} |")
    if d.get("scope"):
        o.append(f"| Gilt für | {d['scope']} |")
    if d.get("owner") or d.get("review_by"):
        o.append(f"| Pflege | {d.get('owner') or '–'} · Review bis {d.get('review_by') or '–'} |")
    o.append("")

    if _nonempty(d.get("profile")):
        o.append("## Relevante Fakten\n")
        for f in d["profile"]:
            if f.get("fact"):
                rel = f" — _{f['relevance']}_" if f.get("relevance") else ""
                o.append(f"- **{f['fact']}**{rel}")
        o.append("")

    ctx = d.get("context") or {}
    if any(ctx.values()):
        o.append("## Kontext\n")
        for key, label in (("role", "Rolle"), ("situation", "Situation"), ("environment", "Umgebung")):
            if ctx.get(key):
                o.append(f"- **{label}:** {ctx[key]}")
        if _nonempty(ctx.get("channels")):
            o.append(f"- **Kanäle:** {', '.join(ctx['channels'])}")
        if _nonempty(ctx.get("constraints")):
            o.append("- **Restriktionen:**")
            o.extend(f"  - {c}" for c in ctx["constraints"])
        o.append("")

    beh = d.get("behaviour") or {}
    if _nonempty(beh.get("variables")):
        o.append("## Verhalten\n")
        o.append("| Variable | 1 | Ausprägung | 5 |\n|---|---|:---:|---|")
        for v in beh["variables"]:
            if v.get("name"):
                o.append(
                    f"| {v['name']} | {v.get('low', '')} | `{_bar(v.get('value', 3))}` {v.get('value', '')} | {v.get('high', '')} |"
                )
        o.append("")
    if _nonempty(beh.get("patterns")):
        o.append("**Muster**\n")
        o.append(_bullets(beh["patterns"]))
        o.append("")

    g = d.get("goals") or {}
    o.append("## Ziele\n")
    if _nonempty(g.get("experience")):
        o.append("**Erlebnisziele (nie verletzen)**\n" + _bullets(g["experience"]) + "\n")
    o.append("**Endziele**\n" + _bullets(g.get("end")) + "\n")
    if _nonempty(g.get("life")):
        o.append("**Lebensziele**\n" + _bullets(g["life"]) + "\n")

    o.append("## Schmerzpunkte\n" + _bullets(d.get("pains")) + "\n")

    if _nonempty(d.get("jobs")):
        o.append("## Jobs-to-be-Done\n")
        for j in d["jobs"]:
            if not j.get("statement"):
                continue
            dims = ", ".join(L(x) for x in j.get("dimension") or [])
            score = ""
            if j.get("importance") or j.get("satisfaction"):
                score = (
                    f" · Wichtigkeit {j.get('importance', '–')}/5 · Zufriedenheit heute {j.get('satisfaction', '–')}/5"
                )
            o.append(f"### {j['id']} — {j['statement']}")
            if dims or score:
                o.append(f"_{dims}{score}_")
            forces = j.get("forces") or {}
            if any(_nonempty(forces.get(k)) for k in ("push", "pull", "anxiety", "habit")):
                o.append("")
                o.append("| Push (weg vom Heute) | Pull (hin zum Neuen) | Angst | Gewohnheit |\n|---|---|---|---|")
                cells = [" / ".join(forces.get(k) or []) or "–" for k in ("push", "pull", "anxiety", "habit")]
                o.append("| " + " | ".join(cells) + " |")
            if _nonempty(j.get("outcomes")):
                o.append("\n**Gewünschte Ergebnisse**\n" + _bullets(j["outcomes"]))
            o.append("")

    if _nonempty(d.get("anti_patterns")):
        o.append("## Tut nicht / will nicht\n" + _bullets(d["anti_patterns"]) + "\n")

    if _nonempty(d.get("quotes")):
        o.append("## Zitate\n")
        for q in d["quotes"]:
            ref = f" ({q['evidence']})" if q.get("evidence") else ""
            o.append(f"> «{q['text']}»{ref}")
        o.append("")

    for heading, text in p.sections.items():
        if heading == "_intro":
            continue
        o.append(f"## {heading}\n\n{text}\n")

    sim = d.get("simulation") or {}
    if any(_nonempty(v) for v in sim.values()):
        o.append("## Einsatz als Prompt-Voreinstellung\n")
        if sim.get("voice"):
            o.append(f"- **Stimme:** {sim['voice']}")
        if _nonempty(sim.get("must")):
            o.append("- **Muss:**")
            o.extend(f"  - {m}" for m in sim["must"])
        if _nonempty(sim.get("must_not")):
            o.append("- **Darf nicht:**")
            o.extend(f"  - {m}" for m in sim["must_not"])
        if sim.get("variance"):
            o.append(f"- **Varianz:** {sim['variance']}")
        o.append("")

    o.append("## Evidenz\n")
    if _nonempty(d.get("evidence")):
        o.append("| ID | Typ | Quelle | Datum | n | Notiz |\n|---|---|---|---|---|---|")
        for e in d["evidence"]:
            o.append(
                f"| {e['id']} | {LE(e['type'])} | {e['source']} | {e.get('date', '')} | {e.get('n', '')} | {e.get('note', '')} |"
            )
        o.append("")
    if _nonempty(d.get("assumptions")):
        o.append("**Annahmen (nicht validiert)**\n" + _bullets(d["assumptions"]) + "\n")
    if _nonempty(d.get("unknowns")):
        o.append("**Offen**\n" + _bullets(d["unknowns"]) + "\n")

    rel = d.get("relations") or {}
    if any(_nonempty(v) for v in rel.values()):
        o.append("## Verknüpfungen\n")
        if _nonempty(rel.get("journeys")):
            o.append(f"- Journeys: {', '.join(f'`{j}`' for j in rel['journeys'])}")
        if _nonempty(rel.get("personas")):
            o.append(f"- Personas: {', '.join(f'`{j}`' for j in rel['personas'])}")
        if _nonempty(rel.get("links")):
            o.extend(f"- {x}" for x in rel["links"])
        o.append("")

    if _nonempty(d.get("changelog")):
        o.append("## Änderungen\n")
        for c in reversed(d["changelog"]):
            o.append(f"- v{c['version']} ({c['date']}): {c['note']}")
        o.append("")
    return "\n".join(o).rstrip() + "\n"


# ----------------------------------------------------------------- card
def render_card(p: Persona) -> str:
    d = p.plain()
    g = d.get("goals") or {}
    beh = (d.get("behaviour") or {}).get("variables") or []
    jobs = [j for j in d.get("jobs") or [] if j.get("statement")]
    o = [f"**{p.display_name}** · {L(d.get('priority'))} · {L(d.get('evidence_level'))} · v{d.get('version')}"]
    if d.get("tagline"):
        o.append(f"«{d['tagline']}»")
    o.append("")
    if beh:
        o.append("  ".join(f"{v['name']} `{_bar(v.get('value', 3))}`" for v in beh if v.get("name")))
        o.append("")
    o.append("**Will:** " + "; ".join(g.get("end") or []) or "–")
    o.append("**Stört:** " + "; ".join(d.get("pains") or []) or "–")
    if jobs:
        o.append("**Job:** " + jobs[0]["statement"] + (f" (+{len(jobs) - 1})" if len(jobs) > 1 else ""))
    if _nonempty(d.get("anti_patterns")):
        o.append("**Nicht:** " + "; ".join(d["anti_patterns"]))
    if d.get("scope"):
        o.append(f"_{d['scope']}_")
    return "\n".join(o).rstrip() + "\n"


# --------------------------------------------------------------- prompt
def render_prompt(p: Persona, mode: str = "simulate") -> str:
    """Prompt block for LLM use.

    mode=simulate → the model acts as this persona (synthetic user, interview partner).
    mode=audience → the model produces something for this persona (content, UI copy, concept).
    Both modes carry the guardrails against the synthetic-persona fallacy.
    """
    d = p.plain()
    g = d.get("goals") or {}
    ctx = d.get("context") or {}
    beh = d.get("behaviour") or {}
    sim = d.get("simulation") or {}
    level = d.get("evidence_level")
    o: list[str] = []

    head = f"PERSONA {p.id} v{d.get('version')} · Evidenz: {L(level)} · Priorität: {L(d.get('priority'))}"
    o.append(f'<persona id="{p.id}" version="{d.get("version")}" evidence="{level}" mode="{mode}">')
    o.append(head)
    if mode == "simulate":
        o.append(
            f"Du bist eine einzelne, konkrete Person des Typs «{p.archetype}»"
            + (f" – nenne dich {d['name']}." if d.get("name") else ".")
        )
        o.append(
            "Du bist kein Durchschnitt und kein Sprecher deiner Gruppe. Du antwortest aus deiner Situation heraus, mit deinen Lücken und Widersprüchen."
        )
    else:
        o.append(
            f"Zielpublikum: eine Person des Typs «{p.archetype}». Alles, was du erzeugst, muss für diese Person in ihrer Situation funktionieren – nicht für «alle»."
        )
    if d.get("tagline"):
        o.append(f"In ihren Worten: «{d['tagline']}»")
    if d.get("scope"):
        o.append(f"Gültigkeitsbereich: {d['scope']}")
    o.append("")

    if _nonempty(d.get("profile")):
        o.append("## Relevante Fakten")
        o.extend(
            f"- {f['fact']}" + (f" (relevant, weil: {f['relevance']})" if f.get("relevance") else "")
            for f in d["profile"]
            if f.get("fact")
        )
        o.append("")
    if any(ctx.values()):
        o.append("## Situation")
        for key, label in (("role", "Rolle"), ("situation", "Situation"), ("environment", "Umgebung")):
            if ctx.get(key):
                o.append(f"- {label}: {ctx[key]}")
        if _nonempty(ctx.get("channels")):
            o.append(f"- Kanäle: {', '.join(ctx['channels'])}")
        for c in ctx.get("constraints") or []:
            o.append(f"- Restriktion: {c}")
        o.append("")
    if _nonempty(beh.get("variables")) or _nonempty(beh.get("patterns")):
        o.append("## Verhalten")
        for v in beh.get("variables") or []:
            if v.get("name"):
                anchor = f" ({v.get('low')} ↔ {v.get('high')})" if v.get("low") and v.get("high") else ""
                o.append(f"- {v['name']}: {v.get('value')}/5{anchor}")
        o.extend(f"- {x}" for x in beh.get("patterns") or [])
        o.append("")
    o.append("## Ziele")
    o.extend(f"- Erlebnis (nie verletzen): {x}" for x in g.get("experience") or [])
    o.extend(f"- Endziel: {x}" for x in g.get("end") or [])
    o.extend(f"- Lebensziel: {x}" for x in g.get("life") or [])
    o.append("")
    if _nonempty(d.get("pains")):
        o.append("## Schmerzpunkte")
        o.extend(f"- {x}" for x in d["pains"])
        o.append("")
    jobs = [j for j in d.get("jobs") or [] if j.get("statement")]
    if jobs:
        o.append("## Jobs-to-be-Done")
        for j in jobs:
            o.append(f"- {j['id']}: {j['statement']}")
            forces = j.get("forces") or {}
            for k, label in (("push", "Push"), ("pull", "Pull"), ("anxiety", "Angst"), ("habit", "Gewohnheit")):
                if _nonempty(forces.get(k)):
                    o.append(f"  - {label}: {'; '.join(forces[k])}")
            for oc in j.get("outcomes") or []:
                o.append(f"  - Ergebnis: {oc}")
        o.append("")
    if _nonempty(d.get("anti_patterns")):
        o.append("## Tut nicht / will nicht")
        o.extend(f"- {x}" for x in d["anti_patterns"])
        o.append("")
    if _nonempty(d.get("quotes")):
        o.append("## So spricht sie")
        o.extend(f"- «{q['text']}»" for q in d["quotes"])
        o.append("")
    if p.sections.get("Szenario"):
        o.append("## Szenario")
        o.append(p.sections["Szenario"])
        o.append("")

    o.append("## Regeln")
    if sim.get("voice"):
        o.append(f"- Stimme: {sim['voice']}")
    for m in sim.get("must") or []:
        o.append(f"- Muss: {m}")
    for m in sim.get("must_not") or []:
        o.append(f"- Darf nicht: {m}")
    if sim.get("variance"):
        o.append(f"- Varianz: {sim['variance']} – wähle dafür eine konkrete, plausible Ausprägung und bleib dabei.")
    if mode == "simulate":
        o.append(
            "- Erfinde keine Fakten über dich, die oben nicht stehen oder nicht aus deiner Situation folgen. Wenn du etwas nicht weisst oder nicht entscheiden kannst, sag das – so wie es echte Personen tun."
        )
        o.append(
            "- Bleib in deiner Perspektive. Du kennst die Innensicht der Organisation nicht, die das Angebot macht."
        )
        o.append(
            "- Antworte nicht gefälliger, als es die Schmerzpunkte und die Zufriedenheit mit heutigen Lösungen hergeben."
        )
    else:
        o.append(
            "- Prüfe jedes Ergebnis gegen die Endziele, die Schmerzpunkte und die Erlebnisziele oben. Was die Erlebnisziele verletzt, ist falsch, auch wenn es funktional stimmt."
        )
        o.append("- Verwende Register und Vokabular der Persona, nicht der anbietenden Organisation.")
    if _nonempty(d.get("unknowns")):
        o.append("- Unbekannt (nicht erfinden, als offen behandeln): " + "; ".join(d["unknowns"]))
    if level == "proto":
        o.append(
            "- Diese Persona ist eine HYPOTHESE (proto). Annahmen: "
            + "; ".join(d.get("assumptions") or [])
            + ". Behandle Aussagen entsprechend vorsichtig."
        )
    elif _nonempty(d.get("assumptions")):
        o.append("- Nicht validierte Annahmen: " + "; ".join(d["assumptions"]))
    o.append("</persona>")
    return "\n".join(o).rstrip() + "\n"


# ===================================================================== set
def render_set(personas: list[Persona], fmt: str, **opts: Any) -> str:
    if fmt == "matrix":
        return render_matrix(personas)
    if fmt == "html":
        return render_html(personas, title=opts.get("title") or "Personas")
    if fmt == "bundle":
        return (
            json.dumps(
                {"generator": f"personakit {__version__}", "personas": [_export_dict(p) for p in personas]},
                ensure_ascii=False,
                indent=2,
            )
            + "\n"
        )
    raise ValueError(f"Unbekanntes Set-Format: {fmt}")


def render_list(personas: list[Persona]) -> str:
    rows = ["| ID | Archetyp | Prio | Status | Evidenz | Version | Review bis |", "|---|---|---|---|---|---|---|"]
    for p in personas:
        d = p.plain()
        rows.append(
            f"| `{p.id}` | {p.archetype} | {L(d.get('priority'))} | {L(d.get('status'))} | {L(d.get('evidence_level'))} | {d.get('version')} | {d.get('review_by') or '–'} |"
        )
    return "\n".join(rows) + "\n"


def render_matrix(personas: list[Persona]) -> str:
    """Comparison of behaviour variables and jobs across personas (choose the primary!)."""
    names: list[str] = []
    for p in personas:
        for v in (p.plain().get("behaviour") or {}).get("variables") or []:
            if v.get("name") and v["name"] not in names:
                names.append(v["name"])
    hdr = "| Verhaltensvariable | " + " | ".join(f"{p.id}" for p in personas) + " |"
    sep = "|---|" + "|".join([":---:"] * len(personas)) + "|"
    rows = [hdr, sep]
    for n in names:
        cells = []
        for p in personas:
            val = next(
                (
                    v.get("value")
                    for v in (p.plain().get("behaviour") or {}).get("variables") or []
                    if v.get("name") == n
                ),
                None,
            )
            cells.append(f"`{_bar(val)}` {val}" if val else "–")
        rows.append(f"| {n} | " + " | ".join(cells) + " |")
    out = ["## Verhaltensmatrix", "", *rows, ""]
    out += [
        "## Jobs-to-be-Done",
        "",
        "| Persona | Job | Wichtigkeit | Zufriedenheit heute | Chance |",
        "|---|---|:---:|:---:|:---:|",
    ]
    for p in personas:
        for j in p.plain().get("jobs") or []:
            if not j.get("statement"):
                continue
            imp, sat = j.get("importance"), j.get("satisfaction")
            opp = f"{imp + max(imp - sat, 0)}" if imp and sat else "–"  # ODI opportunity score (Ulwick)
            out.append(f"| `{p.id}` | {j['id']}: {j['statement']} | {imp or '–'} | {sat or '–'} | {opp} |")
    out.append("")
    out.append("_Chance = Wichtigkeit + max(Wichtigkeit − Zufriedenheit, 0) (ODI-Opportunity-Score, Skala 1–10)._")
    return "\n".join(out) + "\n"


# ----------------------------------------------------------------- html
def render_html(personas: list[Persona], title: str = "Personas") -> str:
    data = [_export_dict(p) for p in personas]
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    return (
        _HTML_TEMPLATE.replace("{{TITLE}}", _html.escape(title))
        .replace("{{DATA}}", payload)
        .replace("{{VERSION}}", __version__)
    )


_HTML_TEMPLATE = r"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{TITLE}}</title>
<style>
:root{--bg:#f6f5f2;--card:#fff;--ink:#1d1d1b;--muted:#6b6b66;--line:#e2e0da;--accent:#1f5f8b;--warn:#b55e00;--neg:#8b1f2d;--chip:#eeede8}
@media (prefers-color-scheme:dark){:root{--bg:#141413;--card:#1e1e1c;--ink:#ecebe6;--muted:#9a9a93;--line:#2c2c29;--accent:#7fb3d9;--warn:#e3a35b;--neg:#e07a87;--chip:#2a2a27}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
header{padding:24px 16px 8px;max-width:1100px;margin:0 auto}h1{margin:0 0 4px;font-size:22px}.sub{color:var(--muted);font-size:13px}
.filters{display:flex;gap:8px;flex-wrap:wrap;padding:8px 16px;max-width:1100px;margin:0 auto}
.filters button{border:1px solid var(--line);background:var(--card);color:var(--ink);border-radius:999px;padding:4px 12px;cursor:pointer;font-size:13px}
.filters button.on{background:var(--accent);color:#fff;border-color:var(--accent)}
main{max-width:1100px;margin:0 auto;padding:8px 16px 48px;display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px;cursor:pointer;display:flex;flex-direction:column;gap:8px}
.card:hover{border-color:var(--accent)}.card h2{margin:0;font-size:17px}.tag{color:var(--muted);font-style:italic;font-size:14px}
.chips{display:flex;gap:6px;flex-wrap:wrap}.chip{background:var(--chip);border-radius:6px;padding:2px 8px;font-size:12px}
.chip.primary{background:var(--accent);color:#fff}.chip.negative{background:var(--neg);color:#fff}.chip.proto{color:var(--warn)}
.bars{display:grid;grid-template-columns:1fr auto;gap:2px 10px;font-size:12px;color:var(--muted)}.bars b{font-weight:500;color:var(--ink)}
.dots{letter-spacing:2px;color:var(--accent)}
dialog{border:none;border-radius:14px;max-width:820px;width:calc(100% - 32px);padding:0;background:var(--card);color:var(--ink)}
dialog::backdrop{background:rgba(0,0,0,.45)}.dlg{padding:22px 24px 28px;max-height:85vh;overflow:auto}
.dlg h2{margin:0 0 2px}.dlg h3{font-size:13px;text-transform:uppercase;letter-spacing:.04em;color:var(--muted);margin:18px 0 6px}
.dlg ul{margin:0;padding-left:18px}.dlg table{border-collapse:collapse;width:100%;font-size:14px}.dlg td,.dlg th{border-bottom:1px solid var(--line);padding:5px 6px;text-align:left;vertical-align:top}
.close{float:right;border:none;background:var(--chip);border-radius:8px;padding:4px 10px;cursor:pointer;color:var(--ink)}
blockquote{margin:4px 0;padding-left:10px;border-left:3px solid var(--line);color:var(--muted)}
.job{border:1px solid var(--line);border-radius:8px;padding:8px 10px;margin:6px 0}.job .f{font-size:12px;color:var(--muted)}
pre{white-space:pre-wrap;font:inherit;margin:0}
</style>
</head>
<body>
<header><h1>{{TITLE}}</h1><div class="sub" id="sub"></div></header>
<div class="filters" id="filters"></div>
<main id="grid"></main>
<dialog id="dlg"><div class="dlg" id="dlgc"></div></dialog>
<script>
const DATA={{DATA}};
const LBL={primary:"Primär",secondary:"Sekundär",supplemental:"Ergänzend",negative:"Negativ",draft:"Entwurf",active:"Aktiv",retired:"Ruhestand",proto:"Proto",qualitative:"Qualitativ",statistical:"Statistisch"};
const esc=s=>String(s??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const dots=v=>"●".repeat(v)+"○".repeat(5-v);
const li=a=>(a&&a.length)?"<ul>"+a.map(x=>"<li>"+esc(x)+"</li>").join("")+"</ul>":"<div class='sub'>–</div>";
let filter="all";
function card(p){const b=(p.behaviour&&p.behaviour.variables||[]).filter(v=>v.name);
return `<div class="card" data-id="${esc(p.id)}"><h2>${esc(p.name?p.name+" – ":"")}${esc(p.archetype)}</h2>
${p.tagline?`<div class="tag">«${esc(p.tagline)}»</div>`:""}
<div class="chips"><span class="chip ${p.priority}">${LBL[p.priority]||p.priority}</span><span class="chip">${LBL[p.status]||p.status}</span><span class="chip ${p.evidence_level}">${LBL[p.evidence_level]||p.evidence_level}</span><span class="chip">v${esc(p.version)}</span></div>
<div class="bars">${b.map(v=>`<b>${esc(v.name)}</b><span class="dots">${dots(v.value)}</span>`).join("")}</div>
<div class="sub">${esc((p.goals&&p.goals.end||[]).slice(0,2).join(" · "))}</div></div>`}
function detail(p){const g=p.goals||{},c=p.context||{},b=p.behaviour||{},s=p.simulation||{},r=p.relations||{};
const jobs=(p.jobs||[]).filter(j=>j.statement).map(j=>{const f=j.forces||{};return `<div class="job"><b>${esc(j.id)}</b> ${esc(j.statement)}<div class="f">${(j.dimension||[]).join(", ")}${j.importance?` · Wichtigkeit ${j.importance}/5`:""}${j.satisfaction?` · Zufriedenheit heute ${j.satisfaction}/5`:""}</div>
${["push","pull","anxiety","habit"].filter(k=>f[k]&&f[k].length).map(k=>`<div class="f"><b>${{push:"Push",pull:"Pull",anxiety:"Angst",habit:"Gewohnheit"}[k]}:</b> ${esc(f[k].join("; "))}</div>`).join("")}
${j.outcomes&&j.outcomes.length?"<div class='f'><b>Ergebnisse:</b> "+esc(j.outcomes.join("; "))+"</div>":""}</div>`}).join("");
const vars=(b.variables||[]).filter(v=>v.name).map(v=>`<tr><td>${esc(v.name)}</td><td class="sub">${esc(v.low||"")}</td><td class="dots">${dots(v.value)}</td><td class="sub">${esc(v.high||"")}</td></tr>`).join("");
const ev=(p.evidence||[]).map(e=>`<tr><td>${esc(e.id)}</td><td>${esc(e.type)}</td><td>${esc(e.source)}</td><td>${esc(e.date||"")}</td><td>${esc(e.n||"")}</td><td>${esc(e.note||"")}</td></tr>`).join("");
const body=Object.entries(p._body||{}).filter(([k])=>k!=="_intro").map(([k,v])=>`<h3>${esc(k)}</h3><pre>${esc(v)}</pre>`).join("");
return `<button class="close" onclick="dlg.close()">Schliessen</button><h2>${esc(p.name?p.name+" – ":"")}${esc(p.archetype)}</h2>
<div class="sub">${esc(p.id)} v${esc(p.version)} · ${LBL[p.priority]||p.priority} · ${LBL[p.status]||p.status} · Evidenz ${LBL[p.evidence_level]||p.evidence_level}${p.review_by?" · Review bis "+esc(p.review_by):""}</div>
${p.tagline?`<div class="tag">«${esc(p.tagline)}»</div>`:""}
${p.scope?`<h3>Gilt für</h3><div>${esc(p.scope)}</div>`:""}
${(p.profile||[]).filter(f=>f.fact).length?`<h3>Relevante Fakten</h3><ul>${p.profile.filter(f=>f.fact).map(f=>`<li><b>${esc(f.fact)}</b>${f.relevance?" — <i>"+esc(f.relevance)+"</i>":""}</li>`).join("")}</ul>`:""}
${Object.values(c).some(x=>x&&x.length)?`<h3>Kontext</h3><ul>${c.role?`<li><b>Rolle:</b> ${esc(c.role)}</li>`:""}${c.situation?`<li><b>Situation:</b> ${esc(c.situation)}</li>`:""}${c.environment?`<li><b>Umgebung:</b> ${esc(c.environment)}</li>`:""}${c.channels&&c.channels.length?`<li><b>Kanäle:</b> ${esc(c.channels.join(", "))}</li>`:""}${(c.constraints||[]).map(x=>`<li><b>Restriktion:</b> ${esc(x)}</li>`).join("")}</ul>`:""}
${vars?`<h3>Verhalten</h3><table>${vars}</table>`:""}${b.patterns&&b.patterns.length?li(b.patterns):""}
<h3>Erlebnisziele</h3>${li(g.experience)}<h3>Endziele</h3>${li(g.end)}${g.life&&g.life.length?"<h3>Lebensziele</h3>"+li(g.life):""}
<h3>Schmerzpunkte</h3>${li(p.pains)}
${jobs?`<h3>Jobs-to-be-Done</h3>${jobs}`:""}
${p.anti_patterns&&p.anti_patterns.length?"<h3>Tut nicht / will nicht</h3>"+li(p.anti_patterns):""}
${p.quotes&&p.quotes.length?"<h3>Zitate</h3>"+p.quotes.map(q=>`<blockquote>«${esc(q.text)}»${q.evidence?" ("+esc(q.evidence)+")":""}</blockquote>`).join(""):""}
${body}
${Object.values(s).some(x=>x&&x.length)?`<h3>Prompt-Einsatz</h3><ul>${s.voice?`<li><b>Stimme:</b> ${esc(s.voice)}</li>`:""}${(s.must||[]).map(x=>`<li><b>Muss:</b> ${esc(x)}</li>`).join("")}${(s.must_not||[]).map(x=>`<li><b>Darf nicht:</b> ${esc(x)}</li>`).join("")}${s.variance?`<li><b>Varianz:</b> ${esc(s.variance)}</li>`:""}</ul>`:""}
<h3>Evidenz</h3>${ev?`<table><tr><th>ID</th><th>Typ</th><th>Quelle</th><th>Datum</th><th>n</th><th>Notiz</th></tr>${ev}</table>`:"<div class='sub'>–</div>"}
${p.assumptions&&p.assumptions.length?"<h3>Annahmen</h3>"+li(p.assumptions):""}${p.unknowns&&p.unknowns.length?"<h3>Offen</h3>"+li(p.unknowns):""}
${(r.journeys||[]).length||(r.personas||[]).length?`<h3>Verknüpfungen</h3><ul>${(r.journeys||[]).map(x=>`<li>Journey: ${esc(x)}</li>`).join("")}${(r.personas||[]).map(x=>`<li>Persona: ${esc(x)}</li>`).join("")}</ul>`:""}
${p.changelog&&p.changelog.length?"<h3>Änderungen</h3><ul>"+[...p.changelog].reverse().map(c=>`<li>v${esc(c.version)} (${esc(c.date)}): ${esc(c.note)}</li>`).join("")+"</ul>":""}`}
function draw(){const g=document.getElementById("grid");const rows=DATA.filter(p=>filter==="all"||p.priority===filter||p.status===filter);g.innerHTML=rows.map(card).join("");
document.querySelectorAll(".card").forEach(el=>el.onclick=()=>{const p=DATA.find(x=>x.id===el.dataset.id);document.getElementById("dlgc").innerHTML=detail(p);dlg.showModal()});
document.getElementById("sub").textContent=`${rows.length} von ${DATA.length} Personas · personakit {{VERSION}}`}
function filters(){const f=document.getElementById("filters");const keys=["all","primary","secondary","supplemental","negative","draft","active","retired"];
f.innerHTML=keys.map(k=>`<button data-k="${k}" class="${k===filter?"on":""}">${k==="all"?"Alle":LBL[k]}</button>`).join("");
f.querySelectorAll("button").forEach(b=>b.onclick=()=>{filter=b.dataset.k;filters();draw()})}
const dlg=document.getElementById("dlg");filters();draw();
</script>
</body>
</html>
"""
