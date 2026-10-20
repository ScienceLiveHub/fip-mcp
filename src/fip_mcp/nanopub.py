"""Fetching nanopublications and following their version chains.

Nanopubs carry trusty URIs, so a fetched nanopub never changes: it is cached on
disk for good. What *does* change is whether a newer version exists, so the
supersedes lookup is never cached.
"""
from __future__ import annotations

import hashlib
import json
import os
import urllib.parse
import urllib.request
from pathlib import Path

from rdflib import Dataset, URIRef

NPX = "http://purl.org/nanopub/x/"
QUERY_ENDPOINT = os.environ.get("FIP_MCP_SPARQL", "https://query.knowledgepixels.com/repo/full")
CACHE_DIR = Path(os.environ.get("FIP_MCP_CACHE", Path.home() / ".cache" / "fip-mcp"))
TIMEOUT = 30


class NanopubError(RuntimeError):
    pass


def np_id(uri: str) -> str:
    """The nanopub's own URI: drop any fragment or sub-path after the RA… hash."""
    uri = uri.split("#", 1)[0]
    head, _, tail = uri.rpartition("/np/")
    if not head:
        return uri
    return f"{head}/np/{tail.split('/', 1)[0]}"


def _get(url: str, accept: str) -> bytes:
    req = urllib.request.Request(url, headers={"Accept": accept, "User-Agent": "fip-mcp"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return resp.read()
    except Exception as e:  # noqa: BLE001 - surfaced verbatim to the agent
        raise NanopubError(f"GET {url} failed: {e}") from e


def fetch(uri: str) -> Dataset:
    """Parse one nanopub (all four graphs) into a Dataset, via the disk cache."""
    uri = np_id(uri)
    path = CACHE_DIR / (hashlib.sha1(uri.encode()).hexdigest() + ".trig")
    if path.exists():
        data = path.read_bytes()
    else:
        data = _get(uri, "application/trig")
        if not data.lstrip().startswith((b"@prefix", b"<", b"PREFIX")):
            raise NanopubError(f"{uri} did not return TriG")
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    ds = Dataset(default_union=True)  # nanopub content lives in named graphs
    ds.parse(data=data, format="trig")
    return ds


def sparql(query: str) -> list[dict]:
    url = QUERY_ENDPOINT + "?" + urllib.parse.urlencode({"query": query})
    rows = json.loads(_get(url, "application/sparql-results+json"))["results"]["bindings"]
    return [{k: v["value"] for k, v in row.items()} for row in rows]


def successors(uri: str) -> list[str]:
    """Nanopubs that declare they supersede `uri` and are not themselves retracted."""
    rows = sparql(
        "PREFIX npx: <%s> SELECT DISTINCT ?new WHERE { GRAPH ?g { ?new npx:supersedes <%s> } "
        "FILTER NOT EXISTS { GRAPH ?h { ?x npx:invalidates ?new } } }" % (NPX, np_id(uri))
    )
    return sorted({r["new"] for r in rows})


def latest(uri: str, rdf_type: str, max_hops: int = 20) -> tuple[str, list[str]]:
    """Follow the supersedes chain, keeping only successors of `rdf_type`.

    The FIP Wizard republishes a FIP *and* its declaration index together, and
    both supersede their predecessors — so the old FIP nanopub has two
    successors, only one of which is a FIP. Filtering on type picks the right one.
    Returns (latest uri, chain walked).
    """
    chain = [np_id(uri)]
    for _ in range(max_hops):
        nxt = [u for u in successors(chain[-1]) if has_type(u, rdf_type)]
        if not nxt:
            break
        if len(nxt) > 1:
            raise NanopubError(f"{chain[-1]} has {len(nxt)} competing successors: {nxt}")
        chain.append(nxt[0])
    return chain[-1], chain


def has_type(uri: str, rdf_type: str) -> bool:
    from rdflib.namespace import RDF

    return any(True for _ in fetch(uri).triples((None, RDF.type, URIRef(rdf_type))))
