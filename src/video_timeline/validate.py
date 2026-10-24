"""Validate Video-to-Geospatial Timeline documents.

The JSON Schema handles shape, types, enums, and ranges. A small semantic pass
adds the rules JSON Schema cannot express: time ranges must be positive,
ordered, non-overlapping, and inside the media duration.
"""

from __future__ import annotations

import argparse
import json
from importlib.resources import files
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

SCHEMA_FILENAME = "video-to-geospatial-timeline.schema.json"
ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "schema" / SCHEMA_FILENAME


def _schema_bytes() -> bytes:
    """Return the schema from the installed package, or from the source tree.

    The wheel ships a copy under ``video_timeline/schema/`` so validation works
    outside a checkout. The repository path is the fallback for editable
    installs, where the canonical ``schema/`` directory stays at the repo root.
    """
    packaged = files("video_timeline") / "schema" / SCHEMA_FILENAME
    try:
        return packaged.read_bytes()
    except (FileNotFoundError, OSError):
        return SCHEMA_PATH.read_bytes()


def load_schema() -> dict[str, Any]:
    """Load the canonical schema bundled with this package."""
    return json.loads(_schema_bytes())


def _format_path(error: Any) -> str:
    path = ".".join(str(part) for part in error.absolute_path)
    return path or "<root>"


def _schema_errors(document: dict[str, Any]) -> list[str]:
    validator = Draft202012Validator(load_schema(), format_checker=FormatChecker())
    errors = sorted(
        validator.iter_errors(document), key=lambda error: list(error.absolute_path)
    )
    return [f"{_format_path(error)}: {error.message}" for error in errors]


def _semantic_errors(document: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    media = document.get("media")
    timeline = document.get("timeline")
    if not isinstance(media, dict) or not isinstance(timeline, list):
        return errors

    duration = media.get("duration_seconds")
    previous_end = 0.0
    seen_ids: set[str] = set()

    for index, entry in enumerate(timeline):
        if not isinstance(entry, dict):
            continue
        start = entry.get("start_seconds")
        end = entry.get("end_seconds")
        if not isinstance(start, (int, float)) or not isinstance(end, (int, float)):
            continue

        prefix = f"timeline[{index}]"
        entry_id = entry.get("id")
        if isinstance(entry_id, str):
            if entry_id in seen_ids:
                errors.append(f"{prefix}.id duplicates an earlier entry: {entry_id}")
            seen_ids.add(entry_id)
        if end <= start:
            errors.append(f"{prefix}.end_seconds must be greater than start_seconds")
        if isinstance(duration, (int, float)) and end > duration:
            errors.append(
                f"{prefix}.end_seconds ({end}) exceeds media.duration_seconds ({duration})"
            )
        if start < previous_end:
            errors.append(
                f"{prefix}.start_seconds must be sorted after the previous entry "
                f"and must not overlap it (previous end: {previous_end})"
            )
        previous_end = max(previous_end, float(end))

    return errors


def validate_document(document: dict[str, Any]) -> list[str]:
    """Return a list of human-readable validation errors.

    An empty list means the document is valid.
    """
    errors = _schema_errors(document)
    if errors:
        return errors
    return _semantic_errors(document)


def validate_file(path: str | Path) -> list[str]:
    """Load a JSON file and return validation errors."""
    document = json.loads(Path(path).read_text(encoding="utf-8"))
    return validate_document(document)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate one or more Video-to-Geospatial Timeline JSON documents."
    )
    parser.add_argument("files", nargs="+", help="JSON files to validate")
    args = parser.parse_args(argv)

    failed = False
    for filename in args.files:
        try:
            errors = validate_file(filename)
        except (OSError, json.JSONDecodeError) as exc:
            failed = True
            print(f"FAIL {filename}")
            print(f"  - could not read JSON: {exc}")
            continue
        if errors:
            failed = True
            print(f"FAIL {filename}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"OK   {filename}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
