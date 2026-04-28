# Build Notes — CRE Signal Agent

## 2026-04-27 — Day 1

### Decisions Made
- LLM stack: OpenRouter (Claude model) for Days 1–4, switch to direct Anthropic Claude API on Saturday 2026-05-02 when key arrives. One env var change.
- Abstraction: thin custom adapter in src/llm/. Rejected Strands (too heavy for 8-day sprint) and LiteLLM (extra dependency for a problem we can solve in ~50 lines).
- Prompt caching: baked in from day 1. Static system prompts (scoring context, thresholds) get cache_control. OpenRouter ignores it; Claude API will use it.
- Structured outputs: Claude tool_use with forced tool_choice for scoring. No free-text parsing — models the behavior the PRD called "future iteration" but it's simpler than the alternative.
- Database: SQLite at data/cre_signal.db. Local demo only. Postgres path is easy if needed later.
- Entity resolution: ZIP-code level for MVP. No geocoding layer yet.
- Time alignment: rolling 30-day window. Percentage change vs prior period.
- Medallion architecture: Bronze (raw API cache in SQLite) → Silver (normalized, ZIP-aligned) → Gold (scored, ranked). Frontend reads Gold only.
- Scheduler: APScheduler (in-process). Cron if ever deployed to a server.

### Progress
- DevSecOps pipeline complete: pre-commit hooks, CI workflows (ci.yml, security.yml, branch-check.yml), PR template, CODEOWNERS, CONTRIBUTING.md
- Project documentation files created

### PRD Cross-Reference (Yaasameen's PRD v1.0)
- **MCP Servers adopted:** All 7 data sources wrapped in MCP servers (`src/mcp/`). Replaces direct httpx API calls. Each server caches to Bronze on every call.
- **Thin custom adapter confirmed:** Rejected Strands Agents SDK despite Yaasameen's PRD specifying it — team agreed thin adapter is right for 8-day scope.
- **HUD added as 7th source:** Original PRD had 6 sources. Yaasameen's PRD adds HUD (huduser.gov) for vacancy surveys.
- **Market memo moved to Post-MVP:** Yaasameen's PRD lists it as P2/Nice-to-have. Removed from 8-day ROADMAP.
- **Sequential build confirmed:** Phase 2 (signal scoring) cannot start until Phase 1 pipeline is stable and returning clean data from all 7 sources.

### Open Questions
- What ZIP codes should we target for the demo? Need to pick 3–5 markets to constrain API usage.
- RentCast free tier = 50 calls/month. What's the minimum ZIP set that makes a compelling demo?
- Confirm Yaasameen's frontend tech stack (React? Next.js?) so AGENTS.md and schema docs can be more specific.
