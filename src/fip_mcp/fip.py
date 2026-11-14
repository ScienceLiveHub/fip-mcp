"""Reading a FAIR Implementation Profile into plain Python objects.

A FIP Wizard release is several nanopubs: the FIP itself, a declaration index,
one nanopub per declaration, and one per FAIR Enabling Resource (FER). This
module walks them in that order and returns one `Fip`.

A Reference FIP (R-FIP) is published differently: the R-FIP nanopub has no
declaration index, and each recommended resource is its own nanopub
(`<resource> fip:recommended-by <community>`) derived from the R-FIP. Those do
not name a FIP question. The principle comes from the FIP ontology on the
network: each FIP type nanopub states which principles the type `fip:enables`
or `fip:supports` (the same relations Nanodash groups the R-FIP page by).
"""
from __future__ import annotations

import json
import urllib.request
from dataclasses import asdict, dataclass, field
from functools import lru_cache

from rdflib import RDF, RDFS, URIRef
from rdflib.namespace import DCTERMS, SKOS

from . import nanopub
from .questions import principle_text, question_info

FIP = "https://w3id.org/fair/fip/terms/"
NPX = "http://purl.org/nanopub/x/"
FIP_TYPE = FIP + "FAIR-Implementation-Profile"
RFIP_TYPE = FIP + "Reference-FAIR-Implementation-Profile"
SCHEMA_URL = URIRef("http://schema.org/url")

USE = {
    "declares-current-use-of": "current",
    "declares-planned-use-of": "planned",
    "declares-planned-replacement-of": "replaced",
}
# An R-FIP's resources are what the community recommends, i.e. its target practice.
RECOMMENDED = "recommended"


@dataclass
class Resource:
    uri: str
    label: str
    types: list[str] = field(default_factory=list)
    comment: str = ""
    url: str = ""
    close_match: list[str] = field(default_factory=list)
    label_variants: list[str] = field(default_factory=list)   # other parts of "A | B" labels
    links: list[str] = field(default_factory=list)            # exactMatch, closeMatch, seeAlso, description source


@dataclass
class Declaration:
    uri: str
    question: str          # e.g. "I1-D", "F2", "FIP-S-Question-Web-API"
    principle: str         # e.g. "I1"; "" for supplementary questions
    axis: str              # "data", "metadata", "both" or "supporting"
    text: str              # the question, in words
    no_choice: bool
    use: dict[str, list[Resource]] = field(default_factory=dict)   # current/planned/replaced
    considerations: str = ""
    case_study: str = ""
    placement: str = "declared"   # "declared" (FIP names the question) or "ontology" (R-FIP, via its types)
    relation: str = ""            # R-FIP only: the resource "enables" or "supports" the principle


@dataclass
class Fip:
    uri: str
    label: str
    description: str
    version: str
    created: str
    community: str
    case_study: str
    object_type: str
    index: str
    version_chain: list[str]
    declarations: list[Declaration]
    kind: str = "FIP"             # "FIP" or "R-FIP"

    def to_dict(self) -> dict:
        return asdict(self)

    def by_question(self) -> dict[str, list[Declaration]]:
        out: dict[str, list[Declaration]] = {}
        for d in self.declarations:
            out.setdefault(d.question, []).append(d)
        return out


def _one(ds, s, p) -> str:
    for o in ds.objects(s, p):
        return str(o)
    return ""


def _local(uri: str) -> str:
    return uri.rsplit("/", 1)[-1].rsplit("#", 1)[-1]


@lru_cache(maxsize=None)
def resource(uri: str) -> Resource:
    """Describe a FER from its own nanopub, or a FAIRsharing DOI from DataCite."""
    if uri.startswith("https://doi.org/10.25504/FAIRsharing."):
        return Resource(uri=uri, label=_fairsharing_title(uri), types=["FAIRsharing record"], url=uri)
    try:
        ds = nanopub.fetch(uri)
    except nanopub.NanopubError:
        return Resource(uri=uri, label=_local(uri))
    s = URIRef(uri)
    # Some FERs are cited as …/RAxxx/Name although the subject is …/RAxxx#Name.
    if not any(True for _ in ds.triples((s, None, None))):
        alt = [x for x in ds.subjects(RDFS.label, None) if _local(str(x)) == _local(uri)]
        s = alt[0] if alt else s
    parts = [p.strip() for p in (_one(ds, s, RDFS.label).strip() or _local(uri)).split("|") if p.strip()]
    links = {str(o) for p in (SKOS.exactMatch, SKOS.closeMatch, RDFS.seeAlso, URIRef(FIP + "has-description-source"))
             for o in ds.objects(s, p)}
    return Resource(
        uri=uri,
        label=parts[0] if parts else _local(uri),
        types=sorted(_local(str(t)) for t in ds.objects(s, RDF.type) if str(t).startswith(FIP)),
        comment=_one(ds, s, RDFS.comment).strip(),
        url=_one(ds, s, SCHEMA_URL) or _one(ds, s, URIRef("https://schema.org/url")),
        close_match=sorted(str(o) for o in ds.objects(s, SKOS.closeMatch)),
        label_variants=parts[1:],
        links=sorted(links),
    )


def _fairsharing_title(doi_url: str) -> str:
    req = urllib.request.Request(doi_url, headers={"Accept": "application/vnd.citationstyles.csl+json"})
    try:
        with urllib.request.urlopen(req, timeout=nanopub.TIMEOUT) as r:
            title = json.loads(r.read()).get("title", "")
    except Exception:  # noqa: BLE001 - a label is a nicety, not a requirement
        return doi_url.rsplit("/", 1)[-1]
    return title.removeprefix("FAIRsharing record for: ") or doi_url.rsplit("/", 1)[-1]


def _declaration(uri: str) -> Declaration:
    ds = nanopub.fetch(uri)
    decl = None
    for s in ds.subjects(URIRef(FIP + "refers-to-question"), None):
        decl = s
        break
    if decl is None:
        raise nanopub.NanopubError(f"{uri} is not a FIP declaration")
    q = _local(_one(ds, decl, URIRef(FIP + "refers-to-question")))
    qid = q.removeprefix("FIP-Question-")
    principle, axis, text = question_info(qid)
    types = {_local(str(t)) for t in ds.objects(decl, RDF.type)}
    use: dict[str, list[Resource]] = {}
    for pred, kind in USE.items():
        for o in ds.objects(decl, URIRef(FIP + pred)):
            use.setdefault(kind, []).append(resource(str(o)))
    return Declaration(
        uri=nanopub.np_id(uri),
        question=qid,
        principle=principle,
        axis=axis,
        text=text,
        no_choice=any("No-Choice" in t for t in types) or not use,
        use=use,
        considerations=_one(ds, decl, URIRef(FIP + "considerations")).strip(),
        case_study=_one(ds, decl, URIRef(FIP + "declared-for-case-study")),
    )


def profile_kind(uri: str) -> str:
    """"FIP" or "R-FIP" for a profile nanopub; raises if it is neither."""
    if nanopub.has_type(uri, FIP_TYPE):
        return "FIP"
    if nanopub.has_type(uri, RFIP_TYPE):
        return "R-FIP"
    raise nanopub.NanopubError(f"{nanopub.np_id(uri)} is neither a FAIR Implementation Profile nor a Reference FIP")


def load(uri: str, follow_versions: bool = True) -> Fip:
    """Load a FIP or R-FIP by its nanopub URI — by default its latest version."""
    kind = profile_kind(uri)
    rdf_type = FIP_TYPE if kind == "FIP" else RFIP_TYPE
    chain = [nanopub.np_id(uri)]
    if follow_versions:
        _, chain = nanopub.latest(uri, rdf_type)
    ds = nanopub.fetch(chain[-1])
    subject = next(iter(ds.subjects(RDF.type, URIRef(rdf_type))), None)
    if subject is None:
        raise nanopub.NanopubError(f"{chain[-1]} is not a {kind}")
    if kind == "FIP":
        index = _one(ds, subject, URIRef(FIP + "has-declaration-index"))
        decl_uris: list[str] = []
        if index:
            idx = nanopub.fetch(index)
            decl_uris = sorted({str(o) for o in idx.objects(None, URIRef(NPX + "includesElement"))})
        decls = [_declaration(u) for u in decl_uris]
    else:
        index = ""
        decls = _rfip_declarations(chain[-1])
    decls.sort(key=lambda d: (d.principle == "", d.question))
    return Fip(
        uri=chain[-1],
        label=_one(ds, subject, RDFS.label),
        description=_one(ds, subject, DCTERMS.description),
        version=_one(ds, subject, URIRef("https://schema.org/version"))
        or _one(ds, subject, URIRef("http://schema.org/version")),
        created=next((str(o) for o in ds.objects(None, DCTERMS.created)), ""),
        community=_one(ds, subject, URIRef(FIP + "declared-by")),
        case_study=_one(ds, subject, URIRef(FIP + "declared-for-case-study")),
        object_type=_one(ds, subject, URIRef(FIP + "declared-for-digital-object-type")),
        index=nanopub.np_id(index) if index else "",
        version_chain=chain,
        declarations=decls,
        kind=kind,
    )


RFIP_SPARQL = """
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX fip: <https://w3id.org/fair/fip/terms/>
PREFIX npx: <http://purl.org/nanopub/x/>
PREFIX np: <http://www.nanopub.org/nschema#>
PREFIX npa: <http://purl.org/nanopub/admin/>
SELECT DISTINCT ?decl ?fsr ?principle ?rel WHERE {
  GRAPH ?p { ?a prov:wasDerivedFrom|fip:wasDerivedFrom <%s> }
  GRAPH ?a { ?fsr fip:recommended-by ?c }
  BIND(IRI(REPLACE(STR(?a), "/assertion$", "")) AS ?decl)
  FILTER NOT EXISTS { GRAPH ?h { ?x npx:invalidates ?decl } }
  OPTIONAL {
    GRAPH npa:graph { ?fsrnp npx:introduces|npx:describes ?fsr ; npx:hasNanopubType ?type .
                      FILTER NOT EXISTS { ?x2 npx:invalidates ?fsrnp } }
    FILTER(STRSTARTS(STR(?type), "https://w3id.org/fair/fip/terms/"))
    GRAPH npa:graph { ?tnp npx:introduces ?type ; np:hasAssertion ?ta .
                      FILTER NOT EXISTS { ?x3 npx:invalidates ?tnp } }
    GRAPH ?ta { ?type ?rel ?principle . VALUES ?rel { fip:enables fip:supports } }
  }
}"""


def _rfip_declarations(rfip_np: str) -> list[Declaration]:
    """One declaration per (resource, principle, relation).

    Recommendations are the nanopubs derived from the R-FIP nanopub (latest
    versions only); each resource's principles are those its FIP types enable
    or support, as stated by the type nanopubs of the FIP ontology.
    """
    rows = nanopub.sparql(RFIP_SPARQL % nanopub.np_id(rfip_np))
    out = []
    for r in rows:
        principle = _local(r["principle"]) if r.get("principle") else ""
        res = resource(r["fsr"])
        if principle:
            text, axis = principle_text(principle) or principle, "both"
        else:
            text, axis = "Recommended resource whose FIP types enable or support no FAIR principle", "unknown"
        out.append(Declaration(
            uri=r["decl"], question=principle or "unplaced", principle=principle, axis=axis, text=text,
            no_choice=False, use={RECOMMENDED: [res]}, placement="ontology",
            relation=_local(r["rel"]) if r.get("rel") else ""))
    return out
