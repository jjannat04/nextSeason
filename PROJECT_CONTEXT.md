
# Next Season — Project Context

## Current implementation status — 28 October 2026

The active scientific release strategy is an **evidence-tiered decision-support research prototype**, not a certified agronomic prescription. Verified and credible provisional core evidence may support `prototype_recommendation`; unresolved/missing records cannot affect scientific ranking or biological hard constraints. Aman rice, maize and sunflower now generate real-data rotation options from normalized evidence and NASA POWER. Mungbean remains reference-only for the rice-following calendar system. Month-window uncertainty, qualitative climate/pH screening, source applicability, deterministic confidence and optional `insufficient_data` dimensions remain visible. See `docs/prototype-methodology.md` and the current section of `PLANS.md`; the previous strict production gate is historical. NASA POWER, SMAP `SPL4SMGP.008`, and GPM IMERG `GPM_3IMERGDF.07` have live-validated extraction at a Bangladesh reference point. Historical stress testing now selects contrasting observed years from complete POWER annual records; GPM multi-month data was separately validated, while incomplete SMAP/GPM annual coverage is not extrapolated into stress scores. Water Commons and crop catalogue expansion remain deferred.

## Team

Team name: OORT CLOUDS

Institution:
Chittagong University of Engineering and Technology (CUET), Bangladesh

Team structure:

- J — team lead and web developer
- B — research lead / scientific validity
- A — crop/agronomy research
- M — soil and rotation research
- S — NASA/environment research
- O — video editing / visual communication

The team is relatively new to NASA Space Apps and is aiming for a global-level submission.

## Challenge

NASA Space Apps Challenge 2026

Challenge:
Field Shift: Adapting Farms with NASA Data

Challenge objective:

Create a decision-support tool using NASA Earth observations together with local soil information, crop characteristics, and farmer priorities to help farmers explore crop-rotation strategies that could strengthen soil health and improve adaptation to changing conditions.

## Project Name

Next Season

## Product Vision

Most crop tools ask:

"What crop should I plant?"

Next Season asks:

"What should I grow next, what should follow after that, and how resilient is that sequence under my farm's conditions?"

Next Season should help a farmer explore several possible futures rather than issue one absolute instruction.

## Primary User

Initially:
smallholder and medium-scale farmers in Bangladesh

Secondary users:

- agricultural extension workers
- cooperatives
- agronomists
- NGOs

Global expansion should be possible through region-specific crop calendars, agronomic rules, and local soil datasets.

## Farmer Workflow

The intended workflow is:

1. Select farm location.
2. Enter field information.
3. Enter previous crops/current rotation.
4. Define hard constraints.
5. Define priorities.
6. Retrieve NASA environmental data.
7. Build an environmental profile.
8. Generate feasible crop rotations.
9. Remove rotations violating hard constraints.
10. Evaluate remaining rotations.
11. Compare multiple alternatives.
12. Explain why each option fits.
13. Stress-test against historical environmental scenarios.
14. Identify missing information.
15. Allow farmer to choose a plan.
16. Produce a printable/shareable rotation plan.

## Farmer Inputs

Potential inputs include:

- location
- farm size
- current crop
- previous crops
- current rotation
- irrigation availability
- irrigation limit
- drainage
- soil texture/type
- soil pH
- salinity
- crop preferences
- crops to avoid
- crops that must remain
- maximum number of changes
- farmer priorities

Unknown values must be allowed.

## Farmer Priorities

Initial priorities:

- water conservation
- soil health
- climate resilience
- income potential
- low input cost

These priorities should influence ranking rather than simply be displayed.

## NASA Data

NASA data must be a central part of the computation.

### NASA POWER

Potential use:

- temperature
- minimum/maximum temperature
- precipitation
- humidity
- solar radiation
- wind
- historical climate baselines

### SMAP

Potential use:

- surface soil moisture
- root-zone soil moisture
- moisture anomaly/context

### GPM IMERG

Potential use:

- precipitation
- precipitation anomaly
- heavy rainfall
- dry/wet historical scenario construction

Potential later sources may include:

- MODIS
- VIIRS
- ECOSTRESS
- Landsat/HLS
- GLDAS
- MERRA-2

Do not add additional NASA datasets merely for quantity.

## Research Data

Researcher-built structured agronomic data is separate from NASA data.

Expected datasets include:

- crops_master.csv
- crop_calendar.csv
- crop_climate_requirements.csv
- crop_soil_requirements.csv
- crop_water_requirements.csv
- crop_rotation_rules.csv
- crop_soil_health_effects.csv
- crop_salinity_response.csv
- crop_stage_sensitivity.csv
- Bangladesh soil reference data
- Bangladesh crop-suitability reference data
- references.csv

Every important research value should be traceable to a source.

## Rotation Engine

The rotation engine should conceptually operate as:

candidate crop combinations
→ planting-calendar filtering
→ farmer hard constraints
→ soil compatibility
→ environmental compatibility
→ crop-sequence/rotation rules
→ water-risk evaluation
→ soil-health contribution
→ farmer-priority weighting
→ scenario robustness
→ ranked alternatives

Hard constraints should remain separate from soft scores.

## Explainability

Every recommended rotation should be able to answer:

- Why does this fit?
- What NASA evidence influenced it?
- What soil information influenced it?
- Which rotation rules matter?
- Which farmer priorities increased/decreased its rank?
- What are the trade-offs?
- What information is missing?
- What could change the result?

Preferred explanation structure:

Evidence
→ interpretation
→ crop impact
→ rotation impact

## Stress Testing

Historical scenarios should initially include:

- historical normal
- dry historical condition
- hot historical condition
- wet historical condition

These are stress tests, not forecasts.

The goal is to identify rotations that remain acceptable across changing conditions.

A possible concept is:

"Robust Rotation"

Meaning:
a rotation that performs reasonably consistently across several tested environmental scenarios.

## Water Commons

Water Commons is the community-scale differentiator.

Several farms may share one irrigation source.

For each farm:

- rotation
- crop calendar
- area
- crop water demand
- constraints

The system should construct estimated demand over time.

Then:

combined demand
vs
available shared irrigation capacity

If demand exceeds capacity, the system may explore:

- planting-window changes
- crop substitution
- alternative rotation

while preserving hard constraints.

The product must make clear:

changing planting timing may reduce peak simultaneous demand but does not automatically reduce total water use.

## Prescreening Commitments

The submitted prescreening video stated that Next Season would:

- compare crop sequences
- use NASA environmental data
- use local soil information
- use crop characteristics
- use farmer priorities
- preserve farmer constraints
- evaluate planting windows
- evaluate soil suitability
- evaluate water requirements
- evaluate heat/dry exposure during crop stages
- compare potential soil-health contributions
- explain why a rotation fits
- explain trade-offs
- identify missing information
- distinguish historical scenarios from forecasts
- support Bangla and English explanations
- provide readable rotation calendars
- provide printable plans
- demonstrate Water Commons

The final product should implement these promises where feasible.

## UX / Design

The full UI has already been designed using Google Stitch.

The Stitch export is stored under:

design/stitch-export/

Treat those designs as the intended visual direction.

Do not independently redesign the interface unless a design is technically unusable or inconsistent.

Key product screens:

1. Landing
2. Farm Location
3. Field Information
4. Farmer Constraints
5. Farmer Priorities
6. Your Field From Space
7. Your Next Seasons
8. Rotation Comparison
9. Why This Rotation?
10. Climate Stress Test
11. Missing Information
12. Water Commons
13. Printable Plan
14. Methodology
15. NASA Data Sources

## Design Philosophy

The product should feel:

- modern
- scientific
- calm
- trustworthy
- premium
- farmer-friendly
- globally competitive

Avoid:

- generic SaaS dashboard aesthetics
- excessive text
- unnecessary AI chatbot interfaces
- fake precision
- visually overwhelming satellite/science terminology

Core UX principle:

"NASA complexity underneath, farmer simplicity above."

## Scientific Integrity

Never show demo values as though they were real measurements.

Clearly distinguish:

- NASA measurements
- NASA-derived indicators
- regional references
- farmer-provided measurements
- agronomic rules
- model/engine scores
- assumptions
- historical scenarios

Do not claim measured soil-health improvement when only estimating potential contribution.

Do not present historical scenario analysis as a weather forecast.

## Definition of Done

The site is considered functionally complete when a user can:

Select a farm
→ retrieve NASA environmental data
→ enter field/crop history
→ enter constraints
→ set priorities
→ generate feasible rotations
→ compare alternatives
→ inspect NASA influence
→ understand explanations
→ stress-test rotations
→ see missing data
→ use Water Commons
→ select a plan
→ print/share the result

All major flows should work without developer explanation.
