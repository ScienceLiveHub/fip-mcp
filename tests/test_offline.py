"""Offline tests: synthetic FIPs and targets, no network."""
from __future__ import annotations

import json

import pytest

from fip_mcp import facts, lookup, target
from fip_mcp.checks import check
from fip_mcp.crosswalk import crosswalk
from fip_mcp.fip import Declaration, Fip, Resource
from fip_mcp.nanopub import np_id
from fip_mcp import questions
from fip_mcp.questions import is_principle, principle_sort_key, principles_for


# What the resource nanopubs say about some resources (links, schema:url).
RESOURCE_META = {
    "Zenodo": {"links": ["https://zenodo.org/"]},
    "NIRD-RDA": {"url": "https://archive.sigma2.no/dataset/x"},
}


def res(label):
    return Resource(uri=f"https://example.org/{label}", label=label, **RESOURCE_META.get(label, {}))


def decl(qid, *labels, no_choice=False, planned=()):
    """A declaration as fip.load builds it; principle/text would come from the ontology."""
    p = "" if qid.startswith("FIP-S") else qid.split("-")[0]
    axis = questions._axis(qid)
    text = f"question {qid}"
    use = {}
    if labels:
        use["current"] = [res(x) for x in labels]
    if planned:
        use["planned"] = [res(x) for x in planned]
    return Declaration(uri="u", question=qid, principle=p, axis=axis, text=text,
                       no_choice=no_choice or not use, use=use)


def make_fip(label, *decls, object_type="https://w3id.org/gff/rao/terms/Spatial-data"):
    return Fip(uri="https://w3id.org/np/RAtest", label=label, description="", version="1", created="",
               community="", case_study="", object_type=object_type, index="", version_chain=[],
               declarations=list(decls))


EO = make_fip(
    "EO",
    decl("F1-D", "DOI"),
    decl("F4-D", "NIRD-RDA", "Zenodo"),
    decl("I1-D", "NetCDF"),
    decl("R1.1-D", "CC BY 4.0"),
    decl("F2", "RO-Crate", "NetCDF CF-1.11"),
    decl("R1.2-D", "NetCDF CF-1.11"),
    decl("A2"),
    decl("FIP-S-Question-Validation-Service", planned=("FAIROS",)),
)


def zenodo_tiff():
    return target.Target(ref="z", kind="zenodo", object_type="dataset", dois=["10.5281/zenodo.1"],
                         repositories=["Zenodo"], repository_hosts=["zenodo.org"],
                         registration_agencies=["DataCite"], licences=["CC-BY-4.0"], access="open",
                         files=["melt_ponds.tif"], urls=["https://zenodo.org/records/1"])


# Stand-ins for the public registries, with the answers they give live.
WIKIDATA = {
    "netcdf": {"Q1361922": {"extensions": ["nc"], "media_types": ["application/netcdf"], "id_patterns": [],
                            "label": "netCDF"}},
    "doi": {"Q25670": {"extensions": [], "media_types": [], "id_patterns": [r"([^/\p{C}]+)/([^\p{C}]+)"],
                       "label": "Digital Object Identifier"},
            "Q5288585": {"extensions": [], "media_types": [], "id_patterns": [], "label": "Doi"}},
    "zarr": {"Q130377195": {"extensions": ["zarr"], "media_types": ["application/vnd.zarr"], "id_patterns": [],
                            "label": "Zarr"},
             "Q130377196": {"extensions": ["zarr"], "media_types": [], "id_patterns": [], "label": "Zarr (other)"}},
}
SPDX = [{"licenseId": "CC-BY-4.0", "name": "Creative Commons Attribution 4.0 International",
         "seeAlso": ["https://creativecommons.org/licenses/by/4.0/legalcode"]},
        {"licenseId": "NetCDF", "name": "NetCDF license", "seeAlso": []},
        {"licenseId": "MIT", "name": "MIT License", "seeAlso": []}]


@pytest.fixture(autouse=True)
def offline_registries(monkeypatch):
    by_qid = {q: c for hits in WIKIDATA.values() for q, c in hits.items()}
    monkeypatch.setattr(lookup, "wikidata_search", lambda label: sorted(WIKIDATA.get(label.lower(), {})))
    monkeypatch.setattr(lookup, "wikidata_claims", lambda qids: {q: by_qid[q] for q in qids if q in by_qid})
    monkeypatch.setattr(lookup, "spdx_licences", lambda: SPDX)
    monkeypatch.setattr(lookup, "doi_agency", lambda doi: "DataCite" if doi.startswith("10.5281/") else "")
    monkeypatch.setattr(lookup, "datacite_repository", lambda doi: (
        {"name": "Zenodo", "url": "https://zenodo.org/"} if doi.startswith("10.5281/") else {}))
    facts._FACTS.clear()
    yield
    facts._FACTS.clear()


def by_q(report):
    return {r["question"]: r for r in report["results"]}


def test_np_id_strips_fragment_and_subpath():
    assert np_id("https://w3id.org/np/RAabc#FITS") == "https://w3id.org/np/RAabc"
    assert np_id("https://w3id.org/np/RAabc/FITS") == "https://w3id.org/np/RAabc"


QUESTION_TRIG = """@prefix fip: <https://w3id.org/fair/fip/terms/> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
<https://w3id.org/np/RAq/assertion> {
  fip:FIP-Question-R1.1-D fip:refers-to-principle <https://w3id.org/fair/principles/terms/R1.1> ;
    skos:definition "Which usage license do you use for your datasets?" .
}"""


def test_question_info_reads_the_ontology(monkeypatch):
    from rdflib import Dataset

    def fake_fetch(uri):
        if not uri.endswith("FIP-Question-R1.1-D"):
            raise questions.nanopub.NanopubError("not defined")
        ds = Dataset(default_union=True)
        ds.parse(data=QUESTION_TRIG, format="trig")
        return ds

    monkeypatch.setattr(questions.nanopub, "fetch", fake_fetch)
    questions.question_info.cache_clear()
    questions.principle_text.cache_clear()
    assert questions.question_info("R1.1-D") == ("R1.1", "data", "Which usage license do you use for your datasets?")
    assert questions.question_info("A2-metadata-preservation-policy") == ("", "both", "A2-metadata-preservation-policy")
    assert questions.question_info("FIP-S-Question-Web-API")[1] == "supporting"
    qs = {"Which usage license do you use for your datasets?": "R1.1"}
    assert principles_for("licenses", qs) == ["R1.1"]
    assert principles_for("i2", qs) == ["I2"]
    with pytest.raises(KeyError):
        principles_for("colour", qs)
    questions.question_info.cache_clear()
    questions.principle_text.cache_clear()


def test_principle_order():
    keys = ["R1.2", "A2", "I1", "F4", "A1.2", "F1", "R1.1"]
    assert sorted(keys, key=principle_sort_key) == ["F1", "F4", "A1.2", "A2", "I1", "R1.1", "R1.2"]
    assert is_principle("A1.1") and not is_principle("unplaced") and not is_principle("FIP-S-Question-X")


def test_check_statuses():
    r = by_q(check(EO, zenodo_tiff()))
    assert r["F1-D"]["status"] == "pass"                 # DOI pattern from Wikidata Q25670
    assert r["F4-D"]["status"] == "pass"                 # Zenodo's own link host = record host
    assert [e["result"] for e in r["F4-D"]["evidence"]] == ["fail", "pass"]   # NIRD fails, Zenodo passes
    assert r["I1-D"]["status"] == "fail" and "fix" in r["I1-D"]   # .nc from Wikidata, none present
    assert r["R1.1-D"]["status"] == "pass"               # CC BY 4.0 -> SPDX by name
    assert r["F2"]["status"] == "fail"                   # RO-Crate (config file name) absent; CF manual
    assert r["R1.2-D"]["status"] == "manual"             # nothing testable known for NetCDF CF-1.11
    assert r["A2"]["status"] == "no-choice"
    assert r["FIP-S-Question-Validation-Service"]["status"] == "planned-only"


def test_facts_record_their_sources():
    f = facts.facts_for(res("NetCDF"))
    assert f.extensions == ["nc"] and any("Wikidata Q1361922" in s for s in f.sources)
    assert facts.facts_for(res("RO-Crate")).files == ["ro-crate-metadata.json"]
    assert facts.facts_for(res("CC BY 4.0")).spdx == "CC-BY-4.0"


def test_ambiguous_wikidata_label_is_not_used():
    f = facts.facts_for(res("Zarr"))
    assert f.extensions == [] and "ambiguous" in f.notes[0]


def test_spdx_name_clash_does_not_make_a_format_a_licence():
    # SPDX has a licence called "NetCDF"; only R1.1 questions test licences.
    netcdf = make_fip("x", decl("I1-D", "NetCDF"))
    t = zenodo_tiff()
    t.files = ["a.nc"]
    assert by_q(check(netcdf, t))["I1-D"]["status"] == "pass"


def test_undeclared_extensions_and_software_warning():
    rep = check(EO, zenodo_tiff())
    assert rep["undeclaredExtensions"] == {"tif": ["melt_ponds.tif"]}
    assert rep["warnings"] == []
    sw = zenodo_tiff()
    sw.object_type = "software"
    assert check(EO, sw)["warnings"]


def test_crosswalk():
    astro = make_fip("Astro", decl("F1-D", "DOI"), decl("I1-D", "Flexible Image Transport System"),
                     decl("R1.1-D", "CC BY 4.0", "CC0 1.0"), decl("A2"))
    rows = {r["question"]: r for r in crosswalk(astro, EO)["rows"]}
    assert rows["F1-D"]["status"] == "same"
    assert rows["I1-D"]["status"] == "differs"
    assert rows["R1.1-D"]["status"] == "overlap"
    assert rows["F4-D"]["status"] == "only-target-chose"
    assert rows["A2"]["status"] == "neither-chose"


def test_local_target(tmp_path):
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "x.nc").write_bytes(b"")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "y.nc").write_bytes(b"")
    (tmp_path / "LICENSE").write_text("Creative Commons Attribution 4.0 International Public License")
    (tmp_path / "CITATION.cff").write_text('cff-version: 1.2.0\ndoi: "10.5281/zenodo.42"\n')
    (tmp_path / "ro-crate-metadata.json").write_text(json.dumps({"@graph": []}))
    t = target.load(str(tmp_path))
    assert t.files == ["CITATION.cff", "LICENSE", "data/x.nc", "ro-crate-metadata.json"]
    assert t.dois == ["10.5281/zenodo.42"] and t.repositories == ["Zenodo"]
    assert t.repository_hosts == ["zenodo.org"] and t.registration_agencies == ["DataCite"]
    assert t.licences == ["CC-BY-4.0"]                    # licence text -> SPDX name
    r = by_q(check(EO, t))
    assert r["I1-D"]["status"] == "pass" and r["F2"]["status"] == "pass"


# --- R-FIPs and compare -------------------------------------------------------------

from fip_mcp.compare import compare, to_xlsx  # noqa: E402


def rfip(label, *rows):
    """An R-FIP as fip.load builds it from Nanodash's query: (resource, principle, relation) rows."""
    decls = [Declaration(uri=f"https://example.org/decl/{name}", question=p or "unplaced", principle=p,
                         axis="both" if p else "unknown", text="", no_choice=False,
                         use={"recommended": [Resource(uri=f"https://example.org/{name}", label=name)]},
                         placement="ontology", relation=rel)
             for name, p, rel in rows]
    f = make_fip(label, *decls)
    f.kind = "R-FIP"
    return f


TARGET = rfip("Target", ("DOI", "F1", "enables"), ("DOI", "F3", "enables"), ("RO-Crate", "F2", "enables"),
              ("ROHub", "F2", "supports"), ("ROHub", "F4", "enables"), ("Zarr v3", "I1", "enables"),
              ("FAIROs", "I2", "supports"), ("Mystery", "", ""))
AS_IS = make_fip("As-Is", decl("F1-D", no_choice=True), decl("I1-D", "NetCDF"), decl("I1-MD", "XML"),
                 decl("R1.1-D", "CC BY 4.0"), decl("R1.1-MD", "CC BY 4.0"))


def rows_of(result):
    return {r["key"]: [c["text"] for c in r["cells"]] for r in result["rows"]}


def test_compare_rows_relations_and_coverage():
    res = compare([TARGET, AS_IS], names=["R-FIP", "FIP"])
    rows = rows_of(res)
    assert [r["key"] for r in res["rows"]] == ["F1", "F2", "F3", "F4", "I1", "I2", "R1.1", "unplaced"]
    assert rows["F1"] == ["DOI", "— (left open)"]
    assert rows["F2"] == ["RO-Crate, ROHub (supports)", "—"]           # enables listed before supports
    assert rows["I1"] == ["Zarr v3", "NetCDF (data), XML (metadata)"]
    assert rows["R1.1"] == ["—", "CC BY 4.0"]                          # data + metadata collapse
    assert rows["unplaced"][0] == "Mystery"
    assert res["principlesCovered"] == ["6 / 7", "2 / 7"]
    assert [p["name"] for p in res["profiles"]] == ["R-FIP", "FIP"]


def test_compare_enables_only():
    rows = rows_of(compare([TARGET, AS_IS], include_supports=False))
    assert rows["F2"][0] == "RO-Crate"
    assert "I2" not in rows                                              # FAIROs only supports I2


def test_compare_xlsx(tmp_path):
    pytest.importorskip("openpyxl")
    from openpyxl import load_workbook

    path = to_xlsx(compare([TARGET, AS_IS], names=["R-FIP", "FIP"]), str(tmp_path / "c.xlsx"))
    ws = load_workbook(path)["Comparison"]
    assert [c.value for c in ws[1]] == ["FAIR Principle", "R-FIP", "FIP"]
    assert ws.cell(row=2, column=1).value == "F1"
    last = [r for r in ws.iter_rows(values_only=True) if r[0] == "Principles Covered"]
    assert last == [("Principles Covered", "6 / 7", "2 / 7")]


def test_crosswalk_with_rfip_is_per_principle():
    out = crosswalk(AS_IS, TARGET)
    assert out["level"] == "principle"
    rows = {r["question"]: r for r in out["rows"]}
    assert rows["I1"]["status"] == "differs" and rows["F1"]["status"] == "only-target-chose"
