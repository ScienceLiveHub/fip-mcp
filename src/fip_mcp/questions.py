"""FIP questions and FAIR principles, read from the FIP ontology on the nanopub network.

Nothing is hard-coded here: a question's principle and wording come from its
term nanopub (`https://w3id.org/fair/fip/terms/FIP-Question-<id>`:
`fip:refers-to-principle`, `skos:definition`), and a principle's wording from
`https://w3id.org/fair/principles/terms/<id>`. Terms are immutable nanopubs and
are cached on disk like any other.

Ids are those of the FIP Wizard; by its naming convention `-D` asks about data,
`-MD` about metadata, no suffix about both, and `FIP-S-Question-…` about
supporting services. A question the ontology does not define keeps its id as
text and no principle; it is reported, never filled in.
"""
from __future__ import annotations

import re
from functools import lru_cache

from rdflib import URIRef
from rdflib.namespace import SKOS

from . import nanopub

FIP_TERMS = "https://w3id.org/fair/fip/terms/"
PRINCIPLE_TERMS = "https://w3id.org/fair/principles/terms/"
_PRINCIPLE_ID = re.compile(r"^[FAIR]\d+(\.\d+)*$")


def _local(uri: str) -> str:
    return uri.rsplit("/", 1)[-1].rsplit("#", 1)[-1]


def _axis(qid: str) -> str:
    if qid.startswith("FIP-S-Question-"):
        return "supporting"
    return "data" if qid.endswith("-D") else "metadata" if qid.endswith("-MD") else "both"


@lru_cache(maxsize=None)
def question_info(qid: str) -> tuple[str, str, str]:
    """(principle, axis, question text) for a FIP Wizard question id, from the ontology."""
    term = qid if qid.startswith("http") else FIP_TERMS + (qid if qid.startswith("FIP-") else f"FIP-Question-{qid}")
    qid = _local(term).removeprefix("FIP-Question-")
    try:
        ds = nanopub.fetch(term)
    except nanopub.NanopubError:
        return "", _axis(qid), qid
    s = URIRef(term)
    principle = next((_local(str(o)) for o in ds.objects(s, URIRef(FIP_TERMS + "refers-to-principle"))), "")
    text = next((str(o) for o in ds.objects(s, SKOS.definition)), qid)
    return principle, _axis(qid), text


@lru_cache(maxsize=None)
def principle_text(principle: str) -> str:
    """The FAIR principle's own wording, e.g. I1 -> "(meta)data use a formal, ..."."""
    try:
        ds = nanopub.fetch(PRINCIPLE_TERMS + principle)
    except nanopub.NanopubError:
        return ""
    return next((str(o) for o in ds.objects(URIRef(PRINCIPLE_TERMS + principle), SKOS.definition)), "")


def is_principle(key: str) -> bool:
    return bool(_PRINCIPLE_ID.match(key))


def principle_sort_key(principle: str) -> tuple:
    """F, A, I, R in the order of the acronym, then numerically (A1.2 before A2)."""
    return ("FAIR".index(principle[0]), tuple(int(n) for n in principle[1:].split(".")))


def principles_for(topic: str, questions: dict[str, str]) -> list[str]:
    """Principles a topic refers to: a principle id ("I1"), or words found in the
    ontology wording of the given questions ({question text: principle}) or of
    their principles. Raises KeyError with the available wording otherwise."""
    key = topic.strip()
    if is_principle(key.upper()):
        return [key.upper()]
    words = [w for w in re.findall(r"[a-z]+", key.lower()) if len(w) > 2]
    stems = [w[:-3] if w.endswith("ies") else w[:-1] if w.endswith("s") else w for w in words]
    hits = set()
    for text, principle in questions.items():
        if not principle:
            continue
        haystack = f"{text} {principle_text(principle)}".lower()
        if stems and all(s in haystack for s in stems):
            hits.add(principle)
    if not hits:
        listing = "; ".join(f"{p}: {t}" for t, p in sorted(questions.items(), key=lambda x: x[1]) if p)
        raise KeyError(f"no question matches {topic!r}; pass a principle id. Questions: {listing}")
    return sorted(hits, key=principle_sort_key)
