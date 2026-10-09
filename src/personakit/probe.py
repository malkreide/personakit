"""Collapse probe: do simulated personas stay distinguishable? (docs/METHOD.md 1.6, docs/PROBE.md)

``build_plan`` turns personas into a plan: the simulate prompt of every persona and 6–10 test
questions per persona, derived deterministically from scenario, jobs, pains, unknowns and end
goals. The plan runs against a model of the user's choice – personakit never calls a model.
``evaluate`` reads the answers and measures, with the standard library only, how similar the
answers of two personas to the same question are (TF-IDF cosine), whether ``simulation.must_not``
rules were broken (configurable keywords) and whether unknowns were left open (uncertainty markers).

Lexical similarity is a coarse proxy; the report says so and lists the limits of the method.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections import Counter
from dataclasses import dataclass, field
from itertools import combinations
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError

from . import __version__
from .lint import ERROR, INFO, WARN
from .model import BOM, Persona, PersonaError
from .render import render_prompt
from .validate import validate_probe_answers, validate_probe_keywords, validate_probe_plan

FORMAT = "1.0"
QUESTIONS_DEFAULT = 8
QUESTIONS_MIN = 6
QUESTIONS_MAX = 10
MAX_JOBS = 3
MAX_PAINS = 3
# Calibrated on washed-out personas (probe/kalibrierung/): see docs/PROBE.md, «Kalibrierung».
# With ≥ 2 samples the light uses the nearness: similarity to the other persona / similarity to itself.
RATIO_WARN = 0.50  # nearness at or above → yellow (personas reduced to their archetype: 0.53–0.61)
RATIO_ALARM = 0.85  # nearness at or above → red (identical prompts: 0.95–1.04; full personas: 0.26–0.41)
MIN_OWN = 0.05  # below this own similarity the nearness is unstable → absolute thresholds instead
# With one sample only the absolute similarity is left (calibrated on answers of about 230 words).
WARN_SIMILARITY = 0.15  # pair mean at or above → yellow
ALARM_SIMILARITY = 0.18  # pair mean at or above → red; per question: counts as "high"
SHARE_RED = 0.5  # share of shared questions ≥ alarm → red
SHARE_YELLOW = 0.25  # … → yellow
VARIANCE_HIGH = 0.80  # mean similarity of a persona's own samples at or above → variance collapsed (Q015)
MIN_SHARED = 3  # fewer shared questions → the light is shaky (Q016)
FORM_LENGTH_RATIO = 0.8  # shorter / longer mean answer length at or above → same length
FORM_STRUCTURE_DIFF = 0.2  # difference in the share of structured answers at or below → same structure
FORM_ASSISTANT_STRUCTURED = 0.5  # form collapse needs assistant form: mostly structured …
FORM_ASSISTANT_WORDS = 150  # … or long answers (Q020)
OPENER_SHARE = 0.1  # the most common opening word of two or more personas, each at this share or more (Q021)
EXCERPT_CHARS = 360

RED, YELLOW, GREEN, NONE = "red", "yellow", "green", "none"
LIGHT_LABEL = {RED: "🔴 rot", YELLOW: "🟡 gelb", GREEN: "🟢 grün", NONE: "⚪ keine Daten"}
_LIGHT_ORDER = {RED: 0, YELLOW: 1, GREEN: 2, NONE: 3}
_LEVEL_ORDER = {ERROR: 0, WARN: 1, INFO: 2}

OPEN, NOT_OPEN, CLAIM = "open", "not_open", "claim"
UNKNOWN_LABEL = {
    OPEN: "offen",
    NOT_OPEN: "nicht erkennbar offen",
    CLAIM: "konkrete Angabe ohne Vorbehalt",
}
_UNKNOWN_ORDER = {CLAIM: 0, NOT_OPEN: 1, OPEN: 2}

GENERIC_QUESTIONS = (
    "Wem vertraust du bei solchen Fragen am meisten – und wem nicht?",
    "Was würde dich davon abhalten, ein neues Angebot überhaupt auszuprobieren?",
    "Wie viel Zeit hast du realistischerweise für so etwas, und wann?",
    "Woran merkst du, dass ein Angebot nicht für dich gemacht ist?",
)

# «…» in a marker stands for up to four words: «weiss … nicht» also hits «weiss ich das selbst nicht».
DEFAULT_OPEN_MARKERS = (
    "weiss … nicht",
    "keine ahnung",
    "nicht sicher",
    "nicht genau",
    "unsicher",
    "kann … nicht … sagen",
    "kann … nicht … beurteilen",
    "ich schätze",
    "schätzungsweise",
    "schwer zu sagen",
    "kommt darauf an",
    "kommt drauf an",
    "vielleicht",
    "vermutlich",
    "wahrscheinlich",
    "ich glaube",
    "nie darüber nachgedacht",
    "müsste ich nachfragen",
    "don't know",
    "not sure",
    "maybe",
)

# A keyword in the same sentence as one of these words is mentioned, not used (Q017). Whole words only.
DEFAULT_CONTEXT_MARKERS = (
    "nicht",
    "nichts",
    "kein",
    "keine",
    "keinen",
    "keinem",
    "keiner",
    "keines",
    "nie",
    "niemals",
    "weder",
    "ohne",
    "unklar",
    "unbekannt",
    "unverständlich",
)
# A verb of saying or writing before the keyword in its sentence: someone else's words (Q017). Whole words only.
DEFAULT_REPORT_MARKERS = (
    "sagt",
    "sagte",
    "sagen",
    "meint",
    "meinte",
    "meinen",
    "schreibt",
    "schrieb",
    "schreiben",
    "steht",
    "stand",
    "stehen",
    "heisst es",
    "hiess es",
    "hört man",
    "liest man",
)
QUOTED, NEGATED, UNKNOWING, REPORTED, ASKED = "quoted", "negated", "unknowing", "reported", "asked"
CONTEXT_LABEL = {
    QUOTED: "zitiert",
    NEGATED: "verneint",
    UNKNOWING: "nicht gewusst",
    REPORTED: "wiedergegeben",
    ASKED: "gefragt",
}

_STOPWORDS = frozenset(
    """
    aber alle allem allen aller alles als also am an ander andere anderen anderer anderes auch auf aus
    bei beim bin bis bist da dabei dadurch dafür dagegen daher dahin damit dann dar daran darauf daraus
    darf darin darum das dass dein deine deinem deinen deiner dem den denn der deren des dessen deshalb
    die dies diese diesem diesen dieser dieses doch dort du durch ein eine einem einen einer eines einfach
    er es etwa etwas euch euer eure für gar gegen gibt hab habe haben hat hatte hätte ich ihm ihn ihnen
    ihr ihre ihrem ihren ihrer im immer in ins ist ja jede jedem jeden jeder jedes jetzt kann kannst kein
    keine keinem keinen keiner man manche mehr mein meine meinem meinen meiner mich mir mit muss musst
    nach nein nicht nichts noch nun nur ob oder ohne schon sehr sein seine seinem seinen seiner selbst
    sich sie sind so solche soll sollte sondern sonst über um und uns unser unsere unter viel vom von
    vor wann war waren warum was weil welche welchem welchen welcher welches wenn wer werde werden wie
    wieder will wir wird wirst wo wohl wollen würde würden zu zum zur zwar zwischen eben halt mal also
    erst ganz gut klar okay genau dann denn the and for that this with you your are was have not but
    """.split()
)
_SUFFIXES = ("ungen", "innen", "ung", "en", "er", "es", "em", "e", "n", "s")
_WORD = re.compile(r"[^\W\d_]+")
_NUMBER = re.compile(r"\d|\bprozent\b|\bpercent\b", re.IGNORECASE)
# Numbers that are no claim about the unknown: list numbering, dates, times of day, years.
_NOT_A_FIGURE = re.compile(
    r"^\s*\d+[.)]\s"
    r"|\b\d{1,2}\.\s?(?:jan|feb|mär|apr|mai|jun|jul|aug|sep|okt|nov|dez)\w*"
    r"|\b\d{1,2}\.\d{1,2}\.(?:\d{2,4})?"
    r"|\b\d{1,2}:\d{2}\b|\b\d{1,2}(?:\.\d{2})?\s?uhr\b"
    r"|\b(?:19|20)\d{2}\b",
    re.IGNORECASE | re.MULTILINE,
)
# «weiss nicht, ob …», «verstehe nicht, was …» before the keyword: the persona says it does not know the term.
_UNKNOWING = re.compile(
    r"(?<!\w)(?:weiss|wüsste|verstehe|kenne|begreife)\W+(?:\w+\W+){0,3}?nicht(?!\w)|(?<!\w)keine ahnung",
    re.IGNORECASE,
)
_JOB_SITUATION = re.compile(
    r"^\s*(wenn\b.+?),\s*(?:möchte|will|muss|brauche|wünsche|hätte)\b", re.IGNORECASE | re.DOTALL
)
_SENTENCE = re.compile(r"(?<=[.!?…])\s+")
_QUOTED_SPAN = re.compile(r"«[^»]*»|„[^“”]*[“”]|“[^”]*”|\"[^\"\n]*\"|‹[^›]*›")
_SENTENCE_END = ".!?\n"
_STRUCTURE = re.compile(r"^\s*(?:#{1,6}\s|[-*•]\s|\d+[.)]\s)|\*\*[^*\n]+\*\*", re.MULTILINE)
_MARKUP = re.compile(r"[*#_`>]+")
_BULLET = re.compile(r"^\s*(?:[-*•]|\d+[.)])\s+", re.MULTILINE)
NEGATION_WINDOW = 4  # words before or after a keyword in which a context marker counts (Q017)


# =================================================================== build
@dataclass(frozen=True)
class Question:
    id: str
    origin: str | None  # persona id, None for generic questions shared by all
    kind: str  # scenario | job | unknown | pain | goal | generic
    ref: str  # S1, J1, U1, P1, G1, X1
    text: str
    ask: tuple[str, ...] = ()

    def export(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "origin": self.origin,
            "kind": self.kind,
            "ref": self.ref,
            "text": self.text,
            "ask": list(self.ask),
        }


def _excerpt(text: str, limit: int = EXCERPT_CHARS) -> str:
    """First paragraph, whole sentences up to ``limit`` characters."""
    para = " ".join(text.strip().split("\n\n")[0].split())
    out = ""
    for sentence in _SENTENCE.split(para):
        if out and len(out) + 1 + len(sentence) > limit:
            break
        out = f"{out} {sentence}".strip()
    if len(out) > limit:
        out = out[:limit].rsplit(" ", 1)[0] + " …"
    return out


def _job_question(statement: str) -> str:
    """Only the situation of a job story – the persona has to bring its own motivation."""
    m = _JOB_SITUATION.match(statement)
    if m:
        situation = " ".join(m.group(1).split())
        return f"Die Situation: «{situation} …» Was tust du dann – Schritt für Schritt –, und was wäre für dich ein gutes Ergebnis?"
    return f"Es geht um diese Aufgabe: «{statement.strip()}» Wie gehst du heute damit um?"


def persona_questions(p: Persona) -> list[Question]:
    """Every candidate question of one persona, in the order they are taken (generic ones excluded)."""
    d = p.plain()
    pid = p.id
    scenario: list[Question] = []
    if p.sections.get("Szenario"):
        text = f"Stell dir diese Situation vor: «{_excerpt(p.sections['Szenario'])}» Was tust du jetzt – und warum?"
        scenario.append(Question(f"{pid}.S1", pid, "scenario", "S1", text))
    jobs: list[Question] = []
    seen: set[str] = set()
    for i, j in enumerate(d.get("jobs") or [], start=1):
        if not j.get("statement") or len(jobs) >= MAX_JOBS:
            continue
        ref = str(j.get("id") or f"J{i}")
        if ref in seen or not re.fullmatch(r"[A-Za-z0-9_-]+", ref):
            ref = f"J{i}"
        seen.add(ref)
        jobs.append(Question(f"{pid}.{ref}", pid, "job", ref, _job_question(str(j["statement"]))))
    unknowns = [
        Question(
            f"{pid}.U{i}",
            pid,
            "unknown",
            f"U{i}",
            f"Eine Frage zu dir und Leuten in deiner Lage: «{u}» Was sagst du dazu?",
        )
        for i, u in enumerate(d.get("unknowns") or [], start=1)
        if u
    ]
    pains = [
        Question(
            f"{pid}.P{i}",
            pid,
            "pain",
            f"P{i}",
            f"Jemand in deiner Lage sagt: «{pain}» Kennst du das? Wie gehst du damit um?",
        )
        for i, pain in enumerate(d.get("pains") or [], start=1)
        if pain
    ][:MAX_PAINS]
    goals = [
        Question(f"{pid}.G{i}", pid, "goal", f"G{i}", f"Was müsste passieren, damit für dich gilt: «{goal}»?")
        for i, goal in enumerate((d.get("goals") or {}).get("end") or [], start=1)
        if goal
    ]
    return scenario + jobs + unknowns[:1] + pains + unknowns[1:] + goals


def build_plan(
    personas: list[Persona], sets: list[str] | None = None, questions: int = QUESTIONS_DEFAULT, samples: int = 1
) -> dict[str, Any]:
    """The probe plan: simulate prompts plus ``questions`` test questions per persona, asked to every persona.

    Unknown questions go only to their own persona: they check whether it keeps its unknowns open.
    """
    if not QUESTIONS_MIN <= questions <= QUESTIONS_MAX:
        raise ValueError(f"questions must be {QUESTIONS_MIN}–{QUESTIONS_MAX}")
    ids = [p.id for p in personas]
    own: list[Question] = []
    generic_needed = 0
    for p in personas:
        picked = persona_questions(p)[:questions]
        own.extend(picked)
        generic_needed = max(generic_needed, questions - len(picked))
    generic = [
        Question(f"X{i}", None, "generic", f"X{i}", text)
        for i, text in enumerate(GENERIC_QUESTIONS[:generic_needed], start=1)
    ]
    plan_questions = [
        Question(q.id, q.origin, q.kind, q.ref, q.text, (q.origin,) if q.kind == "unknown" else tuple(ids))
        for q in own + generic
    ]
    plan_personas = []
    for p in personas:
        d = p.plain()
        sim = d.get("simulation") or {}
        plan_personas.append(
            {
                "id": p.id,
                "version": str(d.get("version", "")),
                "archetype": p.archetype,
                "priority": str(d.get("priority", "")),
                "evidence_level": str(d.get("evidence_level", "")),
                "prompt": render_prompt(p, mode="simulate"),
                "must_not": [{"id": f"N{i}", "rule": str(r)} for i, r in enumerate(sim.get("must_not") or [], start=1)],
                "unknowns": [{"id": f"U{i}", "text": str(u)} for i, u in enumerate(d.get("unknowns") or [], start=1)],
            }
        )
    body = {"personas": plan_personas, "questions": [q.export() for q in plan_questions]}
    plan_id = hashlib.sha256(json.dumps(body, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()[:12]
    return {
        "personakit_probe": FORMAT,
        "generator": f"personakit {__version__}",
        "plan_id": plan_id,
        "samples": samples,
        "sets": list(sets or []),
        "instructions": (
            "Pro Persona, Frage und Durchgang ein neues Gespräch ohne Vorgeschichte: Systemprompt = personas[].prompt, "
            "Nutzernachricht = questions[].text, nur für die Personas in questions[].ask. "
            f"{samples} Durchgang/Durchgänge pro Frage; ab 2 misst evaluate zusätzlich die Varianz jeder Persona. "
            "Antworten unverändert in answers.json (Format: docs/FORMAT.md, Collapse-Probe), dann "
            "personakit probe evaluate <plan> <answers>."
        ),
        **body,
    }


def runs(plan: dict[str, Any]) -> int:
    return sum(len(q["ask"]) for q in plan["questions"]) * int(plan.get("samples") or 1)


def answers_template(plan: dict[str, Any]) -> dict[str, Any]:
    samples = int(plan.get("samples") or 1)
    answers: dict[str, dict[str, Any]] = {p["id"]: {} for p in plan["personas"]}
    for q in plan["questions"]:
        for pid in q["ask"]:
            answers[pid][q["id"]] = "" if samples == 1 else [""] * samples
    return {"personakit_probe_answers": FORMAT, "plan_id": plan["plan_id"], "model": "", "answers": answers}


def keywords_template(plan: dict[str, Any]) -> str:
    """YAML skeleton for --keywords: one empty list per must_not rule, the rule text as comment."""
    o = [
        "# Schlüsselwörter für «personakit probe evaluate --keywords». Treffer am Wortanfang,",
        "# Gross-/Kleinschreibung egal. Regeln ohne Schlüsselwörter gelten als «nicht geprüft».",
        f'personakit_probe_keywords: "{FORMAT}"',
        "must_not:",
    ]
    for p in plan["personas"]:
        if not p["must_not"]:
            continue
        o.append(f"  {p['id']}:")
        for rule in p["must_not"]:
            o.append(f"    # {' '.join(rule['rule'].split())}")
            o.append(f"    {rule['id']}: []")
    o += [
        "# Optional: ersetzt die Standardliste der Unsicherheitsmarker für die Unknown-Prüfung.",
        "# open_markers: [weiss nicht, keine ahnung, vielleicht]",
    ]
    return "\n".join(o) + "\n"


# ================================================================== loading
def _read(path: str | Path) -> str:
    p = Path(path)
    if not p.is_file():
        raise PersonaError(f"Pfad nicht gefunden: {p}")
    try:
        text = p.read_bytes().decode("utf-8")
    except UnicodeDecodeError as e:
        raise PersonaError(f"{p}: Datei ist nicht UTF-8-kodiert (Byte {e.start}); als UTF-8 speichern") from e
    return text[1:] if text.startswith(BOM) else text


def _load_json(path: str | Path, validator, what: str) -> dict[str, Any]:
    try:
        data = json.loads(_read(path))
    except json.JSONDecodeError as e:
        raise PersonaError(f"{path}: kein gültiges JSON ({what}) – Zeile {e.lineno}: {e.msg}") from e
    errs = validator(data)
    if errs:
        raise PersonaError(f"{path}: kein gültiger {what} – " + "; ".join(errs[:5]))
    return data


def load_plan(path: str | Path) -> dict[str, Any]:
    return _load_json(path, validate_probe_plan, "Probe-Plan")


def load_answers(path: str | Path) -> dict[str, Any]:
    return _load_json(path, validate_probe_answers, "Antwortdatei")


def load_keywords(path: str | Path) -> dict[str, Any]:
    try:
        data = YAML(typ="safe", pure=True).load(_read(path))
    except YAMLError as e:
        raise PersonaError(f"{path}: YAML nicht lesbar – {e}") from e
    data = data or {}
    errs = validate_probe_keywords(data)
    if errs:
        raise PersonaError(f"{path}: keine gültige Schlüsselwort-Datei – " + "; ".join(errs[:5]))
    return data


# ================================================================ similarity
def _stem(word: str) -> str:
    for suffix in _SUFFIXES:
        if word.endswith(suffix) and len(word) - len(suffix) >= 4:
            return word[: -len(suffix)]
    return word


def tokenize(text: str, surface: dict[str, Counter] | None = None) -> list[str]:
    """Lower-case letter words of three or more characters, stop words removed, crude German stemming."""
    out = []
    for word in _WORD.findall(text.lower().replace("ß", "ss")):
        if len(word) < 3 or word in _STOPWORDS:
            continue
        stem = _stem(word)
        out.append(stem)
        if surface is not None:
            surface.setdefault(stem, Counter())[word] += 1
    return out


def tfidf(docs: list[list[str]]) -> list[dict[str, float]]:
    """Unit-length TF-IDF vectors (sublinear tf, smoothed idf over ``docs``)."""
    n = len(docs)
    df = Counter(t for d in docs for t in set(d))
    idf = {t: math.log((1 + n) / (1 + c)) + 1 for t, c in df.items()}
    vectors = []
    for d in docs:
        weights = {t: (1 + math.log(c)) * idf[t] for t, c in Counter(d).items()}
        norm = math.sqrt(sum(w * w for w in weights.values()))
        vectors.append({t: w / norm for t, w in weights.items()} if norm else {})
    return vectors


def cosine(a: dict[str, float], b: dict[str, float]) -> float:
    if len(a) > len(b):
        a, b = b, a
    return sum(w * b.get(t, 0.0) for t, w in a.items())


def _mean(values: list[float]) -> float:
    return sum(values) / len(values)


# ================================================================== results
@dataclass(frozen=True)
class ProbeFinding:
    level: str
    code: str
    message: str
    subject: str = ""  # persona id or "a ↔ b"

    def __str__(self) -> str:
        who = f"[{self.subject}] " if self.subject else ""
        return f"{self.level:5} {self.code:<6} {who}{self.message}"


@dataclass
class Pair:
    a: str
    b: str
    similarity: dict[str, float] = field(default_factory=dict)  # question id → mean cosine
    separation: float | None = None  # mean(own similarity) − similarity between, over questions with ≥ 2 samples each
    nearness: float | None = None  # similarity between / mean(own similarity), over the same questions
    light: str = NONE
    same_form: bool | None = None  # same length and structure (FormStats.same_form); None without answers
    top_terms: list[str] = field(default_factory=list)  # terms that carry the most similar question

    @property
    def label(self) -> str:
        return f"{self.a} ↔ {self.b}"

    @property
    def shared(self) -> int:
        return len(self.similarity)

    @property
    def mean(self) -> float | None:
        return _mean(list(self.similarity.values())) if self.similarity else None

    @property
    def max(self) -> float | None:
        return max(self.similarity.values()) if self.similarity else None

    @property
    def top_question(self) -> str | None:
        return max(self.similarity, key=lambda q: self.similarity[q]) if self.similarity else None

    def high(self, alarm: float) -> int:
        return sum(1 for v in self.similarity.values() if v >= alarm)


@dataclass(frozen=True)
class Hit:
    persona: str
    rule: str  # N1 …
    question: str
    keyword: str
    snippet: str
    in_question: bool
    context: str = ""  # "" = used; quoted | negated | asked = mentioned (Q017)


@dataclass
class RuleCheck:
    persona: str
    id: str
    rule: str
    keywords: list[str]
    hits: list[Hit] = field(default_factory=list)

    @property
    def checked(self) -> bool:
        return bool(self.keywords)

    @property
    def uses(self) -> list[Hit]:
        """Hits outside a quote, a negation or a question – the ones that may break the rule."""
        return [h for h in self.hits if not h.context]

    @property
    def mentions(self) -> list[Hit]:
        return [h for h in self.hits if h.context]


@dataclass
class FormStats:
    """How a persona answers, independent of what it says: length, sentences, structure, opening word."""

    answers: int
    words: float  # mean words per answer
    sentence_words: float  # mean words per sentence
    structured: float  # share of answers with headings, lists or bold lead-ins
    openers: Counter = field(default_factory=Counter)  # first content word → number of answers

    @property
    def opener(self) -> tuple[str, float] | None:
        if not self.openers:
            return None
        word, n = self.openers.most_common(1)[0]
        return word, n / self.answers

    def same_form(self, other: FormStats) -> bool:
        short, long = sorted((self.words, other.words))
        return (
            long > 0
            and short / long >= FORM_LENGTH_RATIO
            and abs(self.structured - other.structured) <= FORM_STRUCTURE_DIFF
        )

    @property
    def assistant_form(self) -> bool:
        return self.structured >= FORM_ASSISTANT_STRUCTURED or self.words >= FORM_ASSISTANT_WORDS


@dataclass
class UnknownCheck:
    persona: str
    id: str  # U1 …
    text: str
    question: str
    statuses: list[str] = field(default_factory=list)  # one per sample
    snippet: str = ""

    @property
    def status(self) -> str | None:
        return min(self.statuses, key=lambda s: _UNKNOWN_ORDER[s]) if self.statuses else None


@dataclass
class ProbeResult:
    plan: dict[str, Any]
    answers: dict[str, Any]
    pairs: list[Pair]
    variance: dict[str, float | None]  # persona → mean similarity of its own samples (≥ 2 samples)
    rules: list[RuleCheck]
    unknowns: list[UnknownCheck]
    findings: list[ProbeFinding]
    texts: dict[tuple[str, str], list[str]]
    warn: float = WARN_SIMILARITY
    alarm: float = ALARM_SIMILARITY
    ratio_warn: float = RATIO_WARN
    ratio_alarm: float = RATIO_ALARM
    open_markers: tuple[str, ...] = DEFAULT_OPEN_MARKERS
    markers_custom: bool = False
    form: dict[str, FormStats] = field(default_factory=dict)
    form_collapse: bool = False
    context_markers: tuple[str, ...] = DEFAULT_CONTEXT_MARKERS
    context_custom: bool = False
    report_markers: tuple[str, ...] = DEFAULT_REPORT_MARKERS
    report_custom: bool = False
    answered: int = 0
    samples: int = 0


# ================================================================ evaluate
def _snippet(text: str, start: int = 0, end: int | None = None, width: int = 160) -> str:
    """Whitespace-collapsed excerpt cut at word boundaries; around ``start:end`` when a span is given."""
    flat = " ".join(text.split())
    if end is None:
        return flat if len(flat) <= width else flat[:width].rsplit(" ", 1)[0] + " …"
    # re-find the span in the flattened text: offsets shift when whitespace collapses
    needle = " ".join(text[start:end].split())
    pos = max(flat.lower().find(needle.lower()), 0)
    left = max(0, pos - width // 2)
    right = min(len(flat), pos + len(needle) + width // 2)
    if left:
        left = flat.find(" ", left) + 1 or left  # do not start inside a word
        left = min(left, pos)
    if right < len(flat):
        cut = flat.rfind(" ", pos + len(needle), right)
        right = cut if cut > 0 else right
    return ("… " if left else "") + flat[left:right].strip() + (" …" if right < len(flat) else "")


def _ss(text: str) -> str:
    """Swiss spelling for matching: a model may write «weiß», the keyword list «weiss» (or the other way round)."""
    return text.replace("ß", "ss")


def _word_re(word: str) -> re.Pattern[str]:
    return re.compile(r"(?<!\w)" + re.escape(_ss(word.strip())), re.IGNORECASE)


def _whole_word_re(word: str) -> re.Pattern[str]:
    return re.compile(r"(?<!\w)" + re.escape(_ss(word.strip())) + r"(?!\w)", re.IGNORECASE)


def _marker_re(marker: str) -> re.Pattern[str]:
    """Open marker; «…» (or «...») stands for up to four words in between."""
    parts = [re.escape(_ss(x.strip())) for x in re.split(r"…|\.\.\.", marker) if x.strip()]
    return re.compile(r"(?<!\w)" + r"\W+(?:\w+\W+){0,4}?".join(parts), re.IGNORECASE)


def hit_context(
    text: str,
    start: int,
    end: int,
    markers: list[re.Pattern[str]],
    reports: list[re.Pattern[str]] | None = None,
) -> str:
    """Is the keyword at ``start:end`` mentioned rather than used?

    Quoted; negated nearby; «weiss nicht, ob …» before it; someone else's words («sagt», «steht») before it;
    or asked. Checked in this order, within the keyword's sentence.
    """
    if any(m.start() < start and end <= m.end() for m in _QUOTED_SPAN.finditer(text)):
        return QUOTED
    left = max(text.rfind(c, 0, start) for c in _SENTENCE_END) + 1
    ends = [i for c in _SENTENCE_END if (i := text.find(c, end)) != -1]
    right = min(ends) + 1 if ends else len(text)
    sentence = text[left:right]
    # only a negation near the keyword: «…, dass ich keine Frist verpasse» does not negate an earlier clause
    before = text[left:start].split()[-NEGATION_WINDOW:]
    after = text[end:right].split()[:NEGATION_WINDOW]
    near = " ".join(before + after)
    if any(m.search(near) for m in markers):
        return NEGATED
    head = text[left:start]
    if _UNKNOWING.search(head):
        return UNKNOWING
    if any(m.search(head) for m in reports or []):
        return REPORTED
    if sentence.rstrip().endswith("?"):
        return ASKED
    return ""


def _opener(text: str) -> str | None:
    """First content word of an answer («Ehrlich:», «**Ehrlich gesagt**» → ehrlich); None for stop words."""
    words = _WORD.findall(_ss(_MARKUP.sub(" ", text)).lower())
    if not words or len(words[0]) < 3 or words[0] in _STOPWORDS:
        return None
    return words[0]


def _plain_lines(text: str) -> list[str]:
    """Lines without bullets and Markdown markup – a list item counts as a sentence of its own."""
    return [line for line in _MARKUP.sub(" ", _BULLET.sub("", text)).splitlines() if line.strip()]


def form_stats(samples: list[str]) -> FormStats:
    words = [sum(len(line.split()) for line in _plain_lines(s)) for s in samples]
    sentences = [
        len(x.split()) for s in samples for line in _plain_lines(s) for x in _SENTENCE.split(line) if x.strip()
    ]
    openers = Counter(o for s in samples if (o := _opener(s)))
    return FormStats(
        answers=len(samples),
        words=_mean(words),
        sentence_words=_mean(sentences) if sentences else 0.0,
        structured=sum(1 for s in samples if _STRUCTURE.search(s)) / len(samples),
        openers=openers,
    )


def _basis(pair: Pair, alarm: float) -> str:
    """What the light of a pair rests on, for the findings."""
    if pair.nearness is not None:
        return f"Nähe {pair.nearness:.2f} (Ähnlichkeit zum Gegenüber / zu sich selbst), Ø Ähnlichkeit {pair.mean:.2f}"
    return f"Ø Ähnlichkeit {pair.mean:.2f}, {pair.high(alarm)}/{pair.shared} Fragen ≥ {alarm:.2f} (ein Durchgang, ohne Nähe)"


def _light(pair: Pair, warn: float, alarm: float, ratio_warn: float, ratio_alarm: float) -> str:
    """Nearness when there is a baseline (≥ 2 samples), else the absolute similarity."""
    if not pair.similarity:
        return NONE
    if pair.nearness is not None:
        if pair.nearness >= ratio_alarm:
            return RED
        return YELLOW if pair.nearness >= ratio_warn else GREEN
    mean = pair.mean or 0.0
    share = pair.high(alarm) / pair.shared
    if mean >= alarm or share >= SHARE_RED:
        return RED
    if mean >= warn or share >= SHARE_YELLOW:
        return YELLOW
    return GREEN


def _classify_unknown(text: str, markers: list[re.Pattern[str]]) -> str:
    text = _ss(text)
    if any(m.search(text) for m in markers):
        return OPEN
    return CLAIM if _NUMBER.search(_NOT_A_FIGURE.sub(" ", text)) else NOT_OPEN


def _ids(values: list[str], limit: int = 5) -> str:
    shown = ", ".join(values[:limit])
    return shown + (f" und {len(values) - limit} weitere" if len(values) > limit else "")


def evaluate(  # noqa: C901 – one pass over the answers, intentionally flat
    plan: dict[str, Any],
    answers: dict[str, Any],
    keywords: dict[str, Any] | None = None,
    warn: float = WARN_SIMILARITY,
    alarm: float = ALARM_SIMILARITY,
    ratio_warn: float = RATIO_WARN,
    ratio_alarm: float = RATIO_ALARM,
) -> ProbeResult:
    keywords = keywords or {}
    findings: list[ProbeFinding] = []
    personas = {p["id"]: p for p in plan["personas"]}
    order = [p["id"] for p in plan["personas"]]
    questions = {q["id"]: q for q in plan["questions"]}

    if answers.get("plan_id") and answers["plan_id"] != plan["plan_id"]:
        findings.append(
            ProbeFinding(
                WARN,
                "Q001",
                f"Antworten gehören zu Plan {answers['plan_id']}, ausgewertet wird Plan {plan['plan_id']} – "
                "Personas oder Fragen haben sich seit dem Lauf geändert",
            )
        )

    # ---- collect answers
    texts: dict[tuple[str, str], list[str]] = {}
    ignored: list[str] = []
    empty: dict[str, list[str]] = {}
    for pid, by_question in answers["answers"].items():
        if pid not in personas:
            ignored.append(pid)
            continue
        for qid, value in by_question.items():
            q = questions.get(qid)
            if q is None or pid not in q["ask"]:
                ignored.append(f"{pid}/{qid}")
                continue
            samples = [value] if isinstance(value, str) else list(value or [])
            samples = [s for s in samples if s and s.strip()]
            if samples:
                texts[(pid, qid)] = samples
            else:
                empty.setdefault(pid, []).append(qid)
    if ignored:
        findings.append(
            ProbeFinding(INFO, "Q003", f"{len(ignored)} Antwort(en) ohne Gegenstück im Plan ignoriert: {_ids(ignored)}")
        )
    for pid in order:
        missing = [
            q["id"]
            for q in plan["questions"]
            if pid in q["ask"] and (pid, q["id"]) not in texts and q["id"] not in empty.get(pid, [])
        ]
        expected = sum(1 for q in plan["questions"] if pid in q["ask"])
        if missing:
            findings.append(
                ProbeFinding(WARN, "Q002", f"{len(missing)} von {expected} Antworten fehlen: {_ids(missing)}", pid)
            )
        if empty.get(pid):
            findings.append(ProbeFinding(WARN, "Q004", f"Leere Antwort: {_ids(empty[pid])}", pid))

    # ---- vectors (question words do not count)
    surface: dict[str, Counter] = {}
    keys: list[tuple[str, str, int]] = []
    docs: list[list[str]] = []
    question_tokens = {qid: set(tokenize(q["text"])) for qid, q in questions.items()}
    hollow: dict[str, list[str]] = {}
    for (pid, qid), samples in texts.items():
        for i, s in enumerate(samples):
            toks = [t for t in tokenize(s, surface) if t not in question_tokens[qid]]
            if not toks:
                hollow.setdefault(pid, []).append(qid)
                continue
            keys.append((pid, qid, i))
            docs.append(toks)
    for pid, qids in hollow.items():
        findings.append(
            ProbeFinding(
                WARN,
                "Q004",
                f"Antwort ohne eigene Wörter (nur Füllwörter oder Wörter der Frage), nicht verglichen: {_ids(sorted(set(qids)))}",
                pid,
            )
        )
    vectors: dict[tuple[str, str], list[dict[str, float]]] = {}
    for key, vec in zip(keys, tfidf(docs)):
        vectors.setdefault((key[0], key[1]), []).append(vec)

    def own(pid: str, qid: str) -> float | None:
        vs = vectors.get((pid, qid)) or []
        if len(vs) < 2:
            return None
        return _mean([cosine(x, y) for x, y in combinations(vs, 2)])

    # ---- form of the answers (what lexical similarity cannot see)
    form: dict[str, FormStats] = {}
    for pid in order:
        own_samples = [s for qid in questions for s in texts.get((pid, qid), [])]
        if own_samples:
            form[pid] = form_stats(own_samples)

    # ---- pairs
    pairs: list[Pair] = []
    for a, b in combinations(order, 2):
        pair = Pair(a, b)
        gaps: list[float] = []
        based: list[tuple[float, float]] = []  # (between, own) on questions with a baseline
        for qid in questions:
            va, vb = vectors.get((a, qid)), vectors.get((b, qid))
            if not va or not vb:
                continue
            between = _mean([cosine(x, y) for x in va for y in vb])
            pair.similarity[qid] = between
            wa, wb = own(a, qid), own(b, qid)
            if wa is not None and wb is not None:
                gaps.append((wa + wb) / 2 - between)
                based.append((between, (wa + wb) / 2))
        pair.separation = _mean(gaps) if gaps else None
        if based and _mean([w for _, w in based]) >= MIN_OWN:
            pair.nearness = _mean([b_ for b_, _ in based]) / _mean([w for _, w in based])
        pair.light = _light(pair, warn, alarm, ratio_warn, ratio_alarm)
        if a in form and b in form:
            pair.same_form = form[a].same_form(form[b])
        top = pair.top_question
        if top:
            x, y = vectors[(a, top)][0], vectors[(b, top)][0]
            shared = sorted((t for t in x if t in y), key=lambda t: x[t] * y[t], reverse=True)[:5]
            local: dict[str, Counter] = {}  # word forms as they appear in these two answers
            tokenize(texts[(a, top)][0], local)
            tokenize(texts[(b, top)][0], local)
            pair.top_terms = [(local.get(t) or surface[t]).most_common(1)[0][0] for t in shared]
        pairs.append(pair)
        if pair.light == RED:
            findings.append(
                ProbeFinding(
                    WARN,
                    "Q010",
                    f"Collapse-Verdacht: {_basis(pair, alarm)}",
                    pair.label,
                )
            )
        elif pair.light == YELLOW:
            findings.append(
                ProbeFinding(
                    INFO,
                    "Q011",
                    f"Prüfen: {_basis(pair, alarm)}",
                    pair.label,
                )
            )
        if 0 < pair.shared < MIN_SHARED:
            findings.append(
                ProbeFinding(INFO, "Q016", f"Nur {pair.shared} gemeinsame Frage(n) – Ampel wenig belastbar", pair.label)
            )
    pairs.sort(key=lambda p: (_LIGHT_ORDER[p.light], -(p.mean or 0.0), p.label))
    if any(p.shared for p in pairs) and all(p.nearness is None for p in pairs):
        findings.append(
            ProbeFinding(
                INFO,
                "Q018",
                "Ohne zweiten Durchgang keine Nähe: Die Ampel erkennt so nur den vollständigen Collapse, "
                "nicht Personas, die auf ihren Archetyp geschrumpft sind (probe build --samples 3)",
            )
        )

    # ---- variance of each persona's own samples
    variance: dict[str, float | None] = {}
    for pid in order:
        values = [v for qid in questions if (v := own(pid, qid)) is not None]
        variance[pid] = _mean(values) if values else None
        if variance[pid] is not None and variance[pid] >= VARIANCE_HIGH:
            findings.append(
                ProbeFinding(
                    INFO,
                    "Q015",
                    f"Durchgänge fast gleich (Ø Ähnlichkeit {variance[pid]:.2f}) – Varianz kollabiert, simulation.variance prüfen",
                    pid,
                )
            )

    form_pairs = [p for p in pairs if p.same_form is not None]
    form_collapse = (
        bool(form_pairs) and all(p.same_form for p in form_pairs) and all(f.assistant_form for f in form.values())
    )
    if form_collapse:
        lengths = ", ".join(f"{pid} {f.words:.0f}" for pid, f in form.items())
        findings.append(
            ProbeFinding(
                WARN,
                "Q020",
                f"Formkollaps: alle Personas antworten gleich lang (Ø Wörter: {lengths}) und gleich gegliedert "
                f"({min(f.structured for f in form.values()):.0%}–{max(f.structured for f in form.values()):.0%} mit "
                "Gliederung) – simulation.voice um Länge und Form ergänzen",
            )
        )
    by_opener: dict[str, list[tuple[str, float]]] = {}
    for pid, f in form.items():
        if f.opener and f.opener[1] >= OPENER_SHARE:
            by_opener.setdefault(f.opener[0], []).append((pid, f.opener[1]))
    for word, who in sorted(by_opener.items()):
        if len(who) >= 2:
            shares = ", ".join(f"{pid} {share:.0%}" for pid, share in who)
            findings.append(
                ProbeFinding(
                    INFO, "Q021", f"Gleicher häufigster Antwortanfang «{word}» bei {len(who)} Personas ({shares})"
                )
            )

    # ---- must_not
    custom_context = keywords.get("context_markers")
    context_markers = tuple(str(m) for m in custom_context) if custom_context else DEFAULT_CONTEXT_MARKERS
    context_res = [_whole_word_re(m) for m in context_markers if m.strip()]
    custom_reports = keywords.get("report_markers")
    report_markers = tuple(str(m) for m in custom_reports) if custom_reports else DEFAULT_REPORT_MARKERS
    report_res = [_whole_word_re(m) for m in report_markers if m.strip()]
    configured = keywords.get("must_not") or {}
    for pid, rules in configured.items():
        if pid not in personas:
            findings.append(
                ProbeFinding(WARN, "Q006", f"Schlüsselwörter für unbekannte Persona «{pid}» – nicht geprüft")
            )
            continue
        known = {r["id"] for r in personas[pid]["must_not"]}
        for rid in rules or {}:
            if rid not in known:
                findings.append(
                    ProbeFinding(
                        WARN,
                        "Q006",
                        f"Schlüsselwörter für unbekannte Regel «{rid}» (vorhanden: {', '.join(sorted(known)) or 'keine'}) – nicht geprüft",
                        pid,
                    )
                )
    rule_checks: list[RuleCheck] = []
    for pid in order:
        unchecked: list[str] = []
        for r in personas[pid]["must_not"]:
            words = [str(w) for w in ((configured.get(pid) or {}).get(r["id"]) or []) if str(w).strip()]
            check = RuleCheck(pid, r["id"], r["rule"], words)
            rule_checks.append(check)
            if not words:
                unchecked.append(r["id"])
                continue
            for qid in questions:
                for sample in texts.get((pid, qid), []):
                    sample = _ss(sample)
                    for w in words:
                        m = _word_re(w).search(sample)
                        if m:
                            in_q = bool(_word_re(w).search(_ss(questions[qid]["text"])))
                            context = hit_context(sample, m.start(), m.end(), context_res, report_res)
                            snippet = _snippet(sample, m.start(), m.end(), 120)
                            check.hits.append(Hit(pid, r["id"], qid, w, snippet, in_q, context))
            if check.uses:
                where = sorted({h.question for h in check.uses})
                also = f" (dazu {len(check.mentions)} im Kontext)" if check.mentions else ""
                findings.append(
                    ProbeFinding(
                        WARN,
                        "Q012",
                        f"must_not {r['id']} möglicherweise verletzt: {len(check.uses)} Treffer in {_ids(where)}{also}",
                        pid,
                    )
                )
            elif check.mentions:
                kinds = Counter(CONTEXT_LABEL[h.context] for h in check.mentions)
                summary = ", ".join(f"{n} {label}" for label, n in sorted(kinds.items()))
                findings.append(
                    ProbeFinding(
                        INFO,
                        "Q017",
                        f"must_not {r['id']}: {len(check.mentions)} Treffer nur im Kontext ({summary}) – lesen, nicht zählen",
                        pid,
                    )
                )
        if unchecked:
            findings.append(
                ProbeFinding(INFO, "Q005", f"must_not ohne Schlüsselwörter, nicht geprüft: {', '.join(unchecked)}", pid)
            )

    # ---- unknowns
    custom = keywords.get("open_markers")
    markers = tuple(str(m) for m in custom) if custom else DEFAULT_OPEN_MARKERS
    marker_res = [_marker_re(m) for m in markers if m.strip()]
    unknown_checks: list[UnknownCheck] = []
    for q in plan["questions"]:
        if q["kind"] != "unknown" or not q.get("origin"):
            continue
        pid = q["origin"]
        text = next((u["text"] for u in personas.get(pid, {}).get("unknowns", []) if u["id"] == q["ref"]), q["text"])
        check = UnknownCheck(pid, q["ref"], text, q["id"])
        for sample in texts.get((pid, q["id"]), []):
            check.statuses.append(_classify_unknown(sample, marker_res))
        if check.statuses:
            worst = check.status
            sample = texts[(pid, q["id"])][check.statuses.index(worst)]
            check.snippet = _snippet(sample)
            if worst == CLAIM:
                findings.append(
                    ProbeFinding(
                        WARN,
                        "Q013",
                        f"{q['ref']} beantwortet mit konkreter Angabe ohne Vorbehalt: «{check.snippet}»",
                        pid,
                    )
                )
            elif worst == NOT_OPEN:
                findings.append(ProbeFinding(INFO, "Q014", f"{q['ref']} nicht erkennbar als offen behandelt", pid))
        unknown_checks.append(check)

    findings.sort(key=lambda f: (_LEVEL_ORDER[f.level], f.code, f.subject))
    return ProbeResult(
        plan=plan,
        answers=answers,
        pairs=pairs,
        variance=variance,
        rules=rule_checks,
        unknowns=unknown_checks,
        findings=findings,
        texts=texts,
        warn=warn,
        alarm=alarm,
        ratio_warn=ratio_warn,
        ratio_alarm=ratio_alarm,
        open_markers=markers,
        markers_custom=bool(custom),
        form=form,
        form_collapse=form_collapse,
        context_markers=context_markers,
        context_custom=bool(custom_context),
        report_markers=report_markers,
        report_custom=bool(custom_reports),
        answered=len(texts),
        samples=sum(len(v) for v in texts.values()),
    )


# ================================================================== report
LIMITS = (
    "**Lexikalische Ähnlichkeit ist ein grober Proxy.** Gemessen wird Wortüberlappung, nicht Bedeutung. "
    "Gleicher Inhalt in anderen Worten bleibt unentdeckt (falsch grün); gemeinsames Fachvokabular der Domäne "
    "hebt die Werte ohne Collapse (falsch rot). Ton, Haltung und Entscheidungen misst die Probe nicht.",
    "**Die Schwellen sind an einem Modell kalibriert.** Grundlage sind künstlich verwaschene Personas mit "
    "`claude-haiku-5-5` (probe/kalibrierung/). Die Nähe (ab zwei Durchgängen) ist relativ zur eigenen Streuung "
    "und darum robuster; mit einem Durchgang erkennen die absoluten Schwellen nur den vollständigen Collapse und "
    "hängen von Modell und Antwortlänge ab. Aussagekräftig bleibt der Vergleich: dasselbe Modell vor und nach "
    "einer Änderung, oder zwei Modelle mit demselben Plan.",
    "**Die Form ist nur grob gemessen.** Länge, Gliederung und Antwortanfang zeigen den Assistenten-Kollaps, "
    "nicht aber Tonfall, Register oder Höflichkeit; ob eine lange, gegliederte Antwort zur Persona passt, "
    "entscheidet ihre `simulation.voice`, nicht die Zahl.",
    "**Schlüsselwörter finden nur, was vorher aufgeschrieben wurde.** Ein Treffer ist kein Beweis, kein Treffer keine "
    "Einhaltung. Die Einordnung «zitiert», «verneint», «nicht gewusst», «wiedergegeben», «gefragt» ist eine "
    "Satzregel: Sie trennt Erwähnen von Verwenden meistens, aber nicht immer («Die Kreisschulbehörde ist nicht "
    "zuständig» verwendet den Begriff; eine Aufzählung «Schulamt, Kreisschulbehörde, Schule» gilt als Verwendung).",
    "**Unsicherheitsmarker sind oberflächlich.** «Vielleicht» kann Floskel sein; eine offene Antwort ohne Marker wird "
    "übersehen. Als konkrete Angabe zählt jede Zahl ausser Listennummern, Datum, Uhrzeit und Jahreszahl.",
    "**Unterscheidbar heisst nicht treu.** Personas können sich deutlich unterscheiden und trotzdem alle falsch liegen "
    "(Fidelity Gap, docs/METHOD.md 1.6). Die Probe ersetzt keine Validierung mit realen Personen.",
)


def _fmt(x: float | None) -> str:
    return "–" if x is None else f"{x:.2f}"


def _cell(text: str) -> str:
    return " ".join(str(text).split()).replace("|", "\\|")


def render_report(r: ProbeResult, plan_name: str = "", answers_name: str = "") -> str:  # noqa: C901 – report layout
    plan = r.plan
    title = ", ".join(plan.get("sets") or []) or "Personas"
    model = r.answers.get("model") or "nicht angegeben"
    o = [f"# Collapse-Probe – {title}", ""]
    o.append(
        f"{len(plan['personas'])} Personas · {len(plan['questions'])} Fragen · {r.answered} beantwortet "
        f"({r.samples} Durchgänge) · Modell: {_cell(model)} · Plan `{plan['plan_id']}`"
        + (f" · Dateien: `{plan_name}`, `{answers_name}`" if plan_name and answers_name else "")
    )
    o += [
        "",
        "> Die Ähnlichkeit ist **lexikalisch** (TF-IDF-Kosinus) und damit ein grober Proxy für Collapse. "
        "Ampeln sind Verdachtsmomente, keine Befunde – Grenzen der Methode am Ende des Berichts.",
        "",
        "## Ampel pro Persona-Paar",
        "",
        f"| Paar | Ampel | Nähe | Ø Ähnlichkeit | Max | Fragen ≥ {r.alarm:.2f} | Gemeinsame Fragen | Form |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ]
    form_label = {True: "gleich", False: "verschieden", None: "–"}
    for p in r.pairs:
        high = f"{p.high(r.alarm)}/{p.shared}" if p.shared else "–"
        o.append(
            f"| {p.label} | {LIGHT_LABEL[p.light]} | {_fmt(p.nearness)} | {_fmt(p.mean)} | {_fmt(p.max)} | {high} "
            f"| {p.shared} | {form_label[p.same_form]} |"
        )
    o += [
        "",
        "**Nähe** = Ähnlichkeit zum Gegenüber geteilt durch die Ähnlichkeit jeder Persona zu sich selbst (über die "
        "Fragen mit mindestens zwei Durchgängen je Persona). 1 heisst: einander so ähnlich wie sich selbst. "
        f"Mit Nähe: 🔴 rot ab {r.ratio_alarm:.2f}, 🟡 gelb ab {r.ratio_warn:.2f}. "
        f"Ohne Nähe (ein Durchgang): 🔴 rot ab Ø {r.alarm:.2f} oder wenn mindestens die Hälfte der Fragen ≥ {r.alarm:.2f} "
        f"liegt, 🟡 gelb ab Ø {r.warn:.2f} oder ab einem Viertel der Fragen ≥ {r.alarm:.2f}. "
        "Form: siehe nächster Abschnitt; sie fliesst nicht in die Ampel ein.",
        "",
    ]

    if r.form:
        o += [
            "## Form der Antworten",
            "",
            "| Persona | Antworten | Ø Wörter | Ø Wörter pro Satz | Mit Gliederung | Häufigster Anfang |",
            "|---|---:|---:|---:|---:|---|",
        ]
        for pid, f in r.form.items():
            opener = f"«{f.opener[0]}» {f.opener[1]:.0%}" if f.opener else "–"
            o.append(
                f"| {pid} | {f.answers} | {f.words:.0f} | {f.sentence_words:.1f} | {f.structured:.0%} | {opener} |"
            )
        verdict = (
            "**Formkollaps (Q020):** Alle Personas antworten gleich lang und gleich gegliedert, und zwar in "
            "Assistentenform. Die Wortwahl unterscheidet sie, die Form nicht – das sieht die Ampel oben nicht."
            if r.form_collapse
            else "Kein Formkollaps: Mindestens zwei Personas unterscheiden sich in Länge oder Gliederung, "
            "oder die Antworten sind kurz und ungegliedert."
        )
        o += [
            "",
            f"Gleiche Form = kürzere Ø-Länge mindestens {FORM_LENGTH_RATIO:.0%} der längeren und Anteil gegliederter "
            f"Antworten höchstens {FORM_STRUCTURE_DIFF * 100:.0f} Prozentpunkte auseinander. Gliederung = Überschrift, "
            f"Aufzählung oder **fetter** Einstieg. Formkollaps = alle Paare gleiche Form und alle Personas in "
            f"Assistentenform (mindestens {FORM_ASSISTANT_STRUCTURED:.0%} gegliedert oder Ø mindestens "
            f"{FORM_ASSISTANT_WORDS} Wörter).",
            "",
            verdict,
            "",
        ]

    shown = [p for p in r.pairs if p.light in (RED, YELLOW)] or [p for p in r.pairs if p.shared][:1]
    if shown:
        o += ["## Ähnlichste Antworten", ""]
        for p in shown:
            qid = p.top_question
            if not qid:
                continue
            q = next(x for x in plan["questions"] if x["id"] == qid)
            o += [f"### {p.label} – {LIGHT_LABEL[p.light]}", ""]
            o.append(f"Frage `{qid}` (Ähnlichkeit {p.similarity[qid]:.2f}): {_snippet(q['text'])}")
            o.append("")
            o.append(f"- **{p.a}:** «{_snippet(r.texts[(p.a, qid)][0], width=240)}»")
            o.append(f"- **{p.b}:** «{_snippet(r.texts[(p.b, qid)][0], width=240)}»")
            if p.top_terms:
                o.append(f"- Tragende Wörter: {', '.join(p.top_terms)}")
            o.append("")

    o += ["## Simulationsregeln (`must_not`)", ""]
    if not r.rules:
        o += ["Keine Persona im Plan hat `simulation.must_not`.", ""]
    for pid in [p["id"] for p in plan["personas"]]:
        checks = [c for c in r.rules if c.persona == pid]
        if not checks:
            continue
        o += [f"### {pid}", "", "| Regel | Schlüsselwörter | Ergebnis |", "|---|---|---|"]
        for c in checks:
            if not c.checked:
                result = "nicht geprüft"
            elif c.uses:
                result = f"⚠ {len(c.uses)} Treffer" + (f" (+ {len(c.mentions)} im Kontext)" if c.mentions else "")
            elif c.mentions:
                result = f"{len(c.mentions)} Treffer nur im Kontext"
            else:
                result = "kein Treffer"
            words = ", ".join(c.keywords) if c.keywords else "–"
            o.append(f"| {c.id}: {_cell(c.rule)} | {_cell(words)} | {result} |")
        hits = [h for c in checks for h in c.uses] + [h for c in checks for h in c.mentions]
        if hits:
            o.append("")
            for h in hits:
                tag = f"[{CONTEXT_LABEL[h.context]}] " if h.context else "⚠ "
                note = " (Wort steht auch in der Frage)" if h.in_question else ""
                o.append(f"- {tag}{h.rule} · `{h.question}` · «{h.keyword}»: {h.snippet}{note}")
        o.append("")
    if any(c.mentions for c in r.rules):
        o += [
            "Im Kontext = das Wort steht in Anführungszeichen (zitiert), höchstens vier Wörter neben einer "
            "Verneinung (verneint), nach «weiss/verstehe/kenne … nicht» (nicht gewusst), nach einem Verb des "
            "Sagens oder Schreibens wie «sagt», «steht» (wiedergegeben) oder in einer Frage (gefragt). Solche "
            "Treffer zählen nicht als möglicher Verstoss (Q017), bleiben aber zum Lesen aufgeführt.",
            "",
        ]

    o += ["## Unknowns", ""]
    if not r.unknowns:
        o += ["Der Plan enthält keine Unknown-Fragen.", ""]
    else:
        o += ["| Persona | Unknown | Bewertung | Antwort |", "|---|---|---|---|"]
        for u in r.unknowns:
            if u.status is None:
                verdict, answer = "keine Antwort", "–"
            else:
                verdict = UNKNOWN_LABEL[u.status]
                if len(u.statuses) > 1:
                    verdict += f" ({sum(1 for s in u.statuses if s == OPEN)}/{len(u.statuses)} offen)"
                answer = f"«{_cell(u.snippet)}»"
            o.append(f"| {u.persona} | {u.id}: {_cell(u.text)} | {verdict} | {answer} |")
        o += [
            "",
            "Offen = Antwort enthält einen Unsicherheitsmarker"
            + (" (eigene Liste aus der Schlüsselwort-Datei)" if r.markers_custom else "")
            + "; konkrete Angabe ohne Vorbehalt = Zahl oder Prozentangabe ohne Marker.",
            "",
        ]

    if any(v is not None for v in r.variance.values()):
        o += ["## Varianz je Persona", "", "| Persona | Ø Ähnlichkeit der eigenen Durchgänge |", "|---|---:|"]
        o += [f"| {pid} | {_fmt(v)} |" for pid, v in r.variance.items()]
        o += ["", f"Ab {VARIANCE_HIGH:.2f} antwortet die Persona fast immer gleich (Q015).", ""]

    o += ["## Befunde", ""]
    if r.findings:
        o += ["```"] + [str(f) for f in r.findings] + ["```", ""]
    else:
        o += ["Keine.", ""]

    o += ["## Grenzen der Methode", ""]
    o += [f"- {x}" for x in LIMITS]
    o += [
        "",
        "## Parameter",
        "",
        f"- Schwellen: Nähe gelb {r.ratio_warn:.2f}, rot {r.ratio_alarm:.2f}; ohne Nähe Warnung {r.warn:.2f}, "
        f"Alarm {r.alarm:.2f}; Varianz {VARIANCE_HIGH:.2f}",
        "- Ähnlichkeit: TF-IDF (1 + ln tf, geglättete IDF über alle Antworten dieses Laufs), Kosinus; "
        "pro Frage Mittel über alle Kombinationen der Durchgänge",
        "- Wörter: Kleinschreibung, Buchstabenwörter ab 3 Zeichen, ß → ss, Füllwörter entfernt, "
        "Endungen grob gekürzt; Wörter der Frage zählen nicht",
        f"- Schlüsselwörter: am Wortanfang, Gross-/Kleinschreibung egal · Kontextwörter: {len(r.context_markers)}"
        + (" (eigene Liste)" if r.context_custom else " (Standardliste)")
        + f" · Redeverben: {len(r.report_markers)}"
        + (" (eigene Liste)" if r.report_custom else " (Standardliste)")
        + f" · Unsicherheitsmarker: {len(r.open_markers)}"
        + (" (eigene Liste)" if r.markers_custom else " (Standardliste)"),
        f"- Plan erzeugt mit {r.plan.get('generator') or 'unbekannt'} · ausgewertet mit personakit {__version__}",
        "",
    ]
    return "\n".join(o)


def report_json(r: ProbeResult) -> dict[str, Any]:
    return {
        "generator": f"personakit {__version__}",
        "plan_id": r.plan["plan_id"],
        "model": r.answers.get("model") or None,
        "thresholds": {
            "ratio_warn": r.ratio_warn,
            "ratio_alarm": r.ratio_alarm,
            "warn": r.warn,
            "alarm": r.alarm,
            "variance": VARIANCE_HIGH,
        },
        "pairs": [
            {
                "a": p.a,
                "b": p.b,
                "light": p.light,
                "mean": p.mean,
                "max": p.max,
                "high": p.high(r.alarm),
                "shared": p.shared,
                "separation": p.separation,
                "nearness": p.nearness,
                "same_form": p.same_form,
                "similarity": p.similarity,
                "top_terms": p.top_terms,
            }
            for p in r.pairs
        ],
        "variance": r.variance,
        "form": {
            pid: {
                "answers": f.answers,
                "words": f.words,
                "sentence_words": f.sentence_words,
                "structured": f.structured,
                "opener": f.opener[0] if f.opener else None,
                "opener_share": f.opener[1] if f.opener else None,
            }
            for pid, f in r.form.items()
        },
        "form_collapse": r.form_collapse,
        "must_not": [
            {
                "persona": c.persona,
                "id": c.id,
                "rule": c.rule,
                "keywords": c.keywords,
                "checked": c.checked,
                "hits": [
                    {
                        "question": h.question,
                        "keyword": h.keyword,
                        "snippet": h.snippet,
                        "in_question": h.in_question,
                        "context": h.context or None,
                    }
                    for h in c.hits
                ],
            }
            for c in r.rules
        ],
        "unknowns": [
            {
                "persona": u.persona,
                "id": u.id,
                "text": u.text,
                "question": u.question,
                "status": u.status,
                "statuses": u.statuses,
            }
            for u in r.unknowns
        ],
        "findings": [
            {"level": f.level, "code": f.code, "subject": f.subject, "message": f.message} for f in r.findings
        ],
        "limits": [re.sub(r"\*\*", "", x) for x in LIMITS],
    }
