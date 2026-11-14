"""What can be tested about a FAIR Enabling Resource, and where each fact comes from.

Facts are gathered, in this order, from:
1. the user's config file, then the packaged `data/resources.toml` (explicit
   entries, each with its source);
2. the resource's own nanopub: links (skos:exactMatch / closeMatch, rdfs:seeAlso)
   to Wikidata or SPDX, and its schema:url;
3. public registries by the resource's label: Wikidata (only an unambiguous
   exact label/alias match that carries the property) and the SPDX list.

Every fact records its source, so a check can say why it passed or failed. A
resource with no testable fact is checked by hand (`manual`).
"""
from __future__ import annotations

import os
import re
import sys
from dataclasses import asdict, dataclass, field
from functools import lru_cache
from importlib.resources import files
from pathlib import Path

from . import lookup
from .fip import Resource

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover
    import tomli as tomllib

USER_CONFIG = Path(os.environ.get("FIP_MCP_RESOURCES", Path.home() / ".config" / "fip-mcp" / "resources.toml"))
FACT_FIELDS = ("files", "extensions", "media_types", "url_scheme", "access", "hosts", "registration_agency",
               "spdx", "id_patterns")


@dataclass
class Facts:
    files: list[str] = field(default_factory=list)
    extensions: list[str] = field(default_factory=list)
    media_types: list[str] = field(default_factory=list)
    url_scheme: str = ""
    access: str = ""
    hosts: list[str] = field(default_factory=list)          # explicit: object must be deposited there
    registration_agency: str = ""
    spdx: str = ""
    id_patterns: list[str] = field(default_factory=list)
    web_hosts: list[str] = field(default_factory=list)       # hosts of schema:url and links (a registry's own site)
    sources: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def empty(self) -> bool:
        return not any(getattr(self, f) for f in FACT_FIELDS) and not self.web_hosts

    def to_dict(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v}

    def for_principle(self, principle: str) -> dict:
        """Only the facts a check uses for this principle (see checks._tests)."""
        d = self.to_dict()
        if principle != "R1.1":
            d.pop("spdx", None)          # SPDX also names non-licences, e.g. "NetCDF"
            d["sources"] = [s for s in d.get("sources", []) if not s.startswith("SPDX")]
        if principle != "F4":
            d.pop("web_hosts", None)
        if principle not in ("F1", "F3"):
            d.pop("id_patterns", None)
        return {k: v for k, v in d.items() if v}


@lru_cache(maxsize=None)
def config() -> dict:
    """Merged config: user entries first (they win), then the packaged defaults."""
    entries, ignore = [], set()
    texts = []
    if USER_CONFIG.exists():
        texts.append((str(USER_CONFIG), USER_CONFIG.read_text()))
    texts.append(("fip-mcp data/resources.toml", files("fip_mcp").joinpath("data/resources.toml").read_text()))
    for origin, text in texts:
        data = tomllib.loads(text)
        for e in data.get("resource", []):
            entries.append({**e, "_origin": origin})
        ignore |= {x.lower().lstrip(".") for x in data.get("ignore", {}).get("extensions", [])}
    return {"resources": entries, "ignore_extensions": ignore}


def _names(res: Resource) -> list[str]:
    raw = [res.label, *res.label_variants]
    return [n.strip() for n in raw if n and n.strip()]


def _config_entry(res: Resource) -> dict | None:
    names = {n.lower() for n in _names(res)}
    for e in config()["resources"]:
        for m in e.get("match", []):
            if m.lower() in names or m == res.uri:
                return e
    return None


def _wikidata_qids(res: Resource) -> list[str]:
    return sorted({m.group(1) for u in res.links if (m := re.search(r"wikidata\.org/(?:entity|wiki)/(Q\d+)", u))})


_FACTS: dict[str, Facts] = {}


def facts_for(res: Resource) -> Facts:
    if res.uri not in _FACTS:
        _FACTS[res.uri] = _resolve(res)
    return _FACTS[res.uri]


def _resolve(res: Resource) -> Facts:
    f = Facts()

    entry = _config_entry(res)
    if entry:
        for k in FACT_FIELDS:
            if k in entry:
                setattr(f, k, entry[k] if isinstance(getattr(f, k), str) else list(entry[k]))
        f.sources.append(f"config ({entry['_origin']}): {entry.get('source', 'no source given')}")

    web = [u for u in [res.url, *res.links] if u.startswith("http")]
    if web:
        f.web_hosts = sorted({lookup.host(u) for u in web})
        f.sources.append(f"web addresses in the resource nanopub: {', '.join(web)}")

    try:
        _add_licence(res, f)
        _add_wikidata(res, f, (entry or {}).get("wikidata", ""))
    except lookup.LookupError_ as e:
        f.notes.append(f"lookup failed: {e}")
    return f


def _add_licence(res: Resource, f: Facts) -> None:
    if f.spdx:
        return
    for u in res.links:
        if sid := lookup.spdx_from_url(u):
            f.spdx = sid
            f.sources.append(f"SPDX licence {sid}, via link {u}")
            return
    for n in _names(res):
        if sid := lookup.spdx_from_name(n):
            f.spdx = sid
            f.sources.append(f"SPDX licence {sid}, matched by name {n!r}")
            return


def _add_wikidata(res: Resource, f: Facts, configured: str = "") -> None:
    if f.extensions or f.media_types or f.id_patterns:
        return
    linked = _wikidata_qids(res)
    if configured:
        claims = lookup.wikidata_claims([configured])
        how = "named in the config entry"
    elif linked:
        claims = lookup.wikidata_claims(linked)
        how = "linked from the resource nanopub"
    else:
        candidates = sorted({q for n in _names(res) for q in lookup.wikidata_search(n)})
        if not candidates:
            return
        claims = lookup.wikidata_claims(candidates)
        claims = {q: c for q, c in claims.items() if c["extensions"] or c["media_types"] or c["id_patterns"]}
        if len(claims) > 1:
            f.notes.append("ambiguous Wikidata match by label: " + ", ".join(
                f"{q} ({c['label']})" for q, c in sorted(claims.items())) + "; add a skos:exactMatch or a config entry")
            return
        how = "matched by label; add skos:exactMatch to the resource nanopub to make it explicit"
    for qid, c in sorted(claims.items()):
        f.extensions += [e.lower().lstrip(".") for e in c["extensions"]]
        f.media_types += c["media_types"]
        f.id_patterns += c["id_patterns"]
        if c["extensions"] or c["media_types"] or c["id_patterns"]:
            f.sources.append(f"Wikidata {qid} ({c['label']}), {how}")
