from __future__ import annotations

import copy
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from video_timeline import load_schema, validate_document, validate_file

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
