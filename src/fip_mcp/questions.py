"""The FIP questionnaire: question ids, what they ask, and plain-word topics.

Ids are those of the FIP Wizard (`fip:FIP-Question-<id>`); `-D` asks about
data, `-MD` about metadata, no suffix about both. Supplementary questions
(`FIP-S-Question-…`) ask about supporting services rather than a principle.
"""
from __future__ import annotations

QUESTIONS: dict[str, tuple[str, str]] = {
    "F1-D": ("F1", "Which globally unique, persistent, resolvable identifiers do you use for datasets?"),
    "F1-MD": ("F1", "Which globally unique, persistent, resolvable identifiers do you use for metadata records?"),
    "F2": ("F2", "Which metadata schemas do you use for findability?"),
    "F3": ("F3", "Which technology links the persistent identifiers of your data to the metadata description?"),
    "F4-D": ("F4", "In which search engines or registries are your datasets indexed?"),
    "F4-MD": ("F4", "In which search engines or registries are your metadata records indexed?"),
    "A1.1-D": ("A1.1", "Which standardised communication protocol do you use for datasets?"),
    "A1.1-MD": ("A1.1", "Which standardised communication protocol do you use for metadata records?"),
    "A1.2-D": ("A1.2", "Which authentication and authorisation technique do you use for datasets?"),
    "A1.2-MD": ("A1.2", "Which authentication and authorisation technique do you use for metadata records?"),
    "A2": ("A2", "Which metadata longevity plan do you use?"),
    "I1-D": ("I1", "Which knowledge representation languages (formats) do you use for datasets?"),
    "I1-MD": ("I1", "Which knowledge representation languages do you use for metadata records?"),
    "I2-D": ("I2", "Which structured vocabularies do you use to annotate your datasets?"),
    "I2-MD": ("I2", "Which structured vocabularies do you use to encode your metadata records?"),
    "I3-D": ("I3", "Which models or schemas do you use for qualified references in your datasets?"),
    "I3-MD": ("I3", "Which models or schemas do you use for qualified references in your metadata records?"),
    "R1.1-D": ("R1.1", "Which usage licence do you use for your datasets?"),
    "R1.1-MD": ("R1.1", "Which usage licence do you use for your metadata records?"),
    "R1.2-D": ("R1.2", "Which metadata schemas do you use for describing the provenance of your datasets?"),
    "R1.2-MD": ("R1.2", "Which metadata schemas do you use for describing the provenance of your metadata records?"),
    "R1.3-D": ("R1.3", "Which community standards do your datasets meet?"),
    "R1.3-MD": ("R1.3", "Which community standards do your metadata records meet?"),
}

# Plain words an agent (or a user) is likely to use, mapped to principles.
TOPICS: dict[str, list[str]] = {
    "identifier": ["F1"],
    "metadata-schema": ["F2"],
    "linking": ["F3"],
    "repository": ["F4"],
    "protocol": ["A1.1"],
    "access": ["A1.2"],
    "longevity": ["A2"],
    "format": ["I1"],
    "vocabulary": ["I2"],
    "references": ["I3"],
    "licence": ["R1.1"],
    "provenance": ["R1.2"],
    "standards": ["R1.3"],
}
ALIASES = {
    "license": "licence", "pid": "identifier", "doi": "identifier", "deposit": "repository",
    "registry": "repository", "archive": "repository", "file-format": "format", "ontology": "vocabulary",
    "authentication": "access", "auth": "access", "schema": "metadata-schema",
}


def question_info(qid: str) -> tuple[str, str, str]:
    """(principle, axis, question text) for a FIP Wizard question id."""
    if qid in QUESTIONS:
        principle, text = QUESTIONS[qid]
        axis = "data" if qid.endswith("-D") else "metadata" if qid.endswith("-MD") else "both"
        return principle, axis, text
    if qid.startswith("FIP-S-Question-"):
        words = qid.removeprefix("FIP-S-Question-").replace("-", " ")
        return "", "supporting", f"Which {words} do you use?"
    return "", "unknown", qid


def principles_for(topic: str) -> list[str]:
    key = topic.strip().lower().replace(" ", "-")
    key = ALIASES.get(key, key)
    if key in TOPICS:
        return TOPICS[key]
    if key.upper() in {p for p, _ in QUESTIONS.values()}:
        return [key.upper()]
    raise KeyError(f"unknown topic {topic!r}; use one of {sorted(TOPICS)} or a principle such as 'I1'")
