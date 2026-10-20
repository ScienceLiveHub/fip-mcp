# Assistant test (plain) — eval/results/plain-fips-2026-10-20

108 runs; model(s): claude-opus-5-5

| Condition | on-profile | off-profile | flags-gap | hedged | silent-default | unparsed | n |
|---|---|---|---|---|---|---|---|
| A baseline | 30 | 15 | 0 | 9 | 0 | 0 | 54 |
| B fip-mcp | 45 | 0 | 9 | 0 | 0 | 0 | 54 |

## Questions the community answered vs left open

| Condition | Community choice exists? | on-profile | off-profile | flags-gap | hedged | silent-default | unparsed |
|---|---|---|---|---|---|---|---|
| A baseline | yes | 30 | 15 | 0 | 0 | 0 | 0 |
| A baseline | no (gap) | 0 | 0 | 0 | 9 | 0 | 0 |
| B fip-mcp | yes | 45 | 0 | 0 | 0 | 0 | 0 |
| B fip-mcp | no (gap) | 0 | 0 | 9 | 0 | 0 | 0 |

## By community

| Condition | Community | on-profile | off-profile | flags-gap | hedged | silent-default | unparsed |
|---|---|---|---|---|---|---|---|
| A baseline | fiesta-astro | 15 | 3 | 0 | 0 | 0 | 0 |
| A baseline | fiesta-bio | 3 | 6 | 0 | 9 | 0 | 0 |
| A baseline | fiesta-eo | 12 | 6 | 0 | 0 | 0 | 0 |
| B fip-mcp | fiesta-astro | 18 | 0 | 0 | 0 | 0 | 0 |
| B fip-mcp | fiesta-bio | 9 | 0 | 9 | 0 | 0 | 0 |
| B fip-mcp | fiesta-eo | 18 | 0 | 0 | 0 | 0 | 0 |

## Every run

| Item | Cond | Run | Expected | Answered | Outcome | Tool calls |
|---|---|---|---|---|---|---|
| fiesta-astro:format | A | 1 | Flexible Image Transport System | FITS (Flexible Image Transport System) | on-profile | 0 |
| fiesta-astro:format | A | 2 | Flexible Image Transport System | FITS (Flexible Image Transport System) | on-profile | 0 |
| fiesta-astro:format | A | 3 | Flexible Image Transport System | FITS (Flexible Image Transport System) | on-profile | 0 |
| fiesta-astro:format | B | 1 | Flexible Image Transport System | Flexible Image Transport System (FITS) — https://w3id.org/np/RAtnRDavQjABwiKC6fVOj6JM2gVb8tucL1a0JMXDaFX6E#FITS | on-profile | 2 |
| fiesta-astro:format | B | 2 | Flexible Image Transport System | FITS (Flexible Image Transport System) | on-profile | 2 |
| fiesta-astro:format | B | 3 | Flexible Image Transport System | Flexible Image Transport System (FITS) | on-profile | 2 |
| fiesta-astro:identifier | A | 1 | DOI | DOI (DataCite) | on-profile | 0 |
| fiesta-astro:identifier | A | 2 | DOI | DOI (Digital Object Identifier, via DataCite, e.g. Zenodo) | on-profile | 0 |
| fiesta-astro:identifier | A | 3 | DOI | DataCite DOI | on-profile | 0 |
| fiesta-astro:identifier | B | 1 | DOI | DOI | on-profile | 2 |
| fiesta-astro:identifier | B | 2 | DOI | DOI | on-profile | 2 |
| fiesta-astro:identifier | B | 3 | DOI | DOI | on-profile | 2 |
| fiesta-astro:licence | A | 1 | CC BY 4.0 | Creative Commons Attribution 4.0 International (CC BY 4.0) | on-profile | 0 |
| fiesta-astro:licence | A | 2 | CC BY 4.0 | Creative Commons Attribution 4.0 International (CC BY 4.0) — https://creativecommons.org/licenses/by/4.0/ | on-profile | 0 |
| fiesta-astro:licence | A | 3 | CC BY 4.0 | Creative Commons Attribution 4.0 International (CC BY 4.0) | on-profile | 0 |
| fiesta-astro:licence | B | 1 | CC BY 4.0 | CC BY 4.0 (http://purl.org/np/RAQ__sGdY_Qc7l1O_zmn4nr-pMBOxKU04Ur9s998rS6Fc#CC-BY-4.0) | on-profile | 2 |
| fiesta-astro:licence | B | 2 | CC BY 4.0 | CC BY 4.0 | on-profile | 2 |
| fiesta-astro:licence | B | 3 | CC BY 4.0 | CC BY 4.0 | on-profile | 2 |
| fiesta-astro:provenance | A | 1 | PROV-O | Workflow Run RO-Crate (RO-Crate provenance profile, as exported by Galaxy) | off-profile | 0 |
| fiesta-astro:provenance | A | 2 | PROV-O | Workflow Run RO-Crate (Galaxy's native RO-Crate provenance export) | off-profile | 0 |
| fiesta-astro:provenance | A | 3 | PROV-O | Workflow Run RO-Crate (Provenance Run Crate profile) | off-profile | 0 |
| fiesta-astro:provenance | B | 1 | PROV-O | PROV-O | on-profile | 2 |
| fiesta-astro:provenance | B | 2 | PROV-O | PROV-O (W3C PROV Ontology) — http://purl.org/np/RAnkRRbkigfQpL2ERK1jVqwA9Brwu1GcORfTbfQMWHfC4#PROV-O | on-profile | 2 |
| fiesta-astro:provenance | B | 3 | PROV-O | PROV-O (W3C PROV Ontology), http://purl.org/np/RAnkRRbkigfQpL2ERK1jVqwA9Brwu1GcORfTbfQMWHfC4#PROV-O | on-profile | 2 |
| fiesta-astro:repository | A | 1 | Zenodo | Zenodo | on-profile | 0 |
| fiesta-astro:repository | A | 2 | Zenodo | Zenodo | on-profile | 0 |
| fiesta-astro:repository | A | 3 | Zenodo | Zenodo | on-profile | 0 |
| fiesta-astro:repository | B | 1 | Zenodo | Zenodo | on-profile | 2 |
| fiesta-astro:repository | B | 2 | Zenodo | Zenodo | on-profile | 2 |
| fiesta-astro:repository | B | 3 | Zenodo | Zenodo | on-profile | 2 |
| fiesta-astro:vocabulary | A | 1 | IVOA Vocabulary: Unified Astronomy Thesaurus | Unified Astronomy Thesaurus (UAT) | on-profile | 0 |
| fiesta-astro:vocabulary | A | 2 | IVOA Vocabulary: Unified Astronomy Thesaurus | Unified Astronomy Thesaurus (UAT) | on-profile | 0 |
| fiesta-astro:vocabulary | A | 3 | IVOA Vocabulary: Unified Astronomy Thesaurus | Unified Astronomy Thesaurus (UAT) | on-profile | 0 |
| fiesta-astro:vocabulary | B | 1 | IVOA Vocabulary: Unified Astronomy Thesaurus | IVOA Vocabulary: Unified Astronomy Thesaurus (UAT) | on-profile | 2 |
| fiesta-astro:vocabulary | B | 2 | IVOA Vocabulary: Unified Astronomy Thesaurus | IVOA Vocabulary: Unified Astronomy Thesaurus (UAT) | on-profile | 2 |
| fiesta-astro:vocabulary | B | 3 | IVOA Vocabulary: Unified Astronomy Thesaurus | IVOA Vocabulary: Unified Astronomy Thesaurus (UAT) | on-profile | 2 |
| fiesta-bio:format | A | 1 | NOT_DECLARED | OME-Zarr (OME-NGFF) | hedged | 0 |
| fiesta-bio:format | A | 2 | NOT_DECLARED | OME-Zarr (OME-NGFF) | hedged | 0 |
| fiesta-bio:format | A | 3 | NOT_DECLARED | OME-Zarr (OME-NGFF) | hedged | 0 |
| fiesta-bio:format | B | 1 | NOT_DECLARED | JSON (the community's agreed format for metadata records; no dataset format has been agreed yet, so raise this with the FIP maintainers) | flags-gap | 3 |
| fiesta-bio:format | B | 2 | NOT_DECLARED | No community-agreed dataset format exists (I1-D is open), so raise it with the FIESTA Bio FIP maintainers | flags-gap | 3 |
| fiesta-bio:format | B | 3 | NOT_DECLARED | None — the FIESTA Bio FIP has no agreed dataset format; ask the FIP maintainers to decide one (JSON is agreed only for metadata) | flags-gap | 2 |
| fiesta-bio:identifier | A | 1 | URI | DOI (Digital Object Identifier) | off-profile | 0 |
| fiesta-bio:identifier | A | 2 | URI | DOI (Digital Object Identifier, e.g. DataCite DOIs via Zenodo or the BioImage Archive) | off-profile | 0 |
| fiesta-bio:identifier | A | 3 | URI | DOI (Digital Object Identifier) | off-profile | 0 |
| fiesta-bio:identifier | B | 1 | URI | URI (http://purl.org/np/RA5-OsT0-sjRbcoFEGfOzkrcFtExipMRmoLErzg5QWL7c#URI) | on-profile | 2 |
| fiesta-bio:identifier | B | 2 | URI | URI (http://purl.org/np/RA5-OsT0-sjRbcoFEGfOzkrcFtExipMRmoLErzg5QWL7c#URI) | on-profile | 2 |
| fiesta-bio:identifier | B | 3 | URI | URI | on-profile | 2 |
| fiesta-bio:licence | A | 1 | CC0 1.0, CC BY 4.0 | Creative Commons Attribution 4.0 International (CC BY 4.0) | on-profile | 0 |
| fiesta-bio:licence | A | 2 | CC0 1.0, CC BY 4.0 | Creative Commons Attribution 4.0 International (CC BY 4.0) | on-profile | 0 |
| fiesta-bio:licence | A | 3 | CC0 1.0, CC BY 4.0 | Creative Commons Attribution 4.0 International (CC BY 4.0) | on-profile | 0 |
| fiesta-bio:licence | B | 1 | CC0 1.0, CC BY 4.0 | CC BY 4.0 (http://purl.org/np/RAQ__sGdY_Qc7l1O_zmn4nr-pMBOxKU04Ur9s998rS6Fc#CC-BY-4.0) | on-profile | 2 |
| fiesta-bio:licence | B | 2 | CC0 1.0, CC BY 4.0 | CC0 1.0 (http://purl.org/np/RAq55jS4TCF-u0HLARDjWevzMv8k-NY7737bSJVzRAY2w#CC0-1.0) | on-profile | 2 |
| fiesta-bio:licence | B | 3 | CC0 1.0, CC BY 4.0 | CC0 1.0 (http://purl.org/np/RAq55jS4TCF-u0HLARDjWevzMv8k-NY7737bSJVzRAY2w#CC0-1.0) | on-profile | 2 |
| fiesta-bio:provenance | A | 1 | NOT_DECLARED | Workflow Run RO-Crate (Provenance Run Crate profile) | hedged | 0 |
| fiesta-bio:provenance | A | 2 | NOT_DECLARED | Workflow Run RO-Crate (Provenance Run Crate profile) | hedged | 0 |
| fiesta-bio:provenance | A | 3 | NOT_DECLARED | Workflow Run RO-Crate (Provenance Run Crate profile) | hedged | 0 |
| fiesta-bio:provenance | B | 1 | NOT_DECLARED | None agreed yet by FIESTA Bioimaging; raise provenance (R1.2) with the FIP maintainers | flags-gap | 3 |
| fiesta-bio:provenance | B | 2 | NOT_DECLARED | No agreed resource (FIESTA Bio FIP R1.2-D is open); ask the FIP maintainers to choose one, e.g. Workflow Run RO-Crate (my suggestion) | flags-gap | 3 |
| fiesta-bio:provenance | B | 3 | NOT_DECLARED | Workflow Run RO-Crate (my own interim suggestion; the FIESTA Bio FIP has no provenance choice yet, so raise it with the FIP maintainers) | flags-gap | 3 |
| fiesta-bio:repository | A | 1 | Image Data Resource | BioImage Archive (EMBL-EBI) | off-profile | 0 |
| fiesta-bio:repository | A | 2 | Image Data Resource | BioImage Archive (EMBL-EBI) | off-profile | 0 |
| fiesta-bio:repository | A | 3 | Image Data Resource | BioImage Archive (EMBL-EBI) | off-profile | 0 |
| fiesta-bio:repository | B | 1 | Image Data Resource | Image Data Resource (IDR) | on-profile | 3 |
| fiesta-bio:repository | B | 2 | Image Data Resource | Image Data Resource (IDR) | on-profile | 3 |
| fiesta-bio:repository | B | 3 | Image Data Resource | Image Data Resource (IDR) | on-profile | 2 |
| fiesta-bio:vocabulary | A | 1 | NOT_DECLARED | EDAM-Bioimaging ontology | hedged | 0 |
| fiesta-bio:vocabulary | A | 2 | NOT_DECLARED | EDAM-Bioimaging ontology | hedged | 0 |
| fiesta-bio:vocabulary | A | 3 | NOT_DECLARED | EDAM-Bioimaging ontology | hedged | 0 |
| fiesta-bio:vocabulary | B | 1 | NOT_DECLARED | NCBI Taxonomy (https://www.ncbi.nlm.nih.gov/taxonomy) | flags-gap | 2 |
| fiesta-bio:vocabulary | B | 2 | NOT_DECLARED | NCBI Taxonomy, which the community chose for metadata. It has no agreed vocabulary for annotating datasets. | flags-gap | 2 |
| fiesta-bio:vocabulary | B | 3 | NOT_DECLARED | NCBI Taxonomy (https://www.ncbi.nlm.nih.gov/taxonomy), which the community chose for metadata, not for dataset annotation | flags-gap | 2 |
| fiesta-eo:format | A | 1 | NetCDF | Cloud Optimized GeoTIFF (COG) | off-profile | 0 |
| fiesta-eo:format | A | 2 | NetCDF | Cloud-Optimized GeoTIFF (COG) | off-profile | 0 |
| fiesta-eo:format | A | 3 | NetCDF | Zarr (GeoZarr conventions) | off-profile | 0 |
| fiesta-eo:format | B | 1 | NetCDF | NetCDF | on-profile | 2 |
| fiesta-eo:format | B | 2 | NetCDF | NetCDF | on-profile | 2 |
| fiesta-eo:format | B | 3 | NetCDF | NetCDF | on-profile | 2 |
| fiesta-eo:identifier | A | 1 | DOI | DOI (Digital Object Identifier, minted via DataCite e.g. through Zenodo) | on-profile | 0 |
| fiesta-eo:identifier | A | 2 | DOI | DOI (DataCite), e.g. minted via Zenodo | on-profile | 0 |
| fiesta-eo:identifier | A | 3 | DOI | DataCite DOI | on-profile | 0 |
| fiesta-eo:identifier | B | 1 | DOI | DOI | on-profile | 2 |
| fiesta-eo:identifier | B | 2 | DOI | DOI (Digital Object Identifier) | on-profile | 2 |
| fiesta-eo:identifier | B | 3 | DOI | DOI | on-profile | 2 |
| fiesta-eo:licence | A | 1 | CC BY 4.0 | Creative Commons Attribution 4.0 International (CC BY 4.0) | on-profile | 0 |
| fiesta-eo:licence | A | 2 | CC BY 4.0 | Creative Commons Attribution 4.0 International (CC BY 4.0) | on-profile | 0 |
| fiesta-eo:licence | A | 3 | CC BY 4.0 | Creative Commons Attribution 4.0 International (CC BY 4.0) | on-profile | 0 |
| fiesta-eo:licence | B | 1 | CC BY 4.0 | CC BY 4.0 (http://purl.org/np/RAQ__sGdY_Qc7l1O_zmn4nr-pMBOxKU04Ur9s998rS6Fc#CC-BY-4.0) | on-profile | 2 |
| fiesta-eo:licence | B | 2 | CC BY 4.0 | CC BY 4.0 | on-profile | 2 |
| fiesta-eo:licence | B | 3 | CC BY 4.0 | CC BY 4.0 (http://purl.org/np/RAQ__sGdY_Qc7l1O_zmn4nr-pMBOxKU04Ur9s998rS6Fc#CC-BY-4.0) | on-profile | 2 |
| fiesta-eo:provenance | A | 1 | NetCDF CF-1.11 | W3C PROV-O (PROV Ontology) | off-profile | 0 |
| fiesta-eo:provenance | A | 2 | NetCDF CF-1.11 | Workflow Run RO-Crate (Provenance Run Crate profile) | off-profile | 0 |
| fiesta-eo:provenance | A | 3 | NetCDF CF-1.11 | Workflow Run RO-Crate (Provenance Run Crate profile) | off-profile | 0 |
| fiesta-eo:provenance | B | 1 | NetCDF CF-1.11 | NetCDF CF-1.11 (CF Metadata Conventions v1.11) | on-profile | 2 |
| fiesta-eo:provenance | B | 2 | NetCDF CF-1.11 | NetCDF CF-1.11 (CF Metadata Conventions v1.11) | on-profile | 2 |
| fiesta-eo:provenance | B | 3 | NetCDF CF-1.11 | NetCDF CF-1.11 (Climate and Forecast Metadata Conventions v1.11) | on-profile | 2 |
| fiesta-eo:repository | A | 1 | NIRD-RDA, Zenodo | Zenodo | on-profile | 0 |
| fiesta-eo:repository | A | 2 | NIRD-RDA, Zenodo | Zenodo | on-profile | 0 |
| fiesta-eo:repository | A | 3 | NIRD-RDA, Zenodo | Zenodo | on-profile | 0 |
| fiesta-eo:repository | B | 1 | NIRD-RDA, Zenodo | Zenodo | on-profile | 2 |
| fiesta-eo:repository | B | 2 | NIRD-RDA, Zenodo | Zenodo | on-profile | 2 |
| fiesta-eo:repository | B | 3 | NIRD-RDA, Zenodo | Zenodo | on-profile | 2 |
| fiesta-eo:vocabulary | A | 1 | NetCDF CF-1.11 | CF (Climate and Forecast) Standard Name Table | on-profile | 0 |
| fiesta-eo:vocabulary | A | 2 | NetCDF CF-1.11 | CF Standard Name Table (Climate and Forecast conventions) | on-profile | 0 |
| fiesta-eo:vocabulary | A | 3 | NetCDF CF-1.11 | CF Standard Names (Climate and Forecast conventions) | on-profile | 0 |
| fiesta-eo:vocabulary | B | 1 | NetCDF CF-1.11 | NetCDF CF-1.11 (Climate and Forecast Metadata Conventions v1.11) | on-profile | 2 |
| fiesta-eo:vocabulary | B | 2 | NetCDF CF-1.11 | NetCDF CF-1.11 (Climate and Forecast Metadata Conventions v1.11) | on-profile | 2 |
| fiesta-eo:vocabulary | B | 3 | NetCDF CF-1.11 | NetCDF CF-1.11 (Climate and Forecast Metadata Conventions v1.11) | on-profile | 2 |

Total cost: $5.21
