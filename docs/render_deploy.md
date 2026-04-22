# Render Deploy Guide

This guide is the fastest path to get a public HTTPS MCP endpoint for ReferralReady without buying a domain.

## What Render gives you

- a public HTTPS URL on `onrender.com`
- Git-based deploys from your repository
- a free web service plan that is sufficient for hackathon demos

The free plan can sleep after inactivity, so the first request after an idle period can be slow.

## Prerequisites

- the repository is pushed to GitHub, GitLab, or another Git provider supported by Render
- current tests pass locally:

```bash
pytest -q
```

- local HTTP mode works:

```bash
python -m app.mcp_server --transport streamable-http --host 127.0.0.1 --port 8123 --stateless-http
```

## Option A: Deploy from `render.yaml`

Recommended. This repo already includes [render.yaml](D:/study/42.hacson/referralready-agent/referralready-agent/render.yaml).

1. Push the repo to GitHub.
2. Open [Render Dashboard](https://dashboard.render.com/).
3. Choose `New` -> `Blueprint`.
4. Connect the repository.
5. Render will detect `render.yaml`.
6. Confirm the service settings:
   - name: `referralready-agent`
   - runtime: `python`
   - plan: `free`
   - health check path: `/healthz`
7. Create the Blueprint and wait for the first deploy.

## Option B: Manual Web Service

Use this only if you do not want to use Blueprints.

Create a new `Web Service` with:

- Runtime: `Python`
- Build Command: `pip install -r requirements.txt`
- Start Command: `python -m app.mcp_server --transport streamable-http --host 0.0.0.0 --port $PORT --stateless-http`

## Post-deploy checks

Assume Render gives you a URL such as:

```text
https://referralready-agent.onrender.com
```

Run:

```bash
curl https://referralready-agent.onrender.com/healthz
```

Expected result:

```json
{
  "status": "ok",
  "service": "ReferralReady Agent",
  "synthetic_only": true,
  "streamable_http_path": "/mcp",
  "stateless_http": true
}
```

Your MCP endpoint for Prompt Opinion should then be:

```text
https://referralready-agent.onrender.com/mcp
```

## Prompt Opinion registration

After Render is live:

1. Open Prompt Opinion Marketplace setup.
2. Register the MCP endpoint ending in `/mcp`.
3. Confirm all six tools are visible.
4. Test with `SYN-CKD-004`.
5. Capture the Marketplace URL and the platform invocation video.

See also:

- [docs/marketplace_setup.md](D:/study/42.hacson/referralready-agent/referralready-agent/docs/marketplace_setup.md)
- [docs/prompt_opinion_publish_checklist.md](D:/study/42.hacson/referralready-agent/referralready-agent/docs/prompt_opinion_publish_checklist.md)
