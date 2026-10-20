"""Reading a FAIR Implementation Profile into plain Python objects.

A FIP Wizard release is several nanopubs: the FIP itself, a declaration index,
one nanopub per declaration, and one per FAIR Enabling Resource (FER). This
module walks them in that order and returns one `Fip`.
"""
from __future__ import annotations

import json
import urllib.request
from dataclasses import asdict, dataclass, field
from functools import lru_cache

from rdflib import RDF, RDFS, URIRef
from rdflib.namespace import DCTERMS, SKOS

from . import nanopub
from .questions import question_info

FIP = "https://w3id.org/fair/fip/terms/"
NPX = "http://purl.org/nanopub/x/"
SCHEMA_URL = URIRef("http://schema.org/url")

# Every FER carries these; they say nothing about what kind of resource it is.
GENERIC_TYPES = {"FAIR-Enabling-Resource", "Available-FAIR-Enabling-Resource",
                 "Available-FAIR-Supporting-Resource", "FAIR-Supporting-Resource"}

USE = {
    "declares-current-use-of": "current",
    "declares-planned-use-of": "planned",
    "declares-planned-replacement-of": "replaced",
}


@dataclass
class Resource:
    uri: str
    label: str
    types: list[str] = field(default_factory=list)
    comment: str = ""
    url: str = ""
    close_match: list[str] = field(default_factory=list)


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
    label = _one(ds, s, RDFS.label).strip() or _local(uri)
    return Resource(
        uri=uri,
        label=label.split("|")[0].strip(),
        types=sorted(t for t in (_local(str(t)) for t in ds.objects(s, RDF.type) if str(t).startswith(FIP))
                     if t not in GENERIC_TYPES),
        comment=_one(ds, s, RDFS.comment).strip(),
        url=_one(ds, s, SCHEMA_URL),
        close_match=sorted(str(o) for o in ds.objects(s, SKOS.closeMatch)),
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


def load(uri: str, follow_versions: bool = True) -> Fip:
    """Load a FIP by its nanopub URI — by default its latest version."""
    chain = [nanopub.np_id(uri)]
    if follow_versions:
        _, chain = nanopub.latest(uri, FIP + "FAIR-Implementation-Profile")
    ds = nanopub.fetch(chain[-1])
    fip = None
    for s in ds.subjects(RDF.type, URIRef(FIP + "FAIR-Implementation-Profile")):
        fip = s
        break
    if fip is None:
        raise nanopub.NanopubError(f"{chain[-1]} is not a FAIR Implementation Profile")
    index = _one(ds, fip, URIRef(FIP + "has-declaration-index"))
    created = next((str(o) for o in ds.objects(None, DCTERMS.created)), "")
    decl_uris: list[str] = []
    if index:
        idx = nanopub.fetch(index)
        decl_uris = sorted({str(o) for o in idx.objects(None, URIRef(NPX + "includesElement"))})
    decls = [_declaration(u) for u in decl_uris]
    decls.sort(key=lambda d: (d.principle == "", d.question))
    return Fip(
        uri=chain[-1],
        label=_one(ds, fip, RDFS.label),
        description=_one(ds, fip, DCTERMS.description),
        version=_one(ds, fip, URIRef("https://schema.org/version")) or _one(ds, fip, URIRef("http://schema.org/version")),
        created=created,
        community=_one(ds, fip, URIRef(FIP + "declared-by")),
        case_study=_one(ds, fip, URIRef(FIP + "declared-for-case-study")),
        object_type=_one(ds, fip, URIRef(FIP + "declared-for-digital-object-type")),
        index=nanopub.np_id(index) if index else "",
        version_chain=chain,
        declarations=decls,
    )
