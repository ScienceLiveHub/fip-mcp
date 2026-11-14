"""The operations behind both the MCP tools and the CLI."""
from __future__ import annotations

import json
from functools import lru_cache
from importlib.resources import files

from . import fip as _fip
from . import target as _target
from .checks import check as _check
from .compare import compare as _compare
from .compare import to_xlsx
from .crosswalk import crosswalk as _crosswalk
from .facts import facts_for
from .questions import principles_for


def communities() -> dict:
    data = json.loads(files("fip_mcp").joinpath("data/communities.json").read_text())
    return {k: v for k, v in data.items() if not k.startswith("_")}


def resolve(community: str) -> str:
    """A short name from the registry, or a FIP nanopub URI as-is."""
    if community.startswith("http"):
        return community
    known = communities()
    if community not in known:
        raise KeyError(f"unknown community {community!r}; known: {sorted(known)} (or pass a FIP nanopub URI)")
    return known[community]["fip"]


@lru_cache(maxsize=None)
def load(community: str) -> _fip.Fip:
    return _fip.load(resolve(community))


def profile(community: str) -> dict:
    f = load(community)
    rows = []
    for qid, decls in f.by_question().items():
        rows.append({
            "question": qid, "principle": decls[0].principle, "axis": decls[0].axis, "asks": decls[0].text,
            "choices": {kind: [r.label for d in decls for r in d.use.get(kind, [])]
                        for kind in ("current", "recommended", "planned", "replaced")
                        if any(d.use.get(kind) for d in decls)},
            "noChoice": all(d.no_choice for d in decls),
        })
    return {
        "label": f.label, "kind": f.kind, "uri": f.uri, "version": f.version, "created": f.created,
        "community": f.community, "caseStudy": f.case_study, "objectType": f.object_type,
        "versionChain": f.version_chain,
        "coverage": (f"{sum(not r['noChoice'] for r in rows)}/{len(rows)} questions answered" if f.kind == "FIP"
                     else f"{len({r.uri for d in f.declarations for r in d.use.get('recommended', [])})} "
                          "recommended resources, grouped by the principles their types enable or support"),
        "questions": rows,
    }


def recommend(community: str, topic: str) -> dict:
    f = load(community)
    wanted = set(principles_for(topic, {d.text: d.principle for d in f.declarations}))
    out = []
    for d in f.declarations:
        if d.principle not in wanted:
            continue
        out.append({
            "question": d.question, "asks": d.text, "axis": d.axis,
            "noChoice": d.no_choice,
            "use": {kind: [{"label": r.label, "url": r.url or r.uri, "about": r.comment[:300],
                            "howToRecognise": facts_for(r).for_principle(d.principle)} for r in res]
                    for kind, res in d.use.items()},
            "considerations": d.considerations,
        })
    gaps = [r["question"] for r in out if r["noChoice"]]
    return {
        "fip": f.label, "topic": topic, "answers": out,
        "guidance": (
            "Recommend only the resources listed under `use.current`; mention `planned` ones as upcoming. "
            + (f"The community made no choice for {', '.join(gaps)}: say so plainly, do not substitute your own "
               "preference as if it were the community's, and suggest raising it with the FIP maintainers."
               if gaps else "")
        ).strip(),
    }


def check(community: str, target: str) -> dict:
    return _check(load(community), _target.load(target))


def crosswalk(source: str, target: str) -> dict:
    return _crosswalk(load(source), load(target))


def compare(profiles: list[str], names: list[str] | None = None, include_supports: bool = True,
            xlsx: str | None = None) -> dict:
    result = _compare([load(p) for p in profiles], names=names, include_supports=include_supports)
    if xlsx:
        result["xlsx"] = to_xlsx(result, xlsx)
    return result
