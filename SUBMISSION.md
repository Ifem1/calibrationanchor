# CalibrationAnchor — standalone Intelligent Contract submission

## Purpose

CalibrationAnchor is reusable infrastructure for detecting semantic-consensus regression against an immutable benchmark suite.

It is designed for builders whose contracts depend on judgement that may remain logically unchanged while the validator/model environment evolves.

## Why GenLayer is necessary

Ordinary deterministic contracts cannot independently interpret natural-language benchmark contexts. A centralized benchmark server can, but then the server becomes the source of truth.

CalibrationAnchor uses GenLayer consensus only for the parts that require judgement:

- pinning a live public source by independently observed hash;
- deciding a frozen proposition against frozen context;
- reproducing that decision independently in validators.

Scoring, thresholds, critical-case handling, input-drift separation, state transitions and consumer eligibility are deterministic.

## Reusable primitive boundary

The consumer-facing primitive is intentionally small:

```text
is_latest_stable(suite_id, expected_suite_hash, min_run_id) -> bool
```

A consumer can fail closed without knowing anything about prompts or benchmark execution.

## Meaningful state

CalibrationAnchor stores:

- immutable suites;
- immutable static and pinned-web cases;
- append-only calibration runs;
- per-case results;
- previous-run links;
- behaviour hashes;
- calibration state.

The state becomes more useful over time because repeated runs expose actual behavioural continuity or change.

## Consensus safety

The leader cannot unilaterally set a benchmark outcome. Validators independently reproduce the bounded semantic label. For web cases they also independently re-fetch the pinned input and verify whether the source itself changed.

## Important epistemic boundary

CalibrationAnchor does not certify that the suite creator is objectively correct. It certifies observable consensus behaviour **relative to an explicitly trusted frozen benchmark definition**.

That boundary is deliberate and exposed in both the suite hash and consumer API.

## Category fit

- standalone Intelligent Contract primitive;
- no frontend;
- reusable by other builders;
- custom validator logic;
- meaningful persistent state;
- adversarial tests;
- explicit failure states;
- deterministic protocol mechanics around semantic consensus.

## Target network

GenLayer Studionet only, chain ID `61999`.

## Observed live submission proof

The deployed CalibrationAnchor address is
`0xb489b48ACd1035f48cDFd347346011C8A97f36fb`; its deployment transaction
`0xf130cc9e316a9fe3be6b607e2b9541d650edc4bfe47d09947c8156f3e6f8ef9c`
finalized successfully. Suite 1 is sealed at
`ef3d366b60c54dab2f4bc432b6bcaef5def090b4fe334a8a18d699858b0a0546`.
Run 1 finalized `STABLE`, with all three labels reproduced, full weighted
coverage and agreement (10,000 bps), no flips, no uncertainty, and zero
critical failures. `is_latest_stable` returned true for the exact suite hash
and false for an incorrect hash.

CalibrationGate is deployed at
`0x39aeF5E565Cd7211b10c78E03c754C98f5ACAb94`. Its finalized
`open_if_calibrated()` call stored run 1 and the observed run hash. Machine
readbacks and transaction evidence are in [proof/studionet-live.json](proof/studionet-live.json).

The benchmark remains a trust object: this proof shows consensus agreement
with the frozen suite labels; it does not establish that those labels are
universally true.
