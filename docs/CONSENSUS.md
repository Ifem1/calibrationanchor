# Consensus design

CalibrationAnchor uses custom validator logic in two places.

## Web-source pinning

When a pinned-web case is added:

1. the leader fetches the HTTPS source and returns only a normalized content hash;
2. each validator independently fetches the same URL;
3. the validator accepts only if the page is readable and its normalized hash exactly matches the leader hash.

No semantic conclusion is made during pinning.

## Benchmark execution

For a static case, the leader executes the frozen proposition against the frozen on-chain context.

For a pinned-web case, every node first re-fetches the page:

- no readable page -> `UNAVAILABLE`;
- hash differs from the sealed pin -> `INPUT_DRIFT`;
- hash matches -> semantic benchmark executes.

The semantic output is restricted to three labels. The validator independently executes the same case and requires exact agreement on the bounded label.

This is deliberately stricter than comparing free-form prose. Explanatory model text is not written into authoritative state.

## Deterministic layer

The following are never delegated to an LLM:

- suite sealing;
- case weights;
- critical flags;
- result uniqueness;
- coverage arithmetic;
- agreement arithmetic;
- threshold comparisons;
- final `STABLE` / `SHIFTED` / `UNSAFE` / `INSUFFICIENT_COVERAGE` status;
- run hashes;
- consumer eligibility.

## Failure semantics

`AMBIGUOUS` is a first-class semantic result, not coerced into pass or fail.

`INPUT_DRIFT` and `UNAVAILABLE` are operational states, not semantic outcomes. They reduce coverage instead of being mislabeled as a consensus regression.
