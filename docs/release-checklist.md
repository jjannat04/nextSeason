# Release acceptance checklist

**Status: OPEN — not release complete.** Record tester, date, deployed URL, browser/version and evidence links when each item is completed. Automated tests and source review do not replace the checks below.

## Before deployment

- [ ] Review `git status --short` and staged file names before the first commit. Confirm `.env`, `.env.*` (except `.env.example`), credentials, private caches, `.venv`, `frontend/node_modules` and `frontend/dist` are ignored. Git was initialized in this workspace but no commit was made during release preparation.
- [ ] Run a secret scanner against staged content and Git history once commits exist. The initial untracked-file pattern scan found no credential literals/private-key markers in Git-eligible text files; it did not read the ignored `.env` or prove absence from future commits.
- [ ] Confirm README and scientific methodology Markdown remain in the source repository for transparency; no Markdown or design/research files are copied to the public frontend web root. There were no temporary/unnecessary Markdown files identified for Git exclusion.
- [ ] Supply production backend environment securely: `NEXTSEASON_DEBUG=0`, `NEXTSEASON_ALLOW_FIXTURES=0`, long random `DJANGO_SECRET_KEY`, exact `DJANGO_ALLOWED_HOSTS`, backend-only `EARTHDATA_TOKEN`, persistent private NASA cache paths, HTTPS/proxy settings. Keep same-origin `/api`; do not add broad CORS.
- [ ] Run 91+ backend tests, 26+ frontend tests, Django `check` and `check --deploy`, and `npm run build` on the exact release revision. Investigate new warnings; HSTS subdomain/preload decisions require domain ownership review.

## Manual browser acceptance

- [ ] At **1440 px**, inspect landing, planning steps, NASA cards, rotation timeline, comparison, explanation, stress charts, Water Commons, public pages and report for overflow/readability.
- [ ] Repeat at **1280 px**.
- [ ] Repeat at **1024 px**.
- [ ] Repeat at **768 px**.
- [ ] Repeat at **430 px**.
- [ ] Repeat at **390 px**.
- [ ] Repeat at **360 px**. Check the vertical comparison alternative and horizontal table access, touch targets and keyboard focus.
- [ ] Complete a real-result report in **Chrome A4 portrait print preview**; inspect page breaks, headings, NASA/stress/source blocks and footer.
- [ ] **Save as PDF** and inspect every page for clipping, blanks and source-link readability.
- [ ] Complete **three-farm Water Commons** schedules, shared capacity, conflict/no-conflict and before/after timing state.
- [ ] Complete **five-farm Water Commons** schedules; confirm capacity arithmetic and farmer timing locks. Incomplete schedules must say `insufficient_data` and must not infer a numeric conflict or water savings.
- [ ] Run an **uncached NASA profile request** at Khulna (22.8, 89.55), Dinajpur (25.63, 88.65), and Rangpur (25.7439, 89.2752), using the same historical period and backend credentials. Record POWER, SMAP and IMERG statuses, actual product/period provenance and any asynchronous pending state.
- [ ] **Repeat each same request** and verify appropriate cache reuse or documented stale behavior, with no credentials in keys, files or responses.
- [ ] Visit landing, Water Commons, Methodology, NASA Data, About and References by **direct URL**; verify all public links.
- [ ] **Refresh** each public route. Farm form/result state is currently in browser memory and is not expected to survive refresh.
- [ ] Verify **browser back/forward** across public routes and normal planning navigation/state while the page remains loaded.
- [ ] Simulate or observe **POWER, SMAP and IMERG partial failures** individually. Other sources must remain independent, unavailable values null/unknown, and users must see readable status rather than a stack trace.

## After deployment

- [ ] Confirm valid **HTTPS** and HTTP→HTTPS redirect at the public domain.
- [ ] Confirm the **public frontend URL** serves current assets.
- [ ] Confirm **public backend/API reachability** at same-origin `/api/health`; `fixtures_enabled=false`.
- [ ] Search built JS and browser network traffic for **localhost URLs** and Earthdata credentials; neither may appear in production payloads.
- [ ] Confirm **POWER, SPL4SMGP.008 and GPM_3IMERGDF.07** work from the deployed backend or show truthful provider-specific unavailable/pending states.
- [ ] Confirm the **token never appears** in browser/network responses, frontend assets, logs or public error messages. Do not paste the token into test notes.
- [ ] Confirm **development fixtures are inaccessible** in production, including explicit fixture-mode API attempts.
- [ ] Force malformed input/provider failure and confirm **no stack traces** reach users.
- [ ] Record public demo URL, screenshots/video, operator sign-off and rollback artifact. Only then mark release complete.
