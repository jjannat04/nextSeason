# Research CSV audit and proposed canonical schema

Audit date: October 27, 2026 (Asia/Dhaka). Status: **proposal awaiting approval**.

This is a read-only audit of all 15 researcher CSVs in `research/csv/`. No CSVs were rewritten, values filled, records imported, or application code changed. Documentation changes are this report and the associated PLANS.md update. The per-file inventory at the end includes every column, inferred value type, exact missing-value counts, raw token conventions, observed numeric ranges, duplicate diagnostics, provenance gaps and file-specific disposition. Counts exclude headers; record numbers include the header as record 1 and refer to CSV records, not necessarily physical lines.

## Decision summary

There are **374 data records across 15 well-formed CSVs**. All records match their header width; no exact duplicate rows were found. This is a useful research collection, but **not yet a production-ready decision-engine catalogue**. The critical gaps are calendars explicitly marked unusable, incompatible species/season/variety identities, unsafe salinity thresholds in the soil table, missing stage timing and irrigation inputs, and unreviewed applicability of species proxies.

No current subset can honestly produce a fully verified multi-season rotation today. Normalization alone cannot repair these scientific gaps. A small first slice can be prepared after approval and targeted research completion; the proposed initial catalogue is nine operational crop entries representing seven species, with a four-entry core for the first connected flow. Nine entries must not be advertised as nine independent species.

Audit categories below apply to **fields/claims**, not indiscriminately to whole files. One row may contain safe identity information, a usable source pointer, and an unsafe numeric threshold simultaneously.

## A. Safe to use now

“Safe” here means safe for reference display, form design or metadata handling within stated scope. It does not authorize imports or scientific ranking before approval.

- Raw identities and source pointers as research records; preserve the distinction between rice species, Aman/Aus/Boro production systems, and named cultivars. Taxonomic spelling and variety aliases still need their explicit mapping review.
- The eight master records' names/families/boolean attributes can support an initial catalogue view. The `season_bd` text and missing durations cannot enforce calendar feasibility.
- The 30 AEZ names/IDs and historical area metadata can be displayed as regional reference data with their 1988 source date. They provide no farm soil values or coordinate-to-AEZ geometry.
- The 30 constraint options are **product input definitions**, not measured crop limits. Farmer-entered exclusions, crop locks and dates are viable design concepts; budget/labor/water feasibility stays unknown without supporting data. Five missing public URLs are intentional internal-spec references, not fabricated scientific citations.
- The 21 priority options describe possible objectives. Counts such as distinct families and preferred-crop retention are transparent structural metrics after identity normalization; they do not measure improved soil health. Their default `1` is a UI relative weight, not an evidence-based agricultural weight.
- Case-study descriptions and reported outcomes can be displayed as source-scoped historical examples. They are not engine predictions, field observations for a new farm, or NASA-validated cases.
- Explicit `N/A`, applicability warnings, evidence classes, notes and readiness flags are useful data. Preserve them; do not turn uncertainty into a zero, an automatic approval, or a simulated confidence percentage.

## B. Needs normalization

1. **Four identity schemes:** `C01`–`C08` in files 1–4; numeric `1`–`11` in files 5–7; cultivar slugs in file 8; species/season slugs in files 9/11. Numeric `1` is BARI Mung-6, while `C01` is Aman rice. Never join by index, strip `C`, or merge by a shared number.
2. Split species, production system and variety. Aman/Aus/Boro share a rice species reference; four maize hybrids are not four species. `mungbean`, `Mung Bean`, `mung_bean` and `mung_daal_bari_mung_6` require an explicit species/variety-aware alias map, not fuzzy automatic merging.
3. Use typed missing values with a reason and unchanged raw token. Files use `N/A` and blank strings; no exact `UNKNOWN`, `NULL`, `None`, `NaN` or hyphen-only null tokens were found. Text such as `unverified`, `classes_not_extracted`, `no`, and `conditional` is status information, not null.
4. Parse boolean variants (`true/false`, `yes/no`, `FALSE`) by field definition, not a global string replacement. `production_ready=no` is not equivalent to `nitrogen_fixing=no`; a blank constraint default is unset, not false.
5. Normalize AEZ `13` to a reviewed relation to `AEZ13`; preserve the original. Normalize Barishal/Barisal aliases and administrative hierarchies. A polder, district, soil sample site and whole country must remain different geographic scopes.
6. Split multiple sources and applicability scopes into linked records. Source URLs use `|`, whitespace, concatenated numbered lists, tracking parameters, and malformed suffixes. Keep original URL text and verified canonical URLs separately; preserve identity-bearing query parameters such as EcoCrop `id=`.
7. Convert date fragments into month/day windows with explicit year offsets, sowing/seedbed/transplanting event types and duration basis. Nov–Jan is a cross-year interval, not an invalid descending range. Do not infer dates from master season prose.
8. Introduce controlled vocabularies for texture/drainage, stage, stress type, evidence type and review status; retain free-text qualifiers. `medium` texture is not a verified named texture class. `metric_status` in file 13 mixes statuses with warning sentences: split warning text from a reviewed status.
9. Preserve numeric scalar/range/proxy distinctions. A Kc range is not a point estimate; `legume_bonus=potential_residue_dependent` is not a number. Confidence levels are categorical evidence metadata, not likelihoods.
10. Standardize units with measurement basis, time period and spatial denominator. Annual precipitation, seasonal water depth, irrigation volume per hectare, whole-group volume per week, EC test methods, price-based equivalent yield and actual yield are different quantities.
11. Separate one publication from its several URLs and citations to chapters/tables. `SRC017` and `SRC028` are two records for the same titled MODFLOW work (DOI and publisher routes); resolve after identity verification. Repeated generic EcoCrop titles with different dataset IDs are **not** duplicate publications to merge blindly.
12. Source records' `used_for` names reference historical filenames that differ from the actual repository names. Replace positional/file-name joins with explicit raw-record/claim/source links after approval.

## C. Needs scientific review

| Issue | Evidence / affected records | Required decision |
| --- | --- | --- |
| Observation promoted to tolerance threshold | File 5 numeric crop `1` has `salinity_threshold_ece_ds_m=2.02`; file 7 same crop explicitly says 2.02 is a Polder 30 development-stage observation and NOT a threshold | Quarantine the file 5 threshold. Retain both raw claims and ask B for resolution; do not use it as a hard exclusion |
| Rice tolerance descriptors treated as yield thresholds | File 5 numeric `9` (dhan54) gives 8 and `11` (dhan47) gives 6 dS/m; file 7 intentionally leaves threshold/slope unknown and distinguishes stage tolerance from yield response | Validate measurement method, stage and endpoint; withhold numerical response curves |
| Species proxies labelled with cultivar identities | File 5 pH ranges, file 7 maize 1.7/12 and sunflower 4.8/5, file 6 soil effects, file 8 pair rules | Represent as species/other-cultivar evidence with explicit transfer policy, not local cultivar-specific calibration |
| Different harvest endpoints | File 7 maize notes say reference threshold/slope applies to ear fresh weight, not grain yield | Do not estimate grain-yield loss using this curve without approved transfer |
| Annual rainfall versus seasonal water/stress | File 3 `rainfall_period=annual` in all eight records | Compare only to compatible annual climate statistics if approved; never to a season-total irrigation requirement or daily event |
| Temperature limits versus stage heat injury | File 3 species envelopes include maize absolute max 47°C and sunflower 45°C; file 9 notes a 35°C experiment is not a universal maize threshold | Retain broad envelopes as source claims; cannot use them as flowering damage/fatality thresholds |
| Assumed stage fractions and crop proxies | File 4 notes say fractions assumed; mustard has no timing fractions, development Kc absent for all crops | Approve crop/region timing and interpolation methodology before daily ET or peak-demand calculation |
| Field requirements are not crop failure limits | File 12 rainfed, waterlogging, budget, deadline and soil EC inputs | Separate measured site conditions, farmer hard requirements, and physiological feasibility rules |
| Qualitative classes require operational definitions | File 6 and file 9 descriptors, including “high” overall drought class paired with “sensitive” stages | Clarify class direction and meaning; no automatic ordinal scores or numerical N/SOC gains |
| Polder system evidence expanded to named pairs | All 42 file 8 rules are acceptable at system level; all require calendar verification; 21 are reverse annual phases | Keep conditional directional evidence; do not claim experimentally verified variety-pair transitions |
| Site/scale transfer | Soil sample sites, coastal trials, USA/Midwest residue studies and landscape MODFLOW cases | Never promote site observations to Bangladesh-wide values or basin-model outputs to farm water savings |
| Inconsistent readiness metadata | Files 1/3/4 say sources verified; source registry often says primary source unverified | Keep each assertion and its origin; a reachable/reference source is not an approved engine claim |
| Calendar arithmetic | CAL01 planting July 10–Aug 20 plus 133 days implies some harvests around Nov 20 but the earliest-start combination falls before its listed harvest window; CAL04/CAL05 dates and point durations are not exactly aligned across window endpoints | Researcher must specify paired date distributions, duration basis and inclusive-day convention; independent windows are not interchangeable combinations |
| Cultivar/taxonomy transfer | Generic `Brassica juncea` mustard reference and rice/slugs/season labels may not describe every Bangladesh cultivar a user selects | Verify species and cultivar linkage before inheritance |

Targeted external checks were performed, not a full review of all 74 citations. [FAO salt-tolerance guidance](https://www.fao.org/4/Y4263E/y4263e0e.htm) defines the ECe threshold as the onset of relative yield reduction and ties it to the saturated-paste/root-zone measurement basis; a field observation alone is not that threshold. [FAO-56 chapter 6](https://www.fao.org/4/X0490E/x0490e0b.htm) distinguishes crop coefficient, stage lengths and ETo and calls for local validation of stage models. These checks support the audit's measurement distinctions, not approval of every CSV value.

The [Amtali trial abstract](https://epubs.icar.org.in/index.php/JISCAR/article/view/90041) supports the sequence identities and MBCR values recorded in RC001–RC004 for that trial. It does not supply validated calendars for a new farm. No source verification flags or CSV values were changed during these checks.

## D. Missing critical fields

- **Calendar feasibility:** zero approved calendars; all nine have `production_ready=no`, no source title/URL/year, five lack harvest window and duration. Master durations are absent for all eight entries. No explicit turnaround, seedbed versus field occupancy duration, cultivar, calendar year offset, validated relay overlap, or approved uncertainty window.
- **Core coverage:** sesame has cultivar references and many pair rules but no master/climate/water/calendar entry. Mustard/watermelon appear in the master but lack matching soil/rotation cultivar coverage. Additional species in stage/suitability/case tables lack complete master profiles.
- **Water-risk/Commons:** no numeric seasonal water requirements in any of 32 water rows; stage fractions are assumed; effective-rainfall method, reference ET method inputs, irrigation efficiency, soil-water balance parameters, rice land preparation/percolation assumptions and shared capacity are not delivered as validated data. Seasonal Kc alone cannot establish delivered irrigation demand or weekly conflicts.
- **Stage stress:** 32/34 rows lack numeric thresholds; the only two numerical rows are dhan67 salinity descriptors, not heat/drought injury functions. No crop-stage date model or exposure-duration response. Seven rows explicitly lack crop-specific stage evidence.
- **Soil:** no AEZ-wide pH, texture, salinity or drainage values anywhere in the 30-row reference table; only three limited sample-site records, two with pH ranges. No geographic polygons/approved location lookup. Missing pH test method/depth in requirement/observation contracts.
- **Sources:** missing column-level source locators and approval/reviewer timestamps throughout; seven file 5 rows lack source titles/URLs; seven file 9 placeholder rows lack source titles/URLs; registry lacks all authors and 52 publication years. DOI absence is not itself a defect for a legitimate government source.
- **Ranking:** no reviewed numeric normalization/scoring policy, complete local economics, management-cost/labor time series or quantified soil-health model. General statements/case BCRs cannot substitute for per-crop farm budgets.
- **Validation:** no case coordinates, actual NASA extracts or NASA reanalysis results; no expected engine score/rank/feasibility assertions; no paired complete farm inputs and independently approved expected decisions.
- **Schema:** no approved crop/variety/region crosswalk, source-claim linkage, measurement-basis registry or field-level approval state. Dataset-level confidence cannot approve every value.

## E. Not needed for MVP

Retain these raw records, but defer their engine activation rather than deleting them:

- MODFLOW basin-scale groundwater effects and landscape replacement cases RC013–RC015; no hydrogeological simulator needed for Water Commons.
- Relay/four-/five-crop optimization in RC005–RC012, detailed market access, income variance, credit, mechanization, pesticide-free guarantees and broad labor/capital optimization without supporting inputs. These remain contextual evidence or future objectives.
- File 13 FP020 groundwater abstraction, FP021 rice-equivalent yield, FP012 income variance and FP014 market-access optimization; all need missing specialist datasets. Keep the core five priorities visible, with unsupported dimensions explicitly unavailable rather than fabricated.
- Extending beyond the first region to every crop in files 9/11 or every AEZ. The catalogue/maps can remain reference resources without scientific claims of nationwide validation.
- Numeric SOC/N gains, cultivar-specific salinity/yield curves, automatic soil report extraction, and ornamental numerical confidence. The MVP can use reviewed qualitative contribution statements where evidence permits, without claiming those missing models exist.

## Functional sufficiency

| Capability | Sufficient now? | Exact safe boundary / prerequisite |
| --- | --- | --- |
| Crop filtering | Partial | Identity/family and farmer exclusions after approved crosswalk; local suitability and seed availability not complete |
| Crop calendar feasibility | No | All calendars unverified; no coherent approved site-specific sequence; durations/turnaround incomplete |
| Climate suitability | Partial reference only | Eight species/production entries have broad temperature/annual-rainfall envelopes; not locally validated seasonal/stage risk |
| Soil suitability | Partial reference only | pH/texture claims exist for 11 cultivar-labelled records; seven lack citations, local transfer and salinity conflicts unresolved |
| Water-risk evaluation | No quantitative decision-ready model | Kc references can inform later ET work; not complete crop demand, irrigation or peak risk |
| Crop-rotation rules | Conditional qualitative evidence | 42 unique directional pairs, all acceptable/system-level/calendar-dependent; no prohibited-rule catalogue or universal default for absent pairs |
| Soil-health contribution | Partial qualitative | Family/legume diversity and residue-dependent statements; no numeric N, SOC or measured improvement |
| Salinity handling | Warnings/reference only | Explicit measurement basis and approved scope needed; critical conflicts block hard thresholds and cultivar loss estimates |
| Crop-stage stress sensitivity | Partial qualitative | Some sensitive stages identified, but missing timing/exposure response prevents calibrated numerical stress tests |
| Bangladesh validation cases | Reference cases only | 12 trial records, three landscape scenarios, one survey; no NASA reanalysis or complete reproducible farm cases |

## Proposed canonical internal schema (not implemented)

Use explicit Django domain models and versioned validated releases. Avoid a free-form numeric scoring engine that executes arbitrary `engine_rule` text. All normalized fields link back to unchanged raw records. Do not import until audit approval.

| Entity | Key fields and relations | Required semantics |
| --- | --- | --- |
| `ResearchAsset` | ID, relative path, SHA-256, encoding, header, audited timestamp | Immutable original file identity; distinguish subsequent researcher revisions |
| `RawRecord` | asset FK, CSV record number, raw JSON including every cell, row hash | Original strings preserved exactly, including blank and N/A |
| `CropSpecies` | stable slug, scientific name, family FK, EN/BN names, verified flags | Rice is one species, independent of Aman/Aus/Boro |
| `ProductionSystem` | stable ID, species FK, seasonal/establishment/water regime qualifiers | `rice_aman`, `rice_aus`, `rice_boro`; not automatically interchangeable |
| `Cultivar` | stable ID, species FK, original names/aliases, reviewed systems via explicit relation | Hybrids/BRRI varieties distinct; never infer cultivar from species-level trials |
| `CropAlias` | asset/field namespace, raw ID/name, species/system/cultivar target, mapping type, reviewer/status | Unique within source namespace, not globally; ambiguity blocks activation |
| `Region` / `Applicability` | typed country/division/district/upazila/AEZ/polder/site/region set, parent relations, optional verified geometry, exclusions | Preserve text and uncertainty; global species references and site samples remain separate |
| `SourceWork` / `SourceLocator` | original SRC IDs, title, author/year nullable, DOI, original URL list, verified canonical URL, page/table/section, verification state/date | Many URLs per work and many sources per claim; no URL reachability claim without a check |
| `EvidenceClaim` | raw record/cells, subject IDs, property, raw value, typed scalar/range/category/text/boolean, unit FK, measurement basis, stage, geography, management, period, source links | Species/cultivar/proxy level, value kind, confidence raw/enum, notes, caveats, review status, allowed uses; no lossy promotion of prose to number |
| `UnitDefinition` | dimension, canonical symbol, denominator, period, measurement method, conversion identifier | Conversion only within compatible dimensions/bases; reviewed lossless transformations logged |
| `CropCalendar` | subject/applicability, season, event type, month/day start/end, year offsets, establishment/harvest intervals, duration range and basis, turnaround, occupancy/relay model, claim IDs | Unknown timing remains null; full validation required before feasibility use |
| `ClimateRequirement` | subject/applicability, variable, absolute/optimal envelope, aggregation period, measurement/experiment meaning, claim IDs | Annual rainfall vs stage temperatures explicitly distinguished |
| `SoilRequirement` / `SoilObservation` | subject or site, property, typed value/range, soil depth, test method, sample N/date, spatial scope, claim IDs | Observation is not a threshold; site pH never fills entire AEZ |
| `WaterProfile` / `StageCoefficient` | subject/applicability, stage ID, timing model/range, Kc scalar/range, coefficient method, assumed/verified status, demand definition, management | Development interpolation is a separate approved transform, not filling missing raw Kc values |
| `SalinityResponse` | subject/applicability, ECe or other test method, stage, response kind, endpoint (grain/ear fresh weight/survival), threshold/slope nullable, source claim | Field observation, tested exposure, descriptor and fitted threshold are different response kinds |
| `RotationEvidence` | previous/next subject plus evidence specificity, direction, region, calendar prerequisite, compatibility, management conditions, derivation, claim links | Absent pair is unknown; same family is not intrinsically prohibited; acceptable is not guaranteed feasible |
| `SoilContribution` | subject, practice/condition, categorical effect, supported numeric value nullable, evidence links | Residue retained/removed/incorporated affects claim applicability |
| `StageSensitivity` | subject, stress/stage IDs, sensitivity category/direction, timing linkage, threshold/exposure/response nullable, claim links | Do not coerce qualitative text or tested temperature into damage thresholds |
| `ConstraintDefinition` / `PriorityDefinition` | ID, typed input/metric, display EN/BN, units, required data, executable implementation ID, reviewed enums, caveats | Input definitions are product rules; reference text is never executable code; bind priorities to five reviewed product dimensions |
| `ValidationCase` / `CaseOutcome` / `CaseActivity` | case/source IDs, region/site, study period/design/unit, sequence activities with optional overlap groups, historical outcomes/unit/baseline, raw claims, missing inputs, NASA status | Survey, trial and model endpoints remain separate; reported number not expected future farm output |
| `KnowledgeRelease` / `ReviewDecision` | version/hash, activated claims/mappings, reviewer/date, conflicts and resolution rationale, supersession | Field-level allowlist: reference display, qualitative indicator, soft scoring or hard feasibility, approved separately |

Per-claim envelope must preserve: raw file/record/column/value; original crop ID/name/variety; raw and canonical source URLs/titles; raw confidence and evidence strength separately; original notes; geography/management/stage/period; normalization transforms; and scientific approval state. Null normalized value includes `missing_reason` such as `not_reported`, `explicitly_unverified`, `not_applicable`, `not_extracted`, `ambiguous`, or `conflicting`. Do not infer a precise reason when the CSV only says N/A: retain `unspecified_missing`.

### Proposed crop crosswalk

These are proposed stable identifiers, not edits to CSVs or confirmation of cultivar/system applicability:

| Existing identity | Canonical target proposal | Important boundary |
| --- | --- | --- |
| C01 / aman_rice | species `rice`; system `rice_aman` | Species reference inherited only with reviewed scope |
| C02 / aus_rice | species `rice`; system `rice_aus` | Distinct calendar/system |
| C03 / boro_rice | species `rice`; system `rice_boro` | Seedbed vs transplanting matters |
| C04 / maize | species `maize` | Not automatically any named hybrid |
| C05 / Sunflower | species `sunflower` | HySun-33 is separate cultivar |
| C06 / mung_bean / Mungbean | species `mungbean` | BARI Mung-6 separate cultivar |
| C07 / mustard | species `mustard_b_juncea` pending taxonomy review | Do not map every local mustard variety automatically |
| C08 / Watermelon | species `watermelon` | Missing matched cultivar/rotation evidence |
| Numeric 1 / mung_daal_bari_mung_6 | cultivar `bari_mung_6`, species mungbean | Numeric 1 never maps to C01 |
| Numeric 2 / sesame_bari_til_4 | cultivar `bari_til_4`, species sesame | Add a species/system candidate only after approved new facts; missing master data stays missing |
| Numeric 3 / sunflower_hysun_33 | cultivar `hysun_33`, species sunflower | Preserve raw spelling |
| Numeric 4 / maize_e_34_x_bil_211 | cultivar `maize_e34_x_bil211` | Hybrid name verification required |
| Numeric 5 / maize_pinacle_3_x_bil_211 | cultivar `maize_pinacle3_x_bil211` | Do not silently correct Pinacle/Pinnacle |
| Numeric 6 / maize_bil_79_x_pinacle_16 | cultivar `maize_bil79_x_pinacle16` | Separate hybrid |
| Numeric 7 / maize_bari_hybrid_maize_16 | cultivar `bari_hybrid_maize_16` | Separate hybrid |
| Numeric 8 / rice_brri_dhan51 | cultivar `brri_dhan51`, species rice | Proposed Aman link needs confirmed cultivar evidence |
| Numeric 9 / rice_brri_dhan54 | cultivar `brri_dhan54`, species rice | Salinity descriptor is not a threshold |
| Numeric 10 / rice_brri_dhan52 | cultivar `brri_dhan52`, species rice | No automatic cultivar curve |
| Numeric 11 / rice_brri_dhan47 | cultivar `brri_dhan47`, species rice | System and salinity stage require evidence |
| BRRI_dhan67 / BRRI_dhan83 / other named varieties in 9/11 | Distinct cultivar records linked to reviewed systems | No aliases to the four numeric-ID rice varieties |

Other species slugs (wheat, lentil, chickpea, potato, groundnut, chili, onion, garlic, sugarcane, jute, sesame) remain separately identified reference subjects. Case-only garden pea, red amaranth, radish, sweet gourd and Dhaincha need explicit raw sequence tokens; do not invent complete crop records or map green manure to a generic legume. `Fallow` is a land-use activity, not a species.

### Unit and value policy

| Canonical quantity | Unit / type | Conversion restriction |
| --- | --- | --- |
| Temperature | °C, scalar or range | Preserve species-envelope vs experimental/stage context |
| Rainfall / ET depth | mm with `day/season/year` interval | Aggregation requires actual dates and adequate coverage; annual envelope cannot become seasonal demand |
| Kc | dimensionless scalar/range | Not water depth; development/late curve method and timing must be approved |
| Soil pH | dimensionless with test medium/method | Unknown method preserved; no automatic water/KCl equivalence |
| Salinity | dS/m plus `ECe/ECw/other/unknown` basis | `dS_per_m` spelling normalization is safe; converting soil-water test methods requires reviewed model |
| Salinity loss slope | percentage points of endpoint-relative yield per dS/m | Not a fraction unless explicitly transformed; endpoint and valid stage/domain retained |
| Area | ha | Historical region area differs from farmer field area |
| Irrigation | m³/ha/season or m³/time bucket | 1 mm over 1 ha equals 10 m³ geometrically; gross irrigation still requires agronomic water balance and efficiency |
| Economic value | BDT/ha with date, price basis and season | BCR/MBCR are separate dimensionless outcomes, not money or interchangeable ratios |
| Yield | kg/ha (raw t/ha retained) | Price-weighted rice-equivalent yield cannot be used as physical rice yield |
| Labor | person-days with area and period basis | `person_days_per_year` has no explicit hectare basis; do not infer it from another column |
| Weight, stage fraction, percent | relative weight/fraction/% as distinct types | File 13 defaults 1 mean relative weights, not 100% allocated independently to all objectives |
| IDs, dates, years, categories | string ID / structured interval / integer year / enum | Numeric-looking crop/AEZ IDs are identifiers, not measured quantities |

## Smallest first working slice and 8–10-entry catalogue

**No scientifically complete slice is available as-is.** The smallest promising connected subset is **Aman rice, maize, sunflower and mungbean** at species/production-system level, using the Polder 30 system evidence where applicable. This is a proposed four-entry engineering slice after scientific gates, not an approved cultivar recommendation. Do not combine geographically incompatible provisional calendars merely to make it work. Polder 30 versus Amtali must be a conscious reviewed site choice.

Minimal candidate records for review:

- Files 1 and 3: C01, C04, C05, C06 (four rows each).
- File 2: CAL01, CAL04, CAL05, CAL06 (four rows, **all quarantined** pending primary local calendars; CAL06 is Patuakhali and is not automatically valid in Polder 30).
- File 4: the four stage rows for each of C01/C04/C05/C06 (16 rows, reference Kc only; assumed timing and missing curves remain blocked).
- Files 5–7: numeric `1`, `3`, `4`, `8` as representative raw claim bundles for mungbean/HySun-33/a named maize hybrid/dhan51. This is not cultivar selection; generic facts require reviewed species-level re-expression and variety claims remain separate. File 5 thresholds/citation gaps are withheld.
- File 8: ROT007, ROT027, ROT037 (dry-season crop → dhan51) and ROT071, ROT073, ROT074 (dhan51 → dry-season crop). These six rows establish a reviewable system-evidence graph, not six validated cultivar transitions. Use underlying species-level evidence only after approval, and confirm any named cultivar substitution independently.
- File 9: three maize rows plus four Aman rows as qualitative reference candidates; there is no validated mungbean/sunflower stage timing model to borrow. Preserve the missing mungbean stage row as missing.
- File 10: geography catalogue only; require farmer-entered soil or an approved site-specific source. Do not fill Polder 30 pH from the three unrelated sampled AEZ sites.
- File 14: RC002/RC003 are simple three-crop **Amtali** cases useful as separate trial references after full-method verification; they need Aus crop coverage and cannot validate a Polder 30 rotation. RC001 is usable if mustard is enabled. No currently delivered RC case independently validates the exact proposed four-entry Polder slice.
- Core form definitions: FC002–FC014 as relevant (water fields collect inputs but cannot certify feasibility yet), FC019 seed exclusion, and farmer-defined limits supported by implemented evaluators. Initial transparent metric candidates: FP008 family count and FP018 preferred retention. Water FP001 and stress FP003/FP004 remain disabled until data/method gates pass; five product priorities are not reduced to these structural proxies.

An initial **nine-entry operational catalogue** should target the eight existing master entries (Aman, Aus, Boro, maize, sunflower, mungbean, mustard, watermelon) **plus sesame**. This is **seven species**, since three entries are rice production systems. Sesame has local-system references but lacks master/climate/calendar/Kc records. Watermelon is the weakest connected entry and can remain visible but unavailable for generation until its calendar and sequence evidence exist. Do not meet the numerical target by counting four maize hybrids as four independent crops or by inventing sesame data. If “8–10 crops” must mean distinct species, the current core evidence cannot support that target without new complete profiles; lentil/wheat are possible research candidates, not approved additions.

Milestone 1 should demonstrate one location with approved calendars, dated nonoverlapping multi-season alternatives, at least two materially different feasible sequences, preserved farmer hard constraints, real NASA-dependent comparison, and source-linked explanations. A plan may span consecutive cropping events across more than one year; do not label a two-crop annual system as triple annual cropping. Any fallow/gap must be explicit and validated. True three-season coverage requires a third locally validated slot/crop system rather than calendar fabrication.

## Exact work required before Milestone 1 (approval gated)

| ID | Task | Acceptance evidence |
| --- | --- | --- |
| N01 | Freeze raw research assets by SHA-256; retain raw records and columns | Original CSV bytes unchanged; manifest matches this audit or a reviewed new version |
| N02 | Approve species/system/cultivar/alias crosswalk for all four ID namespaces | Every enabled subject resolves unambiguously; C01 ≠ numeric 1; genus/cultivar transfers explicit |
| N03 | Define field-specific null, boolean, category, numeric/range and status parsers | Blank defaults remain unset; false/zero retained; mixed warning/status text separated; no unknown score defaults |
| N04 | Build source-work/URL/locator mapping proposal; resolve missing scientific citations and duplicate publication identity | Every enabled scientific claim has an exact source and locator; seven uncited soil rows quarantined or repaired by researchers; internal design references identified |
| N05 | Quarantine conflicting soil salinity claims and separate observations, stage descriptors and response thresholds | Numeric crop 1 value 2.02 never acts as cutoff; rice 8/6 claims and maize/sunflower proxies reviewed, resolution logged |
| N06 | Choose first location/region and obtain approved primary calendars, duration basis/range and turnaround for enabled crops | No `production_ready=no` calendar drives feasibility; seedbed vs transplanting and cross-year intervals tested; two distinct complete sequences reviewed |
| N07 | Approve claim geography/management/evidence-level applicability and conditional inheritance | Polder evidence not treated as Rangpur-wide; site pH not AEZ average; variety proxies visibly marked |
| N08 | Approve canonical units and measurement endpoints/periods; register only justified conversions | Annual rainfall not seasonal demand; ECe not ECw; grain not ear fresh weight; ratios and equivalent yields isolated |
| N09 | Validate complete stage/Kc curve and ET/effective-rainfall/irrigation method for slice; otherwise explicitly gate numerical water features | No invented fractions/Kc point values; stage demand and weekly totals trace to reviewed inputs; required uncertainty exposed |
| N10 | Normalize pair evidence and activation prerequisites; specify absent-pair semantics | Six proposed slice relations reviewed; system-level acceptable ≠ guaranteed feasible; hard/soft rules independently approved |
| N11 | Approve climate aggregation, soil and stage stress evaluation rules and priority normalization | Envelope, qualitative warning and numerical score uses are separately authorized; missing dimensions block incomplete ranking or require explicit user reweighting |
| N12 | Select/reference-map first cases, add complete inputs and authentic NASA history, write expected decision assertions with B | At least two reproducible local alternatives and six required sensitivity/constraint checks; historical case outcomes remain distinct from predicted outputs |
| N13 | Produce dry-run import diagnostics **after audit approval**, then activate a versioned field-level allowlist | No silent merges/fills; all rejected/unmapped/conflicting facts reported; imports require approved data, not only successful parsing |

Milestone 1 implementation/data import remains blocked on **audit approval plus the scientific gates**, not merely an importer command. UI/foundation work can be approved separately, but is not scientific readiness. No code or rewritten data accompanies this proposal.

## Per-file audit inventory

The following generated inventory completes the column-level audit. Numeric ranges are observed minima/maxima, **not validated agronomic bounds**. “Category/text” is deliberately conservative; a finite set of long sentences is not automatically an engine enum. Empty source fields and suspicious names are called out separately. Each file's purpose, normalization, unsafe uses, conflicts, scope and MVP disposition appear below its column table.

### 1. 1_crops_master.csv

**Purpose:** Species/production-system identity and high-level catalogue metadata.

**Inventory:** 8 data records; 25 columns; zero inconsistent-width records; 0 exact duplicate rows. Candidate unique key: `crop_id`; duplicate keys: 0.

**Null conventions:** `N/A`: 24 cells. Counts below are per column. `0` means no missing cells, not a scientific zero.

| Column (all original columns) | Apparent value type | Missing cells / raw tokens | Observed range or category examples |
| --- | --- | --- | --- |
| `crop_id` | Identifier/string | 0 | C01, C02, C03, C04, C05 ... |
| `crop_name_en` | Category/text | 0 | Aman rice, Aus rice, Boro rice, Maize ... |
| `scientific_name` | Category/text | 0 | Oryza sativa L., Zea mays L., Helianthus annuus L., Vigna radiata (L.) Wilczek ... |
| `crop_family` | Category/text | 0 | Poaceae, Asteraceae, Fabaceae, Brassicaceae ... |
| `crop_type` | Category/text | 0 | cereal, oilseed, pulse, cucurbit_fruit |
| `season_bd` | Category/text | 0 | Jul-Dec, Mar-May sowing only, Nov-Dec sowing only, Nov-May ... |
| `is_legume` | Boolean-like category | 0 | false, true |
| `is_cereal` | Boolean-like category | 0 | true, false |
| `is_oilseed` | Boolean-like category | 0 | false, true |
| `is_pulse` | Boolean-like category | 0 | false, true |
| `is_vegetable` | Boolean-like category | 0 | false, true |
| `is_root_tuber` | Boolean-like category | 0 | false |
| `typical_duration_days_min` | Undetermined (all missing) | 8 (N/A=8) | Expected type needs schema definition |
| `typical_duration_days_max` | Undetermined (all missing) | 8 (N/A=8) | Expected type needs schema definition |
| `notes` | Text/source/list | 0 | 2 distinct nonmissing values |
| `source_title` | Text/source/list | 0 | 2 distinct nonmissing values |
| `source_url` | Text/source/list | 0 | 6 distinct nonmissing values |
| `source_year` | Undetermined (all missing) | 8 (N/A=8) | Expected type needs schema definition |
| `confidence_level` | Category/text | 0 | medium, low |
| `soil_ph_opt_min` | Numeric | 0 | 5 to 6 |
| `soil_ph_opt_max` | Numeric | 0 | 6.2 to 7.5 |
| `data_status` | Category/text | 0 | partial, species_level |
| `source_verified` | Boolean-like category | 0 | yes |
| `source_scope` | Category/text | 0 | global_species_reference, global_crop_reference |
| `production_ready` | Category/text | 0 | conditional |

**File-specific findings (naming, units, conflicts, unsafe engine use, scope and normalization):

- Names/duplicates: eight unique crop IDs and names, but C01/C02/C03 deliberately share Oryza sativa, family and species references; retain three systems linked to one species. No accidental identical full rows. Crops in other files are not keyed to these IDs.

- Units/ranges: duration is days but entirely missing; pH is dimensionless and numeric bounds are ordered. `season_bd` mixes full windows and sowing-only prose. Do not interpret generic pH optima as cultivar-specific measured requirements.

- Unsafe engine columns: season prose, all missing durations, source_verified=yes and production_ready=conditional are not proof of calendar or regional feasibility. Boolean crop-type flags are overlapping tags; watermelon marked vegetable is a product classification choice, not necessarily a taxonomy error.

- Sources/scope: every row has title/URL, all years missing; links are global species references. No local cultivar support is implied. Confidence and data_status are categories, not numeric scores.

- Normalize: stable species/system IDs, boolean tags, source links, season display text; preserve original scientific-name strings. Needs Bangla crop labels and approved cultivar links. Disposition A identity/reference; B mapping; C local applicability; D duration/calendar.

**Repeated property bundles:** compared `scientific_name`: C01, C02, C03. Repetition is not authorization to delete records or pool cultivar evidence.


### 2. 2_crop_calendar.csv

**Purpose:** Regional planting/harvest windows intended for rotation feasibility.

**Inventory:** 9 data records; 28 columns; zero inconsistent-width records; 0 exact duplicate rows. Candidate unique key: `calendar_id`; duplicate keys: 0.

**Null conventions:** `N/A`: 76 cells. Counts below are per column. `0` means no missing cells, not a scientific zero.

| Column (all original columns) | Apparent value type | Missing cells / raw tokens | Observed range or category examples |
| --- | --- | --- | --- |
| `calendar_id` | Identifier/string | 0 | CAL01, CAL02, CAL03, CAL04, CAL05 ... |
| `crop_id` | Identifier/string | 0 | C01, C02, C03, C04, C05 ... |
| `region_scope` | Category/text | 0 | Polder 30 Batiaghata, coastal low-salinity region, coastal Dacope; Amtali, coastal low-salinity polder ... |
| `division` | Category/text | 4 (N/A=4) | Khulna, Khulna; Barishal, Barishal |
| `district` | Category/text | 4 (N/A=4) | Khulna, Khulna; Barguna, Patuakhali, Satkhira |
| `agro_ecological_zone` | Numeric | 8 (N/A=8) | 13 to 13 |
| `season_name` | Category/text | 0 | Jul-Dec, Mar-May sowing only, Nov-Dec seedbed sowing, Nov-May ... |
| `planting_start_month` | Numeric | 0 | 1 to 12 |
| `planting_start_day` | Numeric | 0 | 1 to 30 |
| `planting_end_month` | Numeric | 0 | 1 to 12 |
| `planting_end_day` | Numeric | 0 | 5 to 31 |
| `harvest_start_month` | Numeric | 5 (N/A=5) | 3 to 11 |
| `harvest_start_day` | Numeric | 5 (N/A=5) | 3 to 26 |
| `harvest_end_month` | Numeric | 5 (N/A=5) | 4 to 12 |
| `harvest_end_day` | Numeric | 5 (N/A=5) | 5 to 31 |
| `typical_duration_days` | Numeric | 5 (N/A=5) | 60 to 133 |
| `transplanting_or_direct_seed` | Category/text | 2 (N/A=2) | transplanting, direct_seed |
| `irrigated_or_rainfed` | Category/text | 6 (N/A=6) | rainfed, irrigated |
| `notes` | Text/source/list | 0 | 1 distinct nonmissing values |
| `source_title` | Undetermined (all missing) | 9 (N/A=9) | Expected type needs schema definition |
| `source_url` | Undetermined (all missing) | 9 (N/A=9) | Expected type needs schema definition |
| `source_year` | Undetermined (all missing) | 9 (N/A=9) | Expected type needs schema definition |
| `confidence_level` | Category/text | 0 | medium, low |
| `source_verified` | Boolean-like category | 0 | no |
| `date_basis` | Category/text | 0 | research_window |
| `data_status` | Category/text | 0 | unverified |
| `production_ready` | Boolean-like category | 0 | no |
| `source_scope` | Category/text | 0 | unverified_local_calendar |

**File-specific findings (naming, units, conflicts, unsafe engine use, scope and normalization):

- Names/duplicates: CAL01-CAL09 unique; C08 has two regional planting records (CAL08/CAL09), not duplicate facts. Region scopes overlap but do not justify choosing one silently. The raw AEZ value 13 is an identifier, not a measurement.

- Units/ranges: month/day values fit ordinary calendar domains; Nov-Jan windows require explicit year offsets. CAL03 is seedbed sowing despite transplanting establishment label. CAL01 and CAL04/CAL05 window-duration consistency needs review; no minimum turnaround exists. Zero/negative duration was not observed in populated values.

- Unsafe engine columns: ALL nine records explicitly source_verified=no, data_status=unverified, production_ready=no. Existing numeric dates/durations must remain inactive regardless of their plausibility. Five records lack harvest/duration, all lack citation. Do not fabricate duration from a season label.

- Sources/scope: all source URLs/titles/years N/A. Polder 30, Patuakhali, Satkhira and broad Bangladesh windows are not interchangeable. No cultivar or fully specified region-year management basis.

- Normalize: structured calendar event types, cross-year offsets, region relations, establishment-to-harvest duration basis, cultivar/system scope and approved sources. Disposition B structural; C scientific review; D critical blocker.

**Missing `source_url` record locators:** 2 [CAL01], 3 [CAL02], 4 [CAL03], 5 [CAL04], 6 [CAL05], 7 [CAL06], 8 [CAL07], 9 [CAL08], 10 [CAL09].


### 3. 3_crop_climate_requirements.csv

**Purpose:** Broad crop-species climate envelopes for temperature and annual rainfall.

**Inventory:** 8 data records; 30 columns; zero inconsistent-width records; 0 exact duplicate rows. Candidate unique key: `crop_id`; duplicate keys: 0.

**Null conventions:** `N/A`: 83 cells. Counts below are per column. `0` means no missing cells, not a scientific zero.

| Column (all original columns) | Apparent value type | Missing cells / raw tokens | Observed range or category examples |
| --- | --- | --- | --- |
| `crop_id` | Identifier/string | 0 | C01, C02, C03, C04, C05 ... |
| `temp_absolute_min_c` | Numeric | 0 | 5 to 15 |
| `temp_optimal_min_c` | Numeric | 0 | 15 to 21 |
| `temp_optimal_max_c` | Numeric | 0 | 28 to 36 |
| `temp_absolute_max_c` | Numeric | 0 | 36 to 47 |
| `rainfall_min_mm` | Numeric | 0 | 300 to 1000 |
| `rainfall_optimal_min_mm` | Numeric | 0 | 500 to 1500 |
| `rainfall_optimal_max_mm` | Numeric | 0 | 700 to 2400 |
| `rainfall_max_mm` | Numeric | 0 | 1250 to 4200 |
| `critical_heat_temp_c` | Undetermined (all missing) | 8 (N/A=8) | Expected type needs schema definition |
| `critical_heat_stage` | Undetermined (all missing) | 8 (N/A=8) | Expected type needs schema definition |
| `humidity_min_pct` | Undetermined (all missing) | 8 (N/A=8) | Expected type needs schema definition |
| `humidity_optimal_min_pct` | Undetermined (all missing) | 8 (N/A=8) | Expected type needs schema definition |
| `humidity_optimal_max_pct` | Undetermined (all missing) | 8 (N/A=8) | Expected type needs schema definition |
| `humidity_max_pct` | Undetermined (all missing) | 8 (N/A=8) | Expected type needs schema definition |
| `solar_requirement_category` | Category/text | 3 (N/A=3) | very_bright, clear_skies |
| `drought_tolerance` | Undetermined (all missing) | 8 (N/A=8) | Expected type needs schema definition |
| `heat_tolerance` | Undetermined (all missing) | 8 (N/A=8) | Expected type needs schema definition |
| `waterlogging_tolerance` | Undetermined (all missing) | 8 (N/A=8) | Expected type needs schema definition |
| `notes` | Text/source/list | 0 | 2 distinct nonmissing values |
| `source_title` | Text/source/list | 0 | 2 distinct nonmissing values |
| `source_url` | Text/source/list | 0 | 6 distinct nonmissing values |
| `source_year` | Undetermined (all missing) | 8 (N/A=8) | Expected type needs schema definition |
| `confidence_level` | Category/text | 0 | medium, high, low |
| `rainfall_period` | Category/text | 0 | annual |
| `source_verified` | Boolean-like category | 0 | yes |
| `data_status` | Category/text | 0 | partial, species_level |
| `evidence_class` | Category/text | 0 | FAO_EcoCrop_global |
| `dataset_scope` | Category/text | 0 | global_species_reference |
| `production_ready` | Category/text | 0 | conditional |

**File-specific findings (naming, units, conflicts, unsafe engine use, scope and normalization):

- Names/duplicates: eight unique crop IDs; three rice-system rows repeat the same species climate values. This is shared species evidence, not three independent rice-season calibrations. No full-row duplicates.

- Units/ranges: temperatures degC; rainfall mm/year explicitly in rainfall_period. Absolute/optimal bounds are ordered. High absolute maxima (maize 47, sunflower 45) are broad source envelopes and cannot be crop-stage lethal/heat-stress thresholds. Do not compare annual rainfall ranges to monthly NASA totals or seasonal irrigation depth.

- Unsafe engine columns: missing critical heat, humidity and drought/heat/waterlogging tolerances cannot drive risk scores; solar labels very_bright/clear_skies are categorical, not numeric solar-radiation demand. Envelopes alone do not define a validated response curve.

- Sources/scope: source URLs/titles populated, years absent. All evidence global; conditional production readiness and differing confidence categories do not establish Bangladesh calibration.

- Normalize: species requirements separate from rice systems, units/time aggregation, envelope vs injury-threshold property, controlled solar categories, explicit unknowns and field-level approvals. Disposition A reference; B types; C scoring interpretation; D stage requirements.

**Repeated property bundles:** compared `temp_absolute_min_c`, `temp_optimal_min_c`, `temp_optimal_max_c`, `temp_absolute_max_c`, `rainfall_min_mm`, `rainfall_optimal_min_mm`, `rainfall_optimal_max_mm`, `rainfall_max_mm`: C01, C02, C03. Repetition is not authorization to delete records or pool cultivar evidence.


### 4. 4_crop_water_requirements.csv

**Purpose:** Reference crop coefficients and proposed growth-stage fractions for water modelling.

**Inventory:** 32 data records; 24 columns; zero inconsistent-width records; 0 exact duplicate rows. Candidate unique key: `crop_id`, `growth_stage`; duplicate keys: 0.

**Null conventions:** `N/A`: 219 cells. Counts below are per column. `0` means no missing cells, not a scientific zero.

| Column (all original columns) | Apparent value type | Missing cells / raw tokens | Observed range or category examples |
| --- | --- | --- | --- |
| `crop_id` | Identifier/string | 0 | C01, C02, C03, C04, C05 ... |
| `growth_stage` | Category/text | 0 | initial, development, mid_season, late_season |
| `stage_start_fraction` | Numeric | 4 (N/A=4) | 0 to 0.81 |
| `stage_end_fraction` | Numeric | 4 (N/A=4) | 0.16 to 1.0 |
| `kc_value` | Numeric | 15 (N/A=15) | 0.3 to 1.2 |
| `water_requirement_mm_min` | Undetermined (all missing) | 32 (N/A=32) | Expected type needs schema definition |
| `water_requirement_mm_typical` | Undetermined (all missing) | 32 (N/A=32) | Expected type needs schema definition |
| `water_requirement_mm_max` | Undetermined (all missing) | 32 (N/A=32) | Expected type needs schema definition |
| `irrigation_dependency` | Category/text | 20 (N/A=20) | rainfed, irrigated |
| `drought_sensitive_stage` | Undetermined (all missing) | 32 (N/A=32) | Expected type needs schema definition |
| `waterlogging_sensitive_stage` | Undetermined (all missing) | 32 (N/A=32) | Expected type needs schema definition |
| `notes` | Text/source/list | 0 | 1 distinct nonmissing values |
| `source_title` | Text/source/list | 0 | 1 distinct nonmissing values |
| `source_url` | Text/source/list | 0 | 1 distinct nonmissing values |
| `source_year` | Integer year | 0 | 1998 to 1998 |
| `confidence_level` | Category/text | 0 | medium, low |
| `source_verified` | Boolean-like category | 0 | yes |
| `data_status` | Category/text | 0 | global_reference_not_local |
| `kc_basis` | Category/text | 0 | FAO56_reference_or_proxy |
| `measurement_type` | Category/text | 0 | reference_coefficient |
| `kc_min` | Numeric | 8 (N/A=8) | 0.3 to 1.2 |
| `kc_max` | Numeric | 8 (N/A=8) | 0.3 to 1.2 |
| `production_ready` | Category/text | 0 | conditional, no |
| `local_calibration_required` | Boolean-like category | 0 | yes |

**File-specific findings (naming, units, conflicts, unsafe engine use, scope and normalization):

- Names/duplicates: 32 unique crop-stage pairs (four stages for each C01-C08); repeated Kc across rice systems is species reference reuse, not independent evidence. No exact duplicates.

- Units/ranges: Kc dimensionless, stage positions fractions 0-1, water quantities mm with absent reference period/method. Known fractions are ordered and cover each crop except mustard, whose four stage fractions are absent. Kc values/ranges are nonnegative and bounded within observed 0.3-1.2, but plausible magnitude is not sufficient validation.

- Unsafe engine columns: all 96 min/typical/max water-requirement cells are N/A; 15 kc_value cells absent, eight development-stage min/max pairs absent. Seven other missing kc_value cells have a range, which is not an implicit average. Notes identify stage fractions as assumed and demand local ETo/calibration. Missing development Kc is not zero. Initial coefficient depends on management/wetting; point lookup alone is insufficient.

- Sources/scope: all cite FAO-56 chapter/table, year 1998 and local_calibration_required=yes; cultivar-specific/local numerical irrigation demand is not established. Proxy scope must be approved, particularly mustard and mungbean coefficients.

- Normalize: stage definitions, scalar/range/derived coefficient kinds, timing evidence, crop/species scope, irrigation system as management context rather than intrinsic crop attribute. Approve interpolation and water-balance method separately. Disposition B mapping; C method; D quantitative water/Commons blocker.

**Repeated property bundles:** compared `growth_stage`, `kc_value`, `kc_min`, `kc_max`: C01/initial, C02/initial, C03/initial; C01/development, C02/development, C03/development, C04/development, C05/development, C06/development, C07/development, C08/development; C01/mid_season, C02/mid_season, C03/mid_season, C04/mid_season; C01/late_season, C02/late_season, C03/late_season; C04/late_season, C06/late_season; C05/initial, C07/initial; C05/mid_season, C07/mid_season; C05/late_season, C07/late_season; C06/initial, C08/initial. Repetition is not authorization to delete records or pool cultivar evidence.


### 5. 5_crop_soil_requirements.csv

**Purpose:** Cultivar-labelled pH, texture, drainage, salinity and fertility requirements.

**Inventory:** 11 data records; 16 columns; zero inconsistent-width records; 0 exact duplicate rows. Candidate unique key: `crop_id`; duplicate keys: 0.

**Null conventions:** `N/A`: 7 cells; blank string: 22 cells. Counts below are per column. `0` means no missing cells, not a scientific zero.

| Column (all original columns) | Apparent value type | Missing cells / raw tokens | Observed range or category examples |
| --- | --- | --- | --- |
| `crop_id` | Identifier/string | 0 | 1, 2, 3, 4, 5 ... |
| `crop_name` | Category/text | 0 | mung_daal_bari_mung_6, sesame_bari_til_4, sunflower_hysun_33, maize_e_34_x_bil_211 ... |
| `ph_absolute_min` | Numeric | 0 | 4.3 to 5.5 |
| `ph_optimal_min` | Numeric | 0 | 5 to 6 |
| `ph_optimal_max` | Numeric | 0 | 6.2 to 7.5 |
| `ph_absolute_max` | Numeric | 0 | 8 to 9 |
| `preferred_texture` | Category/text | 0 | Loamy soil, Loamy Soil, Sandy Loam, Loamy soil, Sandy Loam, Loamy soil, silt_loam |
| `acceptable_textures` | Category/text | 1 (N/A=1) | Clay Loam, Loamy soil, silt_loam |
| `drainage_preference` | Category/text | 0 | Well drained, Poorly to Imperfectly  |
| `waterlogging_tolerance` | Category/text | 2 (N/A=2) | Low, Submergence Tolerant, Submergence Tolerant, High |
| `salinity_tolerance_class` | Category/text | 0 | Moderately Sensitive, Sensitive, Moderately Tolerant |
| `salinity_threshold_ece_ds_m` | Numeric | 3 (N/A=3) | 1.7 to 8 |
| `fertility_requirement` | Category/text | 0 | Medium, High |
| `notes` | Text/source/list | 9 (N/A=1; blank=8) | 2 distinct nonmissing values |
| `source_title` | Text/source/list | 7 (blank=7) | 3 distinct nonmissing values |
| `source_url` | Text/source/list | 7 (blank=7) | 4 distinct nonmissing values |

**File-specific findings (naming, units, conflicts, unsafe engine use, scope and normalization):

- Names/duplicates: 11 unique numeric crop IDs; four maize hybrids share the same numeric pH and salinity claims, four rice varieties share pH values. These are duplicated property claims across distinct cultivars, not duplicate cultivar records. Names are slugs with no mapping to master IDs; spelling Pinacle must be preserved for review.

- Units/ranges: ordered pH envelopes, populated absolute values within 4.3-9; these require source/method verification, not automatic rejection. Texture/drainage/fertility/tolerance are categorical prose. Trailing whitespace in drainage rows 9-12 (CSV record numbers) and URL record 2 needs trimmed normalized copies.

- Conflicts/unsafe columns: crop 1 salinity threshold 2.02 is explicitly an observation in file 7, not threshold. Rice crop 9 value 8 and crop 11 value 6 are unsupported as fitted yield thresholds; file 7 deliberately leaves them unknown. Maize 1.7 and sunflower 4.8 are species/other-hybrid references, not these cultivar calibrations. Withhold all conflicted and unsupported numeric salinity cutoffs. Do not borrow a populated source from an adjacent row.

- Sources/scope: seven rows (numeric IDs 4-7,9-11) have blank titles and URLs; populated citations include generic EcoCrop endpoint with no species ID, concatenated URLs, tracking params/trailing comma, and a Slideshare #8,%20faocrop fragment. Confidence/year/geographic applicability absent as dedicated columns. Generic pH under a named cultivar is an unreviewed transfer.

- Normalize: cultivar crosswalk, claim-specific source link and precision, textures/drainage vocabularies, measurement basis, geography and review status. Disposition B substantial; C threshold conflicts; D provenance.

**Missing `source_url` record locators:** 5 [4], 6 [5], 7 [6], 8 [7], 10 [9], 11 [10], 12 [11].

**Repeated property bundles:** compared `ph_absolute_min`, `ph_optimal_min`, `ph_optimal_max`, `ph_absolute_max`: 4, 5, 6, 7; 8, 9, 10, 11. Repetition is not authorization to delete records or pool cultivar evidence.


### 6. 6_crop_soil_health_effects.csv

**Purpose:** Qualitative soil-health effects and management-dependent rotation contributions.

**Inventory:** 11 data records; 20 columns; zero inconsistent-width records; 0 exact duplicate rows. Candidate unique key: `crop_id`; duplicate keys: 0.

**Null conventions:** `N/A`: 63 cells. Counts below are per column. `0` means no missing cells, not a scientific zero.

| Column (all original columns) | Apparent value type | Missing cells / raw tokens | Observed range or category examples |
| --- | --- | --- | --- |
| `crop_id` | Identifier/string | 0 | 1, 2, 3, 4, 5 ... |
| `crop_name` | Category/text | 0 | mung_daal_bari_mung_6, sesame_bari_til_4, sunflower_hysun_33, maize_e_34_x_bil_211 ... |
| `crop_family` | Category/text | 0 | Fabaceae, Pedaliaceae, Asteraceae, Poaceae |
| `nitrogen_fixing` | Boolean-like category | 0 | yes, no |
| `nitrogen_effect_category` | Category/text | 10 (N/A=10) | potential_n_input_via_symbiotic_fixation |
| `residue_quantity_category` | Undetermined (all missing) | 11 (N/A=11) | Expected type needs schema definition |
| `residue_quality_category` | Category/text | 2 (N/A=2) | nitrogen_rich_fast_decomposing, carbon_rich_high_CN, carbon_rich_high_CN_straw |
| `ground_cover_category` | Undetermined (all missing) | 11 (N/A=11) | Expected type needs schema definition |
| `erosion_protection_category` | Undetermined (all missing) | 11 (N/A=11) | Expected type needs schema definition |
| `root_depth_category` | Undetermined (all missing) | 11 (N/A=11) | Expected type needs schema definition |
| `root_structure_category` | Category/text | 0 | taproot_with_lateral_roots, taproot, fibrous_root_system |
| `organic_matter_contribution_category` | Category/text | 2 (N/A=2) | positive_if_residues_retained, positive_if_stover_retained, positive_if_straw_retained |
| `soil_structure_effect_category` | Category/text | 1 (N/A=1) | potential_improvement_if_residues_incorporated, potential_biopore_and_nutrient_recycling, potential_improvement_if_stover_retained, conditional_improvement_f... |
| `nutrient_demand_category` | Category/text | 3 (N/A=3) | high, substantial_NPK_requirements |
| `known_rotation_benefit` | Category/text | 0 | Legume diversification after rice; symbiotic N fixation and residue return may increase soil nutrient cycling, Non-cereal break crop; deeper nutrient uptake ... |
| `known_rotation_risk` | Category/text | 1 (N/A=1) | Nutrient export with seed/stover removal; residue retention and nutrient replacement matter, Potential allelopathic inhibition of subsequent direct-seeded ri... |
| `evidence_strength` | Category/text | 0 | medium, low |
| `notes` | Text/source/list | 0 | 5 distinct nonmissing values |
| `source_title` | Text/source/list | 0 | 5 distinct nonmissing values |
| `source_url` | Text/source/list | 0 | 5 distinct nonmissing values |

**File-specific findings (naming, units, conflicts, unsafe engine use, scope and normalization):

- Names/duplicates: same 11 numeric cultivar identities as files 5/7, not master IDs. Repeated species-level descriptions across maize/rice cultivars should be one scoped claim with many aliases/subjects only after review, not added as independent evidence. No full-row duplicates.

- Units/ranges: categorical text, booleans and evidence categories; there are no numeric N-fixation/SOC effect columns. legume/root/quality descriptors do not imply quantified benefit. Evidence strength is medium for mungbean and low for the other ten.

- Unsafe engine columns: nitrogen_effect_category missing in 10 rows; residue quantity, ground cover, erosion protection and root depth absent in all 11. Do not score unknown as low/zero or promote potential_if_residues_incorporated to guaranteed improvement. Farmer management and residue fate are missing inputs.

- Sources/scope: every row has multi-source title/URL text. Notes explicitly distinguish Polder 30 productivity from measured soil-health improvements and mention species/other-region evidence. Some evidence from US Midwest or other production systems is not locally calibrated cultivar data.

- Normalize: species/cultivar claim level, management conditions, controlled effect terms with retained qualifiers, many-to-many source links; do not assign numeric bonuses. Disposition A qualified explanations after review; B vocabularies; C transfer/scoring; D quantitative effects.

**Repeated property bundles:** compared `crop_family`, `nitrogen_fixing`, `residue_quality_category`, `organic_matter_contribution_category`: 4, 5, 6, 7; 8, 9, 10, 11. Repetition is not authorization to delete records or pool cultivar evidence.


### 7. 7_crop_salinity_response.csv

**Purpose:** Salinity tolerance references, field observations and limitations by cultivar-labelled crop.

**Inventory:** 11 data records; 14 columns; zero inconsistent-width records; 0 exact duplicate rows. Candidate unique key: `crop_id`; duplicate keys: 0.

**Null conventions:** `N/A`: 59 cells. Counts below are per column. `0` means no missing cells, not a scientific zero.

| Column (all original columns) | Apparent value type | Missing cells / raw tokens | Observed range or category examples |
| --- | --- | --- | --- |
| `crop_id` | Identifier/string | 0 | 1, 2, 3, 4, 5 ... |
| `crop_name` | Category/text | 0 | mung_daal_bari_mung_6, sesame_bari_til_4, sunflower_hysun_33, maize_e_34_x_bil_211 ... |
| `growth_stage` | Category/text | 0 | whole season (Polder 30 field observation), late seedling to maturity (reference threshold); germination/seedling (variety experiment), late seedling to matu... |
| `salinity_tolerance_class` | Category/text | 2 (N/A=2) | sensitive (species-level); BARI Mung-6 described as saline-tolerant in Bangladesh guidance, sensitive (FAO species-level), moderately_tolerant (FAO; species-... |
| `ece_threshold_ds_m` | Numeric | 6 (N/A=6) | 1.7 to 4.8 |
| `yield_loss_pct_per_ds_m` | Numeric | 6 (N/A=6) | 5.0 to 12 |
| `sensitive_stage` | Category/text | 10 (N/A=10) | vegetative growth (species-level evidence) |
| `germination_tolerance` | Category/text | 9 (N/A=9) | Varies by genotype; salinity screening at 7.5 dS/m reported for other sesame accessions, NOT BARI Til-4, HySun-33 germination tested under 4, 8, 12, 16 dS/m ... |
| `seedling_tolerance` | Category/text | 9 (N/A=9) | HySun-33 seedling growth significantly affected by salinity in Khulna University study; no ECe yield threshold from that test, Reported tolerance 12–14 dS/m ... |
| `vegetative_tolerance` | Category/text | 9 (N/A=9) | Salt-sensitive; impaired growth and seed production reported for mungbean (not BARI Mung-6-specific), Reported tolerance 6 dS/m throughout growth, including ... |
| `reproductive_tolerance` | Category/text | 8 (N/A=8) | Seed yield strongly reduced by salt treatments in mungbean experiments (not a field ECe threshold), Salinity affects flowering/harvest performance in sesame ... |
| `notes` | Text/source/list | 0 | 10 distinct nonmissing values |
| `source_title` | Text/source/list | 0 | 8 distinct nonmissing values |
| `source_url` | Text/source/list | 0 | 8 distinct nonmissing values |

**File-specific findings (naming, units, conflicts, unsafe engine use, scope and normalization):

- Names/duplicates: same 11 numeric cultivar identities; four maize rows repeat generic 1.7 threshold/12 slope, but notes say ear fresh weight, not hybrid-specific grain yield. Do not count repeated proxy numbers as four independent experiments. No full-row duplicates.

- Units/ranges: dS/m ECe for response thresholds, percent per dS/m for slope; stage tolerance, measured soil EC and solution exposure in notes are not convertible to that endpoint without method evidence. Numeric sunflower 4.8/5 and maize 1.7/12 are not intrinsically implausible; their unsafe attribution is the issue.

- Conflicts/unsafe columns: six threshold/slope pairs remain absent intentionally. Mungbean observation 2.02 contradicts file 5 threshold assignment; dhan54/dhan47 null fitted thresholds disagree with file 5's numeric labels. Notes with 8.7-11.4 or seedling 12-14 are observations/descriptors, not missing values to extract into yield-threshold fields. No source-derived domain/clamping/slope model approved for current varieties.

- Sources/scope: all titles/URLs present, but year/confidence/scope exist mostly in prose; sunflower slope from OTHER hybrids and Polder 30 observations with unspecified varieties cannot become cultivar-specific calibration. Source notes are essential, not disposable.

- Normalize: typed salinity evidence kind, EC basis, growth stage, cultivar vs proxy, yield endpoint and geographic applicability; claim-level threshold/slope review. Disposition A warnings/reference; B model semantics; C numeric eligibility; D locally applicable curves.

**Repeated property bundles:** compared `ece_threshold_ds_m`, `yield_loss_pct_per_ds_m`: 1, 2, 8, 9, 10, 11; 4, 5, 6, 7. Repetition is not authorization to delete records or pool cultivar evidence.


### 8. 8_crop_rotation_rules.csv

**Purpose:** Directional crop-sequence evidence for Polder 30 rice/dry-season systems.

**Inventory:** 42 data records; 27 columns; zero inconsistent-width records; 0 exact duplicate rows. Candidate unique key: `rule_id`; duplicate keys: 0.

**Null conventions:** `N/A`: 75 cells. Counts below are per column. `0` means no missing cells, not a scientific zero.

| Column (all original columns) | Apparent value type | Missing cells / raw tokens | Observed range or category examples |
| --- | --- | --- | --- |
| `rule_id` | Identifier/string | 0 | ROT007, ROT008, ROT009, ROT017, ROT018 ... |
| `previous_crop_id` | Identifier/string | 0 | mung_daal_bari_mung_6, sesame_bari_til_4, sunflower_hysun_33, maize_e_34_x_bil_211, maize_pinacle_3_x_bil_211 ... |
| `next_crop_id` | Identifier/string | 0 | rice_brri_dhan51, rice_brri_dhan54, rice_brri_dhan52, mung_daal_bari_mung_6, sesame_bari_til_4 ... |
| `previous_family` | Category/text | 0 | Fabaceae, Pedaliaceae, Asteraceae, Poaceae |
| `next_family` | Category/text | 0 | Poaceae, Fabaceae, Pedaliaceae, Asteraceae |
| `compatibility_class` | Category/text | 0 | acceptable |
| `reason_category` | Category/text | 0 | reverse_phase_of_local_cropping_system, documented_local_cropping_system, established_local_cropping_pattern |
| `reason_text` | Text/source/list | 0 | 8 distinct nonmissing values |
| `legume_bonus` | Category/text | 39 (N/A=39) | potential_residue_dependent |
| `nutrient_rotation_benefit` | Category/text | 36 (N/A=36) | potential_if_residues_incorporated, potential_if_legume_biomass_retained |
| `region_scope` | Category/text | 0 | Polder 30, Batiaghata, Khulna (system-level evidence; variety transfer not verified) |
| `notes` | Text/source/list | 0 | 8 distinct nonmissing values |
| `source_title` | Text/source/list | 0 | 4 distinct nonmissing values |
| `source_url` | Text/source/list | 0 | 4 distinct nonmissing values |
| `previous_crop_season` | Category/text | 0 | Rabi, T_Aman |
| `next_crop_season` | Category/text | 0 | T_Aman, Rabi |
| `same_crop_family` | Boolean-like category | 0 | false, true |
| `same_crop_species` | Boolean-like category | 0 | false |
| `family_rotation_rule` | Category/text | 0 | different_family_break, same_family_different_species |
| `seasonal_feasibility` | Category/text | 0 | feasible_at_system_level |
| `seasonal_feasibility_reason` | Category/text | 0 | T. Aman and dry-season crop comprise an observed local annual system, but exact planting/harvesting dates and field drainage must be checked. |
| `calendar_verification_required` | Boolean-like category | 0 | true |
| `rule_derivation` | Category/text | 0 | botanical_family_and_species_identity; seasonal_crop_category; existing_local_cropping_system_evidence |
| `evidence_scope` | Category/text | 0 | Polder 30 crop-species cropping system; exact named cultivar pair NOT experimentally validated |
| `evidence_type` | Category/text | 0 | local_multiyear_cropping_system, local_existing_pattern_with_observational_profitability |
| `local_yield_profitability_evidence` | Category/text | 0 | Rice–mungbean studied in Polder 30; productive improved system, though below rice–maize and rice–sunflower on overall yield; drought-year performance can be ... |
| `selection_limitation` | Category/text | 0 | Conditional on drainage, freshwater, salinity, season timing and climate risk; not a guaranteed high-yield or profitable result. |

**File-specific findings (naming, units, conflicts, unsafe engine use, scope and normalization):

- Names/duplicates: 42 unique rule IDs and unique directional previous/next pairs; ten unique cultivar slugs. Structure is 7 dry-season entries x 3 Aman varieties x 2 directions. Four maize hybrids and three rice varieties expand species-system evidence; these are not 42 independent trials. BRRI dhan47 has no pair evidence here.

- Units/ranges: category/boolean/text only; legume_bonus and nutrient_rotation_benefit are conditional strings or N/A, not numeric scores. All compatibility_class=acceptable and all seasonal_feasibility=feasible_at_system_level. 24 same-family pairs and 18 different-family pairs exist; all same-species flags false. No prohibited/negative examples or numerical penalties.

- Unsafe engine columns: calendar_verification_required=true for ALL 42; acceptable cannot bypass dates/salinity/freshwater/drainage/constraints. Absent pair is unknown, not prohibited or allowed. 21 reverse-phase relations are annual continuations, not separate experimentally verified directional treatments. Family diversity alone does not guarantee disease suppression.

- Sources/scope: all rows contain sources and explicit Polder 30 scope; 36 multiyear-system and six existing-pattern/observational evidence records. Named cultivar-pair transfer explicitly unverified. No duplicate evidence weighting from repeated citations.

- Normalize: species-system evidence vs proposed cultivar links, direction/year transition, conditional prerequisites, evidence records and optional reviewed soft effects. Disposition A scoped historical systems; B claim hierarchy; C pair activation; D calendar/negative-rule coverage.


### 9. 9_crop_stage_sensitivity.csv

**Purpose:** Crop-stage stress sensitivity, qualitative vulnerability and a few variety descriptors.

**Inventory:** 34 data records; 19 columns; zero inconsistent-width records; 0 exact duplicate rows. Candidate unique key: `crop_id`, `variety`, `stress_type`, `growth_stage`; duplicate keys: 0.

**Null conventions:** `N/A`: 223 cells. Counts below are per column. `0` means no missing cells, not a scientific zero.

| Column (all original columns) | Apparent value type | Missing cells / raw tokens | Observed range or category examples |
| --- | --- | --- | --- |
| `crop_id` | Identifier/string | 0 | aman_rice, aus_rice, boro_rice, wheat, maize ... |
| `crop_name` | Category/text | 0 | Aman rice, Aus rice, Boro rice, Wheat ... |
| `season` | Category/text | 15 (N/A=15) | aman, aus, boro, rabi |
| `variety` | Category/text | 31 (N/A=31) | BRRI_dhan67, BRRI_dhan83 |
| `stress_type` | Category/text | 0 | water_deficit, salinity, heat |
| `growth_stage` | Category/text | 7 (N/A=7) | head_development, flowering, grain_filling, stolonization ... |
| `response_type` | Category/text | 7 (N/A=7) | vulnerable, tolerant |
| `stage_sensitivity` | Category/text | 9 (N/A=9) | sensitive, moderate_tolerance |
| `crop_overall_drought_class` | Category/text | 17 (N/A=17) | high, low_medium, medium_high |
| `threshold_min` | Numeric | 32 (N/A=32) | 8 to 12 |
| `threshold_max` | Numeric | 32 (N/A=32) | 8 to 14 |
| `threshold_unit` | Category/text | 32 (N/A=32) | dS_per_m |
| `applicability` | Category/text | 0 | global, southern_saline_bangladesh, bangladesh_drought_prone, two_experimental_genotypes |
| `evidence_type` | Category/text | 0 | derived_species_proxy, direct, derived_pepper_proxy, missing ... |
| `source_title` | Text/source/list | 7 (N/A=7) | 5 distinct nonmissing values |
| `source_url` | Text/source/list | 7 (N/A=7) | 5 distinct nonmissing values |
| `source_year` | Integer year | 27 (N/A=27) | 2012 to 2022 |
| `confidence_level` | Category/text | 0 | medium, high, low |
| `notes` | Text/source/list | 0 | 9 distinct nonmissing values |

**File-specific findings (naming, units, conflicts, unsafe engine use, scope and normalization):

- Names/duplicates: 34 rows across 17 species/production-system slugs; repeated crop rows refer to different stress/stage/variety claims. Composite crop+variety+stress+stage keys are unique. No full-row duplicates. Master lacks eleven of the seventeen listed operational crop entries (only the three rice systems, maize, mungbean and mustard match); varieties dhan67/dhan83 need distinct IDs.

- Units/ranges: 32/34 threshold pairs/units missing; two dhan67 salinity values are 12-14 (seedling) and 8-8 (vegetative-to-reproductive) dS_per_m. They are descriptors, not heat thresholds or fitted salinity yield-loss boundaries. Missing stage dates/fractions prevent mapping flowering/head_development onto calendar days.

- Unsafe engine columns: stage_sensitivity and crop_overall_drought_class have different semantics; high overall drought class is ambiguous, not automatically high tolerance. Seven missing-evidence rows lack stage/response/source. Maize notes explicitly prohibit treating experimental 35C as universal threshold. No exposure duration/response or validated numerical risk mapping.

- Sources/scope: seven rows lack title/URL; 27 years missing. Direct, rice/pepper species proxies, experiments and variety descriptors must remain separate. No numeric heat-response function exists here.

- Normalize: slugs, stress/stage enums, cultivar mapping, source scope, class direction, units/methods and timing links. Disposition A qualified stage notes; B semantic typing; C response interpretation; D stage-dated numerical stress.

**Missing `source_url` record locators:** 19 [mustard, N/A, water_deficit, N/A], 20 [mung_bean, N/A, water_deficit, N/A], 21 [lentil, N/A, water_deficit, N/A], 22 [chickpea, N/A, water_deficit, N/A], 23 [jute, N/A, water_deficit, N/A], 24 [sesame, N/A, water_deficit, N/A], 25 [garlic, N/A, water_deficit, N/A].


### 10. 10_bangladesh_soil_reference.csv

**Purpose:** Historical Bangladesh AEZ catalogue plus a few limited soil-sample observations.

**Inventory:** 30 data records; 26 columns; zero inconsistent-width records; 0 exact duplicate rows. Candidate unique key: `aez_id`; duplicate keys: 0.

**Null conventions:** `N/A`: 456 cells. Counts below are per column. `0` means no missing cells, not a scientific zero.

| Column (all original columns) | Apparent value type | Missing cells / raw tokens | Observed range or category examples |
| --- | --- | --- | --- |
| `aez_id` | Identifier/string | 0 | AEZ01, AEZ02, AEZ03, AEZ04, AEZ05 ... |
| `aez_name` | Category/text | 0 | Old Himalayan Piedmont Plain, Active Tista Floodplain, Tista Meander Floodplain, Karatoya-Bangali Floodplain ... |
| `country` | Category/text | 0 | Bangladesh |
| `region_area_ha` | Numeric | 0 | 804 to 1817172 |
| `region_area_pct` | Numeric | 0 | 0.01 to 12.54 |
| `regional_soil_type` | Undetermined (all missing) | 30 (N/A=30) | Expected type needs schema definition |
| `regional_soil_texture` | Undetermined (all missing) | 30 (N/A=30) | Expected type needs schema definition |
| `regional_soil_ph_min` | Undetermined (all missing) | 30 (N/A=30) | Expected type needs schema definition |
| `regional_soil_ph_max` | Undetermined (all missing) | 30 (N/A=30) | Expected type needs schema definition |
| `regional_salinity_ece_dsm` | Undetermined (all missing) | 30 (N/A=30) | Expected type needs schema definition |
| `regional_drainage` | Undetermined (all missing) | 30 (N/A=30) | Expected type needs schema definition |
| `observed_ph_min` | Numeric | 28 (N/A=28) | 3.81 to 3.96 |
| `observed_ph_max` | Numeric | 28 (N/A=28) | 4.78 to 5.11 |
| `observed_soil_texture` | Category/text | 29 (N/A=29) | medium |
| `observed_salinity_status` | Category/text | 29 (N/A=29) | non_saline |
| `observed_sample_n` | Numeric | 27 (N/A=27) | 10 to 25 |
| `observation_location` | Category/text | 27 (N/A=27) | five_soil_series, Nalitabari_Sherpur, Fulbaria_Mymensingh |
| `observation_scope` | Category/text | 27 (N/A=27) | site_sample_only |
| `source_title` | Text/source/list | 0 | 1 distinct nonmissing values |
| `source_url` | Text/source/list | 0 | 1 distinct nonmissing values |
| `source_year` | Integer year | 0 | 1988 to 1988 |
| `soil_source_title` | Text/source/list | 27 (N/A=27) | 2 distinct nonmissing values |
| `soil_source_url` | Text/source/list | 27 (N/A=27) | 2 distinct nonmissing values |
| `soil_source_year` | Integer year | 27 (N/A=27) | 2016 to 2021 |
| `confidence_level` | Category/text | 0 | high |
| `notes` | Text/source/list | 0 | 3 distinct nonmissing values |

**File-specific findings (naming, units, conflicts, unsafe engine use, scope and normalization):

- Names/duplicates: 30 unique AEZ IDs/names, no duplicates. Not a crop table. AEZxx identity differs from calendar numeric 13. Lookup needs approved geography; no geometries/coordinates supplied.

- Units/ranges: regional area ha and percent refer to historical region inventory, not field area; pH dimensionless and sample size a count. Populated observed pH ranges 3.81-4.78 at Nalitabari and 3.96-5.11 at Fulbaria are acidic observations, not implausible errors to erase. Texture medium is broad prose, not a validated texture class.

- Unsafe engine columns: all six regional soil property columns are N/A for all 30. Only AEZ17,22,28 have observation context; AEZ17 texture/salinity/sample count but no pH. Never fill regional defaults using observed columns. A high confidence label can apply to a historical AEZ source without implying known soil chemistry.

- Sources/scope: base source present for every row, dated 1988. Soil source title/URL/year absent for 27, consistent with absent site observations. Three observed records are site_sample_only, not representative AEZ-wide distributions. No sampling date/depth/test medium or soil prediction surface.

- Normalize: AEZ region relation, separate catalog/observation source claims, sample sites, historical metadata and missing geometry. Disposition A reference catalogue; B relation split; C observation use; D regional soil fallback absent.

**Missing `soil_source_url` record locators:** 2 [AEZ01], 3 [AEZ02], 4 [AEZ03], 5 [AEZ04], 6 [AEZ05], 7 [AEZ06], 8 [AEZ07], 9 [AEZ08], 10 [AEZ09], 11 [AEZ10], 12 [AEZ11], 13 [AEZ12], 14 [AEZ13], 15 [AEZ14], 16 [AEZ15], 17 [AEZ16], 19 [AEZ18], 20 [AEZ19], 21 [AEZ20], 22 [AEZ21], 24 [AEZ23], 25 [AEZ24], 26 [AEZ25], 27 [AEZ26], 28 [AEZ27], 30 [AEZ29], 31 [AEZ30].


### 11. 11_bangladesh_crop_suitability_reference.csv

**Purpose:** Bangladesh crop-zoning source catalogue and variety-specific recommended-area records.

**Inventory:** 37 data records; 18 columns; zero inconsistent-width records; 0 exact duplicate rows. Candidate unique key: `crop_id`, `variety`, `region_name`; duplicate keys: 0.

**Null conventions:** `N/A`: 149 cells. Counts below are per column. `0` means no missing cells, not a scientific zero.

| Column (all original columns) | Apparent value type | Missing cells / raw tokens | Observed range or category examples |
| --- | --- | --- | --- |
| `crop_id` | Identifier/string | 0 | aus_rice, aman_rice, boro_rice, wheat, maize ... |
| `crop_name` | Category/text | 0 | Aus rice, Aman rice, Boro rice, Wheat ... |
| `season` | Category/text | 7 (N/A=7) | aus, aman, boro, rabi |
| `variety` | Category/text | 17 (N/A=17) | BRRI_dhan73, BRRI_dhan78, BRRI_dhan67, BRRI_dhan97 ... |
| `region_name` | Category/text | 0 | Bangladesh, southern_saline_tidal, southern_saline, southern_nonsaline_tidal ... |
| `region_type` | Category/text | 0 | national, descriptive, district_or_region |
| `land_type` | Category/text | 17 (N/A=17) | highland_medium_highland, irrigated_highland_medium_highland, irrigated_highland_medium_highland_medium_lowland, highland_medium_highland_medium_lowland ... |
| `stress_context` | Category/text | 17 (N/A=17) | salinity, salinity_submergence, non_saline_tidal, excluding_drought ... |
| `record_type` | Category/text | 0 | barc_crop_suitability_catalog, source_gap, brri_variety_suitable_area |
| `regional_fit` | Category/text | 17 (N/A=17) | recommended |
| `barc_suitability_class` | Undetermined (all missing) | 37 (N/A=37) | Expected type needs schema definition |
| `assessment_scope` | Category/text | 1 (N/A=1) | national_maps, variety_area |
| `dataset_status` | Category/text | 0 | classes_not_extracted, not_verified, variety_specific |
| `source_title` | Text/source/list | 0 | 17 distinct nonmissing values |
| `source_url` | Text/source/list | 0 | 17 distinct nonmissing values |
| `source_year` | Integer year | 36 (N/A=36) | 2013 to 2013 |
| `confidence_level` | Category/text | 0 | high, low |
| `notes` | Text/source/list | 0 | 5 distinct nonmissing values |

**File-specific findings (naming, units, conflicts, unsafe engine use, scope and normalization):

- Names/duplicates: 37 rows across 17 operational slugs, no exact or crop+variety+region composite duplicates. Repeated BRRI dhan83 district examples and dhan93 division examples are multiple scopes, not repeated independent validation. Many slugs/varieties absent from master.

- Units/ranges: categories/strings, not numeric suitability scores. All 37 barc_suitability_class values missing. Dates are bibliographic only. recommended is a source-scoped area descriptor, not evidence of optimum score for an entered field.

- Unsafe engine columns: first 17 catalogue rows do not supply extracted local map classes; remaining 20 variety-area records cannot turn national map existence into field suitability. assessment_scope and dataset_status must control use, not confidence alone. Region labels include broad exclusions and example areas rather than executable geometry.

- Sources/scope: all source titles/URLs populated, only one year known. Class catalogue, not_verified context and variety_specific information have different validity; preserve variety/season and land/stress qualifiers. Do not apply a saline-coastal recommendation to all Bangladesh rice.

- Normalize: crop/cultivar IDs, region sets and exclusions, recommendation type, map availability separate from class observation. Disposition A source index/qualified variety area text; B geography; C transfer; D extracted suitability classes.


### 12. 12_farmer_constraint_options.csv

**Purpose:** Potential farmer inputs, hard-constraint definitions, labels and requirements.

**Inventory:** 30 data records; 23 columns; zero inconsistent-width records; 0 exact duplicate rows. Candidate unique key: `constraint_id`; duplicate keys: 0.

**Null conventions:** blank string: 93 cells. Counts below are per column. `0` means no missing cells, not a scientific zero.

| Column (all original columns) | Apparent value type | Missing cells / raw tokens | Observed range or category examples |
| --- | --- | --- | --- |
| `constraint_id` | Identifier/string | 0 | FC001, FC002, FC003, FC004, FC005 ... |
| `category` | Category/text | 0 | economic, water, calendar, crop_choice ... |
| `input_key` | Category/text | 0 | max_budget_per_ha, max_irrigation_m3_ha, weekly_irrigation_capacity_m3, rainfed_only ... |
| `input_type` | Category/text | 0 | nonnegative_number, boolean, date_range, text ... |
| `allowed_values` | Category/text | 0 | farmer_defined, true\|false, crop_master_ids, harvester\|thresher\|transplanter\|tractor\|pump\|none\|other |
| `default_value` | Boolean-like category | 23 (blank=23) | FALSE |
| `constraint_mode` | Category/text | 0 | hard_if_enabled, hard_if_verified |
| `engine_rule` | Text/source/list | 0 | 30 distinct nonmissing values |
| `required_data` | Text/source/list | 0 | 30 distinct nonmissing values |
| `evidence_type` | Category/text | 0 | design_option |
| `geographic_applicability` | Category/text | 0 | global, Bangladesh pilot; globally extensible, haor region; Bangladesh, Puthia; Rajshahi; Bangladesh ... |
| `source_title` | Text/source/list | 0 | 10 distinct nonmissing values |
| `source_url` | Text/source/list | 5 (blank=5) | 9 distinct nonmissing values |
| `source_year` | Integer year | 1 (blank=1) | 1996 to 2026 |
| `confidence_level` | Category/text | 0 | medium |
| `notes` | Text/source/list | 0 | 30 distinct nonmissing values |
| `constraint_name_en` | Category/text | 0 | Maximum seasonal input budget, Maximum seasonal irrigation allocation, Maximum weekly irrigation supply, No irrigation available ... |
| `constraint_name_bn` | Category/text | 0 | সর্বোচ্চ মৌসুমি উপকরণ ব্যয়ের সীমা, সর্বোচ্চ মৌসুমি সেচের পানি বরাদ্দ, সর্বোচ্চ সাপ্তাহিক সেচের পানি সরবরাহ, সেচের পানি পাওয়া যায় না ... |
| `unit` | Category/text | 13 (blank=13) | BDT/ha, m3/ha/season, m3/week, date_range ... |
| `minimum_value` | Numeric | 21 (blank=21) | 0 to 1 |
| `maximum_value` | Undetermined (all missing) | 30 (blank=30) | Expected type needs schema definition |
| `required` | Boolean-like category | 0 | false |
| `description` | Text/source/list | 0 | 30 distinct nonmissing values |

**File-specific findings (naming, units, conflicts, unsafe engine use, scope and normalization):

- Names/duplicates: 30 unique constraint_id and input_key records; no duplicates; crop_master_ids placeholders need canonical IDs. Five internal-spec references intentionally have blank public URLs (FC003,006,007,011,016).

- Units/ranges: numbers, booleans, dates, date ranges/lists, text and crop-ID lists mixed by declared input_type. Six nonnegative_number, two positive_integer, one nonnegative_integer and one unrestricted number definitions exist. All max limits blank intentionally; do not fabricate maxima. BDT/ha lacks explicit period on some budget/margin fields. kg fertilizer material != kg nutrient; m3/week group capacity != m3/ha/season.

- Unsafe engine columns: engine_rule is prose, not executable rule code. Budget/labor/machinery/market/pesticide constraints need missing support datasets. soil_ece_dsm is measured site data, not farmer-chosen physiological threshold. allow_relay_cropping=false correctly disables permission, despite generic note saying no restriction unless true; review enabled/disabled semantics per field. credit_unavailable=false does not prove available credit.

- Sources/scope: all source titles present, 25 URLs external; design_option evidence across all rows. General cited decision-making frameworks do not prove numerical crop limits. Most defaults intentionally empty; seven FALSE defaults are UI choices.

- Normalize: parser registry and typed defaults, unit/time scope, controlled options split on |, internal vs scientific sources, implementation binding and missing-data handling. Add explicit max-change constraint/history comparison required by product (not present as a dedicated input_key). Disposition A form requirements; B types; C meaning; D unsupported operational evaluators.

**Missing `source_url` record locators:** 4 [FC003], 7 [FC006], 8 [FC007], 12 [FC011], 17 [FC016].


### 13. 13_farmer_priority_options.csv

**Purpose:** Potential farmer objective metrics and bilingual priority labels.

**Inventory:** 21 data records; 21 columns; zero inconsistent-width records; 0 exact duplicate rows. Candidate unique key: `priority_id`; duplicate keys: 0.

**Null conventions:** No blank or recognized null-token cells. Counts below are per column. `0` means no missing cells, not a scientific zero.

| Column (all original columns) | Apparent value type | Missing cells / raw tokens | Observed range or category examples |
| --- | --- | --- | --- |
| `priority_id` | Identifier/string | 0 | FP001, FP003, FP004, FP005, FP006 ... |
| `category` | Category/text | 0 | water, risk, soil, economic ... |
| `objective_direction` | Category/text | 0 | minimize, maximize |
| `optimization_metric` | Category/text | 0 | gross_irrigation_requirement, stage_specific_water_deficit_exposure, stage_specific_heat_exposure, harvest_overlap_with_flood_risk_window ... |
| `unit` | Category/text | 0 | m3/ha, qualitative, days, count ... |
| `weight_policy` | Category/text | 0 | farmer_configured |
| `metric_status` | Category/text | 0 | requires_local_or_engine_data, Historical risk is not a real-time flood prediction., Requires farmer soil test or geographically appropriate measured ECe; do... |
| `required_data` | Text/source/list | 0 | 21 distinct nonmissing values |
| `evidence_type` | Category/text | 0 | priority_design |
| `geographic_applicability` | Category/text | 0 | global, haor region; Bangladesh, Amtali; Barguna; Bangladesh, coastal Bangladesh ... |
| `source_title` | Text/source/list | 0 | 11 distinct nonmissing values |
| `source_url` | Text/source/list | 0 | 11 distinct nonmissing values |
| `source_year` | Integer year | 0 | 1996 to 2026 |
| `confidence_level` | Category/text | 0 | medium |
| `notes` | Text/source/list | 0 | 4 distinct nonmissing values |
| `priority_name_en` | Category/text | 0 | Conserve irrigation water, Reduce drought sensitivity, Avoid heat-sensitive planting windows, Reduce flood harvest exposure ... |
| `priority_name_bn` | Category/text | 0 | সেচের পানি সাশ্রয়, খরার প্রতি সংবেদনশীলতা কমানো, তাপ-সংবেদনশীল সময়ে রোপণ এড়ানো, বন্যার সময় ফসল কাটার ঝুঁকি কমানো ... |
| `description` | Text/source/list | 0 | 21 distinct nonmissing values |
| `default_weight` | Numeric | 0 | 1 to 1 |
| `minimum_weight` | Numeric | 0 | 0 to 0 |
| `maximum_weight` | Numeric | 0 | 1 to 1 |

**File-specific findings (naming, units, conflicts, unsafe engine use, scope and normalization):

- Names/duplicates: 21 unique priority IDs and optimization metrics; FP002 absent is not a duplicate/error by itself. All default_weight=1, min=0, max=1; unnormalized equal relative defaults not independent allocations of 100%.

- Units/ranges: count/qualitative/percent/money/yield/water/labor with different denominators. Water FP001 m3/ha omits time period; FP020 m3/year whole farm vs per-hectare demand and FP015 person-days/week lacking area basis require contracts. objective_direction maximize/minimize differs from numeric value; do not coerce categories to scores.

- Unsafe engine columns: metric_status mixes requires_local_or_engine_data with 12 explanatory warnings. These sentences are not ready-made enum states; derive approved status separately while preserving caveat text. More cropping intensity or legumes do not prove soil benefits. Costs, yields, markets, variance, groundwater, rice-equivalent-yield and numerical thresholds lack complete inputs.

- Sources/scope: all titles/URLs present; entries describe priority_design, not validated scoring weights. General citations support relevance, not selected default values or a scoring formula. Retain source/date comments without assigning invented metadata.

- Normalize: five product-priority grouping, metric dependency/availability, units and period, warning vs status, relative weights and explicit all-zero policy. Do not double count correlated dimensions such as legume count plus soil-family count without approved rubric. Disposition A objective definitions; B schema; C normalization/scoring; D quantitative data; E advanced metrics.


### 14. 14_rotation_case_studies.csv

**Purpose:** Bangladesh published rotation/system trials, landscape scenarios and adaptation survey references.

**Inventory:** 16 data records; 42 columns; zero inconsistent-width records; 0 exact duplicate rows. Candidate unique key: `case_id`; duplicate keys: 0.

**Null conventions:** blank string: 120 cells. Counts below are per column. `0` means no missing cells, not a scientific zero.

| Column (all original columns) | Apparent value type | Missing cells / raw tokens | Observed range or category examples |
| --- | --- | --- | --- |
| `case_id` | Identifier/string | 0 | RC001, RC002, RC003, RC004, RC005 ... |
| `country` | Category/text | 0 | Bangladesh |
| `district` | Category/text | 0 | Barguna, Bogura, Rajshahi, Rangpur ... |
| `study_location` | Category/text | 0 | Amtali, Gabtali, Pali, Durgapur (MLT site: Puthia, Rajshahi), Regional Agricultural Research Station, Rangpur ... |
| `agroecological_context` | Category/text | 0 | salinity-affected coast, Karatoa-Bangali Floodplain; AEZ-4, High Ganges River Floodplain; AEZ-11, Tista Meander Floodplain; AEZ-3 ... |
| `case_category` | Category/text | 0 | coastal_salinity, floodplain_diversification, intensification, groundwater_pressure ... |
| `evidence_design` | Category/text | 0 | field_trial, hydrological_model, farmer_adaptation_survey |
| `unit_of_analysis` | Category/text | 0 | plot, landscape, farm |
| `candidate_sequence` | Category/text | 0 | Mustard > T. Aus rice > T. Aman rice, Sunflower > T. Aus rice > T. Aman rice, Maize > T. Aus rice > T. Aman rice, Wheat > Mungbean > T. Aman rice ... |
| `crop_order_basis` | Category/text | 0 | seasonal_sequence, area_allocation_scenario, variety_strategy_with_same_rotation |
| `study_period` | Category/text | 0 | 2016-2018, 2021-2022, 2014-2016, 2021-2023 ... |
| `dominant_hazard` | Category/text | 0 | seasonal soil salinity, high rice-based input dependence, limited field time, seasonal land availability ... |
| `reported_metric` | Category/text | 0 | marginal_benefit_cost_ratio, rice_equivalent_yield_gain, labor_employment, land_use_efficiency ... |
| `reported_value` | Numeric | 0 | 0.83 to 354 |
| `reported_unit` | Category/text | 0 | ratio, percent, person_days_per_year, t/ha |
| `validation_status` | Category/text | 0 | documented_in_source |
| `nasa_reanalysis_status` | Category/text | 0 | not_performed |
| `nasa_data_to_fetch` | Category/text | 0 | NASA_POWER_temp_precip;GPM_IMERG_precip;SMAP_soil_moisture |
| `missing_data` | Category/text | 0 | field soil; local prices; NASA climate at parcel level, parcel-level variety and irrigation supply; aquifer model validation; NASA climate, full farm-level c... |
| `geographic_applicability` | Category/text | 0 | Amtali; Barguna; Bangladesh, Gabtali; Bogura; Bangladesh, Puthia; Rajshahi; Bangladesh, Rangpur; Bangladesh ... |
| `source_title` | Text/source/list | 0 | 6 distinct nonmissing values |
| `source_url` | Text/source/list | 0 | 6 distinct nonmissing values |
| `source_year` | Integer year | 0 | 2018 to 2026 |
| `confidence_level` | Category/text | 0 | high, medium |
| `notes` | Text/source/list | 0 | 16 distinct nonmissing values |
| `case_name` | Category/text | 0 | Amtali coastal mustard-Aus-Aman field trial, Amtali coastal sunflower-Aus-Aman field trial, Amtali coastal maize-Aus-Aman field trial, Amtali coastal wheat-m... |
| `division` | Category/text | 0 | Barishal, Rajshahi, Rangpur, Sylhet |
| `upazila` | Category/text | 4 (blank=4) | Amtali, Gabtali, Puthia, Nachol ... |
| `latitude` | Undetermined (all missing) | 16 (blank=16) | Expected type needs schema definition |
| `longitude` | Undetermined (all missing) | 16 (blank=16) | Expected type needs schema definition |
| `current_rotation` | Category/text | 0 | Fallow > Fallow > T. Aman rice, T. Aman rice > Fallow > Boro rice, Mustard > Onion > T. Aman rice, Boro rice > Fallow > T. Aman rice ... |
| `previous_crop_1` | Undetermined (all missing) | 16 (blank=16) | Expected type needs schema definition |
| `previous_crop_2` | Undetermined (all missing) | 16 (blank=16) | Expected type needs schema definition |
| `soil_description` | Text/source/list | 0 | 6 distinct nonmissing values |
| `irrigation_context` | Category/text | 9 (blank=9) | Water-management field trial; farm irrigation limit not provided, Groundwater-dependent Boro cultivation; landscape model scenario |
| `salinity_context` | Category/text | 12 (blank=12) | Seasonal coastal soil salinity risk; field ECe not provided |
| `flood_context` | Category/text | 15 (blank=15) | Early flash-flood hazard; short-duration Boro adaptation survey |
| `farmer_constraints` | Category/text | 0 | irrigation availability;crop windows, irrigation availability;seed availability, soil ECe;crop windows, crop windows;labor availability ... |
| `farmer_priorities` | Category/text | 0 | profitability;cropping intensity, profitability;water efficiency, crop diversity;legumes, cropping intensity;legumes ... |
| `expected_agronomic_patterns` | Category/text | 0 | Diversified pattern trialed; study finds CP1-CP3 improved system productivity and profitability relative to one-crop baseline., Highest reported performance ... |
| `expert_comments` | Undetermined (all missing) | 16 (blank=16) | Expected type needs schema definition |
| `interview_or_published_source` | Category/text | 0 | published_study, published_survey |

**File-specific findings (naming, units, conflicts, unsafe engine use, scope and normalization):

- Names/duplicates: 16 unique case IDs (RC001-RC015 and RC018); gaps RC016/017 do not establish missing research records. Same location/source with different treatments is legitimate. Sequences use > and /, common names and varieties, fallow, landscape replacement text and relay overlap; parse them as activities, not a flat crop list. Case-only species lack master profiles.

- Units/ranges: BCR vs marginal BCR distinct; percentages mean gains, occupancy, adoption or area replacement; 42.55 t/ha is price-weighted rice-equivalent yield, not physical rice yield. Labor 354 person_days_per_year lacks explicit area denominator here. Values are not automatically implausible when endpoint retained. Do not compare all reported_value cells on one scale.

- Unsafe engine columns: no expected rank/score, full field input or NASA result. NASA reanalysis not_performed for all 16. All coordinates/history fields absent, so NASA cannot be fetched at an invented parcel. current_rotation text is source context, not a fully entered present-day farm. RC007/008/012 include overlap, RC013-015 are landscape models, RC018 survey adoption is not yield validation.

- Sources/scope: all titles/URLs present; documented_in_source is author-supplied status, not our universal validation. 12 plot-level trials, three landscape model cases and one farm survey. No trial transfer from Rangpur/Gabtali/Haor to all Bangladesh. RC001-004 abstract independently spot-checked; full methods not extracted.

- Normalize: activity sequence/overlap, outcome metric and baseline/year/unit, design/scale, site certainty and local context. Disposition A references; B typed cases; C endpoint/method review; D reproducible validation inputs; E landscape/complex relay activation.


### 15. 15_sources.csv

**Purpose:** Source registry consolidating URLs and references used by research records.

**Inventory:** 74 data records; 17 columns; zero inconsistent-width records; 0 exact duplicate rows. Candidate unique key: `source_id`; duplicate keys: 0.

**Null conventions:** `N/A`: 295 cells. Counts below are per column. `0` means no missing cells, not a scientific zero.

| Column (all original columns) | Apparent value type | Missing cells / raw tokens | Observed range or category examples |
| --- | --- | --- | --- |
| `source_id` | Identifier/string | 0 | SRC001, SRC002, SRC003, SRC004, SRC005 ... |
| `source_type` | Category/text | 0 | FAO, government, dataset, research_paper ... |
| `title` | Text/source/list | 0 | 65 distinct nonmissing values |
| `authors` | Undetermined (all missing) | 74 (N/A=74) | Expected type needs schema definition |
| `organization` | Category/text | 30 (N/A=30) | Food and Agriculture Organization of the United Nations, Bangladesh Agricultural Research Council, CGIAR/CCAFS, Indian Council of Agricultural Research ... |
| `year` | Integer year | 52 (N/A=52) | 1988 to 2026 |
| `journal_or_publisher` | Category/text | 30 (N/A=30) | Food and Agriculture Organization of the United Nations, Bangladesh Agricultural Research Council, CGIAR/CCAFS, Indian Council of Agricultural Research ... |
| `doi` | Category/text | 57 (N/A=57) | 10.1016/B978-0-323-85195-4.00018-4, 10.1016/j.agee.2016.06.032, 10.1016/j.eja.2020.126130, 10.1016/j.fcr.2022.108763 ... |
| `url` | Text/source/list | 0 | 74 distinct nonmissing values |
| `access_date` | Date string | 0 | 2026-10-27 |
| `used_for` | Category/text | 0 | 9crop_stage_sensitivity.csv, 10bangladesh_soil_reference.csv, 11bangladesh_crop_suitability_reference(4).csv, 13farmer_priority_options_merged.csv ... |
| `crops_covered` | Mixed numeric/text | 19 (N/A=19) | maize, aman_rice \| aus_rice \| boro_rice \| chickpea \| chili \| garlic \| groundnut \| jute \| lentil \| maize \| mung_bean \| mustard \| onion \| potato \| sugarcane \| ... |
| `region_covered` | Category/text | 33 (N/A=33) | five_soil_series, Bangladesh, Chapainawabganj \| Chapainawabganj and Naogaon \| Nachol \| Nachol and Niamatpur, Sunamganj \| Tahirpur and Bishwambharpur (4 surve... |
| `peer_reviewed` | Category/text | 0 | unverified, yes |
| `official_government_source` | Boolean-like category | 0 | no, yes |
| `primary_source` | Category/text | 0 | unverified, yes |
| `notes` | Text/source/list | 0 | 28 distinct nonmissing values |

**File-specific findings (naming, units, conflicts, unsafe engine use, scope and normalization):

- Names/duplicates: 74 unique source IDs and exact URLs; no exact duplicates. SRC017 and SRC028 have identical MODFLOW title and likely one work via DOI/publisher, pending verification. Generic titles repeat for distinct EcoCrop pages and different linked works: not safe to deduplicate by title. Source names with author/year in title are not structured author/year fields.

- Units/ranges: identifiers/categories and access-date/year metadata, no agronomic numeric values. A publication year in a URL/DOI/title is not an authorized fill for missing year. access_date is a supplied metadata assertion, not proof the audit fetched every URL.

- Unsafe engine columns: peer_reviewed/primary_source/official_government_source are categorical assertions; primary_source=yes does not approve extracted facts. Some publisher/DOI/government/aggregator/secondary-host URLs have different evidence roles. Do not execute or auto-trust links or infer source validity from domain alone.

- Missing/source quality: all authors N/A; 52 years N/A; 30 organization/publisher values N/A; 57 DOI values missing (many legitimate non-DOI sources). Source URLs/title all present, but generic EcoCrop endpoint lacks species query, Slideshare fragment malformed, ResearchGate and AGRIS need original work tracing. No exact fact-level source locator field. used_for has historical filenames and crops_covered mixes identity schemes. No full link-resolution or 74-publication scientific review performed.

- Normalize: publication vs URL location, preserve DOI/query IDs, reviewed duplicate-work aliases, original filename/row references replaced by explicit raw-record links, verified access and review state distinct from asserted status. Disposition A source pointers; B citation structure; C verification; D locators/metadata.


## Source-file integrity manifest

SHA-256 values identify the exact CSV bytes audited. Recomputed after documentation work to verify no research CSV changed.

| CSV | SHA-256 |
| --- | --- |
| 1_crops_master.csv | `5036e1713ee96a959ea1018677d263156cd7fc3927f0114872be1ae733e22b98` |
| 2_crop_calendar.csv | `8a8bba445401eb455a247ab6402ca3a4fcd109f6b771031d4dce71e2f6367747` |
| 3_crop_climate_requirements.csv | `31f172ad4151e5e0685639dc85d78e27deef11056a74bc3e50e6ccacf0a126fc` |
| 4_crop_water_requirements.csv | `9d88a8ae4874f707a07ff44da4a2fd770ac84d178e58dbbd19de35af03c3ffe8` |
| 5_crop_soil_requirements.csv | `1add4e1949166be2cc37e61fdee8a93c7dcfe1ea2c37bca589f8a3513b7a965f` |
| 6_crop_soil_health_effects.csv | `8cff1cc397f776deb904b84f0399c8429519187d762ed6780d4a014af9885895` |
| 7_crop_salinity_response.csv | `79278d81c38cf7538226181d36be3c07b30fe357197bd3438d97f867fda08175` |
| 8_crop_rotation_rules.csv | `866d0b088cbb5fdfda78f4a8e9177f6585929b5a30d8bf54bd26f11ecf991e28` |
| 9_crop_stage_sensitivity.csv | `ff4346219ebf4a45339c076266d0172927ca969599643c3e86a5df43c606a657` |
| 10_bangladesh_soil_reference.csv | `c140ef21784a194cde6d6c7adbc2c922eb475447ed3be91539e6cd807637c02d` |
| 11_bangladesh_crop_suitability_reference.csv | `8a4f223bf054d1bc9f150809037d00fde00bae770f247df13fd28f756159f6f3` |
| 12_farmer_constraint_options.csv | `f070d491812409db04ab5150e809ee8d276ca1f29edd3c8db641a724b8d2357f` |
| 13_farmer_priority_options.csv | `1732a2994c7b06caad8e0c7a72451e1b02dd959f399e3eeb4fed3e51f1cc93af` |
| 14_rotation_case_studies.csv | `6a26bd9473d85c080c110d04d8b288b8073df88e8a9eb006ee0f0125e3ddfd47` |
| 15_sources.csv | `e5f11b974ced9a279065037d869dad563e2eb8cebed2428869aac5e80f189f4a` |

## Audit limitations and verification

Every cell was parsed for structural/type/null/duplicate diagnostics. Semantic review inspected the property groups, calendars, claim qualifiers, source conventions and cross-file conflicts described above. No scientific value has been invented or replaced. Zero malformed ranges under basic ordering checks does not validate biology. No importer, database migration or application test was run because this request authorizes an audit only. Citation verification is limited to the three linked external spot checks, not a systematic review of every source. CSV readiness/asserted confidence flags are recorded assertions, not independent validation.
