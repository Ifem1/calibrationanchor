# Deployment and live proof

## Hard network lock

This repository targets **Studionet**:

```text
RPC:      https://studio.genlayer.com/api
Chain ID: 61999
Alias:    studionet
Explorer: https://explorer-studio.genlayer.com/
```

Before every deployment or write sequence:

```powershell
./scripts/verify_studionet.ps1
```

The guard selects `studionet`, prints the resolved network information and refuses to continue unless both the expected chain ID and RPC are present.

Do not sign anything unless the effective network reports chain ID `61999` and the Studionet RPC above.

## Install

```bash
python -m pip install -r requirements-dev.txt
npm install -g genlayer
```

Run local checks first:

```bash
gltest tests/direct -v -s
python scripts/preflight.py
genvm-lint validate contracts/calibrationanchor.py
genvm-lint validate contracts/calibration_gate.py
```

## Deploy CalibrationAnchor

```powershell
./scripts/verify_studionet.ps1
genlayer account show
genlayer deploy --contract contracts/calibrationanchor.py
```

Wait for finalization. Record the **real** contract address and deployment transaction in `proof/`.

## Minimum live lifecycle

The final submission should show all of these on the deployed source:

1. create one suite with explicit thresholds;
2. add at least three static cases;
3. add one pinned web case if a stable public fixture is available;
4. seal the suite and record its exact suite hash;
5. open run 1;
6. execute every case;
7. finalize run 1;
8. read back coverage, agreement, behaviour hash, run hash and calibration state;
9. confirm `is_latest_stable` is true for the exact suite hash;
10. show a wrong suite hash returns false.

A stronger proof also runs a second calibration and demonstrates either a controlled semantic change or a pinned-input drift case.

## Optional live composability proof

After a stable run exists, deploy the small consumer:

```bash
genlayer deploy --contract contracts/calibration_gate.py --args \
  <ANCHOR_ADDRESS> <SUITE_ID> <SUITE_HASH> <MIN_RUN_ID>
```

Then call:

```text
open_if_calibrated()
```

The gate should open only when the anchor's latest finalized run is `STABLE` for that exact suite hash and at least the configured minimum run ID.

## Proof rules

Do not write guessed values into this repository.

Only record:

- finalized contract addresses;
- finalized transaction hashes;
- the exact deployed source commit;
- suite IDs and hashes read from chain;
- run IDs and hashes read from chain;
- explorer links generated from those real values;
- CLI version actually used.

If a deployment is accepted but not finalized, do not call it final.

## Finalized Studionet proof

The source was deployed to Studionet 61999 using CLI version `0.39.2`. The
CalibrationAnchor deployment finalized successfully at
`0xb489b48ACd1035f48cDFd347346011C8A97f36fb` in transaction
`0xf130cc9e316a9fe3be6b607e2b9541d650edc4bfe47d09947c8156f3e6f8ef9c`.

Suite 1 contains three static cases (case IDs 1, 2, 3) and is sealed with hash
`ef3d366b60c54dab2f4bc432b6bcaef5def090b4fe334a8a18d699858b0a0546`. Run 1
finalized in transaction
`0x5babecf55eef61e50bd9932bdcea0a0dc0b2a3ffba5381308afb92c5ced589fc` with
`STABLE`: 3 results, total/valid weight 5/5, coverage/agreement 10,000 bps,
flips/uncertainty 0 bps, zero critical failures, and changed count 0. Its
behavior hash is `a08cfb4bdd3a45d10041473aab1250c1ad98b73a0c4dd73bef24a43cf5fb87a0`
and run hash is `d57e853bac5a6e405c9929ccb395ae555bf72a9fb9c44c25324b749e4cd116cf`.
The supported, not-supported, and ambiguous cases each returned their
corresponding frozen label and `MATCH`.

Run 1 established the baseline semantic anchor. Run 2 opened against the same
sealed Suite 1 and has `previous_run_id: 1`. It finalized `STABLE` in
`0x2867c6ee043fa28509f745056fd52e87796d60f2b734a835a8d01f36d8b7276c` with
three results, total/valid weight 5/5, coverage/agreement 10,000 bps,
flip/uncertain 0 bps, zero critical failures, and `changed_count: 0`. Its
behavior hash is the same as Run 1:
`a08cfb4bdd3a45d10041473aab1250c1ad98b73a0c4dd73bef24a43cf5fb87a0`; its
run hash is `f47dc362232366d27d12b2c9c6859b35816f113bde0cc27a0543b6c523ccc461`.
This is the live longitudinal proof that the same frozen suite remained
stable across two independent calibration runs.

`is_latest_stable(1, exact_suite_hash, 2)` and the same call with minimum run
ID 1 returned true; an all-`f` suite hash returned false. The existing gate
remains open with its pinned minimum run 1 and records Run 1 as the run at
which it opened. The latest Run 2 also satisfies that pinned stable condition,
so redeployment was unnecessary.

CalibrationGate finalized at
`0x39aeF5E565Cd7211b10c78E03c754C98f5ACAb94` in transaction
`0xadf92aaa065608804c2c05efd27d5091310d964b5216d65a289613eb76d2cbf2`.
Its `open_if_calibrated()` transaction
`0x21134caf2cad2ec518507df040f1ec6a5611772ec657bb9c8c7eabf793f287f8`
finalized, and `status()` read back `opened: true`, suite ID 1, run ID 1, and
the run hash above. Full sanitized readbacks are in
[`proof/studionet-live.json`](proof/studionet-live.json).
