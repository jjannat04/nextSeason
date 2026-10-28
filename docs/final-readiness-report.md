# Final readiness report — 28 October 2026

## A. Complete

- The implemented research prototype covers the single-farm journey, three NASA provider adapters, calendar-backed rotation alternatives, hard constraints, farmer priorities, qualitative comparisons, explanations and provenance, four observed-year stress scenarios, missing-information handling, Water Commons, a printable report, and public methodology/NASA/About/references pages.
- Browser QA used the running Django API and React app. A normal Khulna planning journey reached the NASA profile, six rotation options, comparison, explanation, all four stress scenarios, missing information and a selected-option printable report. The normal path used `RESEARCH_EVIDENCE`, with no development fixture. Provisional calendar and unsupported-dimension labels stayed visible.
- A separate browser Water Commons journey with two complete farm schedules detected 16 m³ against 10 m³ weekly capacity, suggested feasible timing changes, and kept total planned irrigation unchanged. Marking one schedule incomplete returned `insufficient_data` without a numeric conflict. The UI allowed adding up to five farms; backend tests cover three- and five-farm aggregation and no-conflict cases.
- Public-page direct hash routes, refresh, navigation, and browser back/forward were checked. The comparison has a vertical mobile detail view; Water Commons has a text alternative and exact-volume table.
- API QA used cached genuine NASA POWER records at Khulna (22.8, 89.55), Dinajpur (25.63, 88.65), and Rangpur (25.7439, 89.2752) for 2024. POWER returned available at all three. SMAP and IMERG returned `authentication_required` in this QA process because Earthdata environment variables were absent; their values remained null, never zero. Khulna Aman temperature interpretation was `potential_concern`, while the two northern locations were `acceptable`. This shows location-sensitive qualitative interpretation; these cases did not establish a changed overall rank.
- Real API cases respected locked crop, excluded crop, max-change and preferred-first constraints; a fully excluded set returned zero feasible rotations. The four stress scenarios retained observed years and POWER provenance, and described historical conditions rather than forecasts. Invalid coordinates returned HTTP 400.
- Frontend errors no longer expose a raw server response or localhost setup instruction. Backend security middleware covers CSRF and clickjacking. Secrets remain in backend environment variables.
- Final automated gate: **91 backend tests passed**, **26 frontend tests passed**, `manage.py check` passed, and TypeScript/Vite production build passed. Output is about 312 kB JS (93 kB gzip) and 29 kB CSS (6 kB gzip).

## B. Needs manual review

- [ ] In Chrome, inspect landing, every planning step, NASA cards, timelines, comparison, explanation, stress charts, Water Commons, public pages and report at **1440, 1280, 1024, 768, 430, 390 and 360 px**. Check horizontal overflow, clipping, label readability, focus, keyboard access and stacked layouts. Exact viewport sizes were not available through this QA browser control.
- [ ] Complete three- and five-farm Water Commons plans in the browser. Check no conflict, conflict, a permitted shift, and a timing-locked or otherwise blocked shift. Backend tests cover the algorithms; only the two-farm full journey was manually exercised here.
- [ ] Open a selected live-result report in Chrome print preview at A4 portrait; use Save as PDF. Check page breaks, timeline, source URLs, NASA/stress sections, footer and blank pages. The report rendered in-browser, but the print dialog could not be reliably controlled in this session.
- [ ] On the intended deployment host, with credentials supplied **only as backend environment variables**, make uncached requests for three Bangladesh locations and then repeat them. Confirm POWER, SPL4SMGP.008 and GPM_3IMERGDF.07 statuses, checksums/provenance, cache hit behavior and nonzero real values where available. This QA process had no Earthdata credentials; earlier live validation is documented in `nasa-data-depth.md` for bounded Khulna windows.
- [ ] Check all external reference links, contrast and keyboard order with the final domain/browser, plus any screen reader used for submission.

## C. Known limitations

- Bangladesh month-level calendars remain provisional for local cultivar/field decisions. Crop-stage response, salinity, yield, income and irrigation demand where unsupported remain `insufficient_data`. Regional NASA estimates are not field measurements; historical scenarios are not forecasts.
- Only three eligible crops are in the current prototype catalogue. The current location QA changed a qualitative crop interpretation, but did not prove the overall candidate ranking changes for those three points.
- `frontend/src/strings.ts` centralizes step names, landing copy and some status text; many strings in `main.tsx`, `ResultScreens.tsx`, `FieldFromSpace.tsx`, `StressTests.tsx`, `WaterCommons.tsx`, `PrintablePlan.tsx` and `PublicPages.tsx` remain inline. No i18n catalogue or functional language toggle is shipped. Reviewed Bangla requires extraction, translation review, number/date conventions and layout QA.
- SMAP/IMERG availability depends on Earthdata permissions, job latency, provider data coverage and server cache. Failure of one source leaves other provider results intact and unsupported indicators unknown.
- The app does not persist plans or provide stable shareable URLs. The printable report is browser print, without server-side PDF storage.

## D. Blockers before deployment/submission

- Deploy behind HTTPS with a long random `DJANGO_SECRET_KEY`, exact `DJANGO_ALLOWED_HOSTS`, `NEXTSEASON_DEBUG=0`, correct same-origin `/api` routing, persistent writable NASA cache directories, and backend-only Earthdata credentials. Verify provider timeout and proxy timeout behavior under real job latency. The repository has no database models or migrations at present; no migration step is needed for this prototype.
- Complete the manual responsive and A4 print checks above, and smoke-test the deployed site and three-location live/cache behavior. These are not certified by the passing unit suite.
- Supply the final public demo URL and screenshots/video for NASA submission. Add a license only after the team chooses one; no license is currently declared.
- Git metadata is absent in this workspace, so tracked-file secret safety and commit history cannot be verified here. `.gitignore` excludes `.env`, `.env.*` except `.env.example`, common credential files, runtime caches and frontend build output. `.env.example` contains variable names without values. Source/build scans found no Earthdata token or Authorization-header logging path; no actual secret value was read or displayed.
- `manage.py check --deploy` with synthetic production variables reports only HSTS include-subdomains and preload warnings. Enabling either requires control of the deployment domain and all its subdomains. Verify the domain policy before changing those settings.

## E. Optional post-submission improvements

- Add a reviewed Bangla catalogue and real locale switch.
- Add plan persistence/share links after defining data retention and privacy requirements.
- Expand scientific coverage only after new cited crop/calendar/sequence evidence is reviewed.

## Local browser checklist

1. Start Django and Vite per the root README. Open the landing page, use the main CTA, and finish every planning step with one real Bangladesh coordinate. Confirm the NASA cards show three independent statuses and that normal recommendations show research evidence rather than fixtures.
2. Compare two rotations, open Why This Rotation, switch through all four historical scenarios, inspect missing information, and open the printable plan. Repeat with exclusions that yield no feasible rotation.
3. Visit Water Commons and analyze complete two-, three-, and five-farm plans. Repeat with an incomplete plan, capacity above demand, and a locked timing constraint. Confirm no unsupported water-saving claim.
4. Visit Methodology, NASA Data, About and References directly by URL; refresh each, then use back/forward and the navbar.
5. Repeat the major screens at the seven widths above. Check keyboard focus and text alternatives.
6. Print the selected plan to A4 PDF. Inspect every PDF page and open each source link.
7. Deploy to the intended HTTPS host and repeat the flow with backend Earthdata credentials. Check three Bangladesh points and repeat each request to observe cache reuse. Inspect logs and frontend network responses for credential absence.
