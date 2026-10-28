# Next Season — discovery and implementation plan

## Release preparation — 28 October 2026

Git was initialized, ignore rules and a secret-pattern scan were checked, and a trusted-proxy HTTPS switch was added for the documented single-origin Nginx/Gunicorn deployment. `docs/deployment-guide.md` contains the deployment steps; `docs/release-checklist.md` contains the outstanding manual gates. No deployment or public release has occurred, and no release is marked complete. The scientific engine, crop catalogue and NASA adapters were not changed.

## Current milestone — final QA and deployment readiness (28 October 2026)

1. **Audit real flows and scientific behavior.** Exercise existing Django APIs with real normalized evidence/cached NASA data for normal planning, optional provider failures, no-option cases and 2/3/5-farm Water Commons scenarios. Compare response provenance, constraints, historical stress labels and unavailable values with documentation. Files: tests and final report only unless a correctness defect is found. Acceptance: no fixtures in normal mode, no fake zeros or unsupported claims. Manual: complete click-through in a browser.
2. **Responsive, navigation, print and accessibility audit.** Inspect current CSS/components at requested widths; fix definite overflow, hidden navigation, focus/label/status problems, and print CSS issues without redesign. Validate route/refresh behavior honestly; add stable public-page routes if missing. Files: frontend UI/styles/tests. Acceptance: all public links and steps reachable; mobile layouts remain readable; A4 CSS is present. Manual: real Chrome sizes, print preview and Save as PDF.
3. **Security and deployment audit.** Check ignored secret patterns, tracked state, source/bundle/log exposure, Django production settings, Vite API target, static serving, cache configuration, provider timeout behavior and migrations. Fix low-risk production configuration gaps where possible; document host/TLS and operations requirements. Files: settings/config, README, docs. Acceptance: no credential surface and explicit deploy checklist. Manual: production host smoke with credentials supplied only in environment.
4. **Submission documentation and final gates.** Refresh README, create docs index and `docs/final-readiness-report.md` with complete/manual/limits/blockers/post-submission categories. Run all backend/frontend tests, Django checks, TypeScript/Vite build. Report exact manual actions and unresolved blockers.

**Constraints:** no new science, NASA datasets or crops. Browser/print and uncached live NASA behavior require network and UI access; a blocked sandbox check must be reported as unverified rather than passed.

**Final QA result (28 October):** The normal browser journey reached a real research-evidence rotation response, explanation, historical scenarios, missing information and printable plan. Two-farm Water Commons conflict and incomplete-plan behavior were verified in the browser; backend tests cover 3/5-farm cases. Public direct routes, refresh and history navigation pass. All 91 backend and 26 frontend tests, Django system check and TypeScript/Vite build pass. Corrected mobile comparison, exact Water Commons volume display, API error copy, public hash routes, report duplication, security middleware and deployment documentation. The exact seven-width responsive inspection, Chrome A4/PDF print QA and uncached three-location Earthdata checks remain manual gates. See `docs/final-readiness-report.md` for evidence, limitations and deployment blockers.

## Current milestone — product packaging and scientific transparency (28 October 2026)

1. **Printable rotation plan.** Add a selected-candidate report backed by the current API response and entered field values. Show calendar month windows and provisional status, NASA provider status and interpretations, four historical stress outcomes where available, supported trade-offs, unresolved gaps and compact source links. Use browser print with A4 CSS; no server PDF or unstable share link. Test selected-candidate and unknown-value rendering. Files: `frontend/src/PrintablePlan.tsx`, `frontend/src/packaging.css`, `frontend/src/main.tsx`, frontend tests. Manual: print preview at A4 portrait and PDF save.
2. **Public methodology, NASA data and About.** Build public pages using the approved top navbar/cards and documented methods. State evidence classes and data flow; source cards must use product names, actual variables, access modes, resolution and limitations from `docs/nasa-data-depth.md`. Create concise references with existing authoritative URLs. Files: `frontend/src/PublicPages.tsx`, `frontend/src/packaging.css`, navigation and tests. Manual: source-link checks and responsive layout.
3. **Water Commons explanation and copy audit.** Add a short disclosure linking to the public methodology section. Search frontend copy for unsupported forecasts, field measurements, yields, irrigation savings, salinity/stage assertions and synthetic scores; correct any misleading claims. Files: `frontend/src/WaterCommons.tsx`, other frontend copy if needed. Tests: text assertions and search review. Manual: compare claims with backend output/methodology.
4. **Verification.** Full backend/frontend suites, frontend build and Django checks. Review report/source rendering with available results; note any unverified print/browser behavior and provenance fields that remain in expandable detail only. No scientific engine changes.

**Dependencies and risks:** the single-farm workflow has no persisted shareable plan URL, so copy/share is omitted. Farm area is not currently sent to the engine; an optional UI-only area can appear in the report without changing scientific evaluation. A report cannot turn provisional calendars into exact dates or pending SMAP/IMERG into observations. Browser print is subject to the user's browser/PDF settings.

**Implemented:** the selected option now opens an A4 browser-print report with the entered location/area/pH/irrigation context, backend crop windows, qualitative supported/unknown dimensions, three NASA source states, four historical stress scenarios where available, evidence references and limitations. Public Methodology, NASA Data and About pages use the existing top navbar and Stitch card/type palette. The Methodology page links evidence states to the actual decision flow; the NASA page uses the live-validated product IDs and variables. Water Commons has a concise “How this works” disclosure and opens the methodology page. A copy audit removed “See more than one possible future” from the landing page, and the new pages exclude the Stitch export's fabricated farmer, station, scores, water/economic claims and PDF/share buttons. No engine/NASA/crop changes were made.

**Verification:** 89 backend tests, 24 frontend tests, frontend TypeScript/Vite build and Django system checks pass. The report and public-page tests cover selected rotation, unsupported dimensions, evidence-state distinctions, exact NASA product names, Water Commons claims and absence of illustrative mock claims. **Manual final QA remains:** inspect desktop/mobile public navigation, A4 print/PDF page breaks and live-result report in a browser; this task's sandbox denied loopback browser access in the preceding milestone. The report deliberately surfaces compact source titles/links and provider status; exact NASA hashes, queries, raw time series and full agronomic trace remain in expandable workflow evidence rather than on paper. No stable plan URL exists, so sharing is by browser print/PDF only.

## Current milestone — Water Commons (28 October 2026)

**Scientific gate:** all 32 raw crop-water rows lack numeric seasonal water depths; the prototype projection marks water `insufficient_data`. FAO Kc references, POWER/IMERG rainfall and SMAP moisture cannot be converted into weekly delivered irrigation volume without supported ETo, effective rainfall, field-water balance, efficiency, durations and rice-specific assumptions. The Commons therefore accepts optional **farmer-entered planned weekly irrigation volumes**, clearly tagged as plans rather than NASA or crop-water requirements. Without a complete volume schedule for all farms, it reports qualitative calendar overlap and `insufficient_data` for capacity conflict, never a fictitious percentage or zero.

1. **Backend input and validation.** Add a separate `/api/water-commons/options` endpoint reusing existing prototype month generation to present only calendar/constraint-backed rotations, and `/api/water-commons/analyze` for 2–5 farms. Each farm supplies identifier, area, crop history/current crop, constraints, selected generated rotation, exact intended planting dates, farmer-assumed durations, allowed whole-week flexibility and optional week-indexed planned delivered irrigation volumes. Group capacity is m³/week and resolution one week. Validate candidate identity, dates within month windows, durations/harvest envelopes, crop IDs, unique farms, nonnegative finite volumes and constraints. No new crop or NASA adapter.
2. **Analysis and adjustments.** Align farmer-entered irrigation volumes to Monday-starting weeks, sum only complete numeric schedules, compare with shared capacity, identify contributors and severity as actual m³/week and ratio. Explore ± whole-week shifts only when all affected crop dates remain inside verified month envelopes and user flexibility/locks permit. Preserve every volume and its total when shifting; show before/after peak and conflicts plus farm-specific trade-off. Rotation switching is not quantified automatically because no supported alternative weekly irrigation schedule exists. A farmer can select another eligible generated rotation, enter its own complete plan, and rerun; absent evidence prevents an invented benefit. Qualitative mode lists overlapping crop periods without claiming capacity exceedance.
3. **Stitch-derived UI.** Add a separate Water Commons route from the landing navbar, independent of the single-farm workflow. Support 2–5 farm cards, server-generated rotation choices, area, intended dates/durations/flexibility, optional weekly irrigation plan, group capacity, conflict timeline, suggested shifts, before/after and provenance/limits. Remove the design's simulated tubewell rates, economic savings, groundwater and percentage claims.
4. **Verification.** Unit/API tests for aggregation, peak conflict, incomplete evidence, constraint/lock enforcement, shift conservation, feasible reduction, provenance and qualitative mode. Frontend tests for add/remove farm limits, conflict and comparison rendering. Browser smoke with a representative test plan. Document method and limits in `docs/water-commons-methodology.md`.

**Risks:** exact dates and durations are farmer planning assumptions within the backend's month-level envelopes, not agronomic estimates. A supplied weekly irrigation plan may omit real rainfall/field losses; it is a planning scenario, not a validated water requirement. No verified volume series means capacity comparison and adjustment benefit are unavailable. The single-farm engine remains unchanged.

**Implemented and checked:** `/api/water-commons/options` and `/api/water-commons/analyze` reuse the existing eligible rotation generator. The backend validates 2–5 farms, selected rotations, crop order, date windows, hard constraints, timing locks, finite declared weekly volumes, and a positive m³/week group capacity. It returns conflict attribution or qualitative overlap, provenance and conservative timing previews. The separate Stitch-derived React screen supports 2–5 farm cards, generated options, intended periods, complete-plan declarations, conflicts and before/after peaks. Method and evidence limits are in `docs/water-commons-methodology.md`. Eight Water Commons backend tests pass, including the dated-event shape used by the UI; the full backend suite has 89 passing tests, the frontend suite has 19 passing tests, the frontend builds, and Django checks pass. **Manual browser check remains unverified:** this sandbox denied loopback access to the dev server. Alternative rotation/crop changes can be chosen as eligible inputs and reanalyzed, but are not automatically suggested without an alternative complete weekly plan. No crop catalogue or NASA adapter changed.

## Current milestone — complete frontend integration (28 October 2026)

**Goal:** a coherent Stitch-derived landing-to-evidence flow using only the existing prototype and three-source NASA APIs. No new scientific dimensions, crops, NASA sources, Water Commons or printed report.

1. **Navigation and inputs.** Separate public landing from the planning stepper. Keep location, field/history, constraints and priorities in one persistent React state; validate before API calls and preserve values when moving backward. Load the three-source environmental profile explicitly, then submit the same inputs for rotation generation. Files: `frontend/src/main.tsx`, `frontend/src/strings.ts`, `frontend/src/styles.css`. Acceptance: a user can traverse every step and return without re-entering fields; no fixture mode is reachable.
2. **Results and evidence.** Render candidate timelines, supported and unsupported dimensions, NASA influence, evidence confidence and gaps from the response. Add up-to-three qualitative comparison, one-candidate explanation, four existing historical scenarios and a data-gap screen. Files: frontend result components, `types.ts`, styles. Acceptance: all figures/labels derive from API results, no arbitrary frontend score; explicit `insufficient_data` equivalents; source links only from provenance. Tests: compare selection, explanation, gaps, fixture isolation.
3. **Operational states and verification.** Show source-level pending/unavailable, separate incomplete-input/backend/no-rotation messages, responsive layout and keyboard/label checks. Run frontend/backend tests, build, Django checks and a browser smoke test across landing, input, NASA, options, comparison, explanation, stress and gaps. Manually inspect desktop/tablet/mobile and scientific claims against Stitch. Blocker: asynchronous SMAP/IMERG jobs may be pending; that state remains honest and retryable.

**Stitch adjustments:** omit illustrative telemetry, named climate events, invented yields, irrigation savings, household income, percentages and synthetic scores. Keep the approved typography, color, cards, sidebar and timeline language. English copy is centralized where newly introduced; Bangla remains an unimplemented language choice, not a machine-translated claim.

**Implemented:** the public landing and ten-step planning flow now share one React state. The field and crop-history form, hard constraints, priorities and explicit three-source NASA profile precede backend generation. Existing `/api/environment-profile` and `/api/rotation-plan` provide all observations, candidate rotations, evidence, ranking, stress scenarios and gaps. Distinct results, up-to-three comparison, per-option explanation, historical stress and missing-information views use those returned records. Earlier inputs survive backward/forward navigation; editing them clears stale recommendations. The normal flow never requests development fixtures, and the existing response guard rejects fixture content. Separate source loading, partial availability, no-option, invalid-input, backend-error and unsupported-dimension states remain visible.

**Verification:** 81 backend tests, 15 frontend tests, production frontend build and Django system checks passed. Browser smoke at the cached Khulna reference point traversed landing → location → field/history → constraints → priorities → NASA profile → four real options → two-option comparison → explanation → historical stress → missing information. The explicit profile refresh showed POWER, SMAP and GPM IMERG independently available for the selected day; sidebar back-navigation preserved entries and results. Desktop layout was visually inspected. CSS has tablet/mobile breakpoints; a device-width browser visual audit remains to be completed.

**Remaining presentation limits:** no production print plan, Water Commons, methodology page or Bangla translation in this milestone. `strings.ts` starts the English message catalogue, but older form/provider copy still needs extraction before a reviewed Bangla catalogue and active language switch can ship. The approved Stitch score bars, simulated telemetry, claimed localized field state, yields, irrigation savings and income were excluded. Comparison uses exact qualitative values and unknowns returned by the backend rather than synthetic scores or rank percentages.

## Current milestone — historical climate stress testing (28 October 2026)

**Goal:** compare existing rotation candidates under four observed historical years (`historical_normal`, `historical_dry`, `historical_hot`, `historical_wet`). These are retrospective tests, never forecasts. Keep the existing three eligible crops, NASA products and Water Commons scope unchanged.

1. **Validate source depth.** For a Bangladesh reference coordinate, check ten complete annual POWER records (2015–2024) for all four existing parameters. Complete a real June–July 2024 IMERG Final subset and check daily coverage, retrieval counts, checksums, cache reuse and job latency. A full-year SMAP subset would require roughly eight three-hourly granules per day and is not a practical synchronous scenario dependency; test a bounded window if feasible, and otherwise retain the existing live one-day evidence as context only. Block affected dimensions if coverage is incomplete.
2. **Construct scenarios.** Use complete POWER annual observations at the requested coordinate, from the fixed 2015–2024 reference decade. Annual T2M mean and PRECTOTCORR total select the representative years by deterministic empirical rank rules: near-median in both variables for normal, minimum precipitation for dry, maximum T2M for hot, maximum precipitation for wet. Preserve annual daily series, exact year, baseline distribution/median, selection rule, query and source checksum. Scenario names describe this sample, not universal drought, heatwave or flood classifications. A missing baseline year prevents classification rather than becoming zero.
3. **Evaluate existing candidates.** Reuse supported crop temperature-envelope screening for each candidate's calendar months and existing published annual rainfall envelopes against complete POWER annual precipitation. Keep soil, rotation rules and farmer constraints fixed. Return all unsupported water, salinity, stage-stress, yield and income effects as `insufficient_data`. Determine robustness from the number of distinct observed scenario years with a supported `potential_concern`; missing mandatory comparisons yields no robustness label. No probabilities or synthetic weather.
4. **API and UI.** Add a `stress_tests` object to prototype rotation responses with four scenarios, per-candidate interpretations, evidence status, NASA provenance and limitations. After backend tests and real-reference verification pass, add “How Does This Rotation Hold Up?” using the Stitch scenario cards and comparison layout while excluding its unsupported synthetic scores, named disasters, forecasts, irrigation, yield and income claims. Highlight all tied best supported candidates as “Most Robust (tie)”.
5. **Verification and report.** Test observation-derived selection, location dependence, dry/wet and hot evidence, missing-value behavior, robustness rules, provenance, API integration and no unsupported scores. Check backend, frontend, accessibility basics and a real-reference API response. Record exact rules, source periods, performance, missingness and scientific limits in `docs/stress-testing-methodology.md`.

**Risks:** POWER annual series can be incomplete or unavailable for an arbitrary location; do not substitute another coordinate. IMERG multi-month jobs can be slow or partial. The published crop rainfall envelopes are global and provisional for Bangladesh, and month-level calendars do not identify crop growth stages. The Stitch screen's simulated disaster names, numeric robustness scores, yield/loss and irrigation claims have no evidence and must not ship.

**Implementation and verification:** Four observed-year scenarios, per-candidate qualitative comparisons, explicit missingness, provenance, robustness ties and the Stitch-derived screen are implemented. Complete 2015–2024 POWER records were verified at Khulna and Dinajpur; a real 61-day IMERG subset and a real seven-day SMAP subset had complete coverage and checksummed source files. See `docs/stress-testing-methodology.md` for rules, actual selected years, source depth, cache and limitations. Backend tests, frontend tests/build and browser verification passed. Unsupported crop-stage, yield, irrigation, flood and income effects remain `insufficient_data`; the prior farmer-priority ranking is unchanged.

## Live Earthdata validation update — 28 October 2026

This user-directed validation remains limited to NASA data depth. At the Khulna reference point (22.8, 89.55), a one-day `SPL4SMGP.008` Harmony job completed and eight source NetCDF granules were verified, checksummed, cached and extracted. SMAP is **LIVE_VALIDATED** for that tested point/day; POWER is available independently. The existing AppEEARS route remains unvalidated, so the SMAP provider uses the verified Harmony route when only the Earthdata environment token is configured. `EARTHDATA_TOKEN` is now accepted for both Harmony adapters; credentials remain server-side.

`GPM_3IMERGDF.07` Final is now **LIVE_VALIDATED** for four one-day extracts at the same point. The initial Harmony job failed with a GES DISC EULA approval error; after owner approval, fresh jobs downloaded genuine Final V07 NetCDF subsets. Native title/DOI/date/units/retrieval count/grid and checksums were verified. A real July 2024 versus July 2023 comparison changed the API indicator to `wetter_than_selected_comparison`. A Django request for January 1, 2024 returned POWER, SMAP and GPM all available with no credential in response/logs. The live-access gate is resolved for the tested one-day scope. Year-scale coverage, annual rainfall scoring and AppEEARS CSV extraction remain separate limitations; no stress-testing or Water Commons work was started. Details and job metadata: `docs/nasa-data-depth.md`.

## Current milestone — NASA DATA DEPTH (October 28)

Scope: unchanged crop catalogue; no Water Commons or major visual redesign. Backend first, then the existing planning NASA-profile section becomes “Your Field From Space”. Preserve source failures, native resolutions, observation periods and provenance.

1. Verify products/access: POWER daily point JSON remains independent; SMAP SPL4SMGP.008 via the live-validated asynchronous Harmony geographic subset (with the existing AppEEARS point adapter as an unvalidated alternative); GPM_3IMERGDF v07 Final via the live-validated asynchronous Harmony geographic subset and NetCDF extraction. Public NASA product/layer/capability metadata was inspected. An Earthdata environment token and GES DISC application approval were used for live validation. These are different source workflows, not interchangeable point APIs.
2. Implement separate adapters, raw checksummed/atomic caches, saved job identities and bounded polling/collection. Fetching jobs never blocks for completion; pending/delayed products stay unavailable. Keep tokens and signed download URLs out of API provenance. Cache keys include exact point, period, product/version, variables and adapter version.
3. Unified profile endpoint returns location/power/smap/gpm/interpreted_indicators/provenance/provider_status/limitations. Optional provider failure must not break POWER or rotations. Validate units, fill values, dates, requested point/grid, temporal completeness and granule provenance. SMAP L4 is an assimilated model product (surface 0–5 cm, root zone 0–100 cm), not an in-field sensor.
4. Indicators: SMAP native seasonally resolved root-zone percentile supplies below/above product median without inventing a volumetric drought threshold. IMERG complete annual totals may be compared with independently checked annual species rainfall references, explicitly not seasonal irrigation. Recent-vs-historical rainfall requires matching complete comparison windows; absent baseline remains insufficient_data. Do not call a short baseline a WMO climate normal. Observed moisture context is separate from crop damage and irrigation demand.
5. Rotation integration: preserve temperature-only behavior without supplementary data; expose supported rainfall reference and moisture-exposure components with NASA trace. Unavailable values have no penalty. No new hard crop limits, numerical water-demand model or catalogue expansion.
6. Tests: individual adapters, partial service failure, units/fill/zero handling, exact-query/checksum cache, async state, provenance, indicator/rotation sensitivity and existing regression suite. Backend checks must pass before frontend work. Then use approved Stitch typography/card/source-impact/limitation language; show simple interpretations/statuses and expandable values, not dense raw data. The supplied export has no dedicated “Your Field From Space” page; reuse its NASA Data Sources inventory cards and planning sidebar, removing illustrative unsupported live/status/forecast claims.

Acceptance: three independently represented providers, real POWER still usable, genuine authenticated ingestion paths with honest unavailable/pending states when access is absent, supported multi-source indicators affect evaluation, source/version/units/time/resolution retained, no failed provider becomes zero, API and browser checks pass. Manual verification: public metadata/access and product units; native percentile meaning; annual versus seasonal rainfall; Stitch alignment; truthful two-source unavailability until owner configures credentials. Deliver exact setup/access limitations and verification outcomes in `docs/nasa-data-depth.md`.

**Implemented:** independent `power.py`, `smap.py`, `gpm.py`; credential-safe bounded transport and raw/job caches; a unified `/api/environment-profile`; `space_profile` on prototype responses; native SMAP root-zone percentile interpretation; complete-annual IMERG/EcoCrop rainfall screening; explicit moisture-exposure preference and preserved unknown optional values. Real source/version/field metadata was checked publicly and stored with hashes. Prototype release fingerprints now include independently checked existing annual-rainfall references; no crop/raw CSV expansion or rewrite occurred. Backend tests passed before the frontend screen was connected.

**UI:** `FieldFromSpace.tsx` uses existing Stitch NASA inventory cards/design tokens and planning sidebar. It exposes three source statuses, farmer-readable summaries, rotation impact and limitations with closed exact-data/provenance disclosures. No illustrative live/synchronized stream, flood forecast, crop-damage or irrigation-saving claim was copied from the designs.

**Verification:** 75 Python tests pass; nine frontend tests, Django checks and frontend build passed in the preceding milestone. Tests prove optional-provider failure isolation, no zero substitution, source-shape parsing, async/cached behavior, raw/source integrity, unit/count/mask/date/grid checks, provenance/token safety, qualitative indicator changes, GPM-driven rank changes and SMAP exposure changes. Live public AppEEARS/CMR/Harmony metadata succeeded. Authentic cached Khulna-reference POWER (2024, 366 days), SMAP (2024-01-01, eight three-hourly files) and GPM Final (four one-day files in 2023/2024) returned available in the unified API for the shared January day. Full source/method/cache/setup report: `docs/nasa-data-depth.md`.

**Remaining scientific/operational limits:** live data evidence is one SMAP day and four IMERG days at one reference point; annual-scale coverage and annual rainfall-based ranking on real full-year data remain unvalidated. The AppEEARS SMAP CSV path remains source-contract-tested only, while the Harmony SMAP NetCDF path is live-validated. Current API reports unsupported dimensions as insufficient data. No next product milestone started.

## Current milestone — evidence-tiered prototype recommendations (supersedes strict release gate)

User-authorized October 28: this is an explainable research prototype. Verified and credible provisional evidence may participate; unresolved/missing evidence cannot influence scientific evaluation or hard constraints. Do not relabel provisional evidence or require optional calibrated models.

Contained implementation: (1) build a separate reproducible prototype projection from normalized references and audited calendars/rules; (2) retain source/status/applicability and exclude unresolved/incomplete calendars; (3) generate conservative recurring month-window rotations with visible idle/fallow periods and farmer constraints; (4) compare NASA POWER observations with published temperature and basic pH ranges using documented qualitative rules; (5) propagate evidence status, deterministic confidence and optional-data explanations; (6) enable the real-data UI under `prototype_recommendation` with one concise disclaimer; (7) test provenance, provisional/unresolved behavior, NASA/location sensitivity, constraints, confidence and fixture isolation, then perform real POWER/API and browser checks.

Expected first subset: Aman, maize and sunflower using complete national references, with coastal sequence applicability labelled provisional. Mungbean late-Rabi/spring field-clearance evidence remains incomplete; do not substitute its August–September calendar into a rice-following Rabi system. No invented duration, exact date, sequence score or family-level benefit. Unknown pair evidence means no bonus/penalty; generation enumerates the documented alternating rice/dry-crop system templates only and does not claim unknown pairs are prohibited.

Acceptance: at least three eligible real crops, multiple feasible alternatives, visible month precision/gaps, authentic NASA-dependent qualitative interpretation, constraints enforced conservatively, traceable statuses/sources and no fixture content in prototype responses. Missing field pH leaves soil evaluation unknown without fabricating a default. Optional active priorities are reported unavailable while supported priorities can still order alternatives with an explicit partial-ranking label. All tests/build/checks and manual real-data verification must pass. No SMAP, IMERG, Water Commons or major visual redesign.

**Implemented outcome:** `prototype_recommendation` is the default API/UI mode. The separate fingerprinted offline prototype projection enables Aman, maize and sunflower; mungbean is reference-only pending a complete season-aligned calendar. Provisional national calendars and conditional coastal sequence/derived annual-return evidence retain raw values, sources, qualifiers, statuses and applicability. Unknown pairs have no biological hard rule or ranking penalty; search is explicitly limited to documented system templates. Conservative month envelopes, visible idle intervals and all farmer constraints replace invented exact-day durations. NASA daily-mean ranges for activity calendar months and farmer pH feed qualitative categories; no calibrated numeric score or prediction is claimed. Optional unsupported goals yield explicit gaps and partial ranking, not total blocking.

**Evidence UX and safety:** deterministic high/moderate/limited confidence and an evidence ledger are attached to every option. One concise prototype disclaimer, source details and Missing Information reasons are visible. The browser always requests real-data prototype mode, has no fixture selector, and rejects fixture markers/wrong modes/untrusted origins. The original raw/staging/reference/audit files remain intact. Explicit legacy `production` requests remain reference-only for compatibility and are not the normal flow.

**Validation outcome:** 51 Python tests and five frontend boundary tests passed; frontend build and Django system checks passed. Added real-projection tests for provisional participation, unresolved exclusion, provenance/status propagation, month bounds and farmer limits, optional gaps, unknown pH, source fingerprint staleness, deterministic confidence, NASA/location changes and climate-driven rank changes, soil/priority sensitivity and fixture rejection. Live NASA POWER 2024 requests at 22.8,89.55 and 25.63,88.65 returned 366 complete daily observations each and six real-data options; crop interpretations differed, while coarse option categories tied honestly. Browser verified six options, month windows/idle gaps, moderate evidence confidence, source statuses and useful gaps without fixture content. Test reference coordinates and pH are not field validation cases. Current documentation: `docs/prototype-methodology.md`, updated API/data/blocker notes and README. No next feature started.

## October 28 production-gate verification pass (current priority)

Scope: verify the four-crop calendars and directional sequence evidence; no new product features. Read all 15 originals and all staging/projection records. Preserve their bytes and existing field-level permissions.

1. Calendar evidence: compare BARC, BRRI/BARI leads, BBS national tables and DAE/BAMIS regional charts. Deliver `data/normalized/crop_calendar_verified.csv` with original records, source locators, month precision, season/region/cultivar scope and separate source-verification versus release status. Never infer exact days, emergence lag or turnaround.
2. Sequence evidence: deliver `data/normalized/crop_rotation_rules_verified.csv`, covering all 16 directed pairs in the four-crop set plus narrower institutional leads. Preserve original cultivar claims, distinguish observed forward systems from inferred annual return phases, keep absent pairs unresolved, and do not introduce weights or blanket family bans.
3. Release decision: deliver `data/normalized/production_crop_subset.csv` and a source-backed decision in `docs/production-gate-verification.md`. Optional water/salinity/stage/soil-health gaps do not block release. Required calendar, climate, soil and executable sequence applicability do.
4. Conditional implementation: activate only if a coherent, geographically applicable multi-crop subset passes the required gates. Otherwise retain production blocking and specify the exact remaining evidence/method decisions. Month-only evidence must never be padded into the current exact-date fixture contract.

Acceptance/tests: byte-identical raw files; reversible evidence records with original values; complete pair coverage; verified facts distinguished from provisional/inaccessible leads; no unsupported day ranges, numeric compatibility scores or missing-as-zero values; production isolation tests and all existing checks pass. Manual review: PDF chart labels versus week numbers; seedbed/transplant/harvest basis; seasonal/cultivar alignment; applicability of each required core comparison. Blockers: no approved co-located calendar/system/cultivar combination, conditional sequence management, and existing global-reference-only climate/soil evaluation permissions. See the verification report for final outcomes; earlier statements that *no calendar evidence exists* describe the previous runtime release.

**Verification outcome:** the three requested CSVs and `production_verification_manifest.json` are present. Thirteen calendar evidence records retain original CAL01/CAL04/CAL05/CAL06 values; eleven remain provisional for local production and two unresolved. Five BBS records independently support complete national month-level references. Eighteen sequence records cover every four-crop pair and two narrower BRRI leads: three source-supported conditional forward systems, three provisional annual returns, ten unresolved pairs and two provisional source-access leads. No fabricated discouraged/avoid relation, numeric gap, exact date or compatibility weight was introduced.

**Production gate: not passed.** No crop is released. `docs/production-gate-verification.md` provides exact publications/pages, chart conflicts, core dimension limits and the smallest unblock target (Aman + BARI Mung-6 at one matching ecosystem/cultivar context). Optional water/salinity/stage dimensions remain `insufficient_data` without becoming extra release requirements. Application code, runtime projection, staging and raw CSVs were not modified; fixture isolation remains enforced. Task D activation was conditional and its scientific prerequisite was not established.

**Validation:** 34 Python tests (including five new evidence/provenance/precision/release tests), three frontend safety tests, production frontend build and Django system checks passed. The first frontend test run hit a sandbox temporary-directory rename restriction; rerunning with TEMP/TMP inside `.runtime/test-tmp` passed without code changes. PDF target tables and regional charts were visually checked. Full BRRI page/journal/BARI detail access limitations remain explicitly provisional, not silently treated as verified sources. No next product phase started.

Prepared October 27, 2026 (Asia/Dhaka). Target: complete working product November 1, 2026.
Status: October 28, 2026 — CSV audit approved; controlled normalization and Milestone 1 implementation authorized. Broader phases remain deferred.
The discovery/audit snapshots below describe the earlier repository state. The user approved the audit and controlled Milestone 1 work on October 28; that implementation is now present. Broader catalogue activation and the original full-product phases remain outside this contained execution.

## Latest data readiness update — October 27 CSV audit

### October 28 execution amendment (takes precedence over earlier phase ordering)

**Execution outcome:** normalization and the engineering vertical slice are implemented. Scientific production recommendations remain intentionally blocked pending local calendar/rule review; Milestone 1 is **not yet scientifically complete**.

- A–D: explicit canonical IDs and 261 namespaced aliases; all 374 records staged with raw/normalized values, provenance, confidence, geography, units and field states; original CSV bytes preserved. Five unresolved occurrences reported (three rice-species/system ambiguities, Dhaincha, Rabi crops). Three salinity conflicts retained unresolved.
- E: only Aman rice, maize, sunflower and mungbean projected for runtime. Exact official-source temperature/optimum-pH transcriptions allow labelled global-species reference comparisons. No unverified local dates, numeric water/stage-stress/salinity/soil-health/economic scores, or automatically inherited cultivar thresholds contribute to production ranking.
- F–G: real POWER daily adapter and exact-query atomic raw-response cache, quality/coverage/unit validation and returned metadata/checksums. Live smoke for the design-example point 25.7439,89.2752 and 2024 returned 366 complete days for all four parameters; repeat used cache. This is not a validated farm case.
- H–L: dated generation, explicit executable-rule gates, crop history/current occupancy, required/excluded crops, locked slots, change limits, deadlines, separate categorical/structural/preference dimensions, transparent priority-ordered ranking and trace-backed explanations. Full candidate path tested using isolated, clearly synthetic development agronomy only. Active unsupported priorities leave ranking incomplete rather than silently reweighting.
- M–N: stateless Django `POST /api/rotation-plan`, input/safety validation, and minimal responsive React/Vite UI styled from Stitch. Production returns authentic evidence and `blocked_scientific_data`, not fictional plans. Fixture mode needs DEBUG plus a separate server switch and explicit request mode; the normal view rejects fixture/mismatched-mode responses. The final user-facing local preview has fixtures disabled.
- Verification: 29 offline Python tests, 3 frontend response-boundary tests, frontend production build and Django checks passed. Browser verified production evidence/blocker, synthetic-only candidates with visible warnings, cleared stale results after input changes, accessible priority-slider names and 390px mobile evidence layout without page-width overflow. Dependency installation used an isolated Python environment; patched Vitest advisory fixed, install audit then reported zero vulnerabilities.
- Deliverables: `docs/normalized-data.md`, `docs/milestone1-api.md`, `docs/research-blockers.md`, updated NASA/architecture/decision notes and runnable README. No SMAP, IMERG, Water Commons, database import, persisted farmer accounts/drafts, reports or full UI polish implemented.

**Next scientific handoff:** resolve P0 items in `docs/research-blockers.md`, then activate only reviewed location/cultivar-scoped calendars and sequence rules in a new controlled release, with independent expected cases. Do not flip all provisional flags or treat the engineering fixture demo as completed agronomic validation. All other N01–N13 tasks below retain their scientific review gates even though offline staging utilities are now implemented.

Follow A–N: canonical crosswalk → provenance-preserving normalized schema → offline normalization utilities → verification/conflict flags → four-crop subset → POWER adapter/cache → environmental profile → generator → hard checks → supported dimensions → priority ranking → explanations → API → minimal React UI. Do not start SMAP, IMERG, Commons or full UI polish.

Four-crop scope: Aman rice, maize, sunflower and mungbean. All have species-level climate references and conditional cropping-system evidence. No verified local calendars exist. The production endpoint must expose this blocker rather than generating research-calendar recommendations. A separate DEVELOPMENT_FIXTURE layer may exercise the complete algorithm; both server configuration and explicit request mode are required and production UI must never render its results as real recommendations.

On October 28 the four official FAO EcoCrop pages were independently inspected: IDs 1574, 238663, 1191 and 2150. Their temperature envelopes and optimal pH match the slice CSVs. Only those exact field transcriptions may be marked source-verified for **global-species reference comparison**, with page locator and retrieval date; this is not local agronomic validation, a stage-injury model or a calendar approval. No arbitrary numeric scores or new crop-cycle values will be imported from those pages. Calendar/sequence activation remains gated.

Implementation files: `backend/next_season/{knowledge,environment,engine,api}/`, `backend/config/`, `data/{crosswalk,normalized}/`, `tests/fixtures/`, `frontend/`, and focused documentation. Keep all 15 raw CSVs byte-identical. Staging outputs may preserve all 374 raw records, but runtime scientific logic reads only the separately reviewed four-crop projection, never the CSVs directly.

Acceptance: reproducible staging/crosswalk coverage and conflict report; explicit unresolved mappings; production POWER profile and source-backed reference comparisons plus honest blocked calendars; development-only end-to-end candidate generation with separate dimensions and traceable explanations; strict user constraints; offline tests for identity/nulls/constraints/priority and environmental sensitivity/provenance/fixture isolation; frontend build and browser review; real POWER smoke request if network permits. Milestone scientific readiness stays incomplete until local calendars/rules are approved. Record outcomes below when verified.

The researcher delivery now contains **15 CSVs and 374 records**. This supersedes the original empty-research inventory and “no research at all” risk below, which describe the earlier discovery snapshot. See [the complete CSV audit](docs/csv-audit.md) for every column, missing-value counts, types/ranges, duplicate checks, conflicts, canonical-schema proposal and source-file hashes.

Current readiness is **research delivered, normalization and scientific approval pending**:

- All CSVs parse with consistent widths; no exact duplicate rows or duplicate tested composite keys. Repeated species-level property bundles across distinct varieties must not be counted as independent evidence.
- Four crop-ID namespaces do not join directly: master C01 is Aman rice; numeric ID 1 is BARI Mung-6. Separate species, production systems and cultivars, with approved aliases scoped to original files.
- All nine calendars are explicitly unverified/not production-ready and have no source title/URL/year; five lack harvest windows/durations. No complete validated calendar set exists for one selected location.
- File 5's mungbean threshold 2.02 dS/m is an observed field value according to file 7, not a tolerance threshold. Rice 8/6 dS/m labels and maize/sunflower proxy thresholds also require claim-level review. Quarantine rather than reconcile automatically.
- Kc references do not supply irrigation demand: all 32 water rows lack numeric water requirements; timing fractions are assumed, mustard fractions missing, and development curves/local water balance need review.
- No AEZ-wide soil-property defaults exist in file 10; only three local observation contexts. Suitability map classes are not extracted in file 11. Stage-stress data is mainly qualitative, with no approved timing/response model.
- Sixteen Bangladesh case records are useful references but all lack coordinates and NASA reanalysis; trial, landscape model and survey outcomes must stay separate. Sources contain missing metadata and no consistently explicit fact-level locators.
- Safe current use is metadata/reference display and product form/metric definitions. Production calendar feasibility, numerical water risk and verified crop-stage ranking are not yet supported. Crop filtering and qualitative suitability/evidence remain conditional on approved mapping and applicability.

**Milestone 1 definition:** first coherent farm-to-plan vertical slice at one researcher-approved location, with at least two distinct dated feasible multi-season alternatives, farmer hard constraints, authentic NASA-dependent evaluation and traceable explanations. Foundation/UI completion alone is not this milestone.

**Proposed catalogue:** nine operational entries (existing eight master entries plus sesame), representing seven species because Aman/Aus/Boro are rice systems. Sesame lacks master/climate/calendar/water coverage; watermelon remains generation-ineligible until connected evidence is delivered. If 8–10 means distinct species, new complete profiles are required. Do not inflate crop count with maize hybrids.

**Smallest candidate slice:** Aman, maize, sunflower and mungbean; proposed raw row subset is listed in the audit. CAL01/CAL04/CAL05/CAL06 come from different or underspecified coastal scopes and are all inactive until reviewed; no claim that their current combination is feasible. Three future crop events may span more than one year. Fallow/gaps must be explicit and cannot be disguised as triple annual cropping.

### Required normalization and review tasks before Milestone 1

Perform these only after audit approval. IDs match the detailed acceptance evidence in `docs/csv-audit.md`:

1. **N01 — raw preservation:** manifest file hashes and retain original CSV record/cell values, including N/A and blanks. Never overwrite researcher originals.
2. **N02 — identity crosswalk:** approve species/system/cultivar and per-file alias mappings for every enabled subject; ambiguous identities block activation.
3. **N03 — typed values:** define null reasons, booleans, enums, scalars/ranges, date windows and status parsers. Preserve default-unset versus false/zero. Split priority warning text from status.
4. **N04 — sources:** create reviewed publication/URL/locator links; resolve duplicate MODFLOW work identity; trace seven uncited soil rows and missing stage placeholders. Treat internal-spec citations separately from science.
5. **N05 — salinity conflicts:** withhold mungbean 2.02 and unreviewed rice/maize/sunflower yield-threshold uses; preserve observations/stage descriptors/proxies as separate claims and log researcher resolutions.
6. **N06 — calendars:** select one site/region; obtain cited approved planting/harvest/duration/turnaround data, seedbed versus field occupancy and cross-year semantics for two complete alternatives. No `production_ready=no` dates enter generation.
7. **N07 — applicability:** approve species-to-variety transfer, management/residue conditions and region scopes. No sample-to-AEZ-wide or coastal-to-Rangpur extrapolation.
8. **N08 — units:** define measurement basis, endpoint, spatial denominator and period. Annual rainfall ≠ seasonal irrigation; ECe ≠ arbitrary EC; equivalent yield ≠ physical yield; BCR ≠ MBCR.
9. **N09 — water methods:** validate stage timing, Kc ranges/interpolation, ETo/effective rainfall, irrigation efficiency and water-balance assumptions before numerical water scores/Commons. Unavailable methods remain explicitly gated.
10. **N10 — rotation evidence:** normalize directional species-system claims and cultivar references; all 42 current relations require calendar verification. Define absent-pair unknown semantics and independently reviewed hard rules.
11. **N11 — evaluation policy:** approve climate aggregation, soil/stage stress interpretations and five-priority scoring/normalization. Missing objectives cannot silently get zero or be reweighted.
12. **N12 — validation:** select site-scoped cases, complete farm inputs/locations and fetch real NASA history; B approves expected decisions and all six mandatory sensitivity/constraint cases. Published metrics are not predicted outcomes.
13. **N13 — gated import:** after approval, implement a dry-run validator and versioned field-level activation allowlist. Successful parsing alone cannot activate scientifically unverified claims; report all quarantined/unmapped facts.

Dependencies: N01–N04 enable a safe data-staging design; N05–N08/N10 require researcher decisions; N09/N11 enable meaningful water/climate ranking; N12 validates the slice; N13 activates only reviewed claims. Missing science is a release blocker, not a null-filling task. Importing, rewriting CSVs or implementing the data layer requires the user's approval of this audit.

The original 57-hour estimate predates this delivery and does not budget a full review of 74 references or completion of missing calendars. Re-estimate Milestone 1 after researcher commitments for N05–N12 are known. November 1 remains high risk until those gates are met.

## 1. Product understanding and delivery boundary

Next Season compares feasible **sequences of crops over several seasons**, rather than recommending one crop. It combines farmer inputs, local agronomic knowledge, NASA environmental evidence, hard constraints, and farmer priorities to expose alternatives and trade-offs. Bangladesh is the first validated region; regional calendars and rules must be replaceable without changing the engine.

The complete flow is location → field/history → constraints → priorities → environmental profile → alternatives → comparison/evidence → historical stress tests → missing information → selected plan → print/share. Water Commons adds coordination across farms sharing irrigation capacity.

NASA inputs must change actual evaluation or ranking under appropriate conditions. A source badge or chart alone does not satisfy integration. Historical records are not forecasts. Estimated soil-health contribution is not measured improvement. Regional gridded observations are not field measurements. Unknown data must remain explicit.

November 1 is a high-risk target from this starting point. Aim for a complete, narrow vertical product: one researcher-approved Bangladesh region, a small approved catalogue sufficient to produce multiple rotations, three consecutive future seasonal slots initially, and a small shared-irrigation group. These are proposed scope decisions, not already validated facts. The current crop is carried forward until its harvest; never schedule a past planting date as a future recommendation. Keep horizon and region configurable.

All required feature areas remain in scope. If research or NASA access gates fail, an honest incomplete feature is preferable to invented output, but it does **not** count as feature-complete. Any deadline scope reduction needs an explicit decision. Accounts, OCR soil-report extraction, forecast alerts, aquifer simulation, live collaboration, global crop coverage, and production-scale optimization are not needed for the initial complete flow.

## 2. Read-only discovery findings

### Repository inventory

- Read `AGENTS.md` and `PROJECT_CONTEXT.md`.
- Actual design root: `design/stitch_next_season_crop_navigator/`; the `design/stitch-export/` path in PROJECT_CONTEXT is stale.
- Read all 14 `code.html` exports and `orbital_agriscience/DESIGN.md`; inspected all 14 screenshots through two contact sheets and checked their image dimensions.
- `research/` contains only an empty `csv/` directory. There are no research records, references, spreadsheets, PDFs, or NASA observations to import.
- `src/` is empty. No package manifests, backend, tests, dependency locks, CI, or deployment configuration exist.
- `README.md`, the previous `PLANS.md`, and `docs/architechture.md`, `docs/decisions.md`, `docs/nasa-data.md` are empty. Preserve the existing misspelled architecture filename until a deliberate documentation rename.
- `git status` reports that this directory is not a Git repository. Do not assume a remote or initialize/push during discovery.

### Stitch framework and suitability

The export consists of standalone HTML documents using Tailwind's browser CDN, repeated inline Tailwind theme configuration, Google Fonts (Inter and Plus Jakarta Sans), Material Symbols, inline SVG/CSS charts, static sample data, and limited DOM scripts. Examples include sidebar state synchronization and scenario-tab styling. There is no React, router, build pipeline, backend/API, real map SDK, persistent state, or computational engine. Controls and links frequently have placeholder `href="#"` destinations; visible micro-interactions do not implement the product workflow.

Use the export as the visual source of truth and a source of selected markup/CSS/SVG structures. Do not ship each HTML page directly or wrap the mockup in an iframe. Convert useful markup into accessible React components, replace DOM scripts with state, compile Tailwind locally, and bind every displayed scientific value to real evidence or an explicit unknown state. Preserve approved typography, spatial hierarchy, cards, colors, navigation intent, timelines, and chart language.

### Screen/component reuse map

| Export | Reusable visual structures | Required functional work |
| --- | --- | --- |
| Landing with hero carousel | Navbar, hero, process cards, NASA panel, rotation teasers, Commons teaser, footer | Real navigation; labelled examples; functioning accessible carousel only if retained |
| Farm location | Map/input split, location summary, coordinates, source-loading list | Real pin/coordinate entry; permission and network fallback; no automatic parcel area inference |
| Field information | Input groups, history cards, units, optional soil fields, summary | Editable dated history/current crop; unknown values; consistent conversions and provenance |
| Constraints | Locked crop chips, exclusions, change limit, planting flexibility | Strict checks, conflict handling, measurable limits; distinguish preferences from hard rules |
| Priorities | Five sliders, presets, weight balance, preview | Normalization, zero-weight behavior, actual recomputation, unavailable objectives |
| Results | Rotation timelines, objective summaries, evidence ribbons, selection | Generated alternatives, computed counts, no-results and insufficient-evidence states |
| Comparison | Alternative cards, grouped trade-off matrix, selection footer | Same run/units/baseline; two or more alternatives where available; unknown cells |
| Explainability | Evidence → crop impact → rotation impact cards; trade-offs | Trace-backed contributions and cited rules; no invented causality |
| Climate stress test | Scenario tabs, performance comparison, risk callouts | Historical scenario selection and reruns; missing overlap handling |
| Missing information | Gap list, edit modal, data-origin summaries | Real missing-field impact and recomputation; no arbitrary confidence percentage |
| Water Commons | Farm cards, stacked demand bars, capacity line, before/after | Group setup, demand estimates, bounded coordination search, no-solution state |
| Printable report | Crop sequence, calendar, evidence ledger, risk blocks | Saved-run snapshot, real print stylesheet, pagination, private sharing |
| Methodology | Pipeline and methodology sections, limits | Describe actual implementation and validation only; top public navbar |
| NASA data sources | Product cards, provenance/limitations layout | Actual products, versions, dates, availability and access status; top public navbar |

There are **14 screen pairs**, while the context lists 15 screens. The dedicated **Your Field From Space / NASA environmental profile** screen is absent. Compose it from existing NASA panels and chart styles; it needs user review against the design language. Crop history is embedded in Field, rather than requiring a separate new screen. Explanations, stress, confidence, and Commons can be result subroutes while the compact eight-step workflow remains consistent.

### Assets

- 14 full-page PNG references; these are review baselines, not application backgrounds or separable source artwork.
- 14 HTML files; one design-token/style document.
- Eight distinct remote `lh3.googleusercontent.com/aida-public/` image references: one landing image, three data-source images, one constraints image, two confidence images, and one location image. Availability, rights, attribution, and local bundling permission are unverified.
- Remote font/icon dependencies; no local font files, standalone logo artwork, crop illustrations, satellite rasters, map tiles, or geospatial datasets.
- Inline SVG diagrams and CSS charts can be adapted after replacing static scientific claims. The satellite/leaf icon treatment can inform branding; it is not a NASA endorsement mark.
- Audit remote imagery and font licences before bundling. Use licensed local assets where possible for demo reliability. Do not suggest the decorative map image is a live satellite observation.

### Design inconsistencies and scientific conflicts

1. DESIGN.md front matter uses black primary/tertiary and a pale-blue canvas, while prose specifies navy/emerald/off-white. HTML also remaps radii (`full` becomes 0.75rem), differing from token definitions. Consolidate tokens against the approved screenshots and document the choice; do not independently redesign.
2. Headers switch between Barisal and Rangpur; step labels/progress disagree; Aman is associated with different seasonal slots; baseline and option identities change across pages. Field, constraints, results, comparison, explanations, and report must consume one persisted farm/run.
3. Hard constraints are represented as “98% compliance,” while cards promise absolute compliance. Use satisfied/violated/unknown checks. A score cannot compensate for a violation; unknown critical feasibility cannot be labelled verified.
4. The methodology claims NSGA-II/Pareto ranking and rejects scalar weighting, while priority screens promise weighted live reranking. Use deterministic objective vectors plus explicit farmer weights; show trade-offs and optionally Pareto dominance without an evolutionary optimizer. Rewrite methodology accordingly.
5. Mock claims include peer review, 1,420 trials, 89.4% concordance, engine version numbers, official compliance, validation badges, calibrated ground-truth pipelines, market feeds and extension networks. No supporting records exist. Remove until actually evidenced.
6. Confidence percentages, nitrogen/SOC gains, yield/revenue, disease immunity, irrigation savings, safe planting dates, and crop-variety claims are unvalidated design examples, not research data. Even cultivar/season pairings need researcher review. Do not import HTML tables as agronomic knowledge.
7. Soil chemistry/texture cannot automatically be filled by SMAP; broad soil moisture does not measure groundwater level or guarantee irrigation access. NASA data cannot guarantee household yields, frost-free windows, aquifer safety, or crop survival.
8. “Live synchronized orbit,” minute-level ingest claims, 72-hour squall prediction, “field forecasting,” and future temperature projections conflict with historical decision support. Replace with actual acquisition/retrieval dates and historical context. SMAP L4 root-zone values are model-assimilated estimates, not direct subsurface radar measurements.
9. The stress example references “2014 SMAP,” which must be rejected against product temporal coverage. Do not assume a common 20/30-year record across all sources. A historical compound event must have actual aligned records; a constructed scenario must be separately labelled and is not a historical replay.
10. Water Commons lists 14.2 ha but its four cards sum to 5.10 ha. It equates 55,000 L/hour with 0.055 m³/second, which are not equivalent. Runtime, weekly capacity, and demand units need reconciliation. Peak staggering alone does not reduce seasonal volume; no claim of cavitation, groundwater recovery or fuel saving without an appropriate model.
11. Print example equates 1.20 ha with 89 decimals; units and dates need centralized conversion. Its decorative QR/hash/domain are not working verification. Remove until real. Never prefill official endorsements or claim a dense report is one A4 page before printing it.
12. Methodology and NASA sources currently use sidebars despite the public-page navbar requirement. The methodology may keep an optional in-page contents rail beneath a public navbar; it should not inherit planning progress.
13. Fixed `w-72` sidebars and `pl-72` offsets, wide matrices, tiny text, hidden scrollbars, and dense jargon require mobile/accessibility work. Mixed screenshot sizes are not dedicated mobile designs. Some malformed comments leak text in the location HTML; duplicate icon links and malformed theme values need cleanup during conversion.
14. EN/বাংলা controls do not provide complete translations; one source-page label is misspelled. Provide reviewed Bangla explanations and verify glyphs/print layout. Simplify technical prose while preserving evidence drill-down.

Missing states: initial empty farm, unknown history, invalid coordinates/units, outside validated region, denied geolocation, missing map tiles, validation errors, source loading/timeout/rate limit/auth failure, partial/stale cache, no agronomic coverage, no feasible rotation, only one alternative, all-zero priorities, unavailable economics, changed-input invalidation, unsaved/resumed draft, inaccessible/expired share, and infeasible Commons coordination. Add these in the existing visual language.

## 3. Research readiness and handoff contract

**Existing structured data: none.** Filenames in PROJECT_CONTEXT and numeric tables in mockups describe expectations, not delivered evidence. No scientific recommendation can yet be validated.

| Dataset / contract | Required fields before use | Features gated |
| --- | --- | --- |
| `references.csv` | Stable source ID, title, authors/organization, year, URL/DOI, exact page/table, access date, licence, reviewer/status | All evidence and scientific release |
| `crops_master.csv` | Stable crop/variety IDs, names EN/BN, family, management system, region applicability, source | Catalogue/history/sequence identities |
| `crop_calendar.csv` | Region/season IDs, planting interval, duration/range, establishment vs harvest convention, turnaround, cross-year handling, source | Feasible sequencing, shifts, printable calendar |
| `crop_climate_requirements.csv` | Parameter, units, optimal/tolerated bounds, stage/aggregation/time basis, severity/rule type, source | NASA-dependent suitability |
| `crop_soil_requirements.csv` | Texture, drainage, pH and measurement conventions, tolerances, regional/cultivar scope, source | Soil sensitivity and eligibility |
| `crop_water_requirements.csv` | Water-demand definition, stage/time distribution, units, method, management, irrigation efficiency/effective-rainfall assumptions if used, source | Water objective, irrigation caps, Commons |
| `crop_rotation_rules.csv` | Prior/successor crop/family, lookback, gap, prohibited vs discouraged, rationale, region, source | Crop-history effects and sequence validity |
| `crop_soil_health_effects.csv` | Direction or supported magnitude, residue/management assumptions, units/time horizon, source | Soil contribution; numeric N/SOC only if supported |
| `crop_salinity_response.csv` | EC definition (e.g. test method), units, crop/stage scope, supported response and uncertainty, source | Salinity evaluation; no mixing unlike EC tests |
| `crop_stage_sensitivity.csv` | Stage start/end or duration, heat/drought/wet sensitivity, thresholds/response, source | Stage exposure and stress replay |
| Bangladesh soil/suitability references | Region geometry/lookup, spatial scale, sampling date, properties/units, uncertainty, source | Explicit regional fallback; not field measurement |
| Economics/labor supplement | Dated regional price/yield/cost ranges, currency/area units, labor profile, management, sources | Income, input-cost and labor claims/limits |
| Shared irrigation inputs | Capacity per time bucket, available hours, area, crop schedules, efficiency assumptions, demand evidence, locks | Commons feasibility |

Every numeric fact needs value/range, unit, applicability, source locator and approval status, either on its row or through an explicit fact/source mapping. Never represent unknown as zero. Keep raw research immutable; validate/import to versioned knowledge releases. Distinguish individual reference quality from overall completeness. Resolve contradictory sources with B before activation.

What can be implemented after plan approval without finished research: foundation, accessible UI shell/forms, typed contracts, persistence, source adapters/cache, provenance panels, CSV validation, report layout, and explicit blocked/unknown states. Generic engine algorithms can be tested using clearly labelled synthetic test fixtures; those fixtures must never enter the production/demo catalogue.

What cannot be credibly completed without research: real candidate calendars, hard agronomic feasibility, meaningful NASA-sensitive scoring, soil/history sensitivity, stage stress evaluation, quantitative water coordination, and financial/soil-gain claims. Unknown objectives may be displayed unavailable, but cannot silently receive a fabricated neutral/high score. If an unavailable objective has positive farmer weight, show the missing evidence and require explicit reweighting or mark ranking incomplete; never silently change the farmer's preferences.

### Research and decision gates

- J: owns implementation, hosting choice and delivery; B: scientific approval and rule/score review; A: crops/calendar/climate/stages; M: soil/sequence/soil-health; S: NASA product/access/quality review; O: demo/story and asset review. These are proposed handoffs, not messages sent to teammates.
- By Oct 28 midday: B approves first region, crop catalogue, calendars, sequence rules and minimum soil/climate requirements; target a small set that genuinely permits multiple alternatives (proposed 6–8 crop/variety entries, not a mandatory scientific count).
- By Oct 29 midday: approved stage/water-demand method, soil-effect rubric, stress selection method, and decision-objective definitions. Economics/labor remain unavailable unless sourced; their absence is a visible completeness gap.
- Start SMAP/IMERG access investigation on Oct 27–28, even though implementation comes later. By Oct 29 demonstrate an authentic extract with provenance for each. By Oct 30 decide whether live refresh and validated cached coverage are viable.
- By Oct 30 evening: complete integrated flow; Oct 31 is validation and release rehearsal; Nov 1 is final smoke/fix buffer. Missed gates require explicit scope/date review, not substitution of Stitch numbers.

Open decisions: exact first region and catalogue; approved horizon/start-date convention; researcher delivery availability; interpretation of “must keep” (specific slot vs anywhere); change-count baseline; irrigation cap units; scoring/risk rubrics and zero weights; Bangla reviewer; public sharing/privacy/retention expectations; deployment host/domain/budget/persistent storage; actual GitHub repository; demo sites with authenticated NASA coverage. Defaults proposed below must be confirmed during phase acceptance.

## 4. Practical technical architecture

### Stack

- Frontend: React, TypeScript, Vite, React Router, compiled Tailwind with shared Stitch tokens. Ordinary controlled forms and a small shared draft-state context; no global state framework initially. Use a lightweight React chart library only where interactive charts justify it; simple timeline/SVG components elsewhere. Provide accessible tabular equivalents.
- Backend: Django + Django REST Framework, synchronous bounded JSON operations, Django validation/admin and migrations. Python scientific/business logic stays independent of HTTP/views and React.
- Persistence: SQLite initially on one server with persistent volume and tested backups; small anonymous/session-owned drafts and immutable run snapshots. Switch to PostgreSQL only if hosting or concurrency demands it; no PostGIS required for point location.
- NASA retrieval: Python HTTP client, source-specific adapters and offline management commands for expensive prefetch/extraction. Add HDF5/NetCDF/grid libraries only after actual chosen formats require them. No browser Earthdata credentials.
- Cache: database metadata plus persistent raw/normalized files outside the public static directory. No Redis/Celery required. Prefetch validated demo locations before presentation; refresh with explicit commands or a simple host scheduler if needed.
- Deployment: one Python-capable server/container serving the built React assets and `/api/v1/` under one origin, with persistent data/cache storage and HTTPS. Exact provider remains unchosen. Gunicorn/appropriate platform WSGI runner and static serving chosen in foundation; no separate frontend hosting requirement.
- Tests: Django/Python test suite for domain and API; Vitest/React Testing Library for meaningful form/state behavior; a small Playwright critical-flow suite and manual visual/print review. Lock compatible dependency versions at implementation time after checking official documentation.
- Map: coordinate input is always sufficient. A small Leaflet map with a permitted basemap can be added, subject to tile/geocoding policies and availability. No fake polygon/area/elevation/AEZ lookup; regional search requires a real approved gazetteer. Polygon drawing and live NDVI layers are deferred.

### Proposed module boundaries (paths do not exist yet)

| Responsibility | Proposed module | Contract / separation |
| --- | --- | --- |
| Frontend/UI | `frontend/src/{app,components,features,styles,locales}` | Render typed API results, collect inputs; never duplicate scientific scoring |
| Backend/API | `backend/config/`, `backend/planning/{api,serializers,services}.py` | Validate ownership/input, orchestrate services, return statuses and evidence |
| NASA ingestion | `backend/environment/adapters/{power,smap,imerg}.py` | Retrieve/decode source-specific data; no agronomic thresholds |
| NASA caching | `backend/environment/{cache,models}.py`, management commands | Cache lookup, manifests, freshness, raw hashes; separate retrieval from reuse |
| Environmental indicators | `backend/environment/{normalize,indicators,provenance}.py` | Unit/time alignment, quality masks, historical summaries and coverage |
| Agronomic knowledge | `research/csv/`, `backend/knowledge/{models,importer,validation}.py` | Versioned sourced facts, approved releases; no NASA fetches |
| Rotation generation | `backend/engine/generation.py` | Enumerate dated seasonal sequences with early calendar pruning |
| Hard constraints | `backend/engine/constraints.py` | Structured pass/fail/unknown checks and rejection reasons |
| Suitability | `backend/engine/suitability.py` | Soil/climate/stage/sequence evidence → objective inputs; explicit missingness |
| Multi-objective ranking | `backend/engine/ranking.py` | Objective vector, reviewed normalization, farmer weights, deterministic alternatives |
| Historical stress testing | `backend/engine/stress.py` | Reevaluate same rotations against documented historical profiles |
| Explainability | `backend/engine/explanations.py` | Render trace-backed EN/BN templates and exact contribution ledger |
| Water Commons | `backend/commons/{demand,coordination,models,api}.py` | Aggregate demand, search allowed shifts/substitutions, recheck all constraints |
| Persistence/database | Django models/migrations in planning/environment/knowledge/commons | Farm, draft, run, candidate/check/trace, group, selected plan and share records |
| Printable reports | `frontend/src/features/reports/`, `styles/print.css`; backend plan snapshots | Read-only selected-run report; browser print/save PDF; same evidence as UI |

### Data flow, engine policy and reproducibility

1. Save a versioned farm draft with coordinates, units, field inputs, current crop, dated history, locks, exclusions, limits and priorities. Each field retains origin: farmer-reported/measured, regional reference, unknown, or explicit assumption.
2. Resolve the supported region with an approved lookup; reject unsupported scientific coverage without blocking basic form exploration. Retrieve/cache environmental observations and compute quality-aware historical indicators.
3. Load an approved knowledge version. Enumerate candidates for consecutive future slots using dated planting windows, durations, turnaround and available crops. Apply history-dependent sequence rules and early hard checks. Include fallow only where an explicit approved option exists. Do not cap an incomplete search and call the surviving list globally optimal.
4. Maintain a separate constraint ledger. Supported numeric caps are checked with units and dates. An unknown critical input yields unverified feasibility or a blocked result; it never becomes a silent pass. Preferences remain soft. Contradictory constraints return actionable explanations; never auto-relax them.
5. Evaluate NASA temperature/rainfall/stage exposure and soil/history effects with reviewed rules. Water demand is a documented estimate with a chosen method; rainfall is not automatically irrigation demand, and evapotranspiration is not groundwater drawdown. FAO-56/GDD methods require sufficient inputs and citations before activation.
6. Produce five objective dimensions: water, soil contribution, climate resilience, income potential, input cost. Normalize with reviewed fixed scales/rubrics rather than candidate-dependent min/max that shifts whenever options change. Store raw indicators, normalized scores, uncertainty and coverage. Scores are decision aids, not probabilities.
7. Normalize explicit farmer weights with defined all-zero handling (ask for a nonzero priority or explicitly select the balanced preset). Compute an inspectable weighted utility over complete supported objectives. Expose raw trade-offs and optional pairwise Pareto labels. Choose several distinct feasible alternatives rather than duplicates of a winning sequence. Deterministic tie-breaking uses stable IDs. No NSGA-II/LLM/PyTorch required.
8. Record rule IDs, NASA observation/subset IDs, contributing dates/units, transformations, objective contributions, failures and missing inputs during evaluation. Explanations use this ledger. A “without water priority” claim requires a real counterfactual rerank, not invented point attribution.
9. Stress testing reuses these candidates and the same evaluation code with actual selected historical periods. Report scenario score changes and worst observed tested score; no yield-loss percentage, probability/VaR, or profit-loss model without supporting research.
10. Snapshot inputs, knowledge version, engine version, source versions/checksums, indicators, scores, weights, scenario definitions and selection. New inputs create a new run and invalidate old previews; reports/share views keep their original snapshot.

Proposed internal API surface (our API, not NASA endpoints): draft create/read/update; environmental-profile request/status; run generation/read; comparison/explanations/stress read or compute; Commons create/evaluate; plan selection/report/share. Design exact URLs and payloads in Phase 0. Slow cache misses return pending/unavailable with a prefetch path rather than holding a web worker indefinitely. Initially precompute expensive SMAP/IMERG extracts by management command; no invented asynchronous worker service.

Persist server-owned session IDs for private drafts. Validate ownership on every object lookup. Public sharing is explicit opt-in, read-only, uses a cryptographically unguessable revocable token, and omits personal farmer details/precise coordinates by default. Do not send reports to an extension worker automatically. Add expiry/retention policy and request limits before deployment.

### NASA products and access investigation

Documentation checked October 27; no authenticated download or numerical API response was validated in discovery. Official links establish product/access differences, not a completed integration:

- [POWER Daily API](https://power.larc.nasa.gov/docs/services/api/temporal/daily/) and [parameter catalogue](https://power.larc.nasa.gov/parameters/): documented daily point JSON interface. Start with verified available temperature and precipitation parameters; verify radiation, humidity/wind and response units before derived methods. Test AG community, date limits, time standard, fill values, rate limits, source grids and historical availability. Do not assume all POWER variables share one grid or units across communities.
- [SMAP SPL4SMGP catalogue, Version 8](https://nsidc.org/data/spl4smgp/versions/8) and [subsetting guidance](https://nsidc.org/data/user-resources/help-center/what-data-subsetting-reformatting-and-reprojection-services-are-available-smap-data): candidate 3-hourly 9-km surface/root-zone product. The catalogue currently points to V8 rather than the mockup's V7. Verify collection/variable names, Earthdata authentication and access agreement, download/subsetting route, format, EASE-Grid extraction, QA/masks, timestamps, temporal coverage and runtime costs. Catalogue flags geolocation issues for May 14–July 28, 2026 with reprocessing underway; consult actual granule status and exclude/flag affected inputs until verified. Do not silently mix reprocessed and superseded files.
- [IMERG overview](https://gpm.nasa.gov/data/imerg) and [NASA precipitation directory](https://gpm.nasa.gov/data/directory): separate Early/Late/Final runs and downloadable/subset products, not a POWER-like point API. Prefer a verified Final historical product for research use; verify exact current collection/version, access route/authentication, geographic/temporal coverage, precipitation variable, rate vs accumulation, missing/quality fields and daily aggregation. Do not copy V07 field names from HTML without reading the selected product documentation/file.

Run small Bangladesh extracts early to resolve access. Select one primary precipitation source for a given evaluation (POWER initially, validated IMERG when available); keep the other as a comparison or explicitly defined derived input. Never sum duplicate rainfall or switch silently. SMAP should influence only reviewed moisture-context rules; IMERG should influence rainfall exposure or stress/scoring, not only visual panels. Keep a regression demonstrating their decision effect once activated.

Cache key includes provider/product/version/run, native spatial selection or reproducible coordinate query, date interval, variables, time standard and extraction/transform version. Preserve original query, raw response/granule IDs, selected cells, quality flags, retrieval date, checksum and normalized units. Do not round coordinates arbitrarily to increase cache hits. Derived profiles also bind baseline period and knowledge/indicator version. Immutable historical archives need no frequent expiry; recent periods need explicit refresh/freshness policies. Mark served data live-retrieved/cached/stale/unavailable accurately. Retry with bounds/backoff; missing values are never zero. Never substitute another location or product without disclosure.

For demo reliability, prepare real, redistributable cached extracts for approved locations with manifests, citations and a refresh/rebuild command. These are genuine historical cached data, not synthetic measurements. Unsupported locations must show coverage limitations. If a source remains inaccessible, show it unavailable and state the resulting feature gap; do not claim all three sources are integrated.

## 5. Phased implementation backlog

All paths below are proposed. Every phase is a small reviewable change with its listed gate; do not begin until this plan is approved. Research/API investigation runs alongside the dependency sequence; the numbering does not postpone access risk until Phase 10.

### Phase 0 — foundation and contracts (Oct 27, ~3 hours)

- **Goal:** A runnable, inspectable skeleton and agreed data contracts.
- **Dependencies:** Plan approval; local runtime compatibility; J's repository/deployment decisions.
- **Files/modules:** `frontend/`, `backend/config/`, dependency/lock files, `.env.example`, `.gitignore`, `README.md`, `docs/architechture.md`, `docs/decisions.md`, API/schema documents.
- **Tasks:** Scaffold React/Django; health API; development proxy and single-origin build; define farm/run/provenance contracts and unknown semantics; migrations/test commands; CI skeleton if GitHub confirmed. Record chosen versions and no-secrets setup. Begin NASA access spike and research handoff.
- **Acceptance:** Clean install, frontend loads/backend health succeeds; migrations work; documented commands reproduce setup. No seeded mock recommendations.
- **Tests:** Build/typecheck, backend health and schema smoke test.
- **Blockers:** Missing runtime/hosting/Git decisions, unresolved contract definitions.
- **Manual verification:** Follow README from clean environment; check environment secrets and deployment filesystem persistence.

### Phase 1 — Stitch UI shell (Oct 27–28, ~4 hours)

- **Goal:** Consistent public and planning shells with reusable visuals.
- **Dependencies:** Phase 0; token conflict resolution.
- **Files/modules:** `frontend/src/{app,components,styles,locales}`, route map, asset inventory.
- **Tasks:** Navbar/sidebar/mobile stepper, typography/tokens, inputs/cards/source badges/timelines/table/chart primitives; route stubs for all screen areas including missing NASA profile; reusable loading/error/unknown states. No fabricated scientific content.
- **Acceptance:** Public navbar and compact planning navigation; all routes reachable; screenshot visual hierarchy retained; responsive layout.
- **Tests:** Route smoke and keyboard navigation checks; production build.
- **Blockers:** Remote image rights/availability, Bangla font choice, NASA profile design gap.
- **Manual verification:** Compare every route to export; 360px/mobile and desktop, focus visibility and Bangla glyphs.

### Phase 2 — farm forms and persistence (Oct 28, ~4 hours)

- **Goal:** Save/resume coherent farm inputs including dated history and explicit unknowns.
- **Dependencies:** Phases 0–1; proposed contracts and units approved.
- **Files/modules:** `frontend/src/features/farm/`, `backend/planning/{models,api,serializers}.py`, migrations.
- **Tasks:** Coordinates/map fallback; field area/soil/drainage/irrigation; current crop and previous seasons; locks/exclusions/change limits/calendar flexibility; priority sliders/presets; input origin; session ownership; stale-run invalidation. Enable only supported hard limits; do not imply unsupported household-yield or labor guarantees.
- **Acceptance:** Refresh resumes draft; back navigation preserves fields; unknown differs from zero; conflicts are actionable; state uses one farm/location throughout.
- **Tests:** Unit/date/conversion validation; conflicting locks; weight sum/zero weights; API ownership; save/resume and input-change invalidation.
- **Blockers:** Region lookup source, ambiguous bigha standards, lock/change-count semantics.
- **Manual verification:** Full EN form flow, unknown history/soil, denied geolocation, manual coordinates, mobile editing.

### Phase 3 — POWER ingestion and cache (Oct 28, ~4 hours)

- **Goal:** Authentic cached historical environmental profiles feeding later evaluation.
- **Dependencies:** Phase 0, location contract; official API spike.
- **Files/modules:** `backend/environment/{adapters/power,cache,normalize,models,indicators}.py`, prefetch command, `docs/nasa-data.md`.
- **Tasks:** Verify parameter metadata and bounded date requests; normalize units/time/fill values; provenance/cache manifests; temperature/rainfall summaries; timeout/retry/stale states; prefetch real demo subsets.
- **Acceptance:** Two approved locations have reproducible authentic profiles with metadata; API failure uses only a matching labelled cache or unavailable state.
- **Tests:** Recorded-response parsing, missing sentinel/unit/time behavior, cache separation by coordinates/variables/version, timeout fallback. Separate small optional live integration smoke test from offline CI.
- **Blockers:** API access/limits, approved baseline/aggregation method.
- **Manual verification:** Compare sample values/dates/units with source response; disconnect network and inspect cache label; inspect map-to-query coordinates.

### Phase 4 — agronomic knowledge layer (Oct 28–29, ~4 hours; research-gated)

- **Goal:** Import a small approved, traceable regional knowledge release.
- **Dependencies:** Phase 0; B/A/M deliver cited records.
- **Files/modules:** `research/csv/`, schemas, `backend/knowledge/`, importer command, import diagnostics.
- **Tasks:** Stable IDs and references; validate units/bounds/season dates/varieties/source locators; separate draft vs approved data; preserve releases; report contradictions and missing required fields. Define reviewed objective rubrics and water method.
- **Acceptance:** Approved catalogue can support multiple sequences; every active rule/value resolves to a source and scope; empty/incomplete knowledge produces honest blocked results.
- **Tests:** Duplicate/missing IDs, broken references, invalid ranges/units/calendar, cross-year windows, inactive data rejection; reviewed valid import.
- **Blockers:** Entire research delivery currently absent; economic/labor/stage/water gaps.
- **Manual verification:** B reviews import report, calendar and representative values against originals; no HTML numbers enter data by default.

### Phase 5 — generation and hard constraints (Oct 29, ~4 hours)

- **Goal:** Produce genuinely feasible dated multi-season candidates with rejection reasons.
- **Dependencies:** Phases 2 and 4; current-crop end date and approved sequence rules.
- **Files/modules:** `backend/engine/{types,generation,constraints}.py`, planning run orchestration, engine tests.
- **Tasks:** Enumerate region/season candidates; durations/turnaround; current-crop continuation; history lookback; locks/exclusions/change counts/irrigation/calendar limits; deduplicate; pass/fail/unknown ledger; no-result explanations and bounded search diagnostics.
- **Acceptance:** Every verified candidate satisfies all hard rules; conflicting or unverifiable critical requirements never produce a “fully feasible” badge; multiple alternatives where data permits.
- **Tests:** Hard-constraint enforcement, crop-history sensitivity, zero-change baseline, cross-year/nonoverlap dates, locks plus exclusions, no feasible set, deterministic generation.
- **Blockers:** Approved durations, rotation rules, volume-based cap method and unknown-feasibility policy.
- **Manual verification:** B checks actual calendars and rejected examples; J exercises conflict recovery without automatic relaxation.

### Phase 6 — suitability, objectives, ranking and comparison (Oct 29–30, ~5 hours)

- **Goal:** NASA-sensitive, priority-sensitive ranking with visible trade-offs.
- **Dependencies:** Phases 3–5; B approves thresholds/normalization/objectives.
- **Files/modules:** `backend/engine/{suitability,ranking}.py`, `frontend/src/features/{rotations,comparison}/`, API results.
- **Tasks:** Soil/environment/stage/sequence evaluations; sourced water/soil/climate/economic dimensions; normalized weights and coverage; deterministic utility; optional Pareto labels; distinct alternatives; shared baseline and comparison units; invalidate on changed inputs.
- **Acceptance:** NASA conditions can change ranking; feasible alternatives expose objective vectors and limitations; priorities affect rank; no invented economics or silent reweighting.
- **Tests:** Location, soil, farmer-priority and NASA-condition sensitivity; monotonic direction for approved rules; unit consistency; missing objective behavior; hard checks remain dominant; deterministic ties and ranking invariance to unrelated candidates.
- **Blockers:** Scientific rubrics and missing research; income/input/labor coverage.
- **Manual verification:** B reviews contrasting farms/priorities and expected directions; UI numbers reconcile with stored calculation ledger.

### Phase 7 — NASA environmental profile (Oct 30, ~2 hours)

- **Goal:** Make environmental conditions and their decision role understandable.
- **Dependencies:** Phases 1 and 3; adapter extensions from Phase 10 when ready.
- **Files/modules:** `frontend/src/features/environment/`, charts/tables/source detail panels.
- **Tasks:** Build missing screen using export language; temperature/rainfall/moisture historical charts, selected location and baseline, native resolution, source quality/freshness, evidence links and unavailable states.
- **Acceptance:** Every plotted value resolves to profile data; regional scale and historical nature are obvious; unavailable source is never marked active.
- **Tests:** Missing series, unit/date labels and partial-source rendering.
- **Blockers:** Profile screen review; series coverage.
- **Manual verification:** Screenshot consistency; keyboard/chart table alternative; mobile layout and matching source dates.

### Phase 8 — explanations and uncertainty (Oct 30, ~3 hours)

- **Goal:** Explain actual decisions and identify what could improve them.
- **Dependencies:** Phases 5–6; reviewed English/Bangla terminology.
- **Files/modules:** `backend/engine/explanations.py`, `frontend/src/features/{explanations,confidence}/`, locale templates.
- **Tasks:** Structured evidence → interpretation → crop impact → rotation impact; contribution/rule/source IDs; trade-offs; field-origin display; missing-field edit/rerun; counterfactuals only through actual engine reruns. Use completeness and limitations rather than invented confidence percentages.
- **Acceptance:** Explanations reconcile with the ledger, cover constraints/priorities/NASA/soil/history, and distinguish assumptions; reviewed EN/BN explanation flow works.
- **Tests:** Trace/source resolution, contribution arithmetic, unknown-data explanations, rerank after correction; locale interpolation.
- **Blockers:** B/translation review; scientifically defensible missing-field impact ordering.
- **Manual verification:** Farmer-readable language; no absolute safety/yield promises; Bangla text and dialogs at mobile widths.

### Phase 9 — historical climate stress testing (Oct 30, ~3 hours)

- **Goal:** Reevaluate rotations under real contrasting historical conditions.
- **Dependencies:** Phases 3–6; approved scenario definition/stage sensitivities and sufficient archive coverage.
- **Files/modules:** `backend/engine/stress.py`, scenario manifests, `frontend/src/features/stress/`.
- **Tasks:** Select normal/dry/hot/wet historical periods using approved reproducible rules; retain location, period and coverage; same candidates/evaluator per scenario; worst-tested score and deltas; cross-source overlap/missing-source warnings. Keep historical replay separate from constructed perturbation tests.
- **Acceptance:** Scenario selection is reproducible and justified by retrieved data; no handpicked mock years; UI says historical stress test, not forecast.
- **Tests:** Climate-stress sensitivity, period alignment, same constraints and candidates, unavailable history, no SMAP use outside its record, reproducible deltas.
- **Blockers:** Archive completeness and researcher-approved scenario/risk methods.
- **Manual verification:** S/B verify selected periods and records; inspect changes against temperature/rainfall/stage evidence.

### Phase 10 — SMAP and IMERG adapters (spike Oct 27–29; integration Oct 30, ~5 hours after access)

- **Goal:** Use authentic moisture and precipitation products in evaluation, not decorative charts.
- **Dependencies:** Phase 3 contracts; credentials/access, selected products/versions, approved moisture/rainfall rules. Investigate before Phases 5–9 are complete.
- **Files/modules:** `backend/environment/adapters/{smap,imerg}.py`, extraction commands, cache manifests, indicator/engine extensions, `docs/nasa-data.md`.
- **Tasks:** Real authenticated small extracts; grid selection/quality/units/time normalization; native coverage and version pinning; audited historical cache; SMAP moisture-context contribution and IMERG rainfall/stress contribution; explicit precipitation-source choice; product-status/error states. Avoid unvalidated downscaling or broad raster infrastructure.
- **Acceptance:** For approved demo sites, real source records affect evaluated indicators and at least a meaningful suitability/stress/ranking case; full provenance and failure behavior. If access fails, record incomplete integration and seek scope/date decision.
- **Tests:** Real-file subset parser fixtures, grid/coordinate masks, rate-to-depth integration, QA/missing handling, version/run cache isolation, overlap coverage, no rainfall double count, decision-sensitivity regression for both sources.
- **Blockers:** Earthdata permissions, download/subset service availability, data sizes, QA notices/reprocessing and stage-rule readiness.
- **Manual verification:** S compares extraction with authoritative product/subset; verify no secrets in browser/logs; rehearse cache-only run and unavailable source labels.

### Phase 11 — Water Commons (Oct 30–31, ~5 hours)

- **Goal:** Coordinate a small group under shared capacity without breaking farm constraints.
- **Dependencies:** Phases 4–6; stage-level irrigation demand method and farmer capacity/calendar inputs. Not dependent on all three NASA sources if POWER-based inputs are sufficiently validated.
- **Files/modules:** `backend/commons/`, `frontend/src/features/commons/`, group snapshots.
- **Tasks:** Manually add several farms/plans and shared volume/time capacity; construct comparable weekly demand buckets with partial-period handling; aggregate/flag conflicts; deterministic bounded search over approved planting shifts and feasible crop alternatives; recheck calendars/constraints, display before/after peak and total, preserve original plan until explicit apply. Explain infeasible/search-exhausted cases; no aquifer safety model.
- **Acceptance:** Demonstrable conflict resolved where feasible; farmer locks preserved; unresolved conflicts remain visible; timing-only changes preserve total demand under fixed crop-demand assumptions. Crop changes alter volume only through supported demand differences.
- **Tests:** Area and mm-to-volume conversions, bucket conservation, capacity exceedance, zero/missing capacity, all-farms locks, season boundaries, no-solution case, invariant total under timing-only shifts, reproducibility.
- **Blockers:** Sourced demand distribution, actual capacity data, acceptable planting shifts/substitution rules. Seasonal totals alone cannot justify a peak-demand curve.
- **Manual verification:** B checks water method; all farm totals/units reconcile; compare chart peak with numeric ledger; test explicit apply/cancel and mobile chart table.

### Phase 12 — printable/shareable selected plan (Oct 31, ~3 hours)

- **Goal:** Deliver a stable, readable plan outside the workflow.
- **Dependencies:** Phases 2, 5–9; persisted selected-run snapshot; privacy defaults.
- **Files/modules:** `frontend/src/features/reports/`, `frontend/src/styles/print.css`, backend selection/share models/API.
- **Tasks:** Calendar, field summary/origins, constraints, trade-offs, source citations, scenario/knowledge versions, assumptions; browser print/save PDF; explicit tokenized read-only share/revoke; omit fake QR/hash/endorsements. Browser PDF is sufficient initially; no server PDF service.
- **Acceptance:** Report matches selected run even after later edits; readable multi-page A4 output; share excludes sensitive details by default and can be revoked.
- **Tests:** Snapshot immutability, selected candidate ownership, share access/revocation, report-to-run consistency; print rendering smoke.
- **Blockers:** Privacy/retention decisions and fonts; product support requirements for downloadable PDF beyond browser print if requested.
- **Manual verification:** Print EN/BN to A4 PDF, inspect every page for clipping/repeated headers; open shared URL privately; revoke; verify no placeholder verification/official signatures.

### Phase 13 — methodology/data transparency (draft Oct 28 onward; finalize Oct 31, ~2 hours)

- **Goal:** Explain actual methods, products and limitations accurately.
- **Dependencies:** Implemented modules and approved research/source citations; content can start earlier.
- **Files/modules:** `frontend/src/features/methodology/`, `frontend/src/features/data-sources/`, `docs/{architechture,decisions,nasa-data}.md`.
- **Tasks:** Public navbar; actual pipeline and scoring formulas; source/product/version/coverage/quality/access/role; research attribution; fallback and unknown policy; stress vs forecast distinction; Commons peak vs total; actual validation performed and remaining limitations. Remove mock peer-review/trial statistics and unsupported dependencies/datasets.
- **Acceptance:** Every technical/scientific claim corresponds to working code or cited research; no source labelled integrated when unavailable; all public links resolve.
- **Tests:** Source-reference integrity, public routes and dataset-status presentation.
- **Blockers:** Final method review, data licences and actual validation evidence.
- **Manual verification:** B/S review wording; public navbar and mobile readability; methodology matches implemented ranking rather than Stitch's NSGA-II claims.

### Phase 14 — integrated validation, accessibility and deployment (incremental; Oct 31–Nov 1, ~6 hours)

- **Goal:** Release the complete narrow flow reproducibly with honest limits.
- **Dependencies:** All feature acceptance gates; hosting/secrets/persistent storage; B scientific signoff.
- **Files/modules:** Domain/API/frontend/E2E tests, CI/deployment configuration, README, release checklist and demo manifests.
- **Tasks:** Verify six mandatory sensitivity/constraint tests; end-to-end farm→NASA→alternatives→compare/explain/stress→Commons→select/print/share; mobile/accessibility/EN/BN; HTTPS/session/security settings, request bounds, no exposed credentials, backups/restore, cache prefetch; actual deployed smoke and offline-cache rehearsal.
- **Acceptance:** Clean build/test/migrations pass; realistic multiple alternatives and no-feasible flows work; all required features demonstrated without developer narration; data provenance visible; release can restore its database/cache. No critical correctness/accessibility defects. Missing research/source gates mean incomplete, not passed.
- **Tests:** Full appropriate suites; golden researcher-reviewed cases; synthetic fixtures clearly isolated; deployed health and browser flow; network failure and stale-cache paths; sensitivity tests verify expected causal direction, not arbitrary score changes.
- **Blockers:** Unfinished scientific gates, source access, hosting availability or unreviewed translations.
- **Manual verification:** J/B/S sign off integrated scenarios; keyboard/focus, contrast, labels, error announcements, chart alternatives, mobile; print PDFs; real share links; fresh-session and offline demo. O rehearses only claims backed by delivered functionality.

## 6. Delivery sequence, effort and risk controls

Estimated focused development effort: roughly **57 hours** plus research, translation, API access delays and scientific review. These are planning estimates, not guarantees. One developer across five remaining working days has little contingency. Keep revisions small and avoid visual redesign or infrastructure expansion. Estimates assume familiarity with React/Django and rapid researcher handoffs; blocked access cannot be solved by allocating a nominal coding hour.

| Date (Dhaka) | Intended checkpoint | Gate / corrective decision |
| --- | --- | --- |
| Oct 27 | Plan approval; foundation/UI start; initiate source/research investigations | No implementation before approval |
| Oct 28 | Saved farm workflow + real POWER/cache; approved minimal catalogue ready | Missing catalogue triggers immediate deadline risk review |
| Oct 29 | Real feasible sequences and initial NASA/priority-sensitive ranking; authentic SMAP/IMERG extracts demonstrated | Freeze supported region/crops and methods; remove unbacked promises, not required features |
| Oct 30 | Complete profile/results/compare/evidence/stress integration; source adapters active; Commons started | Full vertical rehearsal; record any feature blockers explicitly |
| Oct 31 | Commons, report/share and transparency complete; review and deploy | Feature freeze; no cosmetic expansion or new datasets |
| Nov 1 | Release smoke, restoration/offline rehearsal and critical fixes | Declare complete only against definition of done |

Critical path: approved research → candidate feasibility → NASA-sensitive suitability/ranking → explanation/stress/Commons/report validation. POWER and SMAP/IMERG access investigations must overlap early shell work; polished UI cannot unblock missing science.

Major risks and responses:

- **No research at all:** highest risk. Start from approved small catalogue and explicit source contracts. Ask for missing data rather than importing design examples.
- **NASA access/product complexity:** investigate immediately, cache authentic subsets, keep adapters independent. Cache does not remove the need to validate data rights, quality and decision use.
- **Scope vs deadline:** build every required feature narrowly; defer optional OCR/accounts/alerts/optimizers. If core feature gates fail, explicitly renegotiate scope or date.
- **False scientific precision:** make unknown/coverage first-class; use reviewed rubrics and source-linked evidence; remove mock claims from all UI/report/demo narration.
- **Water modelling:** require time-distributed irrigation demand and consistent capacity units; do not derive groundwater safety or water savings from planting shifts alone.
- **One developer + integration time:** use one language for all science (Python), one backend deployment, a small catalogue and short PR/commit-sized phases. Keep API contracts stable; no microservices or AI features.
- **Demo network/deployment loss:** prefetch real data, ship source manifests and reproducible commands, test persistent-volume backups and a cache-only rehearsal. No cross-location fallback.
- **Translation/accessibility/asset gaps:** begin reviewed core EN/BN templates early; retain manual coordinates and chart tables; verify image/font licences and print glyphs.

## 7. Approval and completion checklist

Approval requested for the overall plan and proposed stack/delivery boundary; routine implementation choices can then proceed within the approved phase. Research facts and scientific rules still require researcher validation, not developer invention.

Before implementation begins, confirm or record defaults for first region/catalogue, three-season horizon, researcher handoffs, deployment/Git repository, and sharing/privacy. Unresolved choices need not block independent foundation work after approval; missing scientific data blocks the corresponding scientific feature.

Completion evidence must include:

- Real source-linked environmental profiles and NASA-sensitive evaluation; each active source's actual decision role documented.
- Validated calendar/history/soil/constraint handling; multiple feasible alternatives with priority-sensitive trade-offs.
- Required tests: location sensitivity, farmer-priority sensitivity, soil sensitivity, crop-history sensitivity, climate-stress sensitivity, hard-constraint enforcement.
- Honest unknown/unavailable/no-feasible states, reviewed English/Bangla explanations, historical scenario labels.
- Commons demand/capacity coordination with before/after peak and total accounting; no broken farm constraints.
- Stable selected plan with readable print output and working private-by-default opt-in share.
- Public methodology/data transparency matching the implementation, actual deployed flow, and reliable authentic-cache demo.

Discovery verification: inspected repository files/directories, HTML/text/scripts/assets and all screenshot compositions; consulted official NASA/NSIDC documentation. No application tests could run because no application/test scaffold exists. External authenticated access, scientific values and deployment remain unverified. This document is a proposal, not a claim of implemented functionality.
