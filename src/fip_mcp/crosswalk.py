"""What changes when an object moves from one community's FIP to another's."""
from __future__ import annotations

from .fip import Fip


def _choices(fip: Fip, by_principle: bool = False) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for qid, decls in fip.by_question().items():
        res = [r for d in decls for r in d.use.get("current", []) + d.use.get("recommended", [])]
        key = (decls[0].principle or qid) if by_principle else qid
        row = out.setdefault(key, {"principle": decls[0].principle, "asks": decls[0].text, "labels": []})
        row["labels"] = sorted(set(row["labels"]) | {r.label for r in res})
    return out


def crosswalk(source: Fip, target: Fip) -> dict:
    # R-FIP resources are placed per principle, not per question: compare at that level.
    by_principle = "R-FIP" in (source.kind, target.kind)
    a, b = _choices(source, by_principle), _choices(target, by_principle)
    rows = []
    for qid in sorted(set(a) | set(b), key=lambda q: (q.startswith("FIP-S"), q)):
        sa, sb = a.get(qid, {"labels": []}), b.get(qid, {"labels": []})
        if not sa["labels"] and not sb["labels"]:
            status = "neither-chose"
        elif not sa["labels"]:
            status = "only-target-chose"
        elif not sb["labels"]:
            status = "only-source-chose"
        elif {x.lower() for x in sa["labels"]} == {x.lower() for x in sb["labels"]}:
            status = "same"
        elif set(map(str.lower, sa["labels"])) & set(map(str.lower, sb["labels"])):
            status = "overlap"
        else:
            status = "differs"
        row = {"question": qid, "asks": (a.get(qid) or b.get(qid))["asks"], "status": status,
               "source": sa["labels"], "target": sb["labels"]}
        rows.append(row)
    counts: dict[str, int] = {}
    for r in rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    return {"source": source.label, "target": target.label,
            "level": "principle" if by_principle else "question", "summary": counts,
            "changes": [r for r in rows if r["status"] in ("differs", "overlap", "only-target-chose")],
            "rows": rows}
