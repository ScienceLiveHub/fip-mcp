"""Public registries that hold the facts a check needs, so fip-mcp does not have to.

- Wikidata: file extensions (P1195), media types (P1163) and identifier patterns
  (P1793) of formats and identifier schemes.
- SPDX License List: licence identifiers, names and canonical URLs.
- DataCite: which repository (DataCite client) minted a DOI, and its URL.
- doi.org: the registration agency of a DOI.

Answers change slowly but do change, so they are cached on disk for
FIP_MCP_LOOKUP_TTL_DAYS (default 30), unlike nanopubs, which are cached for good.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import time
import urllib.parse
import urllib.request

from . import nanopub

TTL = float(os.environ.get("FIP_MCP_LOOKUP_TTL_DAYS", "30")) * 86400
CACHE = nanopub.CACHE_DIR / "lookups"
USER_AGENT = "fip-mcp (https://github.com/ScienceLiveHub/fip-mcp)"
WIKIDATA_API = "https://www.wikidata.org/w/api.php"
SPDX_LIST = "https://spdx.org/licenses/licenses.json"
DATACITE_API = "https://api.datacite.org"


class LookupError_(RuntimeError):
    pass


def get_json(url: str) -> object:
    """GET a JSON document through the TTL disk cache."""
    path = CACHE / (hashlib.sha1(url.encode()).hexdigest() + ".json")
    if path.exists() and time.time() - path.stat().st_mtime < TTL:
        return json.loads(path.read_text())
    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=nanopub.TIMEOUT) as r:
            data = json.loads(r.read())
    except Exception as e:  # noqa: BLE001 - surfaced as "could not look up"
        raise LookupError_(f"GET {url} failed: {e}") from e
    CACHE.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data))
    return data


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


# --- Wikidata -----------------------------------------------------------------------

WD_PROPS = {"extensions": "P1195", "media_types": "P1163", "id_patterns": "P1793"}


def wikidata_claims(qids: list[str]) -> dict[str, dict[str, list[str]]]:
    """{QID: {"extensions": [...], "media_types": [...], "id_patterns": [...], "label": str}}."""
    out: dict[str, dict] = {}
    for i in range(0, len(qids), 50):
        batch = qids[i:i + 50]
        data = get_json(f"{WIKIDATA_API}?" + urllib.parse.urlencode(
            {"action": "wbgetentities", "format": "json", "props": "claims|labels", "languages": "en",
             "ids": "|".join(batch)}))
        for qid, ent in data.get("entities", {}).items():
            claims = ent.get("claims", {})
            row = {k: [str(c["mainsnak"]["datavalue"]["value"]) for c in claims.get(p, [])
                       if c.get("mainsnak", {}).get("datavalue")]
                   for k, p in WD_PROPS.items()}
            row["label"] = ent.get("labels", {}).get("en", {}).get("value", qid)
            out[qid] = row
    return out


def wikidata_search(label: str) -> list[str]:
    """QIDs whose English label or alias is exactly `label` (case-insensitive)."""
    data = get_json(f"{WIKIDATA_API}?" + urllib.parse.urlencode(
        {"action": "wbsearchentities", "format": "json", "language": "en", "type": "item", "limit": "20",
         "search": label}))
    return [x["id"] for x in data.get("search", []) if x.get("match", {}).get("text", "").lower() == label.lower()]


# --- SPDX ---------------------------------------------------------------------------

def spdx_licences() -> list[dict]:
    return get_json(SPDX_LIST)["licenses"]


def _url_key(u: str) -> str:
    u = re.sub(r"^https?://(www\.)?", "", u.strip().lower()).rstrip("/")
    return re.sub(r"/(legalcode|deed\.[a-z-]+)$", "", u)


def spdx_from_url(url: str) -> str:
    """SPDX id for an spdx.org/licenses/<id> link or any URL the SPDX list gives for a licence."""
    m = re.match(r"https?://spdx\.org/licenses/([^/.]+)", url)
    if m:
        return m.group(1)
    key = _url_key(url)
    for lic in spdx_licences():
        if any(_url_key(u) == key for u in lic.get("seeAlso", [])):
            return lic["licenseId"]
    return ""


def spdx_from_name(text: str) -> str:
    """SPDX id whose id or full name equals `text` (punctuation and case ignored)."""
    key = norm(text)
    if not key:
        return ""
    for lic in spdx_licences():
        if key in (norm(lic["licenseId"]), norm(lic["name"])):
            return lic["licenseId"]
    return ""


def spdx_in_text(text: str) -> str:
    """SPDX id of the longest licence name found in a licence text (e.g. a LICENSE file)."""
    key = norm(text)
    best = ""
    best_len = 0
    for lic in spdx_licences():
        n = norm(lic["name"])
        if len(n) > best_len and len(n) >= 6 and n in key:
            best, best_len = lic["licenseId"], len(n)
    return best


# --- DOIs ---------------------------------------------------------------------------

def doi_agency(doi: str) -> str:
    """Registration agency of a DOI ("DataCite", "Crossref", ...), or ""."""
    try:
        data = get_json("https://doi.org/ra/" + urllib.parse.quote(doi, safe="/"))
    except LookupError_:
        return ""
    return (data[0] if isinstance(data, list) and data else {}).get("RA", "")


def datacite_repository(doi: str) -> dict:
    """{"name", "url"} of the DataCite client (repository) that minted the DOI, or {}."""
    try:
        data = get_json(f"{DATACITE_API}/dois/{urllib.parse.quote(doi, safe='/')}?include=client")
    except LookupError_:
        return {}
    for inc in data.get("included", []):
        if inc.get("type") == "clients":
            a = inc.get("attributes", {})
            return {"name": a.get("name", ""), "url": a.get("url", "")}
    return {}


def host(url: str) -> str:
    return re.sub(r"^www\.", "", urllib.parse.urlparse(url).netloc.lower())
