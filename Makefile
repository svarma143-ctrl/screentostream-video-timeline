.PHONY: test validate lint check

test:
	python -m pytest -q

validate:
	python -m video_timeline examples/*.json

lint:
	uvx ruff check src tests
	uvx ruff format --check src tests

check: lint test validate
