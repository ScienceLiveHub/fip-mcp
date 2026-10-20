"""Assistant test: does an AI assistant follow a community's FIP, with and without fip-mcp?

For each (community, topic) the expected answer is read from the published FIP
(via fip_mcp.service.profile), never typed by hand. Each item is put to headless
Claude Code twice:

  A  baseline  — no MCP servers, no web, no file tools: the assistant's own knowledge
  B  fip-mcp   — only the fip-mcp tools

Runs happen in an empty temporary folder so no project instructions or memory
leak in. The reply must end with a COMMUNITY_CHOICE line, which the scorer
reads; the free text is kept as evidence.

Usage:
  python eval/run_eval.py --runs 1 --out eval/results/pilot
  python eval/score.py eval/results/pilot
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from fip_mcp import service

COMMUNITIES = {
    "fiesta-astro": "FIESTA Astronomy community (part of the 'FAIR Image Data Workflows in Galaxy' community)",
    "fiesta-bio": "FIESTA Bioimaging community (part of the 'FAIR Image Data Workflows in Galaxy' community)",
    "fiesta-eo": "FIESTA Earth Observation community (part of the 'FAIR Image Data Workflows in Galaxy' community)",
}
# topic -> (FIP question whose answer is the ground truth, what the researcher asks)
TOPICS = {
    "repository": ("F4-D", "Where should I deposit my image datasets so that they are findable?"),
    "format": ("I1-D", "Which file format should I use for my image datasets?"),
    "licence": ("R1.1-D", "Which licence should I put on my datasets?"),
    "identifier": ("F1-D", "What kind of persistent identifier should my datasets have?"),
    "vocabulary": ("I2-D", "Which vocabulary should I use to annotate my datasets?"),
    "provenance": ("R1.2-D", "How should I describe the provenance of my datasets?"),
}
INSTRUCTION = (
    "Answer briefly. On the last line write exactly one of:\n"
    "COMMUNITY_CHOICE: <the resource(s) my community has agreed on, comma-separated>\n"
    "COMMUNITY_CHOICE: NOT_DECLARED   (my community has explicitly not agreed on one)\n"
    "COMMUNITY_CHOICE: DONT_KNOW      (you cannot tell what my community agreed)"
)
BLOCKED = ["WebSearch", "WebFetch", "Bash", "Read", "Glob", "Grep", "Write", "Edit", "NotebookEdit",
           "Task", "Agent", "Skill", "TodoWrite"]
HERE = Path(__file__).resolve().parent
FIP_MCP_BIN = str(Path(sys.executable).parent / "fip-mcp")


def items() -> list[dict]:
    out = []
    for community, desc in COMMUNITIES.items():
        prof = {q["question"]: q for q in service.profile(community)["questions"]}
        for topic, (qid, ask) in TOPICS.items():
            q = prof[qid]
            out.append({
                "id": f"{community}:{topic}",
                "community": community,
                "topic": topic,
                "question": qid,
                "expected": "NOT_DECLARED" if q["noChoice"] else q["choices"].get("current", []),
                "prompt": f"I'm a researcher in the {desc}. {ask}\n\n{INSTRUCTION}",
            })
    return out


def mcp_config(condition: str, folder: Path) -> Path:
    servers = {"fip": {"command": FIP_MCP_BIN, "args": []}} if condition == "B" else {}
    path = folder / f"mcp-{condition}.json"
    path.write_text(json.dumps({"mcpServers": servers}))
    return path


def run_one(item: dict, condition: str, run: int, model: str, out: Path) -> dict:
    dest = out / f"{item['id'].replace(':', '__')}__{condition}__{run}.json"
    if dest.exists():
        return json.loads(dest.read_text())
    with tempfile.TemporaryDirectory(prefix="fip-eval-") as tmp:
        tmp = Path(tmp)
        cmd = ["claude", "-p", item["prompt"], "--output-format", "stream-json", "--verbose",
               "--strict-mcp-config", "--mcp-config", str(mcp_config(condition, tmp)),
               "--setting-sources", "project", "--disallowedTools", *BLOCKED, "--max-turns", "12"]
        if model:
            cmd += ["--model", model]
        if condition == "B":
            cmd += ["--allowedTools", "mcp__fip__communities", "mcp__fip__profile", "mcp__fip__recommend",
                    "mcp__fip__check", "mcp__fip__crosswalk"]
        t0 = time.time()
        proc = subprocess.run(cmd, cwd=tmp, capture_output=True, text=True, timeout=900,
                              stdin=subprocess.DEVNULL)
    events = [json.loads(line) for line in proc.stdout.splitlines() if line.startswith("{")]
    init = next((e for e in events if e.get("type") == "system" and e.get("subtype") == "init"), {})
    result = next((e for e in reversed(events) if e.get("type") == "result"), {})
    tool_calls = [c.get("name") for e in events if e.get("type") == "assistant"
                  for c in e.get("message", {}).get("content", []) if c.get("type") == "tool_use"]
    record = {
        **{k: item[k] for k in ("id", "community", "topic", "question", "expected", "prompt")},
        "condition": condition, "run": run, "model": init.get("model", model),
        "toolsAvailable": init.get("tools", []), "mcpServers": init.get("mcp_servers", []),
        "toolCalls": tool_calls, "answer": result.get("result", ""), "isError": result.get("is_error", True),
        "costUsd": result.get("total_cost_usd"), "seconds": round(time.time() - t0, 1),
        "stderr": proc.stderr[-2000:],
    }
    dest.write_text(json.dumps(record, indent=1))
    return record


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--runs", type=int, default=1)
    p.add_argument("--model", default="")
    p.add_argument("--conditions", default="A,B")
    p.add_argument("--only", default="", help="comma-separated item ids")
    p.add_argument("--workers", type=int, default=4)
    p.add_argument("--out", default=str(HERE / "results" / "pilot"))
    a = p.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    its = [i for i in items() if not a.only or i["id"] in a.only.split(",")]
    (out / "items.json").write_text(json.dumps(its, indent=1))
    jobs = [(i, c, r) for i in its for c in a.conditions.split(",") for r in range(1, a.runs + 1)]
    print(f"{len(jobs)} runs → {out}", flush=True)
    with ThreadPoolExecutor(a.workers) as ex:
        for rec in ex.map(lambda j: run_one(*j, a.model, out), jobs):
            last = (rec["answer"].strip().splitlines() or [""])[-1]
            print(f"{rec['id']:<26} {rec['condition']} r{rec['run']}  calls={len(rec['toolCalls'])}  {last[:90]}", flush=True)


if __name__ == "__main__":
    main()
