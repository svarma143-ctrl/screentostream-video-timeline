.PHONY: test validate

test:
	python -m pytest -q

validate:
	python -m video_timeline examples/*.json
