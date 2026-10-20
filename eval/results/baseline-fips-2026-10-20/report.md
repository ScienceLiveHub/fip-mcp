# Assistant test — eval/results/baseline-fips-2026-10-20

108 runs; model(s): claude-opus-5-5

| Condition | correct | abstained | invented | wrong | unparsed | n |
|---|---|---|---|---|---|---|
| A baseline | 0 | 54 | 0 | 0 | 0 | 54 |
| B fip-mcp | 54 | 0 | 0 | 0 | 0 | 54 |

## Questions the community answered vs left open

| Condition | Community choice exists? | correct | abstained | invented | wrong | unparsed |
|---|---|---|---|---|---|---|
| A baseline | yes | 0 | 45 | 0 | 0 | 0 |
| A baseline | no (gap) | 0 | 9 | 0 | 0 | 0 |
| B fip-mcp | yes | 45 | 0 | 0 | 0 | 0 |
| B fip-mcp | no (gap) | 9 | 0 | 0 | 0 | 0 |

## By community

| Condition | Community | correct | abstained | invented | wrong | unparsed |
|---|---|---|---|---|---|---|
| A baseline | fiesta-astro | 0 | 18 | 0 | 0 | 0 |
| A baseline | fiesta-bio | 0 | 18 | 0 | 0 | 0 |
| A baseline | fiesta-eo | 0 | 18 | 0 | 0 | 0 |
| B fip-mcp | fiesta-astro | 18 | 0 | 0 | 0 | 0 |
| B fip-mcp | fiesta-bio | 18 | 0 | 0 | 0 | 0 |
| B fip-mcp | fiesta-eo | 18 | 0 | 0 | 0 | 0 |

## Every run

| Item | Cond | Run | Expected | Answered | Outcome | Tool calls |
|---|---|---|---|---|---|---|
| fiesta-astro:format | A | 1 | Flexible Image Transport System | DONT_KNOW | abstained | 0 |
| fiesta-astro:format | A | 2 | Flexible Image Transport System | DONT_KNOW | abstained | 0 |
| fiesta-astro:format | A | 3 | Flexible Image Transport System | DONT_KNOW | abstained | 0 |
| fiesta-astro:format | B | 1 | Flexible Image Transport System | Flexible Image Transport System (FITS) | correct | 2 |
| fiesta-astro:format | B | 2 | Flexible Image Transport System | Flexible Image Transport System (FITS) | correct | 2 |
| fiesta-astro:format | B | 3 | Flexible Image Transport System | Flexible Image Transport System | correct | 2 |
| fiesta-astro:identifier | A | 1 | DOI | DONT_KNOW | abstained | 0 |
| fiesta-astro:identifier | A | 2 | DOI | DONT_KNOW | abstained | 0 |
| fiesta-astro:identifier | A | 3 | DOI | DONT_KNOW | abstained | 0 |
| fiesta-astro:identifier | B | 1 | DOI | DOI | correct | 2 |
| fiesta-astro:identifier | B | 2 | DOI | DOI | correct | 2 |
| fiesta-astro:identifier | B | 3 | DOI | DOI | correct | 2 |
| fiesta-astro:licence | A | 1 | CC BY 4.0 | DONT_KNOW | abstained | 0 |
| fiesta-astro:licence | A | 2 | CC BY 4.0 | DONT_KNOW | abstained | 0 |
| fiesta-astro:licence | A | 3 | CC BY 4.0 | DONT_KNOW | abstained | 0 |
| fiesta-astro:licence | B | 1 | CC BY 4.0 | CC BY 4.0 | correct | 2 |
| fiesta-astro:licence | B | 2 | CC BY 4.0 | CC BY 4.0 | correct | 2 |
| fiesta-astro:licence | B | 3 | CC BY 4.0 | CC BY 4.0 | correct | 2 |
| fiesta-astro:provenance | A | 1 | PROV-O | DONT_KNOW | abstained | 0 |
| fiesta-astro:provenance | A | 2 | PROV-O | DONT_KNOW | abstained | 0 |
| fiesta-astro:provenance | A | 3 | PROV-O | DONT_KNOW | abstained | 0 |
| fiesta-astro:provenance | B | 1 | PROV-O | PROV-O | correct | 2 |
| fiesta-astro:provenance | B | 2 | PROV-O | PROV-O | correct | 2 |
| fiesta-astro:provenance | B | 3 | PROV-O | PROV-O | correct | 2 |
| fiesta-astro:repository | A | 1 | Zenodo | DONT_KNOW | abstained | 0 |
| fiesta-astro:repository | A | 2 | Zenodo | DONT_KNOW | abstained | 0 |
| fiesta-astro:repository | A | 3 | Zenodo | DONT_KNOW | abstained | 0 |
| fiesta-astro:repository | B | 1 | Zenodo | Zenodo | correct | 2 |
| fiesta-astro:repository | B | 2 | Zenodo | Zenodo | correct | 2 |
| fiesta-astro:repository | B | 3 | Zenodo | Zenodo | correct | 2 |
| fiesta-astro:vocabulary | A | 1 | IVOA Vocabulary: Unified Astronomy Thesaurus | DONT_KNOW | abstained | 0 |
| fiesta-astro:vocabulary | A | 2 | IVOA Vocabulary: Unified Astronomy Thesaurus | DONT_KNOW | abstained | 0 |
| fiesta-astro:vocabulary | A | 3 | IVOA Vocabulary: Unified Astronomy Thesaurus | DONT_KNOW | abstained | 0 |
| fiesta-astro:vocabulary | B | 1 | IVOA Vocabulary: Unified Astronomy Thesaurus | IVOA Vocabulary: Unified Astronomy Thesaurus | correct | 2 |
| fiesta-astro:vocabulary | B | 2 | IVOA Vocabulary: Unified Astronomy Thesaurus | IVOA Vocabulary: Unified Astronomy Thesaurus | correct | 2 |
| fiesta-astro:vocabulary | B | 3 | IVOA Vocabulary: Unified Astronomy Thesaurus | IVOA Vocabulary: Unified Astronomy Thesaurus | correct | 2 |
| fiesta-bio:format | A | 1 | NOT_DECLARED | DONT_KNOW | abstained | 0 |
| fiesta-bio:format | A | 2 | NOT_DECLARED | DONT_KNOW | abstained | 0 |
| fiesta-bio:format | A | 3 | NOT_DECLARED | DONT_KNOW | abstained | 0 |
| fiesta-bio:format | B | 1 | NOT_DECLARED | NOT_DECLARED | correct | 2 |
| fiesta-bio:format | B | 2 | NOT_DECLARED | NOT_DECLARED | correct | 2 |
| fiesta-bio:format | B | 3 | NOT_DECLARED | NOT_DECLARED | correct | 2 |
| fiesta-bio:identifier | A | 1 | URI | DONT_KNOW | abstained | 0 |
| fiesta-bio:identifier | A | 2 | URI | DONT_KNOW | abstained | 0 |
| fiesta-bio:identifier | A | 3 | URI | DONT_KNOW | abstained | 0 |
| fiesta-bio:identifier | B | 1 | URI | URI | correct | 2 |
| fiesta-bio:identifier | B | 2 | URI | URI | correct | 2 |
| fiesta-bio:identifier | B | 3 | URI | URI | correct | 2 |
| fiesta-bio:licence | A | 1 | CC0 1.0, CC BY 4.0 | DONT_KNOW | abstained | 0 |
| fiesta-bio:licence | A | 2 | CC0 1.0, CC BY 4.0 | DONT_KNOW | abstained | 0 |
| fiesta-bio:licence | A | 3 | CC0 1.0, CC BY 4.0 | DONT_KNOW | abstained | 0 |
| fiesta-bio:licence | B | 1 | CC0 1.0, CC BY 4.0 | CC0 1.0, CC BY 4.0 | correct | 2 |
| fiesta-bio:licence | B | 2 | CC0 1.0, CC BY 4.0 | CC0 1.0, CC BY 4.0 | correct | 2 |
| fiesta-bio:licence | B | 3 | CC0 1.0, CC BY 4.0 | CC0 1.0, CC BY 4.0 | correct | 2 |
| fiesta-bio:provenance | A | 1 | NOT_DECLARED | DONT_KNOW | abstained | 0 |
| fiesta-bio:provenance | A | 2 | NOT_DECLARED | DONT_KNOW | abstained | 0 |
| fiesta-bio:provenance | A | 3 | NOT_DECLARED | DONT_KNOW | abstained | 0 |
| fiesta-bio:provenance | B | 1 | NOT_DECLARED | NOT_DECLARED | correct | 2 |
| fiesta-bio:provenance | B | 2 | NOT_DECLARED | NOT_DECLARED | correct | 2 |
| fiesta-bio:provenance | B | 3 | NOT_DECLARED | NOT_DECLARED | correct | 2 |
| fiesta-bio:repository | A | 1 | Image Data Resource | DONT_KNOW | abstained | 0 |
| fiesta-bio:repository | A | 2 | Image Data Resource | DONT_KNOW | abstained | 0 |
| fiesta-bio:repository | A | 3 | Image Data Resource | DONT_KNOW | abstained | 0 |
| fiesta-bio:repository | B | 1 | Image Data Resource | Image Data Resource | correct | 2 |
| fiesta-bio:repository | B | 2 | Image Data Resource | Image Data Resource | correct | 2 |
| fiesta-bio:repository | B | 3 | Image Data Resource | Image Data Resource | correct | 2 |
| fiesta-bio:vocabulary | A | 1 | NOT_DECLARED | DONT_KNOW | abstained | 0 |
| fiesta-bio:vocabulary | A | 2 | NOT_DECLARED | DONT_KNOW | abstained | 0 |
| fiesta-bio:vocabulary | A | 3 | NOT_DECLARED | DONT_KNOW | abstained | 0 |
| fiesta-bio:vocabulary | B | 1 | NOT_DECLARED | NOT_DECLARED | correct | 2 |
| fiesta-bio:vocabulary | B | 2 | NOT_DECLARED | NOT_DECLARED | correct | 2 |
| fiesta-bio:vocabulary | B | 3 | NOT_DECLARED | NOT_DECLARED | correct | 2 |
| fiesta-eo:format | A | 1 | NetCDF | DONT_KNOW | abstained | 0 |
| fiesta-eo:format | A | 2 | NetCDF | DONT_KNOW | abstained | 0 |
| fiesta-eo:format | A | 3 | NetCDF | DONT_KNOW | abstained | 0 |
| fiesta-eo:format | B | 1 | NetCDF | NetCDF | correct | 2 |
| fiesta-eo:format | B | 2 | NetCDF | NetCDF | correct | 2 |
| fiesta-eo:format | B | 3 | NetCDF | NetCDF | correct | 2 |
| fiesta-eo:identifier | A | 1 | DOI | DONT_KNOW | abstained | 0 |
| fiesta-eo:identifier | A | 2 | DOI | DONT_KNOW | abstained | 0 |
| fiesta-eo:identifier | A | 3 | DOI | DONT_KNOW | abstained | 0 |
| fiesta-eo:identifier | B | 1 | DOI | DOI | correct | 2 |
| fiesta-eo:identifier | B | 2 | DOI | DOI | correct | 2 |
| fiesta-eo:identifier | B | 3 | DOI | DOI | correct | 2 |
| fiesta-eo:licence | A | 1 | CC BY 4.0 | DONT_KNOW | abstained | 0 |
| fiesta-eo:licence | A | 2 | CC BY 4.0 | DONT_KNOW | abstained | 0 |
| fiesta-eo:licence | A | 3 | CC BY 4.0 | DONT_KNOW | abstained | 0 |
| fiesta-eo:licence | B | 1 | CC BY 4.0 | CC BY 4.0 | correct | 2 |
| fiesta-eo:licence | B | 2 | CC BY 4.0 | CC BY 4.0 | correct | 2 |
| fiesta-eo:licence | B | 3 | CC BY 4.0 | CC BY 4.0 | correct | 2 |
| fiesta-eo:provenance | A | 1 | NetCDF CF-1.11 | DONT_KNOW | abstained | 0 |
| fiesta-eo:provenance | A | 2 | NetCDF CF-1.11 | DONT_KNOW | abstained | 0 |
| fiesta-eo:provenance | A | 3 | NetCDF CF-1.11 | DONT_KNOW | abstained | 0 |
| fiesta-eo:provenance | B | 1 | NetCDF CF-1.11 | NetCDF CF-1.11 | correct | 2 |
| fiesta-eo:provenance | B | 2 | NetCDF CF-1.11 | NetCDF CF-1.11 | correct | 2 |
| fiesta-eo:provenance | B | 3 | NetCDF CF-1.11 | NetCDF CF-1.11 | correct | 2 |
| fiesta-eo:repository | A | 1 | NIRD-RDA, Zenodo | DONT_KNOW | abstained | 0 |
| fiesta-eo:repository | A | 2 | NIRD-RDA, Zenodo | DONT_KNOW | abstained | 0 |
| fiesta-eo:repository | A | 3 | NIRD-RDA, Zenodo | DONT_KNOW | abstained | 0 |
| fiesta-eo:repository | B | 1 | NIRD-RDA, Zenodo | NIRD-RDA, Zenodo | correct | 2 |
| fiesta-eo:repository | B | 2 | NIRD-RDA, Zenodo | NIRD-RDA, Zenodo | correct | 2 |
| fiesta-eo:repository | B | 3 | NIRD-RDA, Zenodo | NIRD-RDA, Zenodo | correct | 2 |
| fiesta-eo:vocabulary | A | 1 | NetCDF CF-1.11 | DONT_KNOW | abstained | 0 |
| fiesta-eo:vocabulary | A | 2 | NetCDF CF-1.11 | DONT_KNOW | abstained | 0 |
| fiesta-eo:vocabulary | A | 3 | NetCDF CF-1.11 | DONT_KNOW | abstained | 0 |
| fiesta-eo:vocabulary | B | 1 | NetCDF CF-1.11 | NetCDF CF-1.11 | correct | 2 |
| fiesta-eo:vocabulary | B | 2 | NetCDF CF-1.11 | NetCDF CF-1.11 | correct | 2 |
| fiesta-eo:vocabulary | B | 3 | NetCDF CF-1.11 | NetCDF CF-1.11 | correct | 2 |

Total cost: $5.05
