"""Facts about the thing being checked: a local folder or a Zenodo record.

Only facts that can be read without judgement are collected here — identifiers,
licences, file names, presence of an RO-Crate. Whether those facts satisfy a
community's FIP is decided in `checks.py`.
"""
from __future__ import annotations

import json
import re
import urllib.request
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .nanopub import TIMEOUT

SKIP_DIRS = {".git", ".venv", "venv", "node_modules", ".pixi", "__pycache__", "_build", ".snakemake", "_site"}
MAX_FILES = 5000

# Licence spellings seen in LICENSE files, CITATION.cff, codemeta and Zenodo, to one id.
LICENCES = [
    (r"cc[- ]?by[- ]?4\.0|creative commons attribution 4\.0|creativecommons\.org/licenses/by/4\.0", "CC-BY-4.0"),
    (r"cc0|creative commons zero|publicdomain/zero/1\.0", "CC0-1.0"),
    (r"\bmit\b", "MIT"),
    (r"apache", "Apache-2.0"),
    (r"bsd-3|bsd 3", "BSD-3-Clause"),
    (r"gpl-3|gnu general public license v3|version 3, 29 june 2007", "GPL-3.0"),
]


@dataclass
class Target:
    ref: str
    kind: str                                    # "local" or "zenodo"
    title: str = ""
    object_type: str = ""                        # e.g. "dataset", "software"
    dois: list[str] = field(default_factory=list)
    repositories: list[str] = field(default_factory=list)
    licences: list[str] = field(default_factory=list)
    access: str = ""                             # "open", "restricted", … ; "" = unknown
    files: list[str] = field(default_factory=list)
    urls: list[str] = field(default_factory=list)
    has_ro_crate: bool = False
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["files"] = d["files"][:50] + ([f"… {len(self.files) - 50} more"] if len(self.files) > 50 else [])
        return d


def normalise_licence(text: str) -> str:
    t = text.lower()
    for pattern, spdx in LICENCES:
        if re.search(pattern, t):
            return spdx
    return text.strip()


def repository_for_doi(doi: str) -> str:
    prefix = doi.lower().split("/", 1)[0]
    return {"10.5281": "Zenodo", "10.11582": "NIRD Research Data Archive", "10.6084": "Figshare",
            "10.5061": "Dryad"}.get(prefix, "")


def load(ref: str) -> Target:
    """`ref` is a local path, a Zenodo record URL/id, or a Zenodo DOI."""
    m = re.search(r"zenodo\.(?:org/(?:records?|api/records)/)?(\d+)", ref) or re.fullmatch(r"\d{5,}", ref.strip())
    if m and not Path(ref).exists():
        return _zenodo(m.group(1) if m.lastindex else m.group(0))
    p = Path(ref).expanduser()
    if p.is_dir():
        return _local(p)
    raise ValueError(f"{ref!r} is neither an existing folder nor a Zenodo record")


def _zenodo(recid: str) -> Target:
    req = urllib.request.Request(f"https://zenodo.org/api/records/{recid}", headers={"User-Agent": "fip-mcp"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        rec = json.loads(r.read())
    md = rec.get("metadata", {})
    t = Target(ref=f"https://zenodo.org/records/{rec['id']}", kind="zenodo", title=md.get("title", ""))
    t.object_type = (md.get("resource_type") or {}).get("type", "")
    t.dois = [d for d in (rec.get("doi"), rec.get("conceptdoi")) if d]
    t.repositories = ["Zenodo"]
    lic = (md.get("license") or {}).get("id", "")
    t.licences = [normalise_licence(lic)] if lic else []
    t.access = md.get("access_right", "")
    t.files = [f["key"] for f in rec.get("files", [])]
    t.urls = [rec.get("links", {}).get("self_html", ""), *(f.get("links", {}).get("self", "") for f in rec.get("files", []))]
    t.has_ro_crate = any(Path(f).name == "ro-crate-metadata.json" for f in t.files)
    if str(rec["id"]) != str(recid):
        t.notes.append(f"Zenodo resolved {recid} to record {rec['id']} (latest version).")
    return t


def _local(root: Path) -> Target:
    t = Target(ref=str(root.resolve()), kind="local", title=root.name)
    for path in sorted(root.rglob("*")):
        if any(part in SKIP_DIRS for part in path.relative_to(root).parts):
            continue
        if path.is_file():
            t.files.append(str(path.relative_to(root)))
            if len(t.files) >= MAX_FILES:
                t.notes.append(f"Stopped listing files at {MAX_FILES}.")
                break
    t.has_ro_crate = (root / "ro-crate-metadata.json").exists()

    cff = root / "CITATION.cff"
    if cff.exists():
        text = cff.read_text(errors="replace")
        t.dois += re.findall(r"^doi:\s*[\"']?(10\.\d{4,9}/[^\s\"']+)", text, re.M)
        t.licences += [normalise_licence(x) for x in re.findall(r"^license:\s*[\"']?([^\s\"']+)", text, re.M)]
        t.object_type = t.object_type or ("software" if re.search(r"^type:\s*software", text, re.M) else "")
    for name in ("LICENSE", "LICENSE.md", "LICENSE.txt", "LICENCE"):
        lic = root / name
        if lic.exists():
            t.licences.append(normalise_licence(lic.read_text(errors="replace")[:400]))
            break
    codemeta = root / "codemeta.json"
    if codemeta.exists():
        try:
            cm = json.loads(codemeta.read_text())
            if cm.get("license"):
                t.licences.append(normalise_licence(str(cm["license"])))
            t.urls += [str(cm[k]) for k in ("codeRepository", "url") if cm.get(k)]
            t.object_type = t.object_type or "software"
        except json.JSONDecodeError:
            t.notes.append("codemeta.json is not valid JSON.")
    t.dois = sorted(set(t.dois))
    t.licences = sorted(set(t.licences))
    t.repositories = sorted({r for d in t.dois if (r := repository_for_doi(d))})
    return t
