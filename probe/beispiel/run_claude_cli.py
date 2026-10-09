"""Run a personakit probe plan through the Claude Code CLI – the runner used for this example.

Not part of personakit: personakit never calls a model. This script is one way to fill
answers.json; any other runner works if it keeps the rule «one fresh conversation per
persona × question × sample, system prompt = personas[].prompt, user message = questions[].text».

    python probe/beispiel/run_claude_cli.py probe.json answers.json [--model haiku] [--workers 8]

Needs a logged-in `claude` CLI. Runs from an empty working directory, because the CLI adds a
little environment information to every system prompt. Resumable: answers already in
answers.json are kept, only missing samples are asked.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
import tempfile
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


def ask(prompt: str, question: str, model: str | None, workdir: str) -> tuple[str, list[str]]:
    cmd = ["claude", "-p", "--system-prompt", prompt, "--tools", "", "--no-session-persistence"]
    cmd += ["--model", model] if model else []
    cmd += ["--output-format", "json", question]
    last: Exception | None = None
    for attempt in range(3):
        try:
            run = subprocess.run(cmd, cwd=workdir, capture_output=True, text=True, timeout=300)
            data = json.loads(run.stdout)
            if data.get("is_error") or not data.get("result"):
                raise RuntimeError(run.stdout[:300])
            return data["result"].strip(), list(data.get("modelUsage", {}))
        except Exception as e:  # noqa: BLE001 – retried, then reported
            last = e
            time.sleep(5 * (attempt + 1))
    raise RuntimeError(str(last))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("plan")
    ap.add_argument("answers")
    ap.add_argument("--model", default=None, help="z. B. haiku, sonnet; ohne Angabe: Standard der CLI")
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()

    plan = json.loads(Path(a.plan).read_text(encoding="utf-8"))
    out = Path(a.answers)
    prompts = {p["id"]: p["prompt"] for p in plan["personas"]}
    samples = int(plan.get("samples") or 1)
    result = json.loads(out.read_text(encoding="utf-8")) if out.exists() else {}
    store = result.setdefault("answers", {})
    jobs = [
        (pid, q["id"], q["text"], i)
        for q in plan["questions"]
        for pid in q["ask"]
        for i in range(samples)
        if i >= len(store.get(pid, {}).get(q["id"], [])) or not store[pid][q["id"]][i]
    ]
    models: Counter = Counter()
    failed = 0

    def save() -> None:
        result.update({"personakit_probe_answers": "1.0", "plan_id": plan["plan_id"]})
        out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    with tempfile.TemporaryDirectory() as empty, ThreadPoolExecutor(max_workers=a.workers) as ex:
        futures = {ex.submit(ask, prompts[pid], text, a.model, empty): (pid, qid, i) for pid, qid, text, i in jobs}
        for n, fut in enumerate(as_completed(futures), start=1):
            pid, qid, i = futures[fut]
            try:
                text, used = fut.result()
            except RuntimeError as e:
                failed += 1
                print(f"{pid} {qid} #{i}: {e}", file=sys.stderr)
                continue
            models.update(used)
            store.setdefault(pid, {}).setdefault(qid, [""] * samples)[i] = text
            if n % 20 == 0 or n == len(jobs):
                save()
                print(f"{n}/{len(jobs)}", file=sys.stderr)
    used = ", ".join(f"{m}: {k}" for m, k in sorted(models.items())) or "keine neuen Antworten"
    result["model"] = (
        f"claude CLI -p ({used}), --system-prompt = Persona-Prompt, ohne Tools, "
        f"je Durchgang ein frisches Gespräch, {dt.date.today().isoformat()}"
    )
    save()
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
