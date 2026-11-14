"""Deterministic checks of a target against a community's FIP or R-FIP.

Each declared resource is tested with the facts `facts.py` finds for it (from its
nanopub, public registries, or the config file), never with knowledge built into
this code. A resource with no testable fact is `manual` — the agent should ask
the user, never guess. A question the community left open is `no-choice`: a gap
in the FIP, not in the target.

A question passes if ANY of its declared resources passes: a FIP lists the
choices a community accepts, not a set that must all be present. A resource
passes if ALL its testable facts hold (file evidence counts once: a listed file
name or a matching extension).
"""
from __future__ import annotations

import re
from collections.abc import Callable
from pathlib import PurePath

from .facts import Facts, config, facts_for
from .fip import Fip, Resource
from .target import Target

Test = Callable[[Target], tuple[bool, str]]


def _exts(path: str) -> list[str]:
    """Extensions of a path and of its folders (data.zarr/0.0 -> ["zarr"])."""
    return [p.rsplit(".", 1)[1].lower() for p in PurePath(path).parts if "." in p.strip(".")]


def _file_test(f: Facts) -> Test | None:
    names = {n.lower() for n in f.files}
    exts = {e.lower() for e in f.extensions}
    if not names and not exts:
        return None

    def test(t: Target) -> tuple[bool, str]:
        hits = [p for p in t.files if PurePath(p).name.lower() in names or exts & set(_exts(p))]
        want = ", ".join(sorted(names) + [f".{e}" for e in sorted(exts)])
        return bool(hits), (f"{len(hits)} file(s) matching {want}, e.g. {hits[0]}" if hits else f"no file matching {want}")
    return test


def _java_regex(p: str) -> str:
    """Wikidata patterns use Java classes such as \\p{C} (control chars)."""
    return p.replace(r"\p{C}", r"\x00-\x1f\x7f-\x9f")


def _tests(res: Resource, principle: str) -> list[Test]:
    f = facts_for(res)
    tests: list[Test] = []
    if ft := _file_test(f):
        tests.append(ft)
    if f.spdx and principle == "R1.1":   # SPDX also names non-licence things (e.g. "NetCDF")
        tests.append(lambda t, s=f.spdx: (s in t.licences, f"licence(s): {', '.join(t.licences) or 'none found'}"))
    if f.url_scheme:
        def scheme(t: Target, s=f.url_scheme) -> tuple[bool, str]:
            urls = [u for u in t.urls if u]
            bad = [u for u in urls if not u.lower().startswith(s + "://")]
            return bool(urls) and not bad, (f"{len(urls)} URL(s), {len(bad)} not {s}" if urls else "no URLs to inspect")
        tests.append(scheme)
    if f.access:
        tests.append(lambda t, a=f.access: (t.access == a, f"access: {t.access or 'unknown'}"))
    hosts = set(f.hosts) | (set(f.web_hosts) if principle == "F4" else set())
    if hosts:
        tests.append(lambda t, h=hosts: (bool(h & set(t.repository_hosts)),
                                         f"deposited at: {', '.join(t.repository_hosts) or 'unknown'}"))
    if f.registration_agency:
        tests.append(lambda t, ra=f.registration_agency: (
            ra in t.registration_agencies, f"DOI registration agencies: {', '.join(t.registration_agencies) or 'none'}"))
    if f.id_patterns and principle in ("F1", "F3"):
        def ident(t: Target, pats=f.id_patterns) -> tuple[bool, str]:
            ok = []
            for d in t.dois:
                for p in pats:
                    try:
                        if re.fullmatch(_java_regex(p), d):
                            ok.append(d)
                    except re.error:
                        continue
            return bool(ok), f"identifier(s): {', '.join(t.dois) or 'none found'}"
        tests.append(ident)
    return tests


def check(fip: Fip, t: Target) -> dict:
    results = []
    for qid, decls in fip.by_question().items():
        resources = [r for d in decls for r in d.use.get("current", []) + d.use.get("recommended", [])]
        planned = [r.label for d in decls for r in d.use.get("planned", [])]
        principle, axis, text = decls[0].principle, decls[0].axis, decls[0].text
        row = {"question": qid, "principle": principle, "axis": axis, "asks": text}
        if not resources:
            row.update(status="planned-only" if planned else "no-choice",
                       detail=f"community plans: {', '.join(planned)}" if planned
                       else "the community declared no choice — a gap in the FIP, not in the target")
            results.append(row)
            continue
        evidence, passed, checkable = [], False, False
        for r in resources:
            f = facts_for(r)
            tests = _tests(r, principle)
            if not tests:
                evidence.append({"resource": r.label, "result": "manual", "uri": r.url or r.uri,
                                 "why": "no testable fact found for this resource",
                                 **({"notes": f.notes} if f.notes else {})})
                continue
            checkable = True
            outcomes = [tst(t) for tst in tests]
            ok = all(o for o, _ in outcomes)
            passed |= ok
            evidence.append({"resource": r.label, "result": "pass" if ok else "fail",
                             "evidence": "; ".join(w for _, w in outcomes), "factsFrom": f.sources})
        row.update(status="pass" if passed else "fail" if checkable else "manual",
                   expected=[r.label for r in resources], evidence=evidence)
        if row["status"] == "fail":
            row["fix"] = f"Use one of the community's choices: {', '.join(r.label for r in resources)}."
        results.append(row)

    declared = {e for d in fip.declarations if d.principle == "I1"
                for r in d.use.get("current", []) + d.use.get("recommended", []) for e in facts_for(r).extensions}
    ignore = config()["ignore_extensions"]
    undeclared: dict[str, list[str]] = {}
    for p in t.files:
        exts = _exts(p)
        if not exts or declared & set(exts) or exts[-1] in ignore:
            continue
        undeclared.setdefault(exts[-1], []).append(p)

    counts: dict[str, int] = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    warnings = []
    if t.object_type == "software" and "software" not in fip.object_type.lower():
        warnings.append(f"The FIP is declared for {fip.object_type.rsplit('/', 1)[-1] or 'data'}; the target is "
                        "software. Data questions (formats, data licence) may not apply to it.")
    return {
        "fip": {"label": fip.label, "kind": fip.kind, "uri": fip.uri, "version": fip.version},
        "target": t.to_dict(),
        "summary": counts,
        "undeclaredExtensions": {e: fs[:3] for e, fs in sorted(undeclared.items())},
        "warnings": warnings,
        "results": results,
    }
