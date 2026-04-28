# CRE Signal Agent — Architecture

## System Diagram

```
Public APIs          Bronze Layer         Silver Layer         Gold Layer           LLM Layer            Delivery
-----------          ------------         ------------         ----------           ---------            --------
FRED              →  Raw API cache     →  ZIP-normalized    →  Scored + ranked  →  Brief gen         →  SendGrid
ATTOM             →  SQLite tables     →  30-day window     →  0–100 score      →  Market memo       →  Slack
BLS               →  One row per       →  Null-handled      →  Top 5–10         →  Tool use
RentCast          →  API response      →  Deduplicated      →  Explainable      →  Prompt cache
Census
FHFA
                                                                     |
                                                                     v
                                                           Frontend reads Gold layer JSON
                                                           (Yaasameen's dashboard)
```

## Medallion Layers

| Layer | Contents | Storage | Owner |
|-------|----------|---------|-------|
| Bronze | Raw API responses, cached verbatim, one row per call | SQLite (`bronze_*` tables) | Beatrice |
| Silver | Normalized records, ZIP-aligned, 30-day rolling window, nulls handled | SQLite (`silver_*` tables) | Beatrice |
| Gold | Scored signals (0–100), ranked, with signal flags and explainability fields | SQLite + JSON export | Beatrice |
| Frontend | Renders Gold layer JSON | Browser | Yaasameen |

Bronze is append-only. Silver is rebuilt from Bronze on each run. Gold is rebuilt from Silver on each run.

## LLM Abstraction Layer

```
src/llm/
  adapter.py      # LLMAdapter ABC: complete(messages, system, tools) -> LLMResponse
  openrouter.py   # OpenRouterAdapter(LLMAdapter) — active until Friday 2026-05-01
  anthropic.py    # AnthropicAdapter(LLMAdapter)  — activated Saturday 2026-05-02
  cache.py        # cache_control helpers for prompt caching
```

The adapter interface:

```python
class LLMAdapter(ABC):
    def complete(
        self,
        messages: list[dict],
        system: str | list[dict],  # list[dict] for cache_control blocks
        tools: list[dict] | None = None,
        tool_choice: dict | None = None,
    ) -> LLMResponse: ...
```

Business logic imports `LLMAdapter` only. Swapping providers is a single env var change (`LLM_PROVIDER=openrouter` or `LLM_PROVIDER=anthropic`).

## Tech Stack

| Component | Choice | Notes |
|-----------|--------|-------|
| Language | Python 3.11 | |
| LLM (now) | OpenRouter (Claude model) | `OPENROUTER_API_KEY` |
| LLM (Saturday+) | Anthropic Claude API | `ANTHROPIC_API_KEY` |
| Database | SQLite | `data/cre_signal.db` — Postgres migration path is straightforward |
| Scheduler | APScheduler | In-process; triggers 8am digest pipeline |
| Email delivery | SendGrid | `SENDGRID_API_KEY` |
| Slack delivery | Slack API | `SLACK_BOT_TOKEN` |
| HTTP client | httpx | Async API calls to all data sources |
| Linting | ruff | Lint + format |
| Type checking | mypy | Strict mode |
| Security | bandit + detect-secrets + pip-audit | CI enforced |
| Testing | pytest | Unit + integration |
| CI | GitHub Actions | ci.yml, security.yml, branch-check.yml |

## Data Sources

| Source | What It Provides | API Type |
|--------|-----------------|----------|
| FRED | Macro indicators: vacancy rates, interest rates, unemployment by metro | REST (free) |
| ATTOM | Property-level data: foreclosure activity, distressed sales, assessments | REST (paid sandbox) |
| BLS | Employment by metro and sector, monthly change | REST (free) |
| Census ACS | Population, income, housing unit counts by ZIP | REST (free, API key required) |
| FHFA | House price index by ZIP and metro, quarterly | REST (free) |
| RentCast | Rental market data: median rent, vacancy, rent change by ZIP | REST (50 calls/month free tier) |

All responses are cached in Bronze layer on first fetch. Never make duplicate API calls.

## Key Design Decisions

- **ZIP-code entity resolution:** MVP scores at ZIP level. No geocoding or parcel-level resolution. Keeps data joins simple and all six sources have ZIP-code coverage.
- **Forced tool_choice for structured outputs:** Claude is called with `tool_choice: {"type": "tool", "name": "<tool>"}` wherever JSON output is required. Eliminates free-text parsing and guarantees schema conformance.
- **Prompt caching from day 1:** Static system prompts (signal thresholds, scoring rubric, domain context) are structured with `cache_control` blocks. OpenRouter ignores these silently; the Claude API activates them on Saturday. No retrofit needed.
- **Rolling 30-day window:** All Silver layer signals are computed as percentage change over the trailing 30 days. Keeps temporal comparisons consistent across sources with different update frequencies.
- **SQLite for demo:** Eliminates infrastructure setup. The ORM layer uses SQLAlchemy so Postgres migration is a connection string change. `data/` is gitignored.
- **APScheduler in-process:** No external job queue or cron dependency for the demo. Triggers the full Bronze → Silver → Gold → Brief → Delivery pipeline at 8am daily.

## Signal Thresholds

| Signal | Threshold | Direction |
|--------|-----------|-----------|
| Vacancy rate | > +5% (30-day change) | Rising = distress |
| Rent | < -3% (30-day change) | Falling = distress |
| Price growth | < +1% (annualized) | Stagnation = distress |
| Employment | > -2% (30-day change) | Drop = distress |
| Foreclosure | Any activity | Binary flag |

## Shared JSON Schema

The contract between backend (Gold layer output) and frontend (dashboard rendering) lives in:

```
docs/schema/
  signal_digest.json      # Array of scored signals — what the digest list view renders
  opportunity_brief.json  # Per-ZIP brief structure — what the brief detail view renders
  action_alert.json       # Model / Monitor / Ignore classification — what the alert display renders
```

Do not change any schema file without agreement from both Beatrice (backend) and Yaasameen (frontend). These files define the integration boundary.
