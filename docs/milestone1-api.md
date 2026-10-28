# Milestone 1 API

**NASA DATA DEPTH update:** `POST /api/environment-profile` returns the unified POWER/SMAP/GPM profile, indicators, provenance, provider statuses and limitations. Recommendation responses include it as `space_profile`; the older `environment_profile` remains POWER-only for compatibility. Optional `rainfall_comparison_period` must be earlier and match calendar start/end month-days. Optional priorities `rainfall_suitability` and `moisture_context` expose supported reference/context comparisons, never irrigation-demand estimates. See [full data-depth API and methods](nasa-data-depth.md).

`GET /api/health` reports `recommendation_mode=prototype_recommendation`, prototype status, eligible crop IDs and whether the separate developer-only fixture API is enabled. The UI never offers fixtures.

`POST /api/rotation-plan` is stateless. It validates inputs, retrieves an exact-query POWER cache or requests POWER, loads the reviewed evidence-tiered prototype projection, compares qualitative NASA/climate and soil dimensions, generates conservative month-window rotations, enforces hard constraints, orders supported dimensions by farmer priority and returns explanations/data gaps. It does not save farmer input to a database or import the research CSVs.

Example request (coordinates are the Stitch design example, not a validated farm):

```json
{
  "mode": "prototype_recommendation",
  "location": {"latitude": 25.7439, "longitude": 89.2752, "country_code": "BD"},
  "historical_period": {"start": "2024-01-01", "end": "2024-12-31"},
  "crop_history": ["aman_rice"],
  "soil": {"ph": null, "ph_method": "unspecified", "texture": "unknown"},
  "constraints": {"required_crop_ids": ["aman_rice"], "excluded_crop_ids": []},
  "preferred_crop_ids": [],
  "priorities": {"climate_suitability": 1},
  "horizon": 3
}
```

Accepted crop input IDs are `aman_rice`, `maize`, `sunflower`, `mung_bean`. Aman, maize and sunflower are eligible for generation; mungbean is reference-only and a required mungbean constraint is not silently relaxed. Unknown/legacy IDs are rejected at the API boundary, not silently mapped from an ambiguous namespace. The offline crosswalk is for research staging.

Additional supported inputs: `current_crop={crop_id,harvest_date}`, `constraints.locked_slots={"0":"maize"}`, `earliest_planting`, `latest_harvest`, and `max_changes` with a full ordered `baseline` of horizon length. A current crop must not have an already-past harvest date; prior crops go in ordered `crop_history`. Last history/current crop controls the first transition. Current-crop occupancy and conservative month envelopes prevent overlap; no biological turnaround duration is invented.

Hard constraints never become weighted preferences. Contradictory locks/exclusions are 400 validation errors; valid but impossible limits return no candidates. Unknown input keys, non-finite numbers, invalid dates/IDs, all-zero priorities and invalid baselines are rejected. Past historical intervals are limited to 366 days. Anonymous requests are throttled to 20/minute per process cache/IP. No external URL, custom data file, calendar or evidence bundle is accepted from clients.

## Response

The current prototype policy in [prototype methodology](prototype-methodology.md) supersedes any legacy verified-only/fixture-specific description below. Activities include `planting_window`/`harvest_window` with YYYY-MM endpoints, `idle_before`, source-backed `calendar_evidence` and `sequence_rule_id`. Results include `eligible_crop_ids`, `sequence_evidence_coverage`, per-option `evidence_confidence`, traceable NASA comparisons, unmet-priority metadata and useful data-gap reasons. No source status is silently upgraded.

Keys include `status`, `mode`, `dataset_origin`, `is_recommendation`, `notice`, `environment_profile`, `candidate_rotations`, `crop_comparisons`, `dimension_results`, `ranking`, `explanations`, `data_gaps`, `rejected_candidates`, and `provenance`.

- The default `prototype_recommendation` mode returns `rotation_options` when supported templates meet constraints. It exposes provisional evidence, confidence and unsupported optional dimensions. `location.country_code="BD"` declares the Bangladesh scope; jurisdiction is not independently inferred from coordinates. Explicit legacy `production` requests retain the earlier blocked/reference-only behavior for compatibility.
- Prototype `climate_suitability` compares historical daily-mean T2M ranges for activity calendar months against published global-species optimal/absolute intervals: `good_fit`, `acceptable`, `potential_concern`, or `insufficient_data`. Complete request T2M coverage is required; missing calendar months are exposed and confidence limited. It is not a forecast or stage-injury model. See `docs/prototype-methodology.md` for exact rules.
- `soil_suitability` compares farmer-entered pH to the source's global optimum and includes the unspecified/local test-method limitation. Outside optimum is not automatic crop rejection. Texture/EC fields are collected but not numerically scored.
- `rotation_quality` supports a family-count structural proxy only when family assertions have an activated structural-comparison use. It is not a measured soil-health score. No production family assertion is activated yet; fixture assertions remain synthetic.
- `farmer_priority_fit` is the transparent count of farmer-preferred crop occurrences. Hard required crops are handled separately.
- Water resilience, soil-health contribution, stage stress, salinity risk, income and input cost return `status=insufficient_data`, `value=null`.
- Farmer priorities are ordered by descending weight then name. Supported candidate dimensions are compared lexicographically, not added into one overall score. This initial method intentionally does not claim calibrated utility. Equal vectors share rank with deterministic ID display order. Any positively weighted unavailable goal makes preference ranking incomplete; it is not silently discarded.
- Explanations carry agronomic evidence and NASA parameter/period/response hash through the comparison components and explicit environment-source links. Original file/record/column and raw/normalized values remain available.

400: invalid inputs. 403: disabled/unsafe fixture mode or dataset. 503: POWER unavailable and no valid exact-query cache. Error responses never fabricate environmental profiles or recommendations.

## Fixture boundary

`mode=development_fixture` is accepted only if **both** `NEXTSEASON_DEBUG=1` and `NEXTSEASON_ALLOW_FIXTURES=1`. Dataset path is fixed to `tests/fixtures/development_knowledge.json`; clients cannot choose a path. Production loader rejects fixture origin/markers even if a fixture is accidentally placed at the production path. Fixtures have no place in `data/normalized/slice.json`.

The fixture mode still requests real POWER. Its agronomy is synthetic, marked DEVELOPMENT_FIXTURE in the dataset, source evidence, every calendar/rule, API status/banner, and UI. `is_recommendation=false`. The normal production view refuses responses from a different mode or any embedded fixture marker. Switching modes/inputs aborts an in-flight request and clears old results. Synthetic 2027 schedules are temporary test data, not local research dates.
