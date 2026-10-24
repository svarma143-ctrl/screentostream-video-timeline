from __future__ import annotations

import copy
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from video_timeline import load_schema, validate_document, validate_file
from video_timeline.validate import main

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"


def load_example(name: str = "minimal.json") -> dict:
    return json.loads((EXAMPLES / name).read_text(encoding="utf-8"))


def test_schema_is_valid() -> None:
    Draft202012Validator.check_schema(load_schema())


def test_examples_are_valid() -> None:
    for path in sorted(EXAMPLES.glob("*.json")):
        assert validate_file(path) == [], path


def test_missing_place_is_rejected() -> None:
    document = load_example()
    del document["timeline"][0]["place"]
    errors = validate_document(document)
    assert any("place" in error for error in errors)


def test_end_before_start_is_rejected() -> None:
    document = load_example()
    document["timeline"][0]["end_seconds"] = 4
    errors = validate_document(document)
    assert any("end_seconds must be greater" in error for error in errors)


def test_overlapping_entries_are_rejected() -> None:
    document = load_example()
    second = copy.deepcopy(document["timeline"][0])
    second["id"] = "moment_002"
    second["start_seconds"] = 20
    second["end_seconds"] = 40
    document["timeline"].append(second)
    errors = validate_document(document)
    assert any("must not overlap" in error for error in errors)


def test_duration_is_enforced() -> None:
    document = load_example()
    document["timeline"][0]["end_seconds"] = 200
    errors = validate_document(document)
    assert any("exceeds media.duration_seconds" in error for error in errors)


def test_confidence_range_is_enforced() -> None:
    document = load_example()
    document["timeline"][0]["confidence"] = 1.2
    errors = validate_document(document)
    assert any("confidence" in error for error in errors)


def test_coordinate_bounds_are_enforced() -> None:
    document = load_example("kyoto-pontocho.json")
    document["timeline"][0]["place"]["coordinates"]["latitude"] = 91
    errors = validate_document(document)
    assert any("latitude" in error for error in errors)


def test_unknown_core_field_is_rejected() -> None:
    document = load_example()
    document["timeline"][0]["unexpected"] = True
    errors = validate_document(document)
    assert any("unexpected" in error for error in errors)


def test_duplicate_moment_ids_are_rejected() -> None:
    document = load_example()
    second = copy.deepcopy(document["timeline"][0])
    second["start_seconds"] = 40
    second["end_seconds"] = 60
    document["timeline"].append(second)
    errors = validate_document(document)
    assert any("duplicates an earlier entry" in error for error in errors)


def test_out_of_order_entries_are_rejected() -> None:
    document = load_example()
    document["timeline"][0]["start_seconds"] = 70
    document["timeline"][0]["end_seconds"] = 90
    later = copy.deepcopy(document["timeline"][0])
    later["id"] = "moment_002"
    later["start_seconds"] = 30
    later["end_seconds"] = 50
    document["timeline"].append(later)
    errors = validate_document(document)
    assert any("must be sorted after" in error for error in errors)


def test_evidence_requires_text_or_uri() -> None:
    document = load_example("kyoto-pontocho.json")
    document["timeline"][0]["evidence"][0].pop("text")
    errors = validate_document(document)
    assert any("evidence" in error for error in errors)


def test_lowercase_country_code_is_rejected() -> None:
    document = load_example()
    document["timeline"][0]["place"]["country_code"] = "mx"
    errors = validate_document(document)
    assert any("country_code" in error for error in errors)


def test_unknown_schema_version_is_rejected() -> None:
    document = load_example()
    document["schema_version"] = "0.2.0"
    errors = validate_document(document)
    assert any("schema_version" in error for error in errors)


def test_cli_accepts_a_valid_example(capsys) -> None:
    assert main([str(EXAMPLES / "minimal.json")]) == 0
    assert "OK" in capsys.readouterr().out


def test_cli_reports_malformed_json(tmp_path, capsys) -> None:
    broken = tmp_path / "broken.json"
    broken.write_text("{not json", encoding="utf-8")
    assert main([str(broken)]) == 1
    output = capsys.readouterr().out
    assert "FAIL" in output
    assert "could not read JSON" in output
