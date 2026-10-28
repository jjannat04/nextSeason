# Water Commons methodology (research prototype)

Water Commons compares **planned delivered irrigation** for 2–5 farms sharing one source. It is a weekly planning comparison, not a crop-water, field-water, groundwater, or hydraulic model. The normal single-farm flow remains independent.

## Evidence boundary

The audited `research/csv/4_crop_water_requirements.csv` contains no usable numeric seasonal water-requirement depths for the current crops. Its Kc and assumed stage fractions do not establish irrigation requirement. The normalized prototype subset marks water `insufficient_data`. NASA POWER rainfall, GPM IMERG precipitation, and SMAP soil moisture do not by themselves determine weekly pump deliveries. We therefore do not derive irrigation from those products or silently subtract rainfall.

Each farm may enter a **complete planned weekly delivery schedule** in cubic metres for the whole farm. This is a farmer planning input, never an observed NASA value or a validated crop requirement. If any farm lacks a complete schedule, the response shows calendar overlap only, sets community volume and capacity status to `insufficient_data`, and does not suggest a numeric conflict reduction. An explicit complete-schedule declaration makes omitted occupied weeks zero *planned delivery*; absence of that declaration does not.

Shared capacity is a group-entered positive number in m³/week with a source/basis label. Farm area in hectares is retained as context but does not multiply volumes that already represent the whole farm. Crop durations are inclusive days between farmer-entered planting and expected harvest dates; they are planning assumptions inside the selected calendar's month-level windows, not researcher-verified exact dates.

## Calculation

The API divides each intended crop period into Monday-starting calendar weeks. A planned event must name a unique occupied Monday and a finite nonnegative m³ volume. It aggregates each farm's planned delivery by week, then sums the farms. A conflict exists when the sum **exceeds** the declared weekly capacity. Severity is the arithmetic excess in m³/week and the ratio of planned delivery to declared capacity. A within-capacity result means only that these entered plans fit this entered capacity; it is not a water-availability guarantee. The response includes each contributing farm and the assumptions behind the comparison. A zero is used only for weeks explicitly omitted from a declared complete plan.

## Rotations, adjustments, and farmer autonomy

`/api/water-commons/options` calls the existing prototype calendar/constraint generator. `/api/water-commons/analyze` revalidates the selected generated option, crop order, month-level windows, non-overlapping dates, history/current-crop and farmer constraints; it does not accept an arbitrary crop sequence. The interface records required/excluded crops, first-slot locks, maximum changed slots against a baseline, and each farm's allowed timing flexibility.

For complete numeric plans with a conflict, the adjustment engine tries whole-week shifts of **one farm's entire entered schedule** within its allowed ±0–4 weeks. It rejects a shift if any date leaves its selected month window, crosses an earliest/latest date or current crop, or if any activity has timing locked. It retains crop order, duration, every weekly volume, and the farm total. Only a shift that reduces summed weekly conflict excess is suggested. Suggestions are previews, never applied automatically; each names the affected farmer, changed dates, preserved constraints and local timing trade-off, and gives before/after peaks. A timing shift can reduce simultaneous peak while changing total planned water by exactly zero.

Switching to another existing rotation, including a crop substitution already eligible in the single-farm engine, is **not currently quantified as a Water Commons adjustment**: the current crop-water evidence cannot establish the alternative's weekly delivery schedule. A farmer may choose another eligible rotation and enter its own complete plan, then rerun the comparison. This is a documented functional limit, not an inferred water saving.

## Provenance and limits

The response retains calendar IDs and windows, crop IDs, exact user-entered dates, duration, source/basis for each water plan, group capacity source, completeness status, evidence status and explicit limitations. It distinguishes crop-water requirement (`insufficient_data`), delivered irrigation plan (farmer entered), rainfall contribution (`not_subtracted`) and capacity (group entered). It does not assert that these plans predict real demand, that shifts save water, or that month-level calendar evidence proves exact planting dates. No backend state or credential is persisted for this feature.

The current analysis assumes one shared weekly capacity that is constant across the horizon. It does not model pump duty cycles, daily competition, conveyance losses, rainfall-runoff, reservoir storage, groundwater, irrigation efficiency, water rights, farmer consent beyond preview, or local field conditions. Quantitative estimates depend entirely on the completeness and accuracy of user-entered schedules and capacity.

## Verification

Backend tests cover exact multi-farm summation, conflict attribution, feasible peak reduction with conserved total, locked timing, unknown-water qualitative mode, selected-option and crop-constraint rejection, and provenance through the API. Frontend tests cover farm count limits and rendering of conflict, suggestion, before/after and qualitative states. Manual verification should check a representative 2–5-farm plan with local irrigators, particularly whether their weekly delivery plans and capacity use the same definition of delivered m³/week.
