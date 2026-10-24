# Changelog

## 0.1.1 — 2026-10-24

- Bundle the JSON Schema into the wheel so the installed validator can resolve
  it outside a source checkout.
- Reject duplicate `timeline[].id` values in the semantic pass.
- Report unreadable or malformed JSON as a clean CLI failure instead of a
  traceback.
- Add CLI, duplicate-id, ordering, evidence, country-code, and schema-version
  tests.
- Run Ruff and the test matrix (Python 3.10 and 3.12) in CI, plus a job that
  installs the built wheel in a clean environment and validates an example.

## 0.1.0 — 2026-10-22

- Initial draft of the Video-to-Geospatial Timeline JSON Schema.
- Added media, timeline, place, scene, evidence, bookable, provenance, and MCP
  integration fields.
- Added semantic validation for ordering, overlap, duration, confidence, and
  coordinate bounds.
- Added minimal and full examples, tests, and CI.
