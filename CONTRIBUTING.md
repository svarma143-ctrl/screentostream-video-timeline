# Contributing

Thanks for taking a look. This is a small draft schema, and focused changes are
welcome.

## Development

```bash
uv sync --extra dev
uv run pytest -q
uv run python -m video_timeline examples/*.json
uvx ruff check src tests
uvx ruff format --check src tests
```

Or run everything at once:

```bash
make check
```

CI runs the suite on Python 3.10 and 3.12, and separately installs the built
wheel in a clean virtual environment to prove the schema travels with the
package.

## Schema changes

- Keep the core portable. Put vendor-specific fields under `extensions`.
- Add or update an example when you add a field.
- Add a test for every new semantic rule.
- Treat `schema_version` as a contract: add optional fields in a minor release;
  use a new version for breaking changes.
- Do not put personal data, tokens, secrets, or live inventory promises in an
  example.

## Pull requests

- Explain what changed and why it matters to a builder.
- Keep the diff focused.
- Make sure CI passes.
