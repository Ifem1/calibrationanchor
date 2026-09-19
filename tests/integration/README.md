# Hosted integration proof

Do not run hosted writes automatically from CI.

After deployment on Studionet 61999, execute the lifecycle in `DEPLOYMENT.md` against the finalized address and save sanitized output under `proof/`.

The network assertion is mandatory before any write:

```bash
genlayer network set studionet
genlayer network info
```

The effective chain must be `61999` and the RPC must be `https://studio.genlayer.com/api`.
