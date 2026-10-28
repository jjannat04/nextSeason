# Research values needing human review

**Prototype strategy supersedes the strict gate below.** Aman, maize and sunflower now participate using credible provisional calendars/sequence evidence and explicit qualitative NASA/pH screening. Their local/cultivar uncertainty is propagated, not silently resolved. Optional unsupported dimensions do not block rotation exploration. Mungbean remains calendar-incomplete for the rice-following system. See `docs/prototype-methodology.md` and `data/normalized/prototype_crop_subset.csv`. The older P0 list remains a scientific-improvement backlog, not a requirement for a certified predictive model before prototype use.

## October 28 source-verification update

See `docs/production-gate-verification.md` and the three new verification CSVs in `data/normalized/`. There are now 13 source-scoped calendar records and 18 sequence-evidence records. National BBS calendars and BARC seasonal sowing/DAE guidance are source-supported; this supersedes the earlier claim that no calendar evidence exists, but does not approve the raw local dates. Runtime remains blocked: no co-located cultivar/calendar/conditional-sequence release is established, and climate/soil permissions still cover global reference comparisons only. Optional water, salinity and stage sensitivity are not independent release blockers. The verification report lists exact sources, access limitations and the smallest remaining unblock path. No fixture or provisional data has been activated.

October 28, 2026. Four-crop scope: **Aman rice, maize, sunflower, mungbean**. Please return source URL/title, exact table/page, geography, cultivar/system, measurement basis and reviewer decision with each value. Do not estimate missing values just to complete a column.

## P0 — prevents the scientifically valid four-crop slice

1. **One agreed local calendar set:** choose Polder 30/Batiaghata or another explicitly approved site. For each enabled crop provide planting window, harvest/duration range, seedbed vs direct seeding/transplanting basis, field occupancy, turnaround, water regime and cultivar scope. CAL01/CAL04/CAL05/CAL06 are provisional and do not form an approved co-located set.
2. **Locally permissible dated sequences:** approve the underlying rice → maize/sunflower/mungbean systems and return direction; identify whether any third consecutive slot needs fallow or another year. Existing ROT007/027/037/071/073/074 do not independently validate their named cultivar pairs. Specify any prohibited transition or necessary management condition; absent pairs remain unknown.
3. **Applicability of global envelopes:** the four FAO pages' temperature bounds and optimal pH have been checked as exact reference transcriptions only. Confirm the aggregation period/comparison rule and limits of using them in local soft evaluation. Source verification does not establish a crop-stage heat threshold, seasonal drought limit or hard environmental incompatibility. Any hard crop limit needs its own evidence.
4. **Local soil compatibility beyond the reference check:** confirm pH measurement method/applicability and any actual texture/drainage exclusions needed for the enabled systems. No regional field pH or drainage is provided by the current AEZ table.

Production currently shows genuine POWER data and global-reference comparisons, then blocks recommendation generation on these gaps. Synthetic calendars and sequence rules run only in explicitly enabled DEVELOPMENT_FIXTURE mode.

## P1 — needed before November 1 for the promised scientific features

- **Water/time distribution:** approved crop-stage durations/Kc curves (including development interpolation), ETo method, effective rainfall, irrigation efficiency and rice field-water assumptions. Specify delivered irrigation vs evapotranspiration; weekly demand needs more than seasonal Kc. No current calibrated numeric water-risk result is enabled.
- **Stress timing/response:** growth-stage dates/durations and supported temperature/drought/wet exposure definitions; no universal numeric threshold can be taken from a single experimental temperature. Provide the historical scenario selection/evaluation rule.
- **Residue/soil contribution:** which management-dependent qualitative claims may be used for these crops and how to compare them. Numeric N/SOC gains require evidence; family diversity remains a structural count, not measured soil benefit.
- **Review disputed salinity uses:** numeric crop 1's 2.02 is a field observation, not a threshold; crop 9's 8 and crop 11's 6 are not established yield-response cutoffs. Resolve with measurement basis, growth stage, endpoint and sources. These non-core rice cultivar claims can stay excluded; core mungbean likewise has no calibrated cutoff. Maize 1.7/12 refers to a generic fresh-ear endpoint and sunflower 4.8/5 to other hybrids, not the named varieties' calibrated curves. All remain excluded from numeric scoring.
- **Reproducible validation:** exact approved location plus complete farm/history/soil inputs and expected qualitative feasibility/ranking direction for at least two alternatives. Existing RC cases lack coordinates and NASA reanalysis. Do not invent a parcel location or present a published BCR as forecast farm income.
- **Economics/input needs:** local, dated crop yield/price/cost/management evidence if income or low-input ranking must be active. Otherwise these dimensions remain `insufficient_data`.

## P2 — broader catalogue

- Sesame master/climate/calendar/water records; connected watermelon rules/calendars. Approve additional species independently before enabling them.
- Cultivar identity/system and species-proxy inheritance decisions for the four maize hybrids and named BRRI rice varieties. Preserve Pinacle spelling until the actual hybrid name is confirmed.
- Exact soil/suitability values extracted from approved regional sources, with scale and test method; catalogue availability alone is not a suitability class.
- Resolve unmapped **Dhaincha** species/cultivar and unspecified **Rabi crops** group if these cases enter the catalogue. `Oryza sativa L.` alone is a rice species, not an Aman/Aus/Boro alias; the row's separate system ID is used instead.

## P3 — post-MVP

Locally validated relay/four-/five-crop schedules; market/credit/labor coefficients; basin hydrogeological calibration; quantified soil carbon/nutrient dynamics; extension/soil-report verification protocols. Preserve the raw evidence; do not activate these as farm predictions.
