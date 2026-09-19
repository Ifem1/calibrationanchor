.PHONY: test preflight lint

test:
	gltest tests/direct -v -s

preflight:
	python scripts/preflight.py

lint:
	genvm-lint validate contracts/calibrationanchor.py
	genvm-lint validate contracts/calibration_gate.py
