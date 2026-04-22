# Architecture

ReferralReady is a small MCP server exposing healthcare workflow tools over synthetic FHIR-like data.

```text
Prompt Opinion Agent
  ↓ invokes MCP tools
ReferralReady MCP Server
  ├── data loader
  ├── patient snapshot tool
  ├── clinical signal retrieval tool
  ├── medication context tool
  ├── referral completeness checker
  ├── referral packet generator
  └── care coordination task generator
```

## Design choices

- **MCP first:** Easy to expose as tools and test locally.
- **Synthetic-only:** The loader refuses records not marked `synthetic: true`.
- **Narrow workflow:** Referral packet preparation is safer and more feasible than diagnosis.
- **Checklist + AI:** Rules provide reliability; agent summarization provides readable workflow output.
