"""Build the calibration plans: the example plan with deliberately washed-out personas.

Every stage keeps the questions of probe/beispiel/probe.json and replaces only the prompts, so the
stimulus stays the same and only the persona gets thinner:

    stufe-1  ohne Stimme   – no simulation block, quotes, patterns, profile, anti-patterns, narrative
    stufe-2  nur Archetyp  – the archetype sentence and the required fields, nothing else
    stufe-3  generisch     – the same generic archetype for every persona: a known, total collapse

Prompts use neutral ids (person-a …) so that an id like «eltern-neu-in-zuerich» does not give the
role away; plan and answers keep the real ids. Stage 0 is the Haiku run in probe/beispiel/.

    python probe/kalibrierung/make_plans.py
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

from personakit.model import Persona, find_persona_files
from personakit.render import render_prompt

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
BASE = ROOT / "probe" / "beispiel" / "probe.json"
GENERIC = "Person, die mit der Volksschule der Stadt Zürich zu tun hat"
KEEP = {
    1: {
        "personakit",
        "id",
        "archetype",
        "priority",
        "version",
        "status",
        "evidence_level",
        "language",
        "context",
        "goals",
        "pains",
        "jobs",
        "unknowns",
        "assumptions",
        "evidence",
        "domain",
        "scope",
    },
    2: {"personakit", "id", "archetype", "priority", "version", "status", "evidence_level"},
    3: {"personakit", "id", "archetype", "priority", "version", "status", "evidence_level"},
}
BODY = {1: ("Szenario",), 2: (), 3: ()}  # level-2 sections kept in the prompt


def washed(p: Persona, stage: int, neutral_id: str) -> Persona:
    q = Persona.from_text(p.to_text(), p.path)
    for key in list(q.data):
        if key not in KEEP[stage]:
            del q.data[key]
    q.data["id"] = neutral_id
    q.data["priority"] = "secondary"  # the priority would otherwise tell the roles apart
    q.data["evidence_level"] = "qualitative"
    if stage == 3:
        q.data["archetype"] = GENERIC
        q.data["version"] = "1.0.0"
    q.sections = {k: v for k, v in q.sections.items() if k in BODY[stage]}
    return q


def main() -> None:
    base = json.loads(BASE.read_text(encoding="utf-8"))
    files = {Persona.load(f).id: Persona.load(f) for f in find_persona_files([ROOT / "personas"])}
    neutral = {p["id"]: f"person-{chr(ord('a') + i)}" for i, p in enumerate(base["personas"])}
    for stage in (1, 2, 3):
        plan = copy.deepcopy(base)
        for entry in plan["personas"]:
            q = washed(files[entry["id"]], stage, neutral[entry["id"]])
            entry["prompt"] = render_prompt(q, mode="simulate")
            entry["archetype"] = q.archetype
            entry["must_not"] = []
            entry["unknowns"] = [{"id": f"U{i}", "text": str(u)} for i, u in enumerate(q.data.get("unknowns") or [], 1)]
        body = {"personas": plan["personas"], "questions": plan["questions"]}
        digest = hashlib.sha256(json.dumps(body, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()[:12]
        plan["plan_id"] = digest
        plan["sets"] = [f"kalibrierung-stufe-{stage}"]
        out = HERE / f"stufe-{stage}" / "probe.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"{out.relative_to(ROOT)}: plan {digest}")


if __name__ == "__main__":
    main()
