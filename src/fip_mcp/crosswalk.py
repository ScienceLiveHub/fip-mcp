"""What changes when an object moves from one community's FIP to another's."""
from __future__ import annotations

from .checks import format_names
from .fip import Fip

# Known consequences of moving data between formats. Deterministic, deliberately short.
FORMAT_NOTES = {
    ("NetCDF", "TIFF"): "Export one variable/time slice as a 2-D raster; CF attributes (units, coordinates, "
                        "history) are not carried in a plain TIFF and must be recorded elsewhere.",
    ("TIFF", "NetCDF"): "Wrap the raster with CF coordinates and units; band meaning must be added by hand.",
    ("FITS", "TIFF"): "FITS headers (WCS, calibration, provenance) are lost in a plain TIFF.",
    ("TIFF", "FITS"): "World coordinates and calibration must be written into the FITS header.",
    ("FITS", "NetCDF"): "Map the FITS WCS to CF coordinates; header keywords need explicit attributes.",
    ("NetCDF", "FITS"): "Map CF coordinates to a FITS WCS; only rectilinear grids map cleanly.",
}


def _choices(fip: Fip) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for qid, decls in fip.by_question().items():
        res = [r for d in decls for r in d.use.get("current", [])]
        out[qid] = {"principle": decls[0].principle, "asks": decls[0].text,
                    "labels": sorted({r.label for r in res})}
    return out


def crosswalk(source: Fip, target: Fip) -> dict:
    a, b = _choices(source), _choices(target)
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
        if qid == "I1-D":
            notes = [FORMAT_NOTES[(x, y)] for x in format_names(sa["labels"]) for y in format_names(sb["labels"])
                     if (x, y) in FORMAT_NOTES]
            if notes:
                row["conversion"] = notes
        rows.append(row)
    counts: dict[str, int] = {}
    for r in rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    return {"source": source.label, "target": target.label, "summary": counts,
            "changes": [r for r in rows if r["status"] in ("differs", "overlap", "only-target-chose")],
            "rows": rows}
