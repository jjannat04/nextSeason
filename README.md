# Next Season

**Team OORT CLOUDS · CUET, Bangladesh**  
**NASA Space Apps Challenge 2026 — “Field Shift: Adapting Farms with NASA Data”**

Next Season is a research-prototype tool for comparing **multi-season crop rotations**. A farmer enters location, field pH if known, crop history, hard constraints and priorities. The system generates several calendar-backed sequences, explains supported qualitative comparisons and gaps, and tests options against selected historical NASA years. Water Commons separately compares planned irrigation schedules across farms sharing one source.

## Core innovation and scope

NASA observations can affect interpretation and ordering: POWER temperature screens crop reference ranges; complete annual GPM IMERG rainfall can affect qualitative climate screening; supported SMAP root-zone percentile coverage can affect an optional moisture-exposure preference. These are **regional estimates**, never field measurements or forecasts.

Bangladesh is the first validation context. Eligible rotation crops are **Aman rice, maize and sunflower**, using provisional month-level calendars and documented rice/dry-crop sequence templates. Mungbean remains reference-only because its rice-following calendar is incomplete. Hard constraints are preserved; unresolved and missing values do not score or become zero. Yield, income, precise irrigation requirement, salinity response, stage injury and measured soil-health gain remain unsupported.

## NASA products and architecture

| Source | Product and access | Current role |
|---|---|---|
| NASA POWER | AG community daily point JSON API; `T2M` used, `T2M_MIN`, `T2M_MAX`, `PRECTOTCORR` retained as context | Historical temperature screening and stress-test years |
| SMAP | `SPL4SMGP.008`, Earthdata-authenticated Harmony NetCDF subset; surface/root-zone moisture and native root-zone percentile | Historical moisture context; optional below-median exposure preference |
| GPM IMERG | `GPM_3IMERGDF.07` Final, Earthdata-authenticated Harmony daily NetCDF subset; precipitation | Historical rainfall comparison and complete-year crop reference screening |

React/Vite calls Django REST endpoints under same-origin `/api`. Separate backend adapters ingest and cache NASA products with source/version/period/checksum provenance. Agronomic knowledge is built offline from normalized cited research. Rotation generation, constraints, suitability, ranking, stress testing and Water Commons remain separate Python modules. Browser printing produces A4-friendly reports; no server PDF service is used. See the [architecture](docs/architechture.md), [prototype method](docs/prototype-methodology.md), [NASA implementation](docs/nasa-data-depth.md) and [documentation index](docs/README.md).

## Run locally (Windows PowerShell)

Requires Python 3.12+ and Node.js 24+.

```powershell
python -m venv .venv
python -m pip --python .venv install -r backend/requirements.txt
$env:PYTHONPATH='backend'
$env:NEXTSEASON_DEBUG='1'
$env:NEXTSEASON_ALLOW_FIXTURES='0'
.venv/Scripts/python.exe backend/manage.py check
.venv/Scripts/python.exe backend/manage.py runserver 127.0.0.1:8001 --noreload
```

In a second terminal:

```powershell
cd frontend
npm ci
npm run dev
```

Open Vite's printed URL. It proxies `/api` to Django on port 8001; `NEXTSEASON_API_TARGET` changes this **development** target. The production frontend uses relative `/api` requests and requires a same-origin reverse proxy. Public pages have refreshable hash routes (`#/methodology`, `#/nasa`, `#/references`, `#/water-commons`). Farm inputs/results live in browser memory and do not survive refresh.

The reviewed `data/normalized/prototype_slice.json` is included. If research sources change, rebuild the projection offline and rerun tests:

```powershell
$env:PYTHONPATH='backend'
.venv/Scripts/python.exe -m next_season.knowledge.prototype
.venv/Scripts/python.exe -m unittest discover -s tests
```

### Environment variables

The backend reads its **process environment**; it does not automatically load `.env`. `.env` and secret files are covered by `.gitignore`; `.env.example` lists variable names only.

| Variable | Purpose |
|---|---|
| `EARTHDATA_TOKEN` or `NASA_EARTHDATA_TOKEN` | Backend-only Earthdata bearer token for live-validated Harmony SMAP/IMERG paths |
| `NASA_APPEEARS_TOKEN` | Optional separate AppEEARS token for an older SMAP path; not live-validated |
| `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS` | Required production secret and allowed hostnames |
| `NEXTSEASON_DEBUG`, `NEXTSEASON_ALLOW_FIXTURES` | Keep both off in production; fixtures require both on and cannot become recommendations |
| `NEXTSEASON_CACHE_DIR`, `NEXTSEASON_ENV_CACHE_DIR` | Writable persistent private NASA cache paths |
| `NEXTSEASON_SECURE_SSL_REDIRECT`, `NEXTSEASON_HSTS_SECONDS` | Enable with correctly configured HTTPS and domain policy |

Fresh SMAP/IMERG subsets use asynchronous NASA jobs. Without Earthdata credentials, these sources return `authentication_required` while available POWER data can still work. Completed authentic caches may remain readable. Warm the exact demo location/period using the [preparation command](docs/nasa-data-depth.md); never substitute another point or fake data.

## Water Commons

Groups of 2–5 farms choose existing eligible rotations and enter complete **planned delivered irrigation** schedules in m³/week plus a declared shared capacity. The tool finds arithmetic weekly conflicts and previews feasible timing shifts respecting locks and calendar windows. Incomplete schedules show qualitative overlap and `insufficient_data` for capacity conflict. Timing changes can reduce a simultaneous peak but **do not automatically reduce total water use**. See the [method](docs/water-commons-methodology.md).

## Verify and deploy

```powershell
$env:PYTHONPATH='backend'
.venv/Scripts/python.exe -m unittest discover -s tests
.venv/Scripts/python.exe backend/manage.py check
cd frontend
npm test
npm run build
```

If Windows denies Vitest temporary-file renames, set `TEMP` and `TMP` to a writable workspace directory before `npm test`.

Do **not** deploy Django's development server. Serve `frontend/dist` as static files and proxy `/api` to a WSGI server on the same origin. Set `NEXTSEASON_DEBUG=0`, disable fixtures, supply a unique `DJANGO_SECRET_KEY`, configure `DJANGO_ALLOWED_HOSTS`, HTTPS and persistent private caches, then run `manage.py check --deploy`. The prototype uses no application database or media uploads; there are no app migrations. CORS is not broadly enabled because the intended deployment is same-origin. See the [readiness report](docs/final-readiness-report.md) for remaining checks.

Follow the [deployment guide](docs/deployment-guide.md) and complete the [release acceptance checklist](docs/release-checklist.md) before calling a public release complete.

## Provenance, limits and submission material

Research CSVs stay under `research/csv/`; request-time logic uses the reviewed normalized projection. Exact source URLs and verification states appear in candidate explanations. The [CSV audit](docs/csv-audit.md), [normalization notes](docs/normalized-data.md), [calendar/sequence verification](docs/production-gate-verification.md), [stress-test method](docs/stress-testing-methodology.md), and [NASA depth report](docs/nasa-data-depth.md) explain the limits. This is a prototype, not an agronomic prescription or forecast.

- Screenshots: approved Stitch reference screens are under [`design/stitch_next_season_crop_navigator/`](design/stitch_next_season_crop_navigator/). Add final browser screenshots after manual QA.
- Demo link: **to be added after deployment**.
- License: **no license file is present**; public reuse terms have not been granted.
