"""Offline tests: synthetic FIPs and targets, no network."""
from __future__ import annotations

import json

import pytest

from fip_mcp import target
from fip_mcp.checks import check, format_names
from fip_mcp.crosswalk import crosswalk
from fip_mcp.fip import Declaration, Fip, Resource
from fip_mcp.nanopub import np_id
from fip_mcp.questions import principles_for, question_info


def decl(qid, *labels, no_choice=False, planned=()):
    p, axis, text = question_info(qid)
    use = {}
    if labels:
        use["current"] = [Resource(uri=f"https://example.org/{x}", label=x) for x in labels]
    if planned:
        use["planned"] = [Resource(uri=f"https://example.org/{x}", label=x) for x in planned]
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
                         repositories=["Zenodo"], licences=["CC-BY-4.0"], access="open",
                         files=["melt_ponds.tif"], urls=["https://zenodo.org/records/1"])


def by_q(report):
    return {r["question"]: r for r in report["results"]}


def test_np_id_strips_fragment_and_subpath():
    assert np_id("https://w3id.org/np/RAabc#FITS") == "https://w3id.org/np/RAabc"
    assert np_id("https://w3id.org/np/RAabc/FITS") == "https://w3id.org/np/RAabc"


def test_question_info_and_topics():
    assert question_info("I1-D") == ("I1", "data", question_info("I1-D")[2])
    assert question_info("F2")[1] == "both"
    assert question_info("FIP-S-Question-Web-API")[1] == "supporting"
    assert principles_for("license") == ["R1.1"]
    assert principles_for("I2") == ["I2"]
    with pytest.raises(KeyError):
        principles_for("colour")


def test_check_statuses():
    r = by_q(check(EO, zenodo_tiff()))
    assert r["F1-D"]["status"] == "pass"
    assert r["F4-D"]["status"] == "pass"                 # any declared repository is enough
    assert r["I1-D"]["status"] == "fail" and "fix" in r["I1-D"]
    assert r["R1.1-D"]["status"] == "pass"
    assert r["F2"]["status"] == "fail"                   # RO-Crate checkable and absent; CF manual
    assert r["R1.2-D"]["status"] == "manual"             # CF needs file attributes: never guessed
    assert r["A2"]["status"] == "no-choice"
    assert r["FIP-S-Question-Validation-Service"]["status"] == "planned-only"


def test_off_profile_formats_and_software_warning():
    rep = check(EO, zenodo_tiff())
    assert rep["offProfileFormats"] == {"TIFF": ["melt_ponds.tif"]}
    assert rep["warnings"] == []
    sw = zenodo_tiff()
    sw.object_type = "software"
    assert check(EO, sw)["warnings"]


def test_format_names_from_fer_labels():
    assert format_names(["Network Common Data Form"]) == {"NetCDF"}
    assert format_names(["Flexible Image Transport System"]) == {"FITS"}
    assert format_names(["NetCDF CF-1.11"]) == {"NetCDF"}


def test_crosswalk():
    astro = make_fip("Astro", decl("F1-D", "DOI"), decl("I1-D", "Flexible Image Transport System"),
                     decl("R1.1-D", "CC BY 4.0", "CC0 1.0"), decl("A2"))
    rows = {r["question"]: r for r in crosswalk(astro, EO)["rows"]}
    assert rows["F1-D"]["status"] == "same"
    assert rows["I1-D"]["status"] == "differs" and rows["I1-D"]["conversion"]
    assert rows["R1.1-D"]["status"] == "overlap"
    assert rows["F4-D"]["status"] == "only-target-chose"
    assert rows["A2"]["status"] == "neither-chose"


def test_local_target(tmp_path):
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "x.nc").write_bytes(b"")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "y.nc").write_bytes(b"")
    (tmp_path / "LICENSE").write_text("Creative Commons Attribution 4.0 International")
    (tmp_path / "CITATION.cff").write_text('cff-version: 1.2.0\ndoi: "10.5281/zenodo.42"\n')
    (tmp_path / "ro-crate-metadata.json").write_text(json.dumps({"@graph": []}))
    t = target.load(str(tmp_path))
    assert t.files == ["CITATION.cff", "LICENSE", "data/x.nc", "ro-crate-metadata.json"]
    assert t.dois == ["10.5281/zenodo.42"] and t.repositories == ["Zenodo"]
    assert t.licences == ["CC-BY-4.0"] and t.has_ro_crate
    r = by_q(check(EO, t))
    assert r["I1-D"]["status"] == "pass" and r["F2"]["status"] == "pass"
