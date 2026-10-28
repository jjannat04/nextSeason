# Milestone 1 architecture

React/TypeScript/Vite renders the minimal Stitch-derived planning form and evidence/result cards. Plain scoped CSS reproduces existing tokens in this contained slice; full UI conversion/polish is deferred. The UI collects input but performs no scientific scoring. It aborts/clears stale results on edit or mode change and rejects fixture results in production mode.

Django REST validates the stateless `POST /api/rotation-plan` boundary. `next_season.knowledge` handles offline namespaced mapping, per-field provenance/verification, conflict quarantine and the tiny runtime projection. `next_season.environment` independently retrieves/normalizes/caches POWER. `next_season.engine` separates generation, hard checks, dimension evaluation, priority ordering and response orchestration. No arbitrary researcher prose is executable code.

Raw research CSVs, full evidence staging, activated four-crop projection, real environmental cache and synthetic test fixtures are separate artifact boundaries. Source-check status is not local agronomic approval. Current production has no activated local calendars/rules, so returns useful environmental references and explicit blocked-plan status. The fixture loader requires server debug permission plus an explicit client mode and never issues an agronomic recommendation.

This phase has no database, accounts, persisted farm drafts, task queue or external optimizer. All request inputs/provenance are returned, while only NASA response caching persists. Persistence and the broader product remain later phases. Do not claim existing full-site functionality from the earlier plan.
