# Live proof directory

This directory is intentionally free of invented deployment values.

## Observed run status

The finalized Studionet deployment, both calibration runs, stable-state
checks, and CalibrationGate call are recorded in
[`studionet-live.json`](studionet-live.json). Values there come from CLI
transaction receipts and on-chain readbacks. The Run 1 Case 2 transaction hash
was recovered from the recorded CLI output and independently verified using
its finalized Studionet receipt. The Run 2 Case 3 result was read back in its
finalized state, but its transaction hash was not captured and is intentionally
not claimed.

The machine-readable record contains sanitized observations for:

- deployment address and transaction;
- source commit SHA;
- suite creation;
- each case creation;
- suite sealing and suite hash;
- calibration run opening;
- each case result;
- final run metrics and run hash;
- `is_latest_stable` true for the exact suite hash;
- `is_latest_stable` false for an incorrect suite hash;
- optional CalibrationGate deployment and successful opening.

No private keys, seed phrases, RPC credentials or account passwords belong here.
