.PHONY: test smoke validate verify clean

test:
	python -m pytest

smoke:
	PYTHONPATH=src MEL_LLM_PROVIDER=mock python -m mel_governor.cli --question "How should evidence, interpretation, and normative judgment be distinguished?" --output artifacts/smoke >/dev/null

validate:
	PYTHONPATH=src python tools/validate_release.py --write-evidence

verify: test smoke validate

clean:
	rm -rf artifacts release_evidence .pytest_cache src/*.egg-info
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
