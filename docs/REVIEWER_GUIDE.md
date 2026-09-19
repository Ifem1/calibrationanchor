# Reviewer guide

CalibrationAnchor is not a frontend project and not a generic "AI decides X" wrapper.

The reusable primitive is the **calibration protocol** around semantic consensus:

1. a benchmark definition is sealed;
2. pinned web inputs are separated from semantic behaviour;
3. validators independently reproduce bounded case outcomes;
4. deterministic code aggregates coverage and agreement;
5. repeated runs build comparable behaviour hashes;
6. another IC can fail closed when the latest calibration is not stable.

## What to inspect first

- `contracts/calibrationanchor.py` — source of truth.
- `_pin_web_source` — validator-reproduced source pinning.
- `_case_consensus` — validator-reproduced semantic case execution.
- `finalize_run` — deterministic calibration arithmetic.
- `is_latest_stable` — narrow reuse surface.
- `contracts/calibration_gate.py` — minimal consumer.
- `tests/direct/test_hardening.py` — forged leader results, source drift and hostile text.

## Suggested live proof

Use a four-case suite:

- three static benchmark cases;
- one pinned public web case.

Run 1 should be fully stable.

Then demonstrate source-drift isolation with a separate intentionally mutable fixture or a second suite whose pinned source has changed. The contract must report `INPUT_DRIFT`, reduce coverage and refuse to call that a semantic model flip.

Finally deploy `CalibrationGate` against a stable run, open it successfully, then create a later suite run containing a critical semantic flip and show a fresh gate cannot open.

Never fabricate live proof. `proof/` should contain only real finalized addresses, transaction IDs and readbacks.
