# fip-mcp

An MCP server that turns community **FAIR Implementation Profiles (FIPs)** into
guidance and deterministic compliance checks for AI agents such as Claude Code.

A FIP records a community's agreed FAIR choices: identifiers, repositories, formats,
vocabularies, licences and provenance models. It is published as nanopublications
by the [FIP Wizard](https://fip.fair-wizard.com). Today FIPs are mostly filled in
once and rarely read again. This server makes them operational. An agent helping a
researcher asks the FIP what the community agreed before it suggests anything, and
can check work against the FIP.

## Tools

| Tool | What it does |
|---|---|
| `communities` | Known communities and their FIP nanopubs (any tool also accepts a FIP URI). |
| `profile` | The community's choices question by question, from the **latest** FIP version. |
| `recommend` | What the community agreed for a topic (`format`, `repository`, `licence`, …). |
| `check` | Checks a folder or Zenodo record against the FIP: `pass` / `fail` (+ `fix`) / `manual` / `no-choice`. |
| `crosswalk` | What changes when a workflow or dataset moves between two communities. |

Design rules:

- **Verdicts are code, not LLM judgement.** Each declared resource maps to a probe
  of facts read from the target. A resource with no probe is `manual`, so the agent
  asks the user instead of guessing.
- **A community gap stays a gap.** `no-choice` is reported as a gap in the FIP, and
  the agent is told not to put its own preference in its place.
- **Latest version.** The FIP Wizard republishes a FIP *and* its declaration index,
  and both supersede their predecessors. The resolver only follows successors that
  are themselves FIPs.

## Use

```bash
pip install -e .
claude mcp add fip -- fip-mcp             # as an MCP server
fip-check check fiesta-eo 10.5281/zenodo.20960690   # same operations from the shell
fip-check crosswalk fiesta-bio fiesta-eo
```

Nanopubs are cached in `~/.cache/fip-mcp`. They are immutable, so they are cached
for good. Version lookups always go to the network.

## Status

Prototype, built for the OSCARS-FIESTA project. It covers the Astronomy, Bioimaging
and Earth Observation FIPs of the *FAIR Image Data Workflows in Galaxy* community.
