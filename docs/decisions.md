# Milestone 1 decisions — October 28, 2026

1. Activate four crop identities only: Aman rice, maize, sunflower and mungbean. Normalize the remaining evidence for traceability without enabling those crops in runtime generation.
2. Source-check only exact four-crop EcoCrop temperature and optimum-pH transcriptions against official pages. Their only active scientific use is labelled global-species reference comparison. No local calendar or cultivar response becomes verified by copying that flag.
3. Preserve all raw CSV bytes. Store a separate JSON staging/projection and explicit crosswalk. Runtime does not read raw CSVs or the full staging artifact. Salinity conflicts remain unresolved records, never averaged thresholds.
4. Block production rotations until approved calendars and sequence rules exist. Synthetic 2027 calendars/rules live only in tests/fixtures, require DEBUG plus a dedicated server switch, and remain visibly non-recommendations. No extra scientific values were filled to unblock the UI.
5. Compare supported dimensions lexicographically in farmer-priority order. Show categories/structural metrics, no opaque total score. Active unavailable objectives make ranking incomplete rather than silently changing preferences.
6. POWER alone is sufficient for the first authentic environmental adapter. Cache raw responses by exact query and retain metadata/checksums. SMAP, IMERG and Commons wait for this slice's data gates.
7. Use Django 5.2 LTS/DRF in an isolated environment and React/Vite with lockfile. No Redis, Celery, database import, LLM or optimization framework. Minimal CSS uses Stitch typography/palette/card language; no full UI redesign.
8. Local API defaults to port 8001. Port 8000 was unresponsive in this host's loopback verification; 8001 worked. The Vite proxy can be overridden with NEXTSEASON_API_TARGET. This is a development setup, not public deployment.
