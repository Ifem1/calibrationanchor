# Architecture

## Components

CalibrationAnchor separates semantic judgement from protocol mechanics.

### 1. Suite definition

The suite owner defines thresholds and cases while the suite is `DRAFT`. At least three cases are required before sealing. Sealing computes a `suite_hash` over ordered case definitions and all scoring thresholds. The suite cannot be edited afterwards.

### 2. Case inputs

Static cases store immutable context directly in contract state.

Pinned-web cases fetch and normalize a public HTTPS page at creation time. A custom validator independently fetches the same page and accepts the pin only when the normalized content hash agrees.

### 3. Calibration runs

Only one run may be open for a suite at a time. Opening is permissionless. Each case can then be executed exactly once by any caller.

The semantic output space is deliberately bounded to `SUPPORTED`, `NOT_SUPPORTED`, and `AMBIGUOUS`.

### 4. Deterministic aggregation

Semantic results are converted to protocol outcomes, then weighted counters are maintained in state. Finalization computes coverage, agreement, flip and uncertainty basis points with integer arithmetic.

Final calibration state is entirely deterministic.

### 5. Reuse boundary

`is_latest_stable(suite_id, expected_suite_hash, min_run_id)` is the narrow consumer interface. A downstream IC does not need to understand prompts, web evidence or score arithmetic.

## Why web input drift has its own state

Without source hashing, a benchmark can appear to regress because the source itself changed. CalibrationAnchor refuses to mix these failure modes.

A pinned-web case therefore has three runtime paths:

```text
fetch fails
  -> UNAVAILABLE

fetch succeeds, hash changed
  -> INPUT_DRIFT

fetch succeeds, hash matches
  -> semantic consensus
```

Only the third path contributes to agreement scoring.

## Why there is no automatic benchmark authoring

The benchmark suite is a trust object. Letting an LLM author the gold labels would make the system circular: the same class of model being measured would define what counts as correct.

CalibrationAnchor instead makes authorship explicit and cryptographically binds the suite. Consumers choose which suite hash they trust.
