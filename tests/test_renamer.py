"""Unit tests for renamer.py (pure Python, no Qt needed).

Run with:  py -3 tests\\test_renamer.py   — or —  py -3 -m pytest tests
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import renamer


def test_split_stem():
    assert renamer.split_stem("FBI") == ("FBI", "")
    assert renamer.split_stem("FBI_hi") == ("FBI", "_hi")
    assert renamer.split_stem("FBI+hi") == ("FBI", "+hi")
    assert renamer.split_stem("FBI_HI") == ("FBI", "_hi")
    assert renamer.split_stem("FBI+Hi") == ("FBI", "+hi")
    assert renamer.split_stem("_hi") == ("_hi", "")
    assert renamer.split_stem("sheriff") == ("sheriff", "")


def test_sanitize_model():
    assert renamer.sanitize_model("  Police2 ") == "police2"
    assert renamer.sanitize_model("po lice/..\\2") == "police2"
    assert renamer.sanitize_model("") == ""


def test_detect_and_plan_example_set(tmp: Path):
    names = ["FBI.ytd", "FBI.yft", "FBI_hi.yft", "FBI+hi.ytd"]
    files = []
    for n in names:
        f = tmp / n
        f.write_bytes(b"x")
        files.append(f)

    collected = renamer.collect_files([tmp])
    assert {f.name for f in collected} == set(names)

    base = renamer.detect_base(collected)
    assert base == "fbi"

    plan = renamer.plan_renames(collected, base, "police2")
    got = {src.name: new for src, new in plan}
    assert got == {
        "FBI.ytd": "police2.ytd",
        "FBI.yft": "police2.yft",
        "FBI_hi.yft": "police2_hi.yft",
        "FBI+hi.ytd": "police2+hi.ytd",
    }


def test_mixed_model_and_xml_set(tmp: Path):
    names = ["FBI.yft", "FBI.ytd", "FBI_hi.yft", "FBI+hi.ytd", "FBI.xml", "FBI_hi.xml"]
    for n in names + ["carcols.xml"]:
        (tmp / n).write_bytes(b"x")
    files = renamer.collect_files([tmp])

    groups = renamer.group_by_base(files)
    assert set(groups) == {"fbi", "carcols"}
    assert len(groups["fbi"]) == 6

    assert renamer.detect_base(files) == "fbi"

    plan = renamer.plan_renames(files, "fbi", "police2")
    got = {src.name: new for src, new in plan}
    assert got == {
        "FBI.yft": "police2.yft",
        "FBI.ytd": "police2.ytd",
        "FBI_hi.yft": "police2_hi.yft",
        "FBI+hi.ytd": "police2+hi.ytd",
        "FBI.xml": "police2.xml",
        "FBI_hi.xml": "police2_hi.xml",
    }
    assert "carcols.xml" not in got


def test_mixed_sets_and_foreign_files(tmp: Path):
    for n in ["FBI.ytd", "FBI.yft", "FBI_hi.yft", "police.ytd", "readme.txt"]:
        (tmp / n).write_bytes(b"x")
    files = renamer.collect_files([tmp])

    groups = renamer.group_by_base(files)
    assert set(groups) == {"fbi", "police"}
    assert len(groups["fbi"]) == 3 and len(groups["police"]) == 1

    assert renamer.detect_base(files) == "fbi"

    plan = renamer.plan_renames(files, "fbi", "sheriff")
    assert {new for _, new in plan} == {"sheriff.ytd", "sheriff.yft", "sheriff_hi.yft"}
    plan2 = renamer.plan_renames(files, "police", "fbi2")
    assert {new for _, new in plan2} == {"fbi2.ytd"}


def test_routes_to_els():
    xml, yft = Path("FBI.xml"), Path("FBI.yft")
    assert not renamer.routes_to_els(xml, False, True)
    assert not renamer.routes_to_els(xml, True, False)
    assert not renamer.routes_to_els(yft, True, True)
    assert renamer.routes_to_els(xml, True, True)
    assert renamer.routes_to_els(xml, True, True, is_els_xml=lambda p: True)
    assert not renamer.routes_to_els(xml, True, True, is_els_xml=lambda p: False)


def test_empty_and_edge_cases(tmp: Path):
    assert renamer.collect_files([]) == []
    assert renamer.detect_base([]) == ""
    assert renamer.plan_renames([], "fbi", "police") == []
    assert renamer.plan_renames([], "", "police") == []

    f = tmp / "AMBULANCE_HI.YFT"
    f.write_bytes(b"x")
    files = renamer.collect_files([f])
    base = renamer.detect_base(files)
    assert base == "ambulance"
    plan = renamer.plan_renames(files, base, "Police4")
    assert plan[0][1] == "police4_hi.yft"


def main() -> int:
    failures = 0
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        tests = [
            (test_split_stem, False),
            (test_sanitize_model, False),
            (test_detect_and_plan_example_set, True),
            (test_mixed_model_and_xml_set, True),
            (test_mixed_sets_and_foreign_files, True),
            (test_routes_to_els, False),
            (test_empty_and_edge_cases, True),
        ]
        for i, (fn, needs_tmp) in enumerate(tests):
            sub = root / f"t{i}"
            sub.mkdir()
            try:
                fn(sub) if needs_tmp else fn()
                print(f"PASS  {fn.__name__}")
            except AssertionError as exc:
                failures += 1
                print(f"FAIL  {fn.__name__}: {exc}")
    print("OK" if failures == 0 else f"{failures} test(s) failed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
