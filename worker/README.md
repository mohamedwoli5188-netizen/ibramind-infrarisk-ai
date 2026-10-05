# Judge-facing demo worker

This Cloudflare Worker serves the InfraRisk AI demo UI and proxies inference to Nebius Token Factory. The Nebius API key is stored as a Worker secret and never shipped to the browser or committed to GitHub.

## Deploy

```bash
cd worker
npx wrangler secret put NEBIUS_API_KEY
# set NVIDIA_MODEL in wrangler.toml after verifying an eligible NVIDIA model from /v1/models
npx wrangler deploy
```

The demo uses synthetic evidence only.
