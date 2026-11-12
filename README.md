# fip-mcp

<!-- mcp-name: org.sciencelive4all/fip-mcp -->

An MCP server that turns community **FAIR Implementation Profiles (FIPs)** into
guidance and deterministic compliance checks for AI agents such as Claude Code.

A FIP records a community's agreed FAIR choices: identifiers, repositories, formats,
vocabularies, licences and provenance models. It is published as nanopublications
by the [FIP Wizard](https://fip.fair-wizard.com). Today FIPs are mostly filled in
once and rarely read again. This server makes them operational. An agent helping a
researcher asks the FIP what the community agreed before it suggests anything, and
can check work against the FIP.

fip-mcp was developed in the [OSCARS](https://oscars-project.eu)-funded
**FIESTA** project (*FAIR Image Data Workflows in Galaxy*), and is maintained by
the [Science Live](https://sciencelive4all.org) community.

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

## Install and use

```bash
pipx install fip-mcp
claude mcp add fip -s user -- fip-mcp     # as an MCP server
fip-check check fiesta-eo 10.5281/zenodo.20960690   # same operations from the shell
fip-check crosswalk fiesta-bio fiesta-eo
```

Nanopubs are cached in `~/.cache/fip-mcp`. They are immutable, so they are cached
for good. Version lookups always go to the network.

For development: `pip install -e '.[dev]'` and `python -m pytest -q` (the tests need
no network).

## Status

Prototype. The short names in `src/fip_mcp/data` cover the Astronomy, Bioimaging
and Earth Observation FIPs of the OSCARS-FIESTA community *FAIR Image Data Workflows
in Galaxy*. Any tool also accepts the nanopublication URI of another FIP, but the
`check` probes have so far only been exercised on FIESTA outputs.

## Assistant test

`eval/` tests whether an AI assistant follows a community's FIP, with and without
fip-mcp. It asks 6 questions (repository, data format, licence, identifier,
vocabulary, provenance) for each of the 3 FIESTA communities, 3 runs per condition.
The expected answers are read from the published FIPs, not typed by hand. Results
from 2026-10-20 (Claude Opus 5.5, web and file tools disabled) are in
`eval/results/`:

| Variant | Without fip-mcp | With fip-mcp |
|---|---|---|
| *choice*: "what has my community agreed?" | 54 of 54 abstain | 54 of 54 give the declared choice or report the gap |
| *plain*: "what do you recommend?", declared questions | 30 of 45 on-profile, 15 off-profile | 45 of 45 on-profile |
| *plain*: questions the community left open | 9 of 9 recommend their own default, with a caveat | 9 of 9 report the gap |

```bash
python eval/run_eval.py --runs 3 --out eval/results/<name>     # needs Claude Code
python eval/score.py eval/results/<name>
```

## Citation

Please cite fip-mcp with the metadata in [`CITATION.cff`](CITATION.cff).

## Funding

fip-mcp was developed within **FIESTA**, a project funded by OSCARS (*Open Science
Clusters' Action for Research and Society*). OSCARS is funded by the European
Union's Horizon Europe programme under grant agreement No 101129751. Views and
opinions expressed are those of the authors only and do not necessarily reflect
those of the European Union. Neither the European Union nor the granting authority
can be held responsible for them.

Science Live is a community-driven, unfunded initiative. Further funders will be
listed here as they support the work.
