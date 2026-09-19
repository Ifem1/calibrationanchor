# Threat model

## Malicious suite creator

A creator can choose bad gold labels. CalibrationAnchor does not hide this. The suite hash commits to the full benchmark, and consumers must explicitly choose which suite hash they trust.

Mitigation: transparent case definitions, gold rationales, immutable suite hashes and consumer-side pinning.

## Malicious leader

A leader may attempt to forge a semantic label or claim that a web input drifted/unavailable.

Mitigation: validators independently reproduce the web observation and semantic decision. The validator rejects mismatched runtime states, source hashes or semantic labels.

## Prompt injection inside benchmark data

Static contexts and fetched web text may contain instructions intended to manipulate the model.

Mitigation: benchmark prompts explicitly delimit all context as untrusted data and restrict output to one of three tokens. Tests include instruction-like hostile context.

## Source mutation

A web benchmark source may change between runs.

Mitigation: the source is pinned by normalized hash at suite construction. A later mismatch becomes `INPUT_DRIFT` and is excluded from semantic agreement scoring.

## Source outage

An unavailable source must not become a semantic failure.

Mitigation: outages become `UNAVAILABLE` and reduce coverage. If coverage falls below the frozen minimum, final state is `INSUFFICIENT_COVERAGE`.

## Selective execution

A caller could try to execute only favourable cases.

Mitigation: finalization is impossible until every sealed case has exactly one result.

## Replay or duplicate result

Mitigation: `(run_id, case_id)` has a single result slot. Duplicate execution reverts.

## Benchmark edit after a favourable run

Mitigation: a sealed suite is immutable. Changes require a new suite and therefore a new suite hash.

## Critical-case degradation hidden by averages

Mitigation: any critical semantic flip or critical ambiguity forces `UNSAFE` after coverage is sufficient, regardless of aggregate agreement.

## Stale consumer acceptance

Mitigation: consumers can require both the exact suite hash and a minimum run ID. `is_latest_stable` always evaluates the latest finalized run, so a later unsafe run invalidates the gate.
