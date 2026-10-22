# Video-to-Geospatial Timeline Schema

[![CI](https://github.com/svarma143-ctrl/screentostream-video-timeline/actions/workflows/ci.yml/badge.svg)](https://github.com/svarma143-ctrl/screentostream-video-timeline/actions/workflows/ci.yml)

A small, vendor-neutral JSON Schema for **shoppable/bookable video**: map time
ranges in a video to the places, scenes, evidence, and optional offers they
contain.

**Status:** `0.1.0` draft · **License:** MIT · **Created:** 2026-10-22, during
the Build, Ship, Shape hackathon submission window

This is a standalone schema project extracted from the working
[ScreenToStream Concierge](https://github.com/svarma143-ctrl/screentostream-concierge)
demo. It contains the portable data contract, examples, a validator, and tests.
It does **not** contain the concierge server, travel inventory, pricing engine,
or booking implementation.

---

## Why this exists

A video is a rich intent signal. A guest sees a lantern-lit alley, a market
stall, or a dish and says, “book a weekend there.” Most media metadata describes
the video; it does not describe the **transaction seam** between a moment on
screen and a place or offer a developer can act on.

This schema captures that seam in a form that is:

- **time-addressed** — every moment has a start and end in the video;
- **geospatial** — a moment can resolve to a place with coordinates;
- **evidence-backed** — captions, frames, OCR, transcripts, or manual notes;
- **bookable, but not a booking engine** — optional catalog references, not
  live inventory guarantees;
- **portable** — no vendor-specific fields are required, and `extensions` is
  available when they are;
- **MCP-friendly** — an MCP tool can return this payload without inventing a
  new shape for every content partner.

It is not a travel API, a payment flow, or a replacement for Alexa+ native
travel planning. It is a payload contract for the content-to-transaction layer.

---

## Quick start

```bash
git clone https://github.com/svarma143-ctrl/screentostream-video-timeline.git
cd screentostream-video-timeline

uv sync --extra dev
uv run pytest -q
uv run python -m video_timeline examples/*.json
```

Without `uv`:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
pytest -q
python -m video_timeline examples/*.json
```

Expected output:

```text
OK   examples/kyoto-pontocho.json
OK   examples/minimal.json
```

Validate your own document:

```bash
python -m video_timeline path/to/timeline.json
```

---

## A minimal document

```json
{
  "$schema": "../schema/video-to-geospatial-timeline.schema.json",
  "schema_version": "0.1.0",
  "media": {
    "title": "Market at Dawn",
    "duration_seconds": 120
  },
  "timeline": [
    {
      "id": "moment_001",
      "start_seconds": 12,
      "end_seconds": 28,
      "label": "The market wakes up",
      "scene": { "title": "Market at Dawn" },
      "place": {
        "name": "Oaxaca de Juárez",
        "country": "Mexico",
        "country_code": "MX"
      },
      "confidence": 0.72
    }
  ]
}
```

See [`examples/kyoto-pontocho.json`](examples/kyoto-pontocho.json) for a fuller
example with coordinates, evidence, bookable references, provenance, and MCP
integration hints. The example uses the ScreenToStream demo catalog; the schema
itself is domain-neutral.

---

## Schema at a glance

| Field | Required | What it means |
| :--- | :---: | :--- |
| `schema_version` | yes | Contract version. This draft is `0.1.0`. |
| `id` | no | Stable document id. |
| `media` | yes | Video identity and duration. |
| `timeline` | yes | One or more time-addressed moments. |
| `generated_at` | no | ISO 8601 timestamp for the extraction. |
| `generator` | no | Tool name, version, method, and URL. |
| `provenance` | no | Source, license, method, and observation time. |
| `integrations` | no | Optional MCP server/tool and booking provider hints. |
| `extensions` | no | Vendor-specific data outside the portable core. |

### `media`

| Field | Required | Notes |
| :--- | :---: | :--- |
| `title` | yes | Human-readable title. |
| `duration_seconds` | yes | Positive number. Timeline entries must stay inside it. |
| `episode` | no | Episode or segment label. |
| `language` | no | BCP 47-style language tag. |
| `source` | no | Catalog id, CMS, capture device, or other origin. |
| `external_ids` | no | String-to-string map of external identifiers. |

### `timeline[]`

| Field | Required | Notes |
| :--- | :---: | :--- |
| `id` | yes | Stable, namespaced moment id. |
| `start_seconds` | yes | Start offset in the video. |
| `end_seconds` | yes | Must be greater than `start_seconds`. |
| `start_timecode` / `end_timecode` | no | Display-friendly `HH:MM:SS.mmm` values. |
| `label` | no | Short human-readable label. |
| `scene` | yes | Scene title, summary, subjects, visual hints. |
| `place` | yes | Place name plus optional geography. |
| `bookable` | no | Optional offers or catalog anchors. |
| `evidence` | no | Captions, frames, OCR, transcripts, or manual notes. |
| `confidence` | yes | Calibrated `0..1` confidence. |
| `provenance` | no | Entry-specific provenance. |
| `extensions` | no | Entry-specific vendor data. |

### `place`

`name` is required. Optional fields are `destination_id`, `city`, `region`,
`country`, `country_code` (ISO 3166-1 alpha-2, uppercase), `timezone`,
`coordinates` (`latitude`/`longitude`), and `accuracy_meters`.

### `bookable[]`

`kind` is one of `stay`, `experience`, `dining`, `activity`, `product`, or
`other`. `catalog_ref` is required and must be a stable provider reference, not
a price or a transient URL. Optional fields are `name`, `provider`, `url`,
`price` (`amount`, `currency`, optional `unit`), `availability`, and `metadata`.

**Important:** `availability` is a hint, not a live inventory guarantee. The
schema deliberately separates “this moment is bookable through this reference”
from “this offer is currently available at this price.”

### `evidence[]`

`kind` is one of `caption`, `transcript`, `frame`, `ocr`, `manual`, `model`, or
`other`. Each item must include either `text` or `uri`. Optional fields are
`confidence`, `model`, and `observed_at`.

Use evidence when confidence is below `1.0`. A confidence score without evidence
is hard to audit and easy to over-trust.

---

## Validation rules

The JSON Schema checks shape, types, enums, and ranges. The validator adds these
semantic rules:

- `end_seconds` must be greater than `start_seconds`;
- entries must be ordered and must not overlap;
- entries must fit inside `media.duration_seconds`;
- `confidence` must be between `0` and `1`;
- coordinates must be valid latitude/longitude values;
- `country_code` must be two uppercase letters;
- currency codes must be three uppercase letters;
- core objects reject unknown fields; use `extensions` for vendor data.

Run the validator on every example in CI:

```bash
uv run python -m video_timeline examples/*.json
```

The test suite also covers invalid documents, so the validator is tested against
the failures it is meant to catch.

---

## Integration with MCP

The schema is designed to be a tool result or a resource payload. A typical MCP
flow is:

```text
Fire TV frame / playback position
        │
        ▼
get_viewing_context
        │  returns a Video-to-Geospatial Timeline entry
        ▼
plan_trip / quote_trip
        │  reads place + bookable references
        ▼
book_trip
        │  uses the stable catalog_ref, never a scraped price
        ▼
TV card + calendar export
```

The `integrations.mcp` block is optional. It lets a document point at the server
and tools that can resolve the context or execute a booking without turning the
schema into an MCP-specific format.

Example:

```json
{
  "integrations": {
    "mcp": {
      "server": "https://concierge.example.com/mcp",
      "tools": ["get_viewing_context", "plan_trip", "quote_trip", "book_trip"]
    },
    "booking": {
      "provider": "ScreenToStream Concierge demo",
      "tool": "book_trip"
    }
  }
}
```

---

## Design principles

1. **Time is authoritative.** `start_seconds` and `end_seconds` are the source
   of truth. Timecodes are display helpers.
2. **Observation is separate from offer.** A place or dish is an observation.
   A catalog reference is an optional commercial anchor. Do not mix them.
3. **Confidence needs evidence.** Store captions, frames, OCR, transcripts, or a
   manual note so a downstream agent can audit the match.
4. **No live inventory promises.** `availability` is a hint. Quote and booking
   state belong in the provider's transactional system.
5. **No personal data in the core.** Do not put names, accounts, or tokens in a
   timeline document. Use `extensions` only if your deployment has a separate
   privacy review.
6. **Portable first.** Add vendor fields under `extensions`, not as required
   core fields.
7. **Forward-compatible.** Minor versions add optional fields; breaking changes
   require a new schema version.

---

## Repository layout

```text
schema/      JSON Schema 2020-12 contract
examples/    Valid minimal and full documents
src/         Python loader and semantic validator
tests/       Valid and invalid document tests
```

---

## Related project

[ScreenToStream Concierge](https://github.com/svarma143-ctrl/screentostream-concierge)
is the reference implementation: a self-hosted Alexa+ MCP server that turns a
Fire TV viewing moment into a planned, quoted, and simulated-booked weekend.
This schema is the reusable, standalone piece of that content-to-transaction
seam.

It is deliberately separate from the primary Alexa+ project so other builders
can reuse the data contract without taking on the server, the demo catalog, or
the booking implementation. It is the additional open-source artifact submitted
alongside the Alexa+ primary entry.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the development loop and schema
change rules.

---

## License

MIT. See [LICENSE](LICENSE).
