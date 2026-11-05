# Next Season — future work

This roadmap covers improvements after the current feature-complete prototype. It prioritizes a reliable, honest submission and then scientific validation. It does not authorize promoting provisional evidence or inventing missing agronomic values.

## P0 — before public demo and NASA submission

1. **Verify cross-platform knowledge fingerprints on deployment.** The implementation now canonicalizes text line endings before hashing. LF/CRLF/lone-CR equivalence and real-content-change tests pass; the offline projection was rebuilt; all four stored digests match canonicalized Git blob content; and the local full test suite loads the projection successfully. Still verify `/api/health` from the deployed Linux backend after these changes are committed. Do not bypass the check.
2. **Make the Vercel + Render deployment demonstrably work.** Verify actual URLs, Vercel `/api` rewrite, Django health/recommendation mode, allowed hosts, HTTPS/proxy settings, fixture lockout, and safe error responses. Set `EARTHDATA_TOKEN` only in the Render backend environment.
3. **Test NASA behavior on the chosen free host.** Test cold start, memory and timeouts, first uncached requests, async Harmony job polling, provider partial failures, and repeated requests at three Bangladesh locations. Render Free sleeps and has ephemeral storage; determine whether cache loss or cold starts make the live demo unreliable. Do not promise cache persistence on an ephemeral filesystem.
4. **Complete release acceptance manually.** Check 1440, 1280, 1024, 768, 430, 390 and 360 px; three- and five-farm Water Commons; Chrome A4 preview and Save as PDF; direct public routes, refresh, browser history; keyboard/focus and screen-reader basics; malformed input and provider-failure messages. Record tester, date, browser, URL and evidence in `docs/release-checklist.md`.
5. **Prepare submission media.** Capture a short real-data demo, screenshots of the main farmer journey, NASA source panel, comparison/explanation, stress results, and Water Commons. Add captions/subtitles if video is used. Use current deployed output; remove test tokens and private field data.
6. **Finalize the project page with the team.** Confirm all team member names/roles, actual public demo URL, demo/video links, AI/tool disclosure required by the current portal, challenge selection, open-source/originality declaration, and any license decision. Submit only facts the team verifies.

## P1 — strengthen local scientific validity

1. **Validate a co-located crop system.** Work with Bangladesh agronomists/extension staff to select one ecosystem, location and cultivar/system set for Aman rice, maize and sunflower. Confirm month-level planting/harvest windows, establishment basis, field occupancy, turnaround/fallow and management prerequisites. Keep source, region, variety, year, confidence and verification state with every value.
2. **Validate sequence applicability.** Review the rice-to-dry-crop and return sequences for the selected location/cultivar and management system. Distinguish direct trial evidence from conditional system evidence and inferred annual return. Do not label unsupported crop pairs harmful or safe.
3. **Improve soil interpretation.** Confirm soil pH test-method comparability and local application. Add field texture/drainage/salinity evaluation only when measurements, measurement basis, thresholds/endpoints and cited local applicability are available. Preserve missingness.
4. **Run farmer and extension usability sessions.** Ask participants to complete planning, compare alternatives, interpret NASA limitations, and explain why they would or would not use an option. Record comprehension and workflow issues; do not treat small usability sessions as agronomic validation.
5. **Build Bangladesh validation cases.** With permission, collect documented example farms and expert expectations: coordinates or declared region, field/history inputs, source data period, feasible alternatives, and the reason for each expectation. Use these as regression/validation cases only after scientific reviewers approve them.

## P2 — improve environmental coverage and resilience

1. **Make NASA jobs robust on low-cost hosting.** If bounded live requests exceed serverless/free-host time or storage limits, move asynchronous downloads and caches to a small persistent worker/storage service. Preserve one adapter per provider, exact product/version, checksums, provenance, stale policy and explicit pending/unavailable states.
2. **Measure data coverage by location and time.** Track which months/days are complete for POWER, SMAP and IMERG; test missing granules, reprocessing and stale caches. Keep source estimates regional and observations historical.
3. **Improve environmental interpretation only with evidence.** Add crop-stage stress or water-risk calculations only after local crop-stage dates, validated response functions, water-balance assumptions and cited thresholds exist. Do not translate satellite moisture/rainfall directly into irrigation demand.
4. **Expand climate robustness tests.** Evaluate whether rankings change under supported observed conditions at additional locations and periods; publish the selection procedure and sensitivity. Do not call a historical sample a forecast or formal climate normal.

## P3 — product and accessibility improvements

1. Add a reviewed Bangla translation catalogue, locale switch, date/number formatting, text expansion QA and farmer review. No machine-translated public toggle until reviewed.
2. Add plan persistence or share links only after deciding consent, privacy, retention, access control and deletion requirements.
3. Improve accessible chart summaries, keyboard flows, screen-reader status updates, contrast and touch targets based on manual audit.
4. Improve printable report navigation and source list if farmers/extension staff identify a need; retain the current browser-print approach unless it fails tested use cases.
5. Add additional crops only after a complete, cited, region/cultivar-appropriate calendar and sequence evidence path passes the same review gate.

## P4 — research extensions requiring separate evidence

- Quantified soil-health contribution, nutrient balance and residue management.
- Calibrated water demand, effective rainfall, irrigation efficiency, pumping capacity, and water-rights constraints.
- Salinity and crop-stage heat/drought/wet sensitivity with endpoint, cultivar, stage and measurement method.
- Farm-specific yield, income and input-cost estimates using local dated data and explicit uncertainty.
- Broader regional support beyond Bangladesh with locally reviewed datasets and extension partnerships.

## Do not implement without a new evidence and scope review

- More crops or global claims based only on generic calendars.
- Numeric suitability scores, hidden weights, probabilities or “optimal/best” guarantees unsupported by validation.
- Yield, income, water-savings, soil-health-gain, salinity, disease or crop-failure claims without source-backed methods.
- AI-generated agronomic advice that bypasses cited evidence and deterministic constraints.
- Storing Earthdata credentials in source, browser code, logs, output, or cached metadata.

## Completion tracking

Track near-term release gates in [`docs/release-checklist.md`](docs/release-checklist.md). Record scientific decisions in [`docs/decisions.md`](docs/decisions.md) and update the relevant methodology only after review. Re-run the full test suite after code or projection changes. A task is complete only when its acceptance evidence is recorded.
