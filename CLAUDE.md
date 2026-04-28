# CRE Signal Agent — Claude Code Guide

AI-powered commercial real estate distress signal scorer. Ingests public data, scores via Claude API, delivers a daily ranked digest before 8am.

## Team

- **Beatrice** — backend (`src/`). Uses Claude Code.
- **Yaasameen** — frontend (`frontend/`). Uses non-Claude agents.

Do not touch `frontend/` — that is Yaasameen's domain.

## Branch Naming

CI enforces these prefixes. PRs from branches that don't match will fail the branch-check workflow.

- `feat/*` — new features
- `fix/*` — bug fixes
- `doc/*` — documentation only
- `hotfix/*` — emergency fixes to main

## Commit Message Format

```
feat: short description
fix: short description
docs: short description
chore: short description
test: short description
refactor: short description
```

One line. Imperative mood. No period at the end.

## Tests

Every function in `src/` must have a corresponding test in `tests/unit/`. Run before committing:

```bash
pytest tests/unit/
```

Run integration tests separately (they hit real SQLite and may require env vars):

```bash
pytest tests/integration/
```

## Pre-Commit

Run before pushing:

```bash
pre-commit run --all-files
```

Hooks: ruff (lint + format), mypy, bandit, detect-secrets. If a hook fails, fix the code — do not use `--no-verify` once `src/` exists.

## LLM Abstraction Layer

`src/llm/` contains a thin adapter. Never call the Anthropic SDK or OpenRouter directly from business logic. Always route through the adapter:

```python
from src.llm.adapter import LLMAdapter
```

- **Now through Friday:** `OpenRouterAdapter` is active (`LLM_PROVIDER=openrouter`)
- **Saturday 2026-05-02:** Switch to `AnthropicAdapter` (`LLM_PROVIDER=anthropic`) when the direct API key arrives. This is a one env var change.

## Prompt Caching

Static system prompts (scoring context, signal thresholds, domain knowledge) must use `cache_control`. Use the helpers in `src/llm/cache.py`. Do not skip this — it is designed in from day 1 so the Saturday API switch activates caching automatically.

OpenRouter silently ignores `cache_control`. That is expected and fine.

## Structured Outputs

Use Claude tool use with `tool_choice` forced to a specific tool name for any scored or structured data output. Example:

```python
tool_choice={"type": "tool", "name": "score_signals"}
```

Do not parse free-text LLM responses for structured data anywhere in the codebase.

## Database

- Location: `data/cre_signal.db`
- The `data/` directory is gitignored. Do not commit the database file.
- Schema migrations go in `data/migrations/` (this directory is tracked).
- Medallion layers: Bronze (raw API cache) → Silver (normalized) → Gold (scored + ranked).

## Secrets

- Never hardcode API keys, tokens, or credentials.
- Use environment variables. Load from `.env` via `python-dotenv`.
- `.env` is gitignored. Never commit it.
- Required env vars: `LLM_PROVIDER`, `OPENROUTER_API_KEY`, `ANTHROPIC_API_KEY`, `SENDGRID_API_KEY`, `SLACK_BOT_TOKEN`.
