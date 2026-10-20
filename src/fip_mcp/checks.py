"""Deterministic checks of a target against a community's FIP.

Each declared resource is matched to a probe by its label. A probe reads only
`Target` facts and returns pass/fail with the evidence. A resource with no probe
is reported as `manual` — the agent should ask the user, never guess. A question
the community left open is reported as `no-choice`: that is a gap in the FIP,
not in the target.

A question passes if ANY of its declared resources passes: a FIP lists the
choices a community accepts, not a set that must all be present.
"""
from __future__ import annotations

import re
from collections.abc import Callable
from pathlib import PurePath

from .fip import Fip, Resource
from .target import Target

# File extensions per format, used both to probe I1-D and to spot off-profile formats.
FORMATS: dict[str, tuple[str, ...]] = {
    "NetCDF": (".nc", ".nc4", ".netcdf"),
    "FITS": (".fits", ".fit", ".fts", ".fz"),
    "TIFF": (".tif", ".tiff"),
    "Zarr": (".zarr", ".zarray", ".zattrs"),
    "HDF5": (".h5", ".hdf5", ".he5"),
    "GRIB": (".grib", ".grb", ".grib2"),
    "PNG": (".png",),
    "CSV": (".csv", ".tsv", ".tabular"),
}
DATA_FORMATS = {"NetCDF", "FITS", "TIFF", "Zarr", "HDF5", "GRIB"}
FORMAT_LABELS = [(r"netcdf|network common data form", "NetCDF"), (r"flexible image transport|^fits$", "FITS"),
                 (r"\btiff?\b", "TIFF"), (r"zarr", "Zarr"), (r"hdf5?", "HDF5"), (r"grib", "GRIB")]


def format_names(labels) -> set[str]:
    """Format names (keys of FORMATS) named by FER labels such as 'Network Common Data Form'."""
    return {name for lab in labels for pattern, name in FORMAT_LABELS if re.search(pattern, lab.lower())}

Probe = Callable[[Target], tuple[bool, str]]


def _files_with(t: Target, exts: tuple[str, ...]) -> list[str]:
    return [f for f in t.files if PurePath(f).suffix.lower() in exts or any(p.endswith(exts) for p in PurePath(f).parts)]


def _format(name: str) -> Probe:
    def probe(t: Target) -> tuple[bool, str]:
        hits = _files_with(t, FORMATS[name])
        return bool(hits), (f"{len(hits)} {name} file(s), e.g. {hits[0]}" if hits else f"no {name} files")
    return probe


def _licence(spdx: str) -> Probe:
    def probe(t: Target) -> tuple[bool, str]:
        return spdx in t.licences, f"licence(s) found: {', '.join(t.licences) or 'none'}"
    return probe


def _repository(name: str) -> Probe:
    def probe(t: Target) -> tuple[bool, str]:
        return name in t.repositories, f"repositories: {', '.join(t.repositories) or 'none (no DOI from a known repository)'}"
    return probe


def _doi(t: Target) -> tuple[bool, str]:
    return bool(t.dois), f"DOI(s): {', '.join(t.dois)}" if t.dois else "no DOI found"


def _uri(t: Target) -> tuple[bool, str]:
    ok = bool(t.dois or t.urls)
    return ok, "has DOI or URL" if ok else "no identifier found"


def _https(t: Target) -> tuple[bool, str]:
    urls = [u for u in t.urls if u]
    if not urls:
        return False, "no URLs to inspect"
    plain = [u for u in urls if u.startswith("http://")]
    return not plain, f"{len(urls)} URL(s), {len(plain)} over plain HTTP"


def _http(t: Target) -> tuple[bool, str]:
    urls = [u for u in t.urls if u]
    return bool(urls), f"{len(urls)} URL(s) over HTTP(S)"


def _open(t: Target) -> tuple[bool, str]:
    return t.access == "open", f"access: {t.access or 'unknown'}"


def _ro_crate(t: Target) -> tuple[bool, str]:
    return t.has_ro_crate, "ro-crate-metadata.json present" if t.has_ro_crate else "no ro-crate-metadata.json"


def _json_ld(t: Target) -> tuple[bool, str]:
    hits = [f for f in t.files if f.endswith((".jsonld", "ro-crate-metadata.json", "codemeta.json"))]
    return bool(hits), f"JSON-LD: {', '.join(hits[:3])}" if hits else "no JSON-LD metadata file"


def _datacite(t: Target) -> tuple[bool, str]:
    # These repositories mint their DOIs through DataCite, so their records carry DataCite metadata.
    via = [r for r in t.repositories if r in ("Zenodo", "NIRD Research Data Archive", "Figshare", "Dryad")]
    return bool(via), f"DataCite DOI minted by {', '.join(via)}" if via else "no DataCite-minting repository found"


# (label regex, probe). First match wins; order specific before general.
PROBES: list[tuple[str, Probe]] = [
    (r"netcdf cf|climate and forecast", None),          # needs reading file attributes: manual
    (r"netcdf|network common data form", _format("NetCDF")),
    (r"flexible image transport|^fits$", _format("FITS")),
    (r"\btiff?\b|ome-tiff", _format("TIFF")),
    (r"zarr", _format("Zarr")),
    (r"ro-?crate", _ro_crate),
    (r"json[- ]?ld", _json_ld),
    (r"cc[- ]?by[- ]?4\.0", _licence("CC-BY-4.0")),
    (r"^cc0", _licence("CC0-1.0")),
    (r"zenodo", _repository("Zenodo")),
    (r"nird", _repository("NIRD Research Data Archive")),
    (r"^doi$|digital object identifier", _doi),
    (r"^uri$|uniform resource identifier", _uri),
    (r"^https$", _https),
    (r"^http$", _http),
    (r"opendata|open data|open access", _open),
    (r"zmpp|zenodo metadata", _repository("Zenodo")),   # Zenodo's metadata preservation policy
    (r"datacite", _datacite),
]


def probe_for(res: Resource) -> Probe | None:
    label = res.label.lower().strip()
    for pattern, probe in PROBES:
        if re.search(pattern, label):
            return probe
    return None


def check(fip: Fip, t: Target) -> dict:
    results = []
    for qid, decls in fip.by_question().items():
        resources = [r for d in decls for r in d.use.get("current", [])]
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
            probe = probe_for(r)
            if probe is None:
                evidence.append({"resource": r.label, "result": "manual", "uri": r.url or r.uri})
                continue
            checkable = True
            ok, why = probe(t)
            passed |= ok
            evidence.append({"resource": r.label, "result": "pass" if ok else "fail", "evidence": why})
        row.update(status="pass" if passed else "fail" if checkable else "manual",
                   expected=[r.label for r in resources], evidence=evidence)
        if row["status"] == "fail":
            row["fix"] = f"Use one of the community's choices: {', '.join(r.label for r in resources)}."
        results.append(row)

    declared_formats = format_names(r.label for d in fip.declarations if d.question == "I1-D"
                                    for r in d.use.get("current", []))
    off_profile = {name: _files_with(t, exts)[:3] for name, exts in FORMATS.items()
                   if name in DATA_FORMATS and name not in declared_formats and _files_with(t, exts)}

    counts: dict[str, int] = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    warnings = []
    if t.object_type == "software" and "software" not in fip.object_type.lower():
        warnings.append(f"The FIP is declared for {fip.object_type.rsplit('/', 1)[-1] or 'data'}; the target is "
                        "software. Data questions (formats, data licence) may not apply to it.")
    return {
        "fip": {"label": fip.label, "uri": fip.uri, "version": fip.version},
        "target": t.to_dict(),
        "summary": counts,
        "offProfileFormats": off_profile,
        "warnings": warnings,
        "results": results,
    }
