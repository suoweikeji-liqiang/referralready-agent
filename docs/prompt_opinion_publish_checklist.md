# Prompt Opinion Publish Checklist

Use this checklist to close the Stage 1 loop for Agents Assemble.

## 1. Deploy a reachable MCP server

- Start ReferralReady in streamable HTTP mode:

```bash
python -m app.mcp_server --transport streamable-http --host 0.0.0.0 --port 8000 --stateless-http
```

- Deploy it to a public HTTPS host such as Render, Railway, Fly.io, or Cloud Run
- Verify:

```bash
curl https://<your-host>/healthz
```

Expected result:

- JSON response with `status: ok`
- `synthetic_only: true`

## 2. Register the MCP endpoint in Prompt Opinion

- Log in at `https://app.promptopinion.ai`
- Create or edit the Marketplace entry for `ReferralReady Agent`
- Use the deployed MCP URL and the configured path, default `/mcp`
- Confirm the six MCP tools are discovered
- Keep the safety description explicit:
  - synthetic data only
  - no PHI
  - no diagnosis
  - human review required

## 3. Validate platform invocation

- Search for `ReferralReady Agent` inside Prompt Opinion
- Add or connect it to the active workspace or flow
- Run a stable test prompt such as:

```text
Prepare a nephrology referral packet for synthetic patient SYN-CKD-004. Include the referral rationale, key clinical evidence, missing information before referral, and care coordinator tasks. Do not diagnose or recommend treatment.
```

- Confirm:
  - the agent is discoverable from the platform
  - MCP tools are invoked successfully
  - the packet is returned inside Prompt Opinion
  - output clearly states synthetic-only and human review requirements

## 4. Capture proof for Devpost

The demonstration video should show:

- Prompt Opinion search or discovery of the Marketplace entry
- the project being invoked inside Prompt Opinion
- visible tool execution
- a successful referral packet result
- the safety boundary on screen or spoken clearly

The Devpost submission should include:

- the Prompt Opinion Marketplace URL
- the public video URL
- English description and testing instructions

## 5. Stop criteria for Stage 1

Do not consider Stage 1 closed until all of these are true:

- Marketplace entry is published
- Prompt Opinion can discover the project
- Prompt Opinion can invoke the project directly
- the video shows the same behavior as the live project
- Devpost includes the real Marketplace URL
