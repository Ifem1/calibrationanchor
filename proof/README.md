# Live proof directory

This directory is intentionally free of invented deployment values.

## Observed run status

The finalized Studionet deployment, calibration lifecycle, stable-state
checks, and CalibrationGate call are recorded in
[`studionet-live.json`](studionet-live.json). Values there come from CLI
transaction receipts and on-chain readbacks. A case 2 execution transaction
hash was not retained from the CLI response, so the case result itself is
included without claiming that missing transaction identifier.

After the final 61999 deployment, add sanitized machine-readable records for:

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
