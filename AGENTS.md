# Agent instructions

This is a contract-only GenLayer submission.

Hard constraints:

- target GenLayer Studionet only;
- chain ID must be 61999;
- RPC must be https://studio.genlayer.com/api;
- do not migrate to the Studio development preview;
- do not add a frontend;
- do not replace semantic consensus with a centralized backend;
- do not invent deployment addresses, transaction hashes or live proof;
- preserve `INPUT_DRIFT` and `UNAVAILABLE` as distinct operational states;
- preserve validator-independent reproduction of benchmark labels;
- final calibration state must remain deterministic.

Before any network write, run `genlayer network info` and verify 61999.

When a real deployment is complete, update `DEPLOYMENT.md`, `README.md` and `proof/` with only observed finalized values.
