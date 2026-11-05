# Next Season — NASA Space Apps project submission draft

**Team:** OORT CLOUDS  
**Institution:** Chittagong University of Engineering and Technology (CUET), Bangladesh  
**Challenge:** [Field Shift: Adapting Farms with NASA Data](https://www.spaceappschallenge.org/2026/challenges/field-shift-adapting-farms-with-nasa-data/)  
**Project:** Next Season  
**Submission status:** Draft — team review and final portal fields required.

> This draft describes the implemented prototype and its limits. Replace every bracketed item only with information confirmed by the team. Do not claim a live deployment, field validation, agronomic outcome, or NASA provider availability unless it has been checked for the final demo.

## High-level project summary

Farmers make decisions across seasons, but many crop tools focus on a single crop or a single season. Next Season is a decision-support research prototype that helps farmers in Bangladesh compare feasible three-season crop rotations using NASA Earth observations, farmer-entered field information, crop history, documented agronomic references, hard constraints, and farmer priorities.

Instead of giving one unexplained answer, Next Season presents multiple calendar-backed alternatives, shows which evidence supports each comparison, identifies missing information, and tests the alternatives against selected observed historical conditions. Its Water Commons view lets a group of farms compare their own planned weekly irrigation deliveries with a shared capacity and preview timing shifts that could reduce simultaneous peaks.

NASA observations contribute to the analysis: POWER temperature context supports qualitative climate screening and historical stress tests; complete GPM IMERG rainfall can support historical rainfall comparisons; and supported SMAP root-zone moisture observations can inform a clearly bounded moisture-context preference. These are regional estimates, not field measurements. Historical scenarios are retrospective comparisons, not forecasts.

## Project demonstration

- **Public project/demo URL:** [Add verified deployed URL]
- **Demo video:** [Add public video URL, if available]
- **Screenshots:** [Add final screenshots or links]
- **Source repository:** https://github.com/jjannat04/nextSeason
- **License:** [Team to choose and add; no license is currently declared]

Before submission, test each link in a private browser window. Do not include credentials, private NASA cache files, private farmer information, or unreviewed research files in public media.

## The problem and intended users

Smallholder and medium-scale farmers in Bangladesh face changing temperature and rainfall, local soil differences, water constraints, and the need to plan crop sequences rather than isolated plantings. Choosing a sequence requires balancing what can fit the local calendar, crop history and constraints, environmental context, and a farmer's priorities.

Next Season is intended for farmers, agricultural extension workers, cooperatives, and agronomists who want to explore and compare options. The current prototype supports a small evidence-reviewed crop subset in Bangladesh; it is not a substitute for local agronomic advice.

## What the prototype does

1. Collects a Bangladesh location, historical period, optional pH and field context, crop history/current crop, constraints, and priorities.
2. Retrieves independent NASA POWER, SMAP and GPM IMERG provider results with their status and provenance.
3. Generates multiple three-season crop rotations from the reviewed prototype crop subset and month-level calendars. When the farmer enters a three-crop status-quo pattern that exactly matches a supported, feasible option, it is labeled as the current-strategy baseline and preselected with two alternatives for comparison. This is conditional on the request; the engine does not invent an existing sequence or past dates.
4. Enforces required/excluded crops, crop locks, change limits and calendar bounds as hard constraints.
5. Compares supported qualitative climate/soil reference dimensions and farmer priorities without presenting an opaque total score.
6. Explains evidence, limitations and missing values for each option.
7. Compares options under four selected observed POWER years: historical normal, dry, hot and wet. These labels are relative to a defined historical sample; they are not forecasts or formal drought/flood declarations.
8. Provides a printable plan using browser print.
9. Lets 2–5 farms compare their own complete weekly planned irrigation deliveries against a declared shared capacity. Timing shifts are previews and preserve total entered volumes.

## How NASA data is used

| NASA source | Product and access | Data in the prototype | Role in evaluation |
|---|---|---|---|
| NASA POWER | Daily point AG API, JSON | `T2M` is used for temperature screening; `T2M_MIN`, `T2M_MAX`, and `PRECTOTCORR` are retained and used where specified by historical stress/rainfall methods. | Historical temperature interpretation and observed-year selection/evaluation; complete annual precipitation context where supported. |
| SMAP | `SPL4SMGP.008`, Earthdata-authenticated asynchronous Harmony NetCDF subset | Surface soil moisture, root-zone soil moisture, root-zone percentile, time and grid metadata where supported. | Environmental moisture context; a limited optional comparison of below-median exposure when coverage supports it. Root-zone values are model-assimilated estimates, not direct subsurface field measurements. |
| GPM IMERG | `GPM_3IMERGDF.07` Final daily, Earthdata-authenticated asynchronous Harmony NetCDF subset | Daily precipitation, retrieval count, date, grid and product metadata. | Historical rainfall context and comparison against cited annual crop reference ranges when period completeness is sufficient. Final Run data is delayed; it is not near-real-time. |

The adapters are separate because the products have different access and extraction behavior. Cache identity includes the relevant point, dates, product/version and query parameters. NASA source files retain checksums where downloaded. Provider status, source metadata, units, coverage and limitations are preserved. A provider failure remains unavailable/unknown; it is never replaced with zero or another location's data.

Live extraction of each named product has been documented for bounded requests at a Bangladesh reference coordinate. This evidence does not imply that all dates and coordinates are available instantly. In the final deployed demo, report the actual status for each provider and point.

NASA sources and methods:

- [NASA POWER daily API](https://power.larc.nasa.gov/docs/services/api/temporal/daily/)
- [SMAP SPL4SMGP version 8](https://nsidc.org/data/spl4smgp/versions/8)
- [GPM IMERG Final V07 daily product](https://doi.org/10.5067/GPM/IMERGDF/DAY/07)
- Implementation, extracted variables, provenance, caching and limitations: [`docs/nasa-data-depth.md`](docs/nasa-data-depth.md)

## Agronomic evidence and scientific limits

The current eligible crops are Aman rice, maize and sunflower. Mungbean remains reference-only because the selected rice-following calendar is incomplete. Runtime recommendations use the reviewed normalized projection, not raw researcher CSVs. Calendars and sequence evidence are provisional for local cultivar and management decisions. Evidence status, source geography and gaps are shown to users.

Temperature and pH references include global species-level references; their local use is qualitative and explicitly limited. Unsupported crop-stage injury, salinity response, calibrated irrigation demand, yield, income, and quantified soil-health effects remain `insufficient_data`. Water Commons compares user-entered delivery plans, not modeled crop demand. The product does not claim that timing shifts save total water.

Historical stress scenarios use observed POWER data from a fixed decade and deterministic selection rules. They are historical examples, not predictions of future climate or farm outcomes. Regional NASA products must not be represented as a field measurement.

Scientific method details:

- [`docs/prototype-methodology.md`](docs/prototype-methodology.md)
- [`docs/production-gate-verification.md`](docs/production-gate-verification.md)
- [`docs/stress-testing-methodology.md`](docs/stress-testing-methodology.md)
- [`docs/water-commons-methodology.md`](docs/water-commons-methodology.md)
- [`docs/csv-audit.md`](docs/csv-audit.md) and [`docs/normalized-data.md`](docs/normalized-data.md)

## What is innovative about the approach

- **Rotation-first planning:** compares crop sequences across seasons instead of returning a single crop suggestion.
- **NASA data changes the decision context:** observed environmental values can change qualitative interpretation and supported rotation ordering; NASA is not merely shown as decoration.
- **Evidence and uncertainty are visible:** source, applicability, confidence/status, limitations and missing dimensions are kept with results. The prototype avoids invented precision and opaque aggregate scores.
- **Constraints are explicit:** farmer requirements and exclusions remain hard filters that priorities cannot override.
- **Shared water planning is conservative:** farms compare their declared schedules and capacity; proposed timing changes preserve each farm's total entered delivery.
- **Scientific boundaries are part of the experience:** the interface distinguishes historical context from forecasts and regional data from field measurements.

## Technical tools and architecture

- **Frontend:** React 19, TypeScript, Vite, HTML and CSS.
- **Backend:** Python 3.12+, Django 5.2 and Django REST Framework.
- **NASA processing:** provider-specific Python adapters; `requests`, NumPy and NetCDF4 for supported NASA output handling.
- **Knowledge and engine:** cited normalized JSON/CSV projection; separate modules for identity/normalization, generation, constraints, suitability, ranking, stress testing and Water Commons.
- **Testing:** Python `unittest`; Vitest and React Testing Library; TypeScript/Vite production build.
- **Persistence:** no application database or migrations. NASA caches use local filesystem paths and therefore require a host with suitable persistence for stable cache behavior.
- **Hosting plan:** Vercel Hobby frontend with `/api` rewrite and Render Free Django backend is configured in the repository; public deployment health and live-provider behavior must be confirmed before this statement is changed to “deployed.”

## Development and current validation

The source repository is at https://github.com/jjannat04/nextSeason. The app can be run locally with the instructions in `README.md`. Do not commit `.env` or NASA credentials. The backend reads `EARTHDATA_TOKEN` (or `NASA_EARTHDATA_TOKEN`) from the backend process environment only; the React client never needs this token.

The last recorded automated run on 30 October passed 91 backend tests, 26 frontend tests, and the TypeScript/Vite build. Earlier browser verification exercised the single-farm flow and a two-farm Water Commons case. These results do not certify uncompleted viewport checks, print preview/PDF, three-/five-farm manual flows, or deployed uncached NASA requests.

**Release verification still required:** offline data fingerprints now canonicalize text line endings, and tests confirm CRLF/LF equivalence while preserving detection of actual content edits. The projection was rebuilt, all four fingerprints match canonicalized Git blob content, and the local backend suite passes. After committing these changes, verify `/api/health` from a clean checkout and the deployed Linux backend before presenting the public app. The scientific data safety check remains enabled.

## Future work

Near-term work is to resolve the cross-platform fingerprint release blocker, verify the actual Vercel/Render deployment and Earthdata behavior, and complete the manual acceptance checklist. Longer-term work includes local cultivar/calendar/sequence validation with Bangladesh agronomists, reviewed Bangla localization, accessible chart and keyboard refinements, and expansion of crop coverage only when cited regional evidence is approved. See [`futurework.md`](futurework.md) for the prioritized roadmap.

## Team and contribution

**Team name:** OORT CLOUDS  
**Institution:** CUET, Bangladesh  
**Team member names and roles:** [Confirm and enter each member's preferred public name and contribution before submission.]

The current project context lists team roles by initials only. Do not publish initials as full identities or invent a contribution statement. Confirm each member has been added to the official team/project page.

## AI tools and originality disclosure

**Team confirmation required:** [List the AI tools actually used by team members during ideation, coding, research, design and writing, and describe their use accurately.]

This draft and project handoff were prepared with AI writing assistance. AI must not be presented as the source of agronomic facts or NASA observations. Review all claims, citations, code and media as a team; retain responsibility for the submitted work. Add or revise this section to match the portal's current AI disclosure question and the team's actual tool-use record.

## Submission completion checklist

- [ ] Verify the official portal fields and deadline shown for the team's registered local event.
- [ ] Confirm team names, roles, membership and selected challenge.
- [ ] Verify the rebuilt projection and `/api/health` from a clean checkout and the deployed Linux backend.
- [ ] Confirm the actual Vercel URL, Render URL, HTTPS, `/api` proxy, fixture lockout and provider response states.
- [ ] Complete [`docs/release-checklist.md`](docs/release-checklist.md), including responsive widths, 3/5-farm Commons, A4/PDF and real uncached/repeated NASA requests.
- [ ] Add a public demo link and a short demo video or presentation, if requested. Test access in a private browser window; add subtitles/captions where required.
- [ ] Attach final screenshots that show real UI states and honest source availability; do not use Stitch-only mock claims or fake results.
- [ ] Review AI-use disclosure, NASA citations, originality/terms statements, privacy and project license with the team.
- [ ] Paste the final reviewed text into the official portal and save/submit before its deadline. The official 2026 page currently lists the submission window as 14 November 9:00 a.m. through 15 November 11:59 p.m. local time; verify the team event's local time in the portal before relying on it.

## NASA Space Apps links

- [2026 Challenge: Field Shift](https://www.spaceappschallenge.org/2026/challenges/field-shift-adapting-farms-with-nasa-data/)
- [2026 event and submission timeline](https://www.spaceappschallenge.org/2026/)
- [NASA Space Apps resources](https://www.spaceappschallenge.org/resources/)

