# Next Season — project progress and AI handoff

**Snapshot:** 30 October 2026 (Asia/Dhaka)  
**Project:** Team OORT CLOUDS, Chittagong University of Engineering and Technology (CUET), Bangladesh  
**Challenge:** NASA Space Apps Challenge 2026, “Field Shift: Adapting Farms with NASA Data”  
**GitHub:** https://github.com/jjannat04/nextSeason  
**Status:** Feature-complete **research prototype**. Public deployment and submission acceptance are **not yet confirmed**.  
**Internal target:** Working site by 1 November 2026; actual NASA submission deadline and final submitted URL should be confirmed by the team.

> This is a handoff snapshot, not a substitute for reading the current source. Start with `README.md`, this file, the source modules, and the scientific documents linked below. Verify every statement against the current commit before changing science or claiming deployment success. Do not copy secrets into prompts, files, logs, browser responses, or AI-provider context.

## 1. What the product is

Next Season helps a Bangladesh farmer compare **sequences of crops over several seasons**. A farmer enters location, field pH if known, crop history/current crop, hard constraints, and priorities. The system retrieves NASA environmental context, generates calendar-backed rotation alternatives, filters hard-constraint violations, compares supported qualitative dimensions, explains trade-offs and missing evidence, tests candidates against observed historical years, and produces a printable plan. **Water Commons** separately compares 2–5 farms' farmer-entered weekly irrigation delivery schedules against a shared capacity and previews feasible timing shifts.

The core question is: **“What sequence of crops over the next several seasons is feasible, resilient, and aligned with this farmer's priorities?”** NASA observations must influence evaluation or ordering, not merely decorate a page. The first deployment context is Bangladesh; global extension requires new region-specific evidence.

## 2. Scientific release position and non-negotiable rules

- Current mode is `prototype_recommendation`, an **evidence-tiered research prototype**, not a certified production agronomic prescription. The older strict production gate and `production` request mode are historical/blocked; do not describe the current recommendations as production-certified.
- The three eligible crops are **Aman rice, maize, and sunflower**. **Mungbean** is retained as reference-only because the rice-following calendar system is incomplete. Do not expand the catalogue without reviewed evidence.
- Bangladesh month-level calendars and sequence evidence are **provisional** for local cultivar and management use. Global crop temperature and pH envelopes are qualitative reference comparisons, not local field limits. Unresolved evidence cannot create a biological hard constraint or a scientific ranking effect.
- NASA POWER/SMAP/GPM values are regional grid/model or satellite estimates, **not field measurements**. Historical stress scenarios are retrospective observed-year comparisons, **not forecasts**. Unsupported crop-stage injury, salinity response, yield, income, numerical irrigation requirement, and quantified soil-health gain remain `insufficient_data`; never replace missing values with zero.
- Do not invent crop requirements, compatibility scores, NASA measurements, agronomic thresholds, near-real-time values, yield claims, or water savings. Water Commons timing shifts preserve each farm's entered total planned delivered water; they can reduce a shared peak, not total consumption by default.
- Do not add an LLM layer, extra infrastructure, new crops, or new NASA sources for submission polish. Keep scientific logic testable and separate from presentation and provider ingestion.

## 3. Implemented product

| Area | Current implementation |
|---|---|
| Farm workflow | Location, historical period, optional pH/method/area/irrigation context, crop history/current crop, required/excluded crops, first-slot lock, max changes/baseline, calendar bounds, preferred crops and priority sliders. |
| NASA profile | Separate NASA POWER, SMAP, and GPM IMERG adapters; provider status, raw/derived values, interpretation, provenance, limitations and cache metadata. A source failure does not create zero values or fail all sources. |
| Rotation engine | Three-season calendar-backed alternatives, documented rice/dry-crop sequences, hard-constraint filtering, supported qualitative suitability, priority ordering without opaque total scores, and explanation/evidence gaps. |
| Historical stress | Four selected observed POWER years: historical normal, dry, hot, wet; per-candidate qualitative comparisons and documented robustness selection. |
| Water Commons | 2–5 farms, explicit weekly m³ plans and shared capacity, arithmetic conflicts, no numeric conflict when schedules are incomplete, allowable whole-week timing-shift previews with locks/windows preserved, before/after peak and unchanged total. |
| UI and packaging | Stitch-derived React design, planning sidebar, public top navigation, NASA data/Methodology/About/References pages, mobile comparison alternative, expandable details, A4 browser-print plan. Public pages use hash routes. Form/result state is in browser memory and does not survive refresh. |

### NASA products and access

| Provider | Exact product and method | Current scientific effect |
|---|---|---|
| POWER | NASA POWER daily point AG JSON; historical `T2M` plus retained `T2M_MIN`, `T2M_MAX`, `PRECTOTCORR` context. | Crop temperature reference screening and observed-year stress selection/evaluation. |
| SMAP | `SPL4SMGP.008`, Earthdata-authenticated Harmony geographic NetCDF subset; surface/root-zone soil moisture and native root-zone percentile where supported. | Moisture context and optional below-median exposure preference when coverage is sufficient. |
| GPM IMERG | `GPM_3IMERGDF.07` Final, Earthdata-authenticated Harmony daily NetCDF subset; precipitation. | Historical rainfall comparison and complete-year reference screening when coverage is sufficient. |

SMAP and IMERG Harmony extraction was live-validated for bounded windows at a Khulna reference point, with native product identity and file checksums; see [`docs/nasa-data-depth.md`](docs/nasa-data-depth.md). This does **not** prove that every new coordinate, long period, or free cloud host will work. NASA jobs may remain pending and be polled on later requests.

## 4. Repository and architecture map

- `frontend/`: React 19 + TypeScript + Vite. `src/main.tsx` owns the workflow; `FieldFromSpace.tsx`, `ResultScreens.tsx`, `StressTests.tsx`, `WaterCommons.tsx`, `PrintablePlan.tsx`, and `PublicPages.tsx` render the main surfaces. `src/routes.ts` handles public hash routes. `frontend/vercel.json` currently rewrites `/api/:path*` to `https://nextseason.onrender.com/api/:path*`; **this is configuration, not proof the deployed endpoint works**.
- `backend/config/`: Django 5.2 settings, WSGI and URL routes. `backend/next_season/api/` holds DRF serializers/views. Public endpoints are `GET /api/health` and `POST /api/environment-profile`, `/api/rotation-plan`, `/api/water-commons/options`, `/api/water-commons/analyze`.
- `backend/next_season/environment/`: distinct POWER, SMAP Harmony/AppEEARS, GPM Harmony, profile, caching and provenance code. Exact implementation/access limits are in [`docs/nasa-data-depth.md`](docs/nasa-data-depth.md).
- `backend/next_season/knowledge/`: crop identities, schema, normalization, reviewed projection builder and runtime repository. Runtime reads `data/normalized/prototype_slice.json`, **not raw CSVs**. `repository.py` validates source fingerprints before enabling prototype recommendations.
- `backend/next_season/engine/`: generation/month windows, constraints, evaluation/ranking, environmental interpretation, stress testing, service orchestration and Water Commons. See [`docs/prototype-methodology.md`](docs/prototype-methodology.md), [`docs/stress-testing-methodology.md`](docs/stress-testing-methodology.md), and [`docs/water-commons-methodology.md`](docs/water-commons-methodology.md).
- `data/normalized/` and `data/crosswalk/`: reviewed runtime data, source evidence, manifests and crop identity crosswalk. `data/nasa/product_metadata.json` records NASA product metadata.
- `research/csv/` (15 original researcher CSVs) and `design/` (approved Stitch export) **exist locally but are Git-ignored and are absent from the current GitHub checkout**. If another provider needs the raw inputs/designs, transfer them separately through a secure authorized channel. Do not treat their absence from GitHub as missing runtime dependencies.
- `tests/` and frontend `*.test.tsx`/`*.test.ts` cover the core logic. The project has **no application database, migrations, Celery, Redis, authentication, persisted plans, or server PDF service**.

## 5. Evidence and provenance

The raw CSVs were audited and normalized. The reviewed projection combines `data/normalized/slice.json`, `crop_calendar_verified.csv`, `crop_rotation_rules_verified.csv`, and `rainfall_references_verified.json`. Each result preserves source/evidence status and geographical/variety applicability where known. Source URLs and exact verification decisions are documented in [`docs/csv-audit.md`](docs/csv-audit.md), [`docs/normalized-data.md`](docs/normalized-data.md), and [`docs/production-gate-verification.md`](docs/production-gate-verification.md). Unknown secondary dimensions stay visible. Do not silently promote provisional records to verified.

## 6. Verified progress versus outstanding work

**Previously verified on 28 October:** 91 backend tests and 26 frontend tests passed; Django system check and TypeScript/Vite build passed. Browser QA completed a real single-farm Khulna journey through NASA profile, six candidate options, compare/explain/stress/missing-info and printable page. A complete two-farm Water Commons conflict and an incomplete-plan case were exercised. Public direct routes, refresh and browser back/forward were checked. API checks with cached real POWER data at Khulna (22.8, 89.55), Dinajpur (25.63, 88.65), and Rangpur (25.7439, 89.2752) showed location-dependent qualitative temperature interpretation. These checks are documented in [`docs/final-readiness-report.md`](docs/final-readiness-report.md). **Rerun tests on the current commit before release.**

**Still unconfirmed:** Exact-width responsive checks at 1440/1280/1024/768/430/390/360 px; Chrome A4 print preview and Save as PDF; full 3- and 5-farm Water Commons browser flows; uncached/repeated NASA requests at three Bangladesh points on the chosen deployed backend; external links/accessibility; final public URL, screenshots/video, and submission sign-off. See [`docs/release-checklist.md`](docs/release-checklist.md). Do not mark these passed from unit tests alone.

### Immediate release blocker: cross-platform source fingerprints

`backend/next_season/knowledge/prototype.py` currently fingerprints the **raw bytes** of four normalized input files. `repository.py` compares those hashes on every prototype load. On this Windows checkout, all four local files match the recorded hashes, but the corresponding blobs in the current Git commit do **not** match: Git normalized line endings to LF (`core.autocrlf=true` locally). A Linux/Render checkout can therefore show **“Prototype sources changed; rebuild and review the offline projection”** and block `/api/health` eligibility and recommendations, even if scientific records are unchanged. This was confirmed read-only on 28 October; do not claim it has been fixed until verified on a fresh LF checkout and deployed host.

Fix this as a **release correctness task**: define a deterministic, cross-platform fingerprint of the intended text contents (or enforce exact bytes with Git attributes), preserve meaningful change detection, regenerate the reviewed projection, add tests for CRLF/LF equivalence and actual content changes, run all tests, inspect the projection diff for scientific changes, and only then commit/push. **Do not disable the safety check or alter agronomic values just to pass it.**

### Deployment state

Git remote is the GitHub URL above; latest observed local commit was `e77aefe` (“Configure Vercel API proxy”). The working tree was clean at this snapshot before this handoff file. The user intends **Vercel Hobby frontend + Render Free Django backend**. `frontend/vercel.json` contains a rewrite to `nextseason.onrender.com`. Whether either public service is live/healthy is **unknown from this workspace**. Do not infer deployment success from a committed configuration file.

Render should run Django/Gunicorn with `NEXTSEASON_DEBUG=0`, `NEXTSEASON_ALLOW_FIXTURES=0`, an exact `DJANGO_ALLOWED_HOSTS`, a long random `DJANGO_SECRET_KEY`, backend-only `EARTHDATA_TOKEN`, HTTPS/proxy settings, and private cache paths. Vercel should build `frontend/` with Vite (`npm run build`, output `dist`) and route same-origin `/api` to Render. Render Free sleeps after inactivity and has ephemeral filesystem; NASA caches and async-job metadata can be lost on restart/sleep. Validate cold-start, memory, timeout, and live NASA behavior before a judge demo. The existing [`docs/deployment-guide.md`](docs/deployment-guide.md) describes a **single Linux VM**, not this chosen Vercel+Render setup, so do not follow its Nginx/systemd steps for the current hosting choice. The platform-specific instructions must be reconciled after the checksum fix.

## 7. Security and repository hygiene

- `.gitignore` excludes `.env`, `.env.*` except `.env.example`, common key files, `.runtime/`, virtual environment, Node dependencies, frontend build, design, raw research, and local `AGENTS.md`, `PLANS.md`, `PROJECT_CONTEXT.md`. The three internal Markdown files were removed from current tracking; prior Git history may still contain them. Do not assume `.gitignore` erases history.
- Never display, log, commit, cache in metadata, return through an API, or send to the frontend any Earthdata credential. The backend reads `EARTHDATA_TOKEN` or `NASA_EARTHDATA_TOKEN` from its process environment. `.env` is not loaded automatically by Django. `NASA_APPEEARS_TOKEN` is distinct and its older access path has not been live-validated.
- A pre-commit pattern scan previously found no credential literals in Git-eligible text files; it did **not** examine actual ignored secret values or prove future Git history is clean. Recheck staged files and history before submission. Do not paste credentials into AI chats.
- Development fixtures are isolated and require both Django debug and an explicit fixture switch. The deployed `/api/health` must show `fixtures_enabled: false` and `recommendation_mode: prototype_recommendation`. Public errors must not reveal stack traces or secrets.

## 8. Local development and tests

Windows PowerShell, from repository root:

```powershell
$env:PYTHONPATH='backend'
$env:NEXTSEASON_DEBUG='1'
$env:NEXTSEASON_ALLOW_FIXTURES='0'
.\.venv\Scripts\python.exe backend\manage.py check
.\.venv\Scripts\python.exe backend\manage.py runserver 127.0.0.1:8010 --noreload
```

Use port `8010` when an older Milestone 1 process occupies `8001`. In a **second** PowerShell window:

```powershell
cd frontend
$env:NEXTSEASON_API_TARGET='http://127.0.0.1:8010'
npm run dev
```

Both the Django and Vite `/api/health` URLs must show `milestone: prototype.1` and `recommendation_mode: prototype_recommendation`. If they show `milestone: 1`/`blocked_scientific_data`, an old backend is serving that port. For first setup, follow `README.md` for venv and `npm ci`; a running Vite process can lock Rolldown's native Windows binary and make `npm ci` fail with EPERM.

Tests/build from repository root:

```powershell
$env:PYTHONPATH='backend'
.\.venv\Scripts\python.exe -m unittest discover -s tests
.\.venv\Scripts\python.exe backend\manage.py check
cd frontend
npm test
npm run build
```

If Vitest temporary-file renames fail on Windows, point `TEMP` and `TMP` to a writable workspace temp directory. Production checks also need `manage.py check --deploy` with synthetic or properly protected production environment variables. Do not print the token during checks.

## 9. Suggested next-agent order through submission

1. Read this handoff and the current `README.md`, [`docs/prototype-methodology.md`](docs/prototype-methodology.md), [`docs/nasa-data-depth.md`](docs/nasa-data-depth.md), [`docs/stress-testing-methodology.md`](docs/stress-testing-methodology.md), [`docs/water-commons-methodology.md`](docs/water-commons-methodology.md), and [`docs/release-checklist.md`](docs/release-checklist.md). Treat local `AGENTS.md` as repository guidance if present, but remember it is Git-ignored.
2. Resolve and test the cross-platform fingerprint blocker **without changing scientific data**. Verify from a fresh Git checkout with LF line endings; ensure `/api/health` enables the prototype and the fixture mode remains inaccessible.
3. Reconcile Vercel+Render deployment configuration/documentation; verify the actual public endpoints, backend environment, no credential exposure, and cache/async-job behavior on the free host. The Vercel rewrite's current Render hostname is a configuration value to verify.
4. Complete manual acceptance items at the seven viewport widths, 3/5-farm Commons, A4/PDF, public routes, three-location NASA uncached/repeated requests, partial provider failure, accessibility and security. Mark only observed passes.
5. Capture final screenshots/demo, determine license/submission text with the team, and record the actual public URL and submission date. Do not label the prototype production-certified or the release complete before team sign-off.

## 10. What another AI should ask the team if needed

- What is the **actual** Vercel frontend URL and Render backend URL, and are both currently deployed? Do not ask for or receive token values.
- What is the exact NASA Space Apps submission deadline/time zone and required deliverables for this team?
- Has the team approved a public license, final demo script, and screenshot/video assets?
- Can the team supply the ignored local raw `research/csv/` and Stitch `design/` folders if a scientific/design review truly requires them?
- Who will sign off the manual release checklist, especially live Earthdata/cache behavior and the responsive/print checks?

## 11. Important document caveats

Several older documents describe earlier milestones. `PROJECT_CONTEXT.md` and `docs/research-blockers.md` include superseded strict-gate language; the current prototype methodology and source code govern the present release. `docs/final-readiness-report.md` was written before Git was initialized and still says Git metadata was absent. `docs/release-checklist.md` likewise has old first-commit wording. `README.md` links local ignored research/design paths, which a GitHub-only checkout will not contain. Update these documents when fixing the release blocker, but preserve the scientific audit history.
