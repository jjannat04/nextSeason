# Evidence-tiered prototype recommendations

**NASA DATA DEPTH amendment:** separate SMAP/IMERG adapters, a unified profile, source status, annual rainfall reference screening and explicitly preferred moisture-exposure context now extend this prototype. The new source effects, quality policies and credential-dependent limitations are documented in [NASA DATA DEPTH](nasa-data-depth.md); they supersede earlier statements that rainfall is context-only in all cases. No numerical irrigation/stage-damage model or new crop is introduced.

Effective 28 October 2026, superseding the earlier strict production-gate strategy. Next Season is an explainable decision-support research prototype. It explores crop sequences; it does not forecast yield or issue certified prescriptions.

## Release and eligible crops

The normal browser and default API mode are `prototype_recommendation`. Three crops qualify: **Aman rice, maize and sunflower**. Mungbean remains visible for reference, but is excluded from this release's generated rice/dry-season rotations: its complete BBS calendar concerns August–September establishment, while its late-Rabi/spring calendar lacks a supported final field-clearance window. The engine does not combine those seasons or convert days-after-emergence into a guessed planting-to-harvest duration.

The executable projection is `data/normalized/prototype_slice.json`; `prototype_crop_subset.csv` records the current crop decisions. Both are produced offline by:

```powershell
$env:PYTHONPATH='backend'
.venv/Scripts/python.exe -m next_season.knowledge.prototype
```

Inputs are the existing normalized species reference projection, `crop_calendar_verified.csv` and `crop_rotation_rules_verified.csv`. Raw researcher CSVs and staging remain unchanged and are not read by request-time logic. Source fingerprints must match; a changed input requires an offline rebuild and tests. This is a new allowed use of evidence, not a relabelling of provisional claims as verified. The earlier `production_crop_subset.csv` and strict-gate report are historical audit artifacts, not the active prototype eligibility file. Explicit legacy `production` requests retain their old blocked/reference-only contract for compatibility; normal operation does not use that mode.

## Evidence states and permissions

| State | Prototype use |
|---|---|
| `verified` | Normal use within the stated source scope |
| `provisional` | Usable with source, status, confidence, geographic/cultivar applicability and limitations propagated |
| `unresolved` | No scientific ranking effect or biological hard constraint |
| `missing` | No scientific ranking effect or biological hard constraint; no zero/default substitution |

Every participating crop needs known identity, a complete usable calendar, temperature requirements, basic pH requirements and a connection to a supported sequence system. These may be verified or provisional. At least three crops must qualify for this release to generate options. Optional water, salinity, stage stress, soil-health response and economics do not control that gate.

## Calendars and temporal feasibility

Selected source records are VCAL01 (HYV transplanted Aman), VCAL03 (Rabi maize) and VCAL04 (winter sunflower), all **provisional** for local/cultivar applicability. They come from BBS *Yearbook of Agricultural Statistics-2024*, published June 2025, §1.8, printed pp24–25/PDF pp39–40. Original values, source URL/title/year, locators, country scope and textual boundaries remain in every calendar trace. See [the source verification report](production-gate-verification.md) for exact links, SHA-256 and the regional BAMIS conflicts.

The recurring scheduler uses conservative month envelopes, not exact planting or harvest dates. It retains source qualifiers such as early/middle/late in evidence. Past/occupied months are removed; only complete future planting months remain. A successor's earliest planting month must start after its predecessor's latest harvest month. Earliest/latest farmer dates are checked against whole-month start/end bounds **as computational bounds, not agronomic event dates**. No duration or minimum turnaround is fabricated. Unknown field-preparation needs remain explicit local checks.

The search uses the earliest conservative occurrence of each documented system phase, two or three crop activities and a bounded current-year-through-current-year-plus-four search. It does not optimize planting dates. Idle intervals are displayed in whole months and are not described as required biological fallow. A late Aman envelope may miss the next Rabi establishment window and create a long uncropped interval. These are not claimed to be three crops in one year. Broad calendars are conservative and do not prove field-level sowing-date feasibility.

## Sequence evidence and unknown pairs

The active conditional systems are Aman–maize and Aman–sunflower, from IRRI's [1 March 2021 research summary](https://ricetoday.irri.org/crop-diversification-in-rice-based-systems-in-the-polders-of-bangladesh-yield-stability-profitability-and-associated-risk/). IRRI discusses coastal polder water management and climatic trade-offs. Reverse transitions are explicitly marked as inferred annual return phases, not independently tested cultivar-pair treatments. Applicability outside the examined ecosystem/cultivars is provisional. The source conditions (drainage, timely harvest, freshwater, salinity and rainfall context) remain in the trace; the prototype does not claim to verify those field conditions.

`direct_sequence_evidence` describes evidence about a named crop system, including a clearly marked derived return phase. It does not imply an exact cultivar-pair experiment. `family_level_evidence` is reserved for an authoritative general rule: none has been activated. `no_evidence` denotes an unsupported pair. The API's `sequence_evidence_coverage` lists every pair and gives unknown pairs `ranking_effect=none`, with no hard constraint. No repeat-family prohibition, nitrogen bonus, rotation-health score or numeric minimum gap is inferred from botanical family.

The candidate search enumerates documented alternating rice/dry-crop system templates; it is not an exhaustive catalogue of all agronomically possible sequences. An unsupported pair is outside that search, not assigned an avoid/discouraged classification or a ranking penalty. If a crop-history transition is outside the documented templates, no candidate is claimed for it and the coverage ledger identifies the missing evidence. No source-supported class other than `acceptable` is currently active, so sequence comparisons can honestly tie.

## NASA-dependent qualitative climate screening

The provider retrieves real NASA POWER daily point data at the entered coordinates: `T2M`, `T2M_MIN`, `T2M_MAX`, `PRECTOTCORR`, AG community, UTC. Exact-query, checksummed raw caching remains unchanged. Only **T2M daily means** influence the present climate interpretation; rainfall is shown as context, not irrigation demand. Other parameters are not silently treated as stage thresholds.

For each activity, select observations from the historical request whose month-of-year falls inside the conservative planting-to-final-harvest envelope. This is a historical month-of-year analogue, not a coherent future growing season or forecast. Calculate observed minimum, maximum and mean of daily T2M. Compare the observed daily-mean range to the published EcoCrop temperature envelope:

| Rule | Interpretation |
|---|---|
| Every selected daily mean lies within the published optimal interval | `good_fit` |
| Every selected daily mean lies within the absolute interval, but some fall outside the optimal interval | `acceptable` |
| Any selected daily mean falls outside the absolute reference interval | `potential_concern` |
| Missing/unusable requirement, incomplete POWER T2M coverage, or no historical observations for the calendar months | `insufficient_data` |

This is a transparent screening heuristic, not a calibrated injury, survival, yield or adaptation model. Global species requirements and their application to local systems are kept distinct: exact reference transcriptions remain verified, while local applicability is provisional. No climate category is a biological hard crop exclusion. Missing calendar months are exposed and reduce evidence confidence to limited; an observation-free month is never assigned zero temperature.

Source reference envelopes (°C; absolute minimum / optimal minimum / optimal maximum / absolute maximum): rice 10/20/30/36, maize 10/18/33/47, sunflower 5/17/34/45. Source links are [rice](https://ecocrop.apps.fao.org/ecocrop/srv/en/dataSheet?id=1574), [maize](https://ecocrop.apps.fao.org/ecocrop/srv/en/dataSheet?id=238663) and [sunflower](https://ecocrop.apps.fao.org/ecocrop/srv/en/dataSheet?id=1191); prior field-level verification is preserved in the normalized projection. These are not stage-specific heat thresholds.

Every component returns NASA parameter, observed values, unit, request period, selected dates/months/day count, missing months, location, URL and response checksum, plus the exact crop requirements, source and interpretation. Rotation climate interpretation is the most concerning component category, without an opaque numerical average. Annual crop-reference cards use the full requested period and may therefore differ from the calendar-month results of a rotation.

## Soil and separate ranking dimensions

Basic soil screening compares farmer-entered pH with the published species optimal interval: inside=`good_fit`, outside=`potential_concern`; missing pH or unsupported requirements=`insufficient_data`. Outside optimum is not a hard exclusion. No texture, drainage or regional soil default is fabricated. Measurement-method/local applicability remains provisional. Missing field pH does not disqualify the crop's supported soil-requirement record; it makes that farm comparison unknown and confidence limited.

Separate dimensions are climate, basic soil, qualitative sequence evidence, farmer preferred-crop occurrence count, and the explicitly unsupported optional dimensions. That count is a factual preference count, not a scientific score. Rotation soil screening uses its most concerning crop interpretation. There is no family-diversity health bonus.

Ranking is lexicographic: farmer priority magnitudes establish dimension precedence; equal priorities sort by dimension name. For supported qualitative dimensions only, `good_fit` precedes `acceptable`, which precedes `potential_concern`. These ordinal positions are comparison keys, not measured utilities or 0–100 scores. Equal results share rank; stable ID determines display order. No artificial distinction is added to ties.

Unsupported active goals remain in `unavailable_priorities`. Supported dimensions can order results under `partial_ranking`; the UI states that the unavailable goals remain unmet. If no active goal can be evaluated, options are unranked by stable ID. No hidden reweighting or missing-as-zero conversion occurs.

## Deterministic evidence confidence

Confidence is evidence quality, **not a probability of success**:

- `high`: all required calendar, requirement/applicability, sequence and farm-comparison states verified, with complete selected calendar-month observations and a specified pH test method.
- `moderate`: all required states usable, at least one provisional, with those contextual inputs present.
- `limited`: missing/unusable comparisons, missing calendar-month observations, or an unspecified pH method. A crop's unresolved required record cannot be smuggled into evaluation by a confidence label.

Unsupported optional dimensions do not by themselves reduce this label or block generation. The present release normally has moderate evidence confidence for a full historical year plus entered pH/method, or limited confidence when those inputs are incomplete. Each option lists its required evidence states and optional gaps separately. No probabilities are generated.

## User-facing boundaries and validation

One concise disclaimer appears above the workflow. UI terms are “Rotation options”, “Explore alternatives” and “Compare strategies”. Missing Information currently appears as the existing “What still needs evidence?” section; it consumes API data-gap reasons for water, salinity, stage sensitivity, soil health and economics. No new screen or major visual redesign was introduced.

Fixtures remain isolated under `tests/fixtures/`, require DEBUG plus a separate server flag and explicit developer API mode, and never become recommendations. The normal UI has no fixture toggle and rejects a fixture marker, wrong mode or non-research dataset origin. Raw agronomy is never synthesized when NASA or scientific data is unavailable.

Validation on 28 October: 51 Python tests, five frontend safety tests, frontend build and Django system checks. Tests cover provisional participation, unresolved exclusion, original provenance, source staleness, source/status propagation, unknown-not-zero, optional gaps/partial ranking, conservative deadlines/occupancy, NASA location sensitivity and climate-driven rank changes, farmer priorities/soil changes, deterministic confidence, and fixture rejection. Browser check showed six real-data options, provisional calendars, moderate confidence and visible gaps. Live 2024 POWER requests at reference points 22.8,89.55 and 25.63,88.65 each returned 366 complete days and six options; coarse option categories tied, while crop-level interpretations differed. Reference points and entered example pH are smoke inputs, not validated farms or field measurements. Runtime results/cache/screenshot remain under ignored `.runtime/`.

Remaining limits: month-envelope conservatism and long gaps, coastal-to-other-locality transfer, unverified cultivar specifics, no independently validated farmer case, incomplete mungbean system, coarse temperature/pH interpretation and unsupported optional dimensions. These are disclosed limits of the enabled prototype, not a reintroduced certified-prescription gate.
