# NASA DATA DEPTH — implementation and access report

28 October 2026. Scope: the existing three eligible crops; no catalogue expansion, Water Commons or major visual redesign. The backend integrations and “Your Field From Space” screen are implemented. **SMAP and GPM IMERG are now live-validated for the specified Bangladesh point and tested dates.** The unified API returned all three NASA sources available for the same one-day period. A subsequent stress-testing milestone validated a seven-day SMAP subset, a 61-day IMERG subset and ten complete annual POWER records at two points; see `docs/stress-testing-methodology.md`. IMERG annual rainfall effects remain unvalidated.

## Live Earthdata validation status — 28 October 2026

| Provider | Status | Evidence and remaining condition |
|---|---|---|
| NASA POWER | Available | Authentic cached Khulna-reference 2024 daily response; 366 complete days and SHA-256 recorded below. |
| SMAP `SPL4SMGP.008` | **LIVE_VALIDATED** for the tested point/day | Authenticated Harmony job `2a973d61-5ee9-407f-a641-c8da2b59b598` completed; eight matching three-hourly NetCDF files were downloaded, checksummed and parsed. Surface/root-zone volumetric moisture and root-zone percentile each have eight valid samples. The source granule version is `Vv8012` within collection `SPL4SMGP.008`. |
| GPM `GPM_3IMERGDF.07` Final | **LIVE_VALIDATED** for the tested point/days | After the owner approved the GES DISC Earthdata application, fresh Harmony jobs completed. Four real daily NetCDF subsets (January 1 and July 1 in 2023 and 2024) passed native DOI/title/date/unit/count/grid checks and retained raw SHA-256 hashes. The first failed job remains archived in the private cache for diagnosis; it was not treated as rainfall. |

The user required environment-variable-only credential handling. An attempted local validation helper that would have loaded `.env` was rejected by automatic approval review for violating that requirement. The Earthdata token was subsequently made available through the Windows User environment and passed only to the validation process. No credential value was displayed, cached, logged or sent to the frontend. The API was checked with Django DEBUG disabled. The SMAP job ran from `2026-10-28T07:30:44.398Z` to `07:31:49.506Z` (about 65 seconds), then eight output files were collected over bounded requests. The first IMERG job failed after about 12.5 seconds while GES DISC application approval was missing. After approval, four one-day IMERG jobs completed in approximately 13.7, 16.5, 22.2 and 23.5 seconds respectively; this is observed job latency for these small requests, not a guarantee for longer windows.

Security checks: `.gitignore` covers `.env`, `.env.*` except the names-only `.env.example`, local Earthdata cookie/netrc files, and common private key extensions. A byte-for-byte scan found no occurrence of the active token outside `.env` in workspace files, including source, fixtures, docs, frontend output and private NASA caches. A Django API request with the live token returned no token in its body or captured application logs; no `Authorization:` header appeared in captured logs. Frontend source/output contains no Earthdata variable or Authorization references. This checkout has no `.git` directory, so Git's tracked-file/index state could not be verified here; the ignore rules are present for the repository once Git metadata is available.

SMAP extraction example, Khulna reference coordinate **22.8°N, 89.55°E**, `2024-01-01`: selected EASE-Grid cell 22.7883129°N, 89.5798798°E; filename observation timestamps `01:30`–`22:30` UTC; eight valid samples per variable. Mean surface moisture `0.3113507405 m³/m³`, mean root-zone moisture `0.3737844452 m³/m³`, mean native root-zone percentile `64.9994049`. One source file SHA-256 is `92c7dc113698484d148487bde5470d7f5c2ae4c2244c46d025d181cfecc730ce`; all eight source files retain hashes in the private cache. The NetCDF `time` value for the `01:30` filename resolves to `01:28:55.816` UTC; both source times are retained, and the parser checks they agree within three minutes. These are gridded, model-assimilated estimates, not a field measurement.

IMERG extraction example at the **same coordinate**: the `2024-01-01` Final V07 NetCDF source has native DOI `10.5067/GPM/IMERGDF/DAY/07`, BeginDate/EndDate `2024-01-01`, `precipitation` units `mm/day`, `precipitation_cnt` units `count`, and 48 valid half-hourly samples at the selected 0.1° cell (22.75°N, 89.550003°E). Its measured precipitation is genuinely `0.0 mm/day`; zero was not substituted for unavailable data. The source SHA-256 is `13066c6db896d4fc26a560edaabcd107112341c1744169203eac1950e0bfd030` and Harmony job ID is `74f77366-ce1a-4e2a-b7f9-53193464733f`. A matched `2023-01-01` extraction was also complete with `0.0 mm/day`, so the API correctly returned `equal_to_selected_comparison`.

For a non-equal real historical comparison, `2024-07-01` returned `18.0450000763 mm/day` (SHA-256 `a508930a50be546ccd4f258e59d22d2a1822ef950c5c06f9168a50818da83ec4`) and `2023-07-01` returned `10.1549997330 mm/day` (SHA-256 `2044799c229ec4794dcbe3ce28164263b61a9db88069a164b5de3dc24da48913`). Both have complete 48-sample days and the same product and point. The existing comparison code and Django API returned `wetter_than_selected_comparison`. This compares two selected days, not a climate normal, trend, forecast or significant anomaly.

## Exact products and access

| Provider | Product / identifier | Access implemented | Variables actually used |
|---|---|---|---|
| NASA POWER | Daily point API, AG community, UTC; product metadata and response checksum preserved | Direct public HTTPS JSON; no Earthdata token for this endpoint | `T2M` for temperature screening; `T2M_MIN`, `T2M_MAX`, `PRECTOTCORR` retained as context |
| SMAP | `SPL4SMGP.008`; CMR `C3480440870-NSIDC_CPRD` | **Live-validated:** Earthdata-authenticated Harmony asynchronous geographic subset, then NetCDF download through NASA's Harmony staging CDN. Existing AppEEARS point adapter remains available when a separate AppEEARS API token is configured. | Native `Geophysical_Data/sm_surface`, `Geophysical_Data/sm_rootzone`, `Geophysical_Data/sm_rootzone_pctl`, `cell_lat`, `cell_lon`, `time` |
| GPM IMERG | `GPM_3IMERGDF.07` Final daily; CMR `C2723754864-GES_DISC`; DOI `10.5067/GPM/IMERGDF/DAY/07` | Earthdata-authenticated **Harmony geographic subset**, then native NetCDF output downloads and nearest-cell extraction | `precipitation`, `precipitation_cnt`, `lat`, `lon`, `time` |

These are separate provider adapters in `backend/next_season/environment/{power,smap,gpm}.py`, with the validated SMAP Harmony path in `smap_harmony.py`. They do not share a made-up NASA point API. AppEEARS task/bundle semantics differ from Harmony job/output semantics. Public catalogue, product-layer and capability responses were inspected live; their URLs, hashes and selected original metadata are recorded in `data/nasa/product_metadata.json`.

The exact live Harmony entry paths were:

```text
GET https://harmony.earthdata.nasa.gov/C3480440870-NSIDC_CPRD/ogc-api-coverages/1.0.0/collections/all/coverage/rangeset
GET https://harmony.earthdata.nasa.gov/C2723754864-GES_DISC/ogc-api-coverages/1.0.0/collections/all/coverage/rangeset
```

Each request supplied an inclusive `time` subset, `lat`/`lon` bounds of ±0.1° around 22.8°N, 89.55°E, `format=application/netcdf`, `forceAsync=true`, `skipPreview=true` and `ignoreErrors=false`. The validation period was one day per job. The client then polled `GET https://harmony.earthdata.nasa.gov/jobs/{job_id}` and downloaded only `rel=data` links returned by that completed job. NASA's authenticated output link redirected to its staging CloudFront host; the transport removed the bearer header on that cross-host redirect. Signed URL query strings were stripped before cache or API provenance. Request parameters, submission/completion times, input granule counts and source hashes are preserved in the private cache and returned provenance.

Authoritative documentation:

- [POWER daily API](https://power.larc.nasa.gov/docs/services/api/temporal/daily/).
- [NSIDC SMAP v008](https://nsidc.org/data/spl4smgp/versions/8) and [product specification v1.7, June 2025](https://nsidc.org/sites/default/files/documents/technical-reference/smap_l4_sm_psd_v17_for_l4sm_version_8.pdf), Appendix D, printed p83/PDF p93, for units and seasonal-percentile meaning. Product fields cover surface 0–5 cm and root zone 0–100 cm on the 9 km EASE-Grid 2.0, sampled every three hours. Root-zone values are model-assimilated estimates, not direct subsurface measurements.
- [AppEEARS API](https://appeears.earthdatacloud.nasa.gov/api/), [live SMAP layer metadata](https://appeears.earthdatacloud.nasa.gov/api/product/SPL4SMGP.008).
- [IMERG Final daily product](https://doi.org/10.5067/GPM/IMERGDF/DAY/07), [NASA product explanation](https://data.nasa.gov/dataset/gpm-imerg-final-precipitation-l3-1-day-0-1-degree-x-0-1-degree-v07-gpm-3imergdf-at-ges-dis-13ed8), [Harmony API](https://harmony.earthdata.nasa.gov/docs) and [live collection capabilities](https://harmony.earthdata.nasa.gov/capabilities?shortName=GPM_3IMERGDF).

IMERG V07 daily `precipitation` is a daily mean rate in **mm/day**, not the half-hourly mm/hour field or an older-version variable name. Native resolution is 0.1° × 0.1°. The adapter requires 48 valid half-hourly retrievals before calling a UTC day complete; this is a conservative application quality policy. NASA's V07 daily mean may still be populated with fewer retrievals. Such a day remains unknown for complete totals in this application. Final Run is post-real-time and delayed; it is never presented as a fabricated recent observation.

## Service setup and asynchronous behavior

Supply locally in the **backend process environment**, as documented in `.env.example`:

- `EARTHDATA_TOKEN` (or `NASA_EARTHDATA_TOKEN`): an Earthdata Login bearer token accepted by Harmony. The former is the preferred local name supplied for this validation and is sufficient for the validated SMAP Harmony path.
- `NASA_APPEEARS_TOKEN` (optional): a separate AppEEARS API token for the older point/CSV path. This is not interchangeable with an Earthdata bearer token, and that path has not been live-validated.

Do not commit tokens or paste them into chat, requests from the frontend, URLs or logs. The app does not automatically load `.env` files. No account creation, authentication acceptance or credential generation was performed on the user's behalf.

With `EARTHDATA_TOKEN` and no AppEEARS-specific token, SMAP submits a Harmony geographic subset for the exact `SPL4SMGP.008` collection/point/period, saves the job ID, polls on repeated requests and downloads at most two files per call. The validated one-day job returned nine source granules, including the preceding day's `22:30` granule; only eight files whose filename observation date matched the requested day entered the profile. The parser verifies native granule identity/version, source title, variable units/ranges, grid cell, time agreement and three-hour cadence before marking the profile available. The existing AppEEARS point path is still implemented but has not been live-validated; an Earthdata bearer token alone received HTTP 403 from that service.

IMERG submits a version-pinned Harmony request with geographic and time subsetting and native NetCDF output. It saves the returned job ID and returns pending. Later requests check that job; successful outputs are collected in batches of at most two files per call, with progress cached. The first one-day job failed because NASA's subsetter could not read the source `.dmrpp` file while GES DISC reported EULA acceptance failure. The exact failed-job cache was archived, and the owner approved the required application. Four subsequent one-day jobs completed and their genuine Final V07 NetCDF files were downloaded. The parser checks native title/DOI/source dates, `precipitation` mm/day, half-hour retrieval counts, grid axes, masks and observed dates before accepting values. Each daily point retains the raw output hash, source-file URL with signed query removed, sampled native cell and native production/source period. Authentication, expired outputs, a failed job, an unsupported schema or no usable coverage produces explicit unavailability. No background service or queue was added.

An optional preparation command resumes real jobs and warms caches before demos:

```powershell
$env:PYTHONPATH='backend'
.venv/Scripts/python.exe -m next_season.environment.prepare --latitude 22.8 --longitude 89.55 --start 2024-01-01 --end 2024-12-31 --attempts 200
```

It exits without polling when access is not configured, supports 1–200 attempts and waits two seconds between attempts. A large year extraction may need many invocations because each SMAP day has eight three-hourly source files; year-scale latency, pagination and complete annual rainfall coverage have not been validated. Completed authentic historical caches remain readable without credentials. One-day authenticated extraction/schema/latency was validated as described above; mocked service-contract tests alone do not constitute live satellite-value validation.

## Unified API

`POST /api/environment-profile`:

```json
{
  "location": {"latitude": 22.8, "longitude": 89.55, "country_code": "BD"},
  "historical_period": {"start": "2024-01-01", "end": "2024-12-31"}
}
```

The response contains `location`, `power`, `smap`, `gpm`, `interpreted_indicators`, `provenance`, `provider_status`, and `limitations`. Each provider preserves its product/query, requested observation period, source resolution, variables/units, coverage, retrieval metadata, source links and checksums as applicable. Failed provider series are empty and summaries/derived results null; they are not zero-filled. The endpoint returns a partial profile (200) when a provider fails, including if POWER is unavailable.

The recommendation API returns this same object under **`space_profile`**, while retaining its older POWER-only `environment_profile` field for compatibility. The normal UI uses `space_profile`. POWER remains required for the existing temperature-backed recommendation flow; its failure can still prevent recommendations, while SMAP/IMERG failure cannot. Independent provider errors and statuses remain inspectable through the unified endpoint.

Optional `rainfall_comparison_period` accepts an earlier past window of at most 366 days with the same starting/ending calendar month-days. The same IMERG product, point and complete coverage are required. February 29 is excluded only from the matched comparison, never erased from raw data. The result says drier/wetter than the **selected comparison**, not a climate normal, forecast, drought probability or significant trend. No percentage anomaly is created against zero rainfall. This API option is not exposed as a new workflow screen; by default the app reports insufficient comparison evidence.

## Interpreted indicators and rotation effects

| Source | Indicator / dimension | Supported effect and limits |
|---|---|---|
| POWER | Historical calendar-month daily-mean temperature range | Existing qualitative `climate_suitability`; retained independent behavior |
| SMAP | Mean native seasonally resolved root-zone percentile; below/at/above product median | `historical_moisture_context`; source-defined seasonal percentile, not an invented volumetric drought threshold |
| SMAP | Fraction of supported samples below native percentile 50 within activity calendar months | Only the explicit `moisture_context` farmer preference ranks by less below-median exposure. It is a factual sample fraction, not a crop-damage, irrigation-demand or soil-health score |
| IMERG | Complete selected-period precipitation total | Historical rainfall context; incomplete totals remain null |
| IMERG | Complete January–December year versus published annual species rainfall envelope | `rainfall_suitability`, and the more concerning supported temperature/rainfall category in `climate_suitability`; can change default climate ranking |
| IMERG | Matching historical comparison-window totals | Qualitative drier/wetter context; no standalone crop bonus/penalty |

SMAP's native percentile uses NASA's multiyear climatology resolving the seasonal cycle; 50 is the statistical median. A mean percentile is not the percentile of the mean moisture. No crop drought injury threshold is inferred. The product may mask percentile values where seasonal variability is too small; those remain unknown. Incomplete percentile coverage or missing activity calendar months cannot produce a supported rotation moisture comparison.

Annual rainfall envelopes were independently rechecked against the same official EcoCrop pages already used for the three crops: [rice](https://ecocrop.apps.fao.org/ecocrop/srv/en/dataSheet?id=1574), [maize](https://ecocrop.apps.fao.org/ecocrop/srv/en/dataSheet?id=238663), [sunflower](https://ecocrop.apps.fao.org/ecocrop/srv/en/dataSheet?id=1191), Ecology → Rainfall (annual). Exact original values, sources, units and verification are preserved in `data/normalized/rainfall_references_verified.json` and added to the fingerprinted offline prototype projection. No crop was added. These references are global and provisional in local application, not Bangladesh seasonal irrigation requirements.

Rainfall screening uses the same qualitative categories: inside the optimal annual interval=`good_fit`; inside the broader absolute interval=`acceptable`; outside=`potential_concern`. Shorter periods are **not annualized** and never compared with annual requirements. A crop is not hard-excluded by this soft reference check. Missing IMERG does not add a concern or dilute POWER; it simply leaves rainfall unscored and preserves the temperature-only result. No SMAP or IMERG failure is a biological hard constraint. Soil pH remains a separate farmer-input dimension.

## Cache/provenance strategy

- POWER's independent exact-query raw JSON cache stays unchanged, including its recent-period refresh rule.
- SMAP/IMERG use private caches under `.runtime/environment/smap` and `.runtime/environment/gpm`; `NEXTSEASON_ENV_CACHE_DIR` changes that parent. `NEXTSEASON_CACHE_DIR` remains the separate POWER directory.
- Keys include exact coordinates, inclusive dates, product/version, requested variables/layers and adapter version. Different points, periods or products cannot share values. Files store pending job state, resumable collection state or completed profiles, with checksummed JSON and atomic replacement.
- Original downloaded CSV/NetCDF bytes are content-addressed under each provider's `raw/`. Cache reads check their SHA-256 against the recorded objects. The AppEEARS SMAP path also checks the bundle's published checksum; the Harmony SMAP path computes and retains SHA-256 for each native output. Corruption causes a cache miss, never a fallback to another point or product.
- Closed historical satellite outputs are reusable without an automatic TTL. Explicit reprocessing/refresh requires targeted cache maintenance/repreparation; this milestone does not automatically detect NASA reprocessing or refresh a previously partial extract. A pending job older than 24 hours is reported as `job_timeout` without inserting a value; later successful NASA completion can still be accepted. Failed/expired jobs need owner investigation/repreparation. This limitation is deliberate and documented rather than claiming current data freshness.
- Public provenance strips signed URL query strings and never includes bearer tokens. HTTPS/trusted NASA output hosts are checked; authorization is not forwarded to signed S3 or the verified Harmony CloudFront output host. Raw objects contain source URLs, product/job identity, bytes and hashes; no frontend credential handling is needed.
- Local process locks prevent concurrent same-provider job/cache races within one process. No distributed job lock, scheduled ingestion, shared worker queue or multi-worker cache coordination is claimed. Use preparation for demonstration reliability.

## UI and verification

`frontend/src/FieldFromSpace.tsx` replaces the old single-source evidence block. It follows the approved Stitch NASA Data Sources inventory cards and Orbital Agriscience spacing/colors/type; the supplied export has no dedicated “Your Field From Space” screen. The planning sidebar is retained. Illustrative synchronized/live/validated stream badges and unsupported design claims about floods, irrigation offsets and stage-specific risk were not copied as scientific facts.

All three providers remain visible, including unavailable sources. Default content is interpretation, a small summary, source status, limitations and the connection to rotation evaluation. Exact values/coverage/provenance and time-indexed observations are closed disclosures. No dense raw data appears by default. Existing data-gap explanations remain available.

Validation: **75 Python tests** pass; nine frontend tests, Django checks and frontend build passed in the preceding NASA-depth milestone. Tests cover POWER independence, each provider failing independently, no credentials/no network, missing versus genuine zero, SMAP timestamps/point/schema and bundle hashes, native NetCDF masks/units/counts/grid, missing dates/duplicates, async submission/collection, cache identity/integrity, credential/signed-URL exclusion, source provenance, supported percentile/rainfall comparisons, GPM-driven rotation ranking changes, SMAP exposure changes and source failure without a ranking penalty. Added isolated tests cover the `EARTHDATA_TOKEN` alias, simulated invalid-token/HTTP and request-timeout failures, explicit stale-job timeout, empty/corrupt source rejection, the live-observed SMAP Harmony schema, and bearer stripping on a Harmony staging redirect. The mock tests alone do not establish live access; the real SMAP files and job above provide that evidence for the tested day.

Live public NASA metadata was retrieved successfully. A cached authentic 2024 POWER request at the Khulna reference point 22.8,89.55 returned 366 complete days; checksum `449e0269d7e7325ebf09cee18bfd4122f374d78bf551ac00b3b939bc1607796a`. A Django API request for the validated `2024-01-01` period returned HTTP 200 with **POWER, SMAP and GPM all available**, root-zone moisture `above_product_seasonal_median`, historical rainfall available, and the matching prior-year rainfall comparison `equal_to_selected_comparison`. The separate real July comparison returned `wetter_than_selected_comparison`. The active token did not appear in either API response or captured application logs. No fixture content was used.

**Limitations:** the live evidence covers one SMAP day and four IMERG days at one reference point. It proves source access, native extraction, caching, quality checks, an actual non-equal comparison, and a three-source unified profile; it does not establish year-scale ingestion reliability or crop-specific annual rainfall scoring on complete observed years. The AppEEARS SMAP path still lacks live CSV validation. These one-day comparisons are historical observations, not forecasts or climate normals. No other product milestone has been started.
