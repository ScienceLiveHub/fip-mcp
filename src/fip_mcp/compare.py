"""Side-by-side comparison of several FIPs and R-FIPs, one row per FAIR principle.

Typical use: a community's As-Is FIP (current practice) next to one or more
Reference FIPs (target practice), to see per principle what has to change.

Where each resource sits comes from the nanopub network, never from this code:
- FIP: the declaration names its question, and the question its principle.
- R-FIP: the resource's FIP types `enable` or `support` principles (FIP ontology),
  grouped exactly as Nanodash shows them on the R-FIP page. Resources that only
  *support* a principle are labelled "(supports)" and can be left out.
"""
from __future__ import annotations

from .fip import RECOMMENDED, Fip
from .questions import is_principle, principle_sort_key

USES = ("current", RECOMMENDED, "planned", "replaced")
AXIS = {"data": "data", "metadata": "metadata"}


def _norm(s: str) -> str:
    return s.strip().lower()


def _entries(fip: Fip, include_supports: bool) -> tuple[dict[str, list[dict]], set[str]]:
    """principle/question key -> entries, plus the keys the FIP explicitly left open."""
    cells: dict[str, list[dict]] = {}
    left_open: set[str] = set()
    for d in fip.declarations:
        key = d.principle or d.question
        if d.no_choice:
            left_open.add(key)
            continue
        if d.relation == "supports" and not include_supports:
            continue
        for use in USES:
            for r in d.use.get(use, []):
                cells.setdefault(key, []).append({"label": r.label, "uri": r.uri, "use": use, "axis": d.axis,
                                                  "relation": d.relation or "declared"})
    return cells, left_open


def _merge(entries: list[dict]) -> list[dict]:
    """One entry per resource and use; data and metadata collapse into their union."""
    out: dict[tuple[str, str], dict] = {}
    for e in entries:
        k = (_norm(e["label"]), e["use"])
        if k not in out:
            out[k] = {**e, "axes": set(), "relations": set()}
        out[k]["axes"].add(e["axis"])
        out[k]["relations"].add(e["relation"])
    for e in out.values():
        axes, rels = e.pop("axes"), e.pop("relations")
        e.pop("axis", None)
        e["axes"] = "both" if "both" in axes or {"data", "metadata"} <= axes or len(axes) != 1 else next(iter(axes))
        # "enables" wins over "supports" when both hold for the same principle.
        e["relation"] = "declared" if "declared" in rels else "enables" if "enables" in rels else "supports"
    return sorted(out.values(), key=lambda e: (USES.index(e["use"]), e["relation"] == "supports", _norm(e["label"])))


def _text(entries: list[dict], left_open: bool) -> str:
    if not entries:
        return "— (left open)" if left_open else "—"
    parts = []
    for e in entries:
        notes = [AXIS[e["axes"]]] if e["axes"] in AXIS else []
        if e["use"] in ("planned", "replaced"):
            notes.append(e["use"])
        if e["relation"] == "supports":
            notes.append("supports")
        parts.append(f"{e['label']} ({', '.join(notes)})" if notes else e["label"])
    return ", ".join(parts)


def _row_name(key: str) -> str:
    if key.startswith("FIP-S-Question-"):
        return "Supporting: " + key.removeprefix("FIP-S-Question-").replace("-", " ")
    return "Unplaced" if key == "unplaced" else key


def compare(fips: list[Fip], names: list[str] | None = None, include_supports: bool = True,
            include_supporting_questions: bool = False) -> dict:
    """Rows = FAIR principles covered by at least one profile (FAIR order); columns = profiles."""
    names = list(names or [])
    names += [f.label for f in fips[len(names):]]
    per = [_entries(f, include_supports) for f in fips]

    keys = {k for cells, _ in per for k in cells}
    principles = sorted((k for k in keys if is_principle(k)), key=principle_sort_key)
    tail = sorted(k for k in keys if k.startswith("FIP-S-Question-")) if include_supporting_questions else []
    tail += ["unplaced"] if "unplaced" in keys else []

    rows = []
    for key in principles + tail:
        cells = []
        for cells_of, left_open in per:
            entries = _merge(cells_of.get(key, []))
            cells.append({"entries": entries, "text": _text(entries, key in left_open)})
        rows.append({"row": _row_name(key), "key": key, "isPrinciple": is_principle(key), "cells": cells})

    covered = [sum(1 for r in rows if r["isPrinciple"] and r["cells"][i]["entries"]) for i in range(len(fips))]
    notes = []
    if any(f.kind == "R-FIP" for f in fips):
        notes.append("R-FIP resources are grouped by the principles their FIP types enable or support "
                     "(FIP ontology), as on the Nanodash R-FIP page.")
        if include_supports:
            notes.append("'(supports)' = the resource supports rather than enables that principle.")
    if any(r["key"] == "unplaced" for r in rows):
        notes.append("Unplaced = recommended resources whose types enable or support no principle.")
    notes.append("'(left open)' = the FIP explicitly declared no choice; '—' = nothing declared.")
    return {
        "profiles": [{"name": n, "label": f.label, "kind": f.kind, "uri": f.uri, "version": f.version,
                      "created": f.created, "community": f.community, "caseStudy": f.case_study}
                     for n, f in zip(names, fips)],
        "principlesShown": len(principles),
        "principlesCovered": [f"{c} / {len(principles)}" for c in covered],
        "rows": rows,
        "notes": notes,
    }


def to_xlsx(result: dict, path: str) -> str:
    """Write a `compare` result as a formatted spreadsheet (needs `pip install fip-mcp[xlsx]`)."""
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    except ImportError as e:  # pragma: no cover - optional dependency
        raise RuntimeError("writing .xlsx needs openpyxl: pip install 'fip-mcp[xlsx]'") from e

    navy, grey, same = (PatternFill("solid", fgColor=c) for c in ("0F2547", "F2F2F2", "E3ECF7"))
    thin = Side(style="thin", color="BFBFBF")
    box = Border(left=thin, right=thin, top=thin, bottom=thin)
    top = Alignment(wrap_text=True, vertical="top")

    wb = Workbook()
    ws = wb.active
    ws.title = "Comparison"
    ws.append(["FAIR Principle"] + [p["name"] for p in result["profiles"]])
    for c in ws[1]:
        c.font, c.fill, c.border = Font(bold=True, color="FFFFFF"), navy, box
        c.alignment = Alignment(wrap_text=True, vertical="center")
    for r in result["rows"]:
        ws.append([r["row"]] + [c["text"] for c in r["cells"]])
        labels = [frozenset(_norm(e["label"]) for e in c["entries"]) for c in r["cells"]]
        all_same = len(set(labels)) == 1 and labels[0]
        for j, c in enumerate(ws[ws.max_row]):
            c.alignment, c.border = top, box
            if j == 0:
                c.font = Font(bold=True)
            elif str(c.value).startswith("—"):
                c.font, c.fill = Font(color="808080", italic=True), grey
            elif all_same:
                c.fill = same
    ws.append(["Principles Covered"] + result["principlesCovered"])
    for c in ws[ws.max_row]:
        c.font, c.border = Font(bold=True), box
    ws.column_dimensions["A"].width = 22
    for j in range(len(result["profiles"])):
        ws.column_dimensions[chr(ord("B") + j)].width = 42
    ws.freeze_panes = "B2"
    n = ws.max_row + 2
    for k, note in enumerate(result["notes"]):
        ws.cell(row=n + k, column=1, value=note).font = Font(italic=True, size=9)

    src = wb.create_sheet("Sources")
    cols = ["name", "label", "kind", "version", "created", "uri", "community", "caseStudy"]
    src.append(cols)
    for c in src[1]:
        c.font, c.fill = Font(bold=True, color="FFFFFF"), navy
    for p in result["profiles"]:
        src.append([p[k] for k in cols])
    for col, w in zip("ABCDEFGH", [24, 50, 8, 9, 22, 62, 50, 38]):
        src.column_dimensions[col].width = w
    wb.save(path)
    return path
