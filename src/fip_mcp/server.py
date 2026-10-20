"""MCP server: community FAIR Implementation Profiles as guidance and checks for agents.

A FIP is a community's declared FAIR choices (identifiers, repositories, formats,
vocabularies, licences, provenance), published as nanopublications. This server
reads them from the nanopub network so an agent helping a researcher uses the
community's agreed resources instead of its own defaults, and can check work
against them deterministically.

Run:  fip-mcp          (stdio transport)
Add:  claude mcp add fip -- fip-mcp

Environment:
    FIP_MCP_SPARQL   nanopub SPARQL endpoint (default https://query.knowledgepixels.com/repo/full)
    FIP_MCP_CACHE    nanopub cache folder (default ~/.cache/fip-mcp)
"""
from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from . import service

mcp = FastMCP("fip")


def _fail(error: Exception) -> dict:
    """Return the failure verbatim so the agent can relay what actually broke."""
    return {"ok": False, "error": str(error), "errorType": type(error).__name__}


@mcp.tool()
def communities() -> dict:
    """Known communities and the FIP each one has published. Any tool below also
    accepts a FIP nanopub URI in place of a short name."""
    return service.communities()


@mcp.tool()
def profile(community: str) -> dict:
    """The community's FAIR choices, question by question, from the LATEST version
    of its FIP (the supersedes chain is followed and returned as `versionChain`).

    `noChoice: true` means the community left that question open. Treat it as a
    gap in the profile, not as permission to pick something yourself.
    """
    try:
        return service.profile(community)
    except Exception as e:  # noqa: BLE001
        return _fail(e)


@mcp.tool()
def recommend(community: str, topic: str) -> dict:
    """What the community has agreed for one topic, with each resource's URL and
    description. Call this BEFORE suggesting a repository, file format, licence,
    vocabulary or identifier scheme to a researcher in this community.

    topic: identifier, metadata-schema, linking, repository, protocol, access,
    longevity, format, vocabulary, references, licence, provenance, standards —
    or a FAIR principle such as "I1".
    """
    try:
        return service.recommend(community, topic)
    except Exception as e:  # noqa: BLE001
        return _fail(e)


@mcp.tool()
def check(community: str, target: str) -> dict:
    """Check a folder or a Zenodo record against the community's FIP.

    target: a local folder path, a Zenodo record URL or id, or a Zenodo DOI.

    The verdicts are deterministic: each declared resource is matched to a probe
    of facts read from the target (DOIs, licence, repository, file formats,
    RO-Crate). Statuses: pass, fail (with `fix`), manual (no automatic probe —
    ask the user, do not guess), no-choice (the community left it open),
    planned-only. `offProfileFormats` lists data formats present in the target
    that the community did not declare. Report results as given; do not upgrade
    a `manual` to `pass`.
    """
    try:
        return service.check(community, target)
    except Exception as e:  # noqa: BLE001
        return _fail(e)


@mcp.tool()
def crosswalk(source: str, target: str) -> dict:
    """What changes when a workflow or dataset moves from the `source` community's
    practices to the `target` community's: per FIP question, same / overlap /
    differs / only one side chose / neither chose, with conversion notes for
    data formats. Use it when reusing a method across disciplines."""
    try:
        return service.crosswalk(source, target)
    except Exception as e:  # noqa: BLE001
        return _fail(e)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
