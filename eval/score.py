"""Score assistant-test transcripts against the FIP ground truth.

Reads only the final COMMUNITY_CHOICE line of each reply. Outcomes:
  correct    names a community choice (or NOT_DECLARED where the community made none)
  abstained  DONT_KNOW
  invented   names a resource where the community made no choice
  wrong      names something else, or NOT_DECLARED where a choice exists
  unparsed   no COMMUNITY_CHOICE line
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

# FER label (lower case) -> pattern an answer may use for it
SYNONYMS = {
    "zenodo": r"zenodo",
    "image data resource": r"image data resource|\bidr\b",
    "nird-rda": r"\bnird\b",
    "flexible image transport system": r"\bfits\b|flexible image transport",
    "netcdf": r"netcdf",
    "netcdf cf-1.11": r"\bcf\b|climate and forecast|cf[- ]?conventions|cf-1",
    "cc by 4.0": r"cc[- ]?by[- ]?4|creative commons attribution 4",
    "cc0 1.0": r"\bcc0\b|cc[- ]?zero",
    "doi": r"\bdoi",
    "uri": r"\buris?\b|\burls?\b",
    "ivoa vocabulary: unified astronomy thesaurus": r"unified astronomy thesaurus|\buat\b",
    "prov-o": r"\bprov(-o)?\b",
}
OUTCOMES = ["correct", "abstained", "invented", "wrong", "unparsed"]


def choice_line(answer: str) -> str | None:
    for line in reversed(answer.strip().splitlines()):
        m = re.match(r"\W*COMMUNITY_CHOICE\W*:\s*(.*)", line.strip(), re.I)
        if m:
            return m.group(1).strip().strip("*`").strip()
    return None


def outcome(expected, answer: str) -> str:
    value = choice_line(answer)
    if value is None:
        return "unparsed"
    v = value.lower()
    if v.startswith("dont_know") or v.startswith("don't_know"):
        return "abstained"
    if expected == "NOT_DECLARED":
        return "correct" if v.startswith("not_declared") else "invented"
    if v.startswith("not_declared"):
        return "wrong"
    hit = any(re.search(SYNONYMS.get(e.lower(), re.escape(e.lower())), v) for e in expected)
    return "correct" if hit else "wrong"


def main(folder: str) -> None:
    recs = [json.loads(p.read_text()) for p in sorted(Path(folder).glob("*__[AB]__*.json"))]
    rows = []
    for r in recs:
        r["outcome"] = outcome(r["expected"], r["answer"])
        rows.append(r)
    by_cond: dict[str, Counter] = defaultdict(Counter)
    by_cell: dict[tuple, Counter] = defaultdict(Counter)
    gap = defaultdict(Counter)
    for r in rows:
        by_cond[r["condition"]][r["outcome"]] += 1
        by_cell[(r["condition"], r["community"])][r["outcome"]] += 1
        gap[(r["condition"], r["expected"] == "NOT_DECLARED")][r["outcome"]] += 1
    lines = [f"# Assistant test — {folder}", "", f"{len(rows)} runs; model(s): "
             f"{', '.join(sorted({r['model'] for r in rows}))}", "",
             "| Condition | " + " | ".join(OUTCOMES) + " | n |", "|---|" + "---|" * (len(OUTCOMES) + 1)]
    names = {"A": "A baseline", "B": "B fip-mcp"}
    for c in sorted(by_cond):
        n = sum(by_cond[c].values())
        lines.append(f"| {names[c]} | " + " | ".join(str(by_cond[c][o]) for o in OUTCOMES) + f" | {n} |")
    lines += ["", "## Questions the community answered vs left open", "",
              "| Condition | Community choice exists? | " + " | ".join(OUTCOMES) + " |",
              "|---|---|" + "---|" * len(OUTCOMES)]
    for (c, is_gap), cnt in sorted(gap.items()):
        lines.append(f"| {names[c]} | {'no (gap)' if is_gap else 'yes'} | " + " | ".join(str(cnt[o]) for o in OUTCOMES) + " |")
    lines += ["", "## By community", "", "| Condition | Community | " + " | ".join(OUTCOMES) + " |",
              "|---|---|" + "---|" * len(OUTCOMES)]
    for (c, com), cnt in sorted(by_cell.items()):
        lines.append(f"| {names[c]} | {com} | " + " | ".join(str(cnt[o]) for o in OUTCOMES) + " |")
    lines += ["", "## Every run", "", "| Item | Cond | Run | Expected | Answered | Outcome | Tool calls |", "|---|---|---|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: (r["id"], r["condition"], r["run"])):
        exp = r["expected"] if isinstance(r["expected"], str) else ", ".join(r["expected"])
        lines.append(f"| {r['id']} | {r['condition']} | {r['run']} | {exp} | {choice_line(r['answer']) or '—'} | "
                     f"{r['outcome']} | {len([t for t in r['toolCalls'] if t.startswith('mcp__fip')])} |")
    cost = sum(r["costUsd"] or 0 for r in rows)
    lines += ["", f"Total cost: ${cost:.2f}"]
    report = "\n".join(lines)
    Path(folder, "report.md").write_text(report + "\n")
    print(report)


if __name__ == "__main__":
    main(sys.argv[1])
