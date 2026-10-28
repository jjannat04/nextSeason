# Historical climate stress testing — method and validation

28 October 2026. This milestone compares existing Bangladesh prototype rotations against **observed historical years**. It does not predict future weather, crop yields, irrigation demand, flood damage or farm income. No new crop or NASA product was added.

## NASA source depth and measured coverage

| Provider | Product and variables | Live depth checked | Decision use |
|---|---|---|---|
| NASA POWER | Daily point, agricultural community, UTC; `T2M`, `T2M_MIN`, `T2M_MAX` in °C and `PRECTOTCORR` in mm/day | Complete January–December daily data for every year 2015–2024 at Khulna reference (22.8°N, 89.55°E) and Dinajpur reference (25.63°N, 88.65°E). All four parameters had 365/366 valid days per year and original response SHA-256 hashes. Repeated requests hit exact-query cache. | Scenario selection and supported qualitative crop temperature/annual rainfall reference screens. |
| GPM IMERG | `GPM_3IMERGDF.07` Final daily; `precipitation` mm/day, `precipitation_cnt` count, native DOI `10.5067/GPM/IMERGDF/DAY/07` | Live June 1–July 31, 2024 Khulna subset: **61/61 valid days**, no missing days, 48 half-hourly retrievals for each day, 61 checksummed NetCDF files, total 589.169988 mm. The Harmony job took about 213 seconds; submission through bounded collection took about 472 seconds. Repeat request was cached. | Proven multi-month source capability and historical rainfall context. Not substituted for the ten-year POWER baseline or used as incomplete annual rainfall. |
| SMAP | `SPL4SMGP.008`, native `Geophysical_Data/sm_surface`, `sm_rootzone`, `sm_rootzone_pctl` | Live June 1–7, 2024 Khulna Harmony subset: **56/56 valid three-hourly samples** for each variable, 56 checksummed NetCDF files, no missing sample. Submission to complete collection took about 8 minutes 8 seconds; repeat request was cached. Example source-file SHA-256: `fef9fc2d4c082590928dfbd9a70fafcadacdc0342c516f2215c7623718e25a8e`. | Proven seven-day moisture coverage. No year-wide crop-stage or water-stress score is inferred from this short window. |

The two POWER locations are **reference coordinates**, not verified field measurements. The full public responses used for offline regression are retained in `tests/fixtures/nasa_power_khulna_2015_2024.json` and `nasa_power_dinajpur_2015_2024.json`, each with its exact query and raw-response checksum. These fixtures are test-only; production fetches per requested coordinate and does not substitute their values for another location.

## Baseline and scenario selection

For the farmer's requested coordinate, the service retrieves ten **complete calendar years**, 2015 through 2024, from NASA POWER. Every daily value for all four named parameters must be present, with exactly 365 or 366 valid days. If any year is incomplete or unavailable, all four scenario classifications and robustness labels return `insufficient_data`. Unknown values never become zero. The fixed decade makes results reproducible; it is an empirical ten-year sample, **not a formal climate normal**. The plan's user-selected historical period remains separate from this baseline.

For each complete year, annual mean `T2M` is the mean of its daily values and annual precipitation is the sum of daily `PRECTOTCORR` in mm/day. The baseline medians are the median of the ten annual values for each metric. Both metrics are ranked low to high among the ten years; ties use earlier year first. The selection rules are:

| Scenario | Exact deterministic rule |
|---|---|
| `historical_normal` | Minimize the larger of the two absolute rank distances from the ten-year midpoint (rank index 4.5) for annual mean temperature and annual precipitation. Break ties by the sum of those distances, then earlier year. “Normal” means closest to the middle of this observed sample in both metrics. |
| `historical_dry` | Lowest complete annual POWER precipitation total. Earlier year breaks a tie. This is a relative sample label, not a formal drought designation. |
| `historical_hot` | Highest complete annual mean POWER `T2M`. Later year breaks a tie. This is a relative annual label, not a crop-stage heatwave designation. |
| `historical_wet` | Highest complete annual POWER precipitation total. Later year breaks a tie. This is a relative sample label, not a flood claim. |

There is no anomaly threshold or probability. The selected years may overlap if the same observed year meets multiple rules; no synthetic year is created to force distinct scenarios. The response includes the rule, observed annual values, rank, baseline medians, full baseline-year values, source query, period, daily coverage and SHA-256 so a user can see why a year was called dry, hot or wet.

At the live Khulna reference point, the baseline annual medians were **25.9111 °C** for mean `T2M` and **2,346.65 mm** for `PRECTOTCORR` total. The selected observed years were:

| Scenario | Year | Annual mean T2M | Annual precipitation |
|---|---:|---:|---:|
| Normal | 2024 | 25.9649 °C | 2,448.82 mm |
| Dry | 2022 | 25.5413 °C | 1,693.45 mm |
| Hot | 2016 | 26.2598 °C | 2,663.28 mm |
| Wet | 2017 | 25.5479 °C | 3,482.43 mm |

The second live location changes the contrast: Dinajpur's lowest-rain year in this sample was **2015**, and highest-rain year was **2020**. This demonstrates that scenario selection follows the requested location's real observations. These statements describe the retrieved NASA POWER grid values, not station rainfall or field measurements.

## Rotation interpretation and robustness

Every candidate retains its original crop sequence, month-level calendar, hard constraints, soil result and farmer-priority ranking. Stress testing does **not** generate a new crop option or relax a constraint. For each selected observed year:

1. Existing crop-temperature screening compares complete daily POWER `T2M` for each activity's occupied calendar months with the published species optimal and absolute temperature ranges. The most concerning supported crop category is retained.
2. A complete January–December `PRECTOTCORR` total is compared with the existing source-verified annual species rainfall envelope. Inside optimal=`good_fit`; inside broader absolute=`acceptable`; outside=`potential_concern`. The annual global species envelope is provisional for Bangladesh and does not represent seasonal effective rainfall, irrigation requirement or yield.
3. The scenario's rotation category is the most concerning supported category across crop temperature and annual rainfall reference screens. If a mandatory comparison is missing, the interpretation is `insufficient_data` rather than assigning a category.
4. Irrigation demand, salinity, crop-stage stress, soil-health change, yield and income effects always remain `insufficient_data` here. SMAP's short validated windows and IMERG's incomplete annual baseline are not silently extrapolated into these dimensions.

The deterministic robustness label counts **distinct observed scenario years** with a supported `potential_concern` category. Zero concerning years=`robust`; one=`moderately_robust`; two or more=`sensitive`. If any of the four scenario interpretations lacks mandatory evidence, no robustness label is assigned. When multiple scenario types select the same year, it counts once. “Most Robust” highlights all tied candidates with the fewest distinct concerning years **within the tested set**, even if their absolute label remains `sensitive`. There is no synthetic score, probability or hidden tie-break.

For the current Khulna test request, the six existing candidates all remain `sensitive` by this rule. Two tie for the fewest concerning years (three distinct years); the other four have four. This is a qualitative comparison under broad provisional species envelopes, not a predicted crop-failure claim.

## API, provenance and cache

`POST /api/rotation-plan` in `prototype_recommendation` mode adds `stress_tests`. It contains `historical_normal`, `historical_dry`, `historical_hot`, `historical_wet`, `baseline`, `robustness` and a historical-not-forecast notice. Each scenario returns `environmental_conditions`, per-candidate `rotation_interpretation`, `evidence_status`, `provenance` and `limitations`. Provenance includes NASA POWER, daily point AG, all four variables, the selected calendar year, baseline 2015–2024 period, exact query, response SHA-256, cache status and per-variable daily coverage. Crop comparisons retain their underlying published agronomic evidence and the observed source checksum.

POWER's existing cache keys include exact latitude/longitude, dates, variables, AG community, UTC and adapter version. Closed historical years are reusable; repeated Khulna and Dinajpur baseline requests were cache hits. GPM's separate private cache includes point, period, product/version, variables and adapter version; raw NetCDF files retain SHA-256 checksums. SMAP and GPM credentials never enter cache keys, files, logs or API responses. Historical product reprocessing requires deliberate cache refresh; cached historical observations are not forecasts.

## Visual implementation and exclusions

The “How Does This Rotation Hold Up?” screen adapts the approved Stitch scenario selector and comparison cards. It shows actual observed years and annual metrics, a source/method disclosure, candidate categories, tied relative best candidates and a visible **historical replay, not a forecast** notice. The Stitch artwork's named disaster events, 20+ year climatology, thermal anomalies, numeric `/100` robustness scores, yield and household-margin changes, irrigation savings, flood/inundation outcomes and crop-stage damage claims were illustrative and are omitted because the implemented evidence cannot support them.

Tests include recorded authentic NASA POWER response/checksum validation, source-derived scenario selection, real location sensitivity, dry/wet/hot contrast, missing observations, API provenance, unsupported dimensions and exact robustness rules. Synthetic provider failure tests remain separate from the authentic public-response fixtures.
