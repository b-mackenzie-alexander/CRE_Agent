# CRE Signal Agent — Roadmap

**Sprint:** 2026-04-27 to 2026-05-06 (8 working days)

## Phase 1: Infrastructure & Pipeline (Days 1–2)

- [x] DevSecOps pipeline (CI, pre-commit, branch protection) `[Beatrice]`
- [ ] Project documentation (CLAUDE.md, AGENTS.md, ARCHITECTURE.md, ROADMAP.md) `[Beatrice]`
- [ ] LLM abstraction layer (OpenRouter adapter, cache_control, tool use) `[Beatrice]`
- [ ] Bronze layer: data ingestors (FRED, RentCast, ATTOM, BLS, Census, FHFA) `[Beatrice]`
- [ ] Frontend scaffold (project setup, routing, layout) `[Yaasameen]`
- [ ] Shared JSON schema definition `[Both]`

## Phase 2: Signal Scoring (Days 3–4)

- [ ] Silver layer: ZIP normalization, time alignment, null handling `[Beatrice]`
- [ ] Gold layer: signal scoring engine (weighted 0–100 score) `[Beatrice]`
- [ ] Signal threshold config (vacancy, rent, price, employment, foreclosure) `[Beatrice]`
- [ ] Frontend: digest list view (reads Gold layer JSON) `[Yaasameen]`
- [ ] Frontend: opportunity card component `[Yaasameen]`

## Phase 3: Brief Generation (Days 5–6)

- [ ] Opportunity brief generator (Claude tool use → structured JSON) `[Beatrice]`
- [ ] Draft market memo generator (Claude → analyst-ready text) `[Beatrice]`
- [ ] Action alert logic (Model / Monitor / Ignore classification) `[Beatrice]`
- [ ] Frontend: brief detail view `[Yaasameen]`
- [ ] Frontend: action alert display `[Yaasameen]`

## Phase 4: Delivery & Integration (Days 7–8)

- [ ] APScheduler setup (8am daily trigger) `[Beatrice]`
- [ ] SendGrid email digest template `[Beatrice]`
- [ ] Slack digest integration `[Beatrice]`
- [ ] Claude API key swap (Saturday 2026-05-02) `[Beatrice]`
- [ ] End-to-end integration test `[Both]`
- [ ] Frontend: full pipeline demo ready `[Yaasameen]`
- [ ] Demo preparation `[Both]`
