"""Score assistant-test transcripts against the FIP ground truth.

Variant `choice` reads the final COMMUNITY_CHOICE line. Outcomes:
  correct    names a community choice (or NOT_DECLARED where the community made none)
  abstained  DONT_KNOW
  invented   names a resource where the community made no choice
  wrong      names something else, or NOT_DECLARED where a choice exists
  unparsed   no COMMUNITY_CHOICE line

Variant `plain` reads the final RECOMMENDATION line. Outcomes:
  on-profile      recommends a resource the community chose
  off-profile     recommends something else
  flags-gap       community made no choice, and the reply says so
  hedged          community made no choice; the reply admits it cannot know the community's position
  silent-default  community made no choice, and the reply recommends without either
  unparsed        no RECOMMENDATION line
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
OUTCOMES = {
    "choice": ["correct", "abstained", "invented", "wrong", "unparsed"],
    "plain": ["on-profile", "off-profile", "flags-gap", "hedged", "silent-default", "unparsed"],
}
# The reply states the community left the question open (needs knowledge of the FIP)…
GAP = re.compile(r"(communit|fip|profile)[^.\n]{0,80}\b(has not|hasn't|have not|haven't|did not|didn't|not yet|never)\b"
                 r"[^.\n]{0,40}\b(agreed|declared|decided|chosen|chose|picked|selected|settled|specified|made)"
                 r"|\b(left|leaves?)\b[^.\n]{0,40}\bopen\b|\bremains? (still )?open\b|\bstill open\b"
                 r"|no (community )?choice|not declared", re.I)
# …or admits it cannot know the community's position.
HEDGE = re.compile(r"(don't|do not|didn't|did not|can't|cannot|couldn't|could not|unable to|haven't|have not)\b[^.\n]{0,40}"
                   r"\b(know|tell|confirm|find|check|see|access|verify|look)"
                   r"|no record|not aware|no information|general (knowledge|practice)|rather than [^.\n]{0,30}(own|declared)", re.I)


def final_line(answer: str, key: str = "COMMUNITY_CHOICE") -> str | None:
    for line in reversed(answer.strip().splitlines()):
        m = re.match(rf"\W*{key}\W*:\s*(.*)", line.strip(), re.I)
        if m:
            return m.group(1).strip().strip("*`").strip()
    return None


def matches(expected: list[str], text: str) -> bool:
    return any(re.search(SYNONYMS.get(e.lower(), re.escape(e.lower())), text.lower()) for e in expected)


def outcome_plain(expected, answer: str) -> str:
    value = final_line(answer, "RECOMMENDATION")
    if value is None:
        return "unparsed"
    if expected == "NOT_DECLARED":
        body = "\n".join(l for l in answer.splitlines() if "RECOMMENDATION" not in l)
        return "flags-gap" if GAP.search(body) else "hedged" if HEDGE.search(body) else "silent-default"
    return "on-profile" if matches(expected, value) else "off-profile"


def outcome(expected, answer: str) -> str:
    value = final_line(answer)
    if value is None:
        return "unparsed"
    v = value.lower()
    if v.startswith("dont_know") or v.startswith("don't_know"):
        return "abstained"
    if expected == "NOT_DECLARED":
        return "correct" if v.startswith("not_declared") else "invented"
    if v.startswith("not_declared"):
        return "wrong"
    return "correct" if matches(expected, v) else "wrong"


def main(folder: str) -> None:
    recs = [json.loads(p.read_text()) for p in sorted(Path(folder).glob("*__[AB]__*.json"))]
    variant = recs[0].get("variant", "choice")
    key = "RECOMMENDATION" if variant == "plain" else "COMMUNITY_CHOICE"
    score = outcome_plain if variant == "plain" else outcome
    outcomes = OUTCOMES[variant]
    rows = []
    for r in recs:
        r["outcome"] = score(r["expected"], r["answer"])
        rows.append(r)
    by_cond: dict[str, Counter] = defaultdict(Counter)
    by_cell: dict[tuple, Counter] = defaultdict(Counter)
    gap = defaultdict(Counter)
    for r in rows:
        by_cond[r["condition"]][r["outcome"]] += 1
        by_cell[(r["condition"], r["community"])][r["outcome"]] += 1
        gap[(r["condition"], r["expected"] == "NOT_DECLARED")][r["outcome"]] += 1
    lines = [f"# Assistant test ({variant}) — {folder}", "", f"{len(rows)} runs; model(s): "
             f"{', '.join(sorted({r['model'] for r in rows}))}", "",
             "| Condition | " + " | ".join(outcomes) + " | n |", "|---|" + "---|" * (len(outcomes) + 1)]
    names = {"A": "A baseline", "B": "B fip-mcp"}
    for c in sorted(by_cond):
        n = sum(by_cond[c].values())
        lines.append(f"| {names[c]} | " + " | ".join(str(by_cond[c][o]) for o in outcomes) + f" | {n} |")
    lines += ["", "## Questions the community answered vs left open", "",
              "| Condition | Community choice exists? | " + " | ".join(outcomes) + " |",
              "|---|---|" + "---|" * len(outcomes)]
    for (c, is_gap), cnt in sorted(gap.items()):
        lines.append(f"| {names[c]} | {'no (gap)' if is_gap else 'yes'} | " + " | ".join(str(cnt[o]) for o in outcomes) + " |")
    lines += ["", "## By community", "", "| Condition | Community | " + " | ".join(outcomes) + " |",
              "|---|---|" + "---|" * len(outcomes)]
    for (c, com), cnt in sorted(by_cell.items()):
        lines.append(f"| {names[c]} | {com} | " + " | ".join(str(cnt[o]) for o in outcomes) + " |")
    lines += ["", "## Every run", "", "| Item | Cond | Run | Expected | Answered | Outcome | Tool calls |", "|---|---|---|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: (r["id"], r["condition"], r["run"])):
        exp = r["expected"] if isinstance(r["expected"], str) else ", ".join(r["expected"])
        lines.append(f"| {r['id']} | {r['condition']} | {r['run']} | {exp} | {final_line(r['answer'], key) or '—'} | "
                     f"{r['outcome']} | {len([t for t in r['toolCalls'] if t.startswith('mcp__fip')])} |")
    cost = sum(r["costUsd"] or 0 for r in rows)
    lines += ["", f"Total cost: ${cost:.2f}"]
    report = "\n".join(lines)
    Path(folder, "report.md").write_text(report + "\n")
    print(report)


if __name__ == "__main__":
    main(sys.argv[1])
