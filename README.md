# CalibrationAnchor

CalibrationAnchor is consensus regression infrastructure. It measures the observable semantic behavior of GenLayer against an immutable benchmark suite, distinguishes adjudication change from input-source drift, stores comparable behavior anchors over time, and lets another Intelligent Contract fail closed when the latest calibration is no longer acceptable.

It answers a question that ordinary application tests cannot answer safely:

> Has a frozen benchmark suite continued to produce the semantic decisions its consumers rely on, or has the adjudication behaviour materially shifted?

The primitive stores immutable benchmark cases, runs them through GenLayer consensus, separates **model/consensus behaviour changes** from **web-input drift**, computes deterministic calibration metrics, and exposes a stable view that other Intelligent Contracts can consume.

There is **no frontend**. CalibrationAnchor is intended to be reused by other contracts, tooling and protocol operators.

## Network

This repository targets **GenLayer Studionet only**:

- Chain ID: `61999`
- RPC: `https://studio.genlayer.com/api`
- Network alias: `studionet`
- Explorer: `https://explorer-studio.genlayer.com/`

Do not deploy this repository to the Studio development-preview chain.

## Why this primitive exists

A contract can be perfectly deterministic around a semantic decision while still depending on an adjudication environment that evolves over time: models, validator mixes, prompting behaviour and consensus configuration can change.

CalibrationAnchor gives builders a reusable way to bind downstream safety to a **frozen benchmark definition** and the latest finalized calibration state.

It deliberately does **not** claim that a benchmark creator's gold labels are universally true. A suite is a curated trust object. Consumers decide which suite hash they trust. CalibrationAnchor answers a narrower question:

> Given this exact frozen suite, what did the current GenLayer consensus environment decide, how much did it agree with the suite's expected outcomes, and did that behaviour change from the previous run?

## Core mechanism

A suite is created in draft form with deterministic thresholds:

- minimum valid coverage;
- agreement required for `STABLE`;
- agreement floor below which the run is `UNSAFE`;
- maximum allowed uncertainty.

The owner then adds up to 32 immutable cases.

### Static cases

A static case stores its context directly on-chain with:

- a proposition;
- a frozen gold verdict;
- a human-readable gold rationale;
- a weight;
- an optional critical flag.

### Pinned web cases

A web case pins a public HTTPS source by **consensus-observed normalized source hash** at case creation.

At run time:

1. validators fetch the source again;
2. if the input hash differs, the case becomes `INPUT_DRIFT` and is excluded from semantic agreement scoring;
3. if the source is unavailable, the case becomes `UNAVAILABLE`;
4. only when the source hash still matches does the semantic benchmark execute.

That separation is important: a changed webpage is not silently misreported as a model regression.

## Bounded semantic output

Every benchmark proposition is classified into exactly one semantic label:

- `SUPPORTED`
- `NOT_SUPPORTED`
- `AMBIGUOUS`

The leader does not get to write arbitrary trusted prose into protocol state. Validators independently re-run the same frozen case and must agree on the bounded result.

## Run outcomes

Each case becomes one deterministic run outcome:

- `MATCH`
- `FLIP`
- `UNCERTAIN`
- `INPUT_DRIFT`
- `UNAVAILABLE`

A critical `FLIP` or `UNCERTAIN` makes a sufficiently covered run `UNSAFE`. A critical case whose input drifted or became unavailable forces `INSUFFICIENT_COVERAGE` instead of being averaged away.

## Calibration states

After every case has executed, the contract deterministically computes:

- coverage basis points;
- agreement basis points;
- flip basis points;
- uncertain basis points;
- critical failures;
- changed-case count relative to the previous run;
- a behaviour hash;
- a final run hash.

The run is then classified as:

- `STABLE`
- `SHIFTED`
- `UNSAFE`
- `INSUFFICIENT_COVERAGE`

Consensus produces the per-case semantic observations. **Protocol code, not the LLM, computes the final calibration state.**

## Reuse by other Intelligent Contracts

Consumers can pin a suite hash and require the latest finalized run to be stable:

```python
anchor = ICalibrationAnchor(anchor_address)
if not anchor.view().is_latest_stable(suite_id, expected_suite_hash, minimum_run_id):
    raise gl.vm.UserError("semantic calibration is not currently acceptable")
```

`contracts/calibration_gate.py` is a minimal standalone consumer demonstrating this boundary.

## State model

```text
Suite
  ├─ thresholds
  ├─ frozen suite_hash
  ├─ Case 1
  ├─ Case 2
  └─ ...

CalibrationRun N
  ├─ pinned suite_hash
  ├─ previous_run_id
  ├─ Result(case 1)
  ├─ Result(case 2)
  ├─ ...
  ├─ behavior_hash
  ├─ run_hash
  └─ STABLE / SHIFTED / UNSAFE / INSUFFICIENT_COVERAGE
```

A sealed suite is immutable. New calibration runs reference the same suite hash and can be compared over time.

## Security properties

CalibrationAnchor is designed around these invariants:

1. a sealed benchmark cannot be edited;
2. a run is pinned to the sealed suite hash;
3. every case executes at most once per run;
4. validators independently reproduce the bounded semantic result;
5. web source drift is separated from semantic drift;
6. the LLM does not choose thresholds or final calibration status;
7. critical semantic failures fail closed;
8. consumer contracts can require the exact suite hash and a minimum run ID;
9. no private evidence is required;
10. benchmark history is append-only.

See [docs/THREAT_MODEL.md](docs/THREAT_MODEL.md) and [docs/CONSENSUS.md](docs/CONSENSUS.md).

## Repository layout

```text
contracts/
  calibrationanchor.py       main primitive
  calibration_gate.py        minimal consumer IC

tests/direct/
  test_calibrationanchor.py  lifecycle and state tests
  test_hardening.py          adversarial / validator / input-drift tests

docs/
  ARCHITECTURE.md
  CONSENSUS.md
  THREAT_MODEL.md
  REVIEWER_GUIDE.md

scripts/
  preflight.py

examples/
  benchmark_suite.md

fixtures/
  example_cases.json

proof/
  README.md                  required live-evidence checklist
```

## Test locally

Use Python 3.12+.

```powershell
./scripts/verify_studionet.ps1
```

```bash
python -m pip install -r requirements-dev.txt
gltest tests/direct -v -s
python scripts/preflight.py
```

The test suite covers the full lifecycle, benchmark immutability, threshold logic, web pinning, source drift, consensus forgery rejection, critical-case safety, repeat-run behaviour hashes and consumer-facing stable-state semantics.

## Deploy

```powershell
./scripts/verify_studionet.ps1
genlayer deploy --contract contracts/calibrationanchor.py
```

Before signing, verify the CLI reports chain ID `61999` and RPC `https://studio.genlayer.com/api`.

After the primitive is finalized, deploy the optional consumer only if you want a live composability proof:

```bash
genlayer deploy --contract contracts/calibration_gate.py --args <ANCHOR_ADDRESS> <SUITE_ID> <SUITE_HASH> <MIN_RUN_ID>
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for the exact proof sequence.

## Live Studionet proof

CalibrationAnchor is deployed at `0xb489b48ACd1035f48cDFd347346011C8A97f36fb`
with finalized deployment transaction
`0xf130cc9e316a9fe3be6b607e2b9541d650edc4bfe47d09947c8156f3e6f8ef9c`.
Suite 1 is sealed at hash
`ef3d366b60c54dab2f4bc432b6bcaef5def090b4fe334a8a18d699858b0a0546`.
Run 1 finalized `STABLE` with full coverage and agreement (10,000 bps each),
zero flips, zero uncertainty, and no critical failures. The exact suite hash
passes `is_latest_stable`; an incorrect hash returns false.

Run 1 established the baseline semantic anchor. Run 2 reused the same sealed
Suite 1 and also finalized `STABLE`: it linked to Run 1, reproduced all three
labels, retained 10,000 bps coverage and agreement, and recorded
`changed_count: 0`. The behavior hash stayed the same across both runs. This is
the live longitudinal proof that consensus reproduced the behavior of the
same frozen suite across two independent calibration runs. The exact suite
hash passes `is_latest_stable` with minimum run ID 2 as well as 1.

CalibrationGate is deployed at `0x39aeF5E565Cd7211b10c78E03c754C98f5ACAb94`.
Its finalized `open_if_calibrated()` transaction succeeded and its readback
records run 1 and run hash
`d57e853bac5a6e405c9929ccb395ae555bf72a9fb9c44c25324b749e4cd116cf`.
The existing gate remains open based on Run 1 (its configured minimum is 1);
the latest Run 2 is also stable for that exact suite. See
[proof/studionet-live.json](proof/studionet-live.json) for sanitized
machine-readable observations and transaction evidence.

## What CalibrationAnchor does not claim

CalibrationAnchor does not prove that the benchmark creator chose objectively correct gold labels. It proves observable GenLayer consensus behaviour relative to the exact frozen benchmark suite selected by the consumer. It does not compare hidden model identities, reveal validator internals or prove that every possible task is stable.

That narrow boundary is intentional. It makes the primitive auditable and reusable instead of pretending that one contract can certify an entire AI system.

## License

MIT.
