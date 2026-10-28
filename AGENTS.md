
# Next Season — Repository Instructions

## Project

This repository contains "Next Season", Team OORT CLOUDS' NASA Space Apps Challenge 2026 project for the challenge:

"Field Shift: Adapting Farms with NASA Data"

Next Season is a NASA-powered, multi-season crop-rotation decision-support system.

The primary goal is to help farmers compare feasible crop rotations using:

- NASA Earth observations
- local soil information
- crop characteristics
- crop history
- farmer constraints
- farmer priorities

The first validated deployment context is Bangladesh, but the architecture should remain globally extensible.

## Core Product Principle

Do not reduce this project to a generic crop recommender.

The central question is:

"What sequence of crops over the next several seasons is feasible, resilient, and aligned with this farmer's priorities?"

The system must produce multiple rotation alternatives and explain their trade-offs.

## NASA Data Requirement

NASA data must be central to the decision engine, not decorative.

Primary planned sources:

- NASA POWER
- SMAP
- GPM IMERG

Environmental observations must affect crop suitability, risk evaluation, stress testing, or rotation ranking.

A useful test is:

"If NASA environmental conditions change, could the rotation ranking change?"

If not, NASA data is not integrated deeply enough.

## Scientific Integrity

Never invent agronomic values, NASA measurements, thresholds, crop requirements, or scientific claims.

Use researcher-provided structured data and cited sources.

If data is unavailable:

- mark it unknown,
- use an explicitly documented fallback,
- or ask for clarification.

Do not silently fabricate values for demos.

Keep regional estimates distinct from field measurements.

Historical scenarios must not be presented as forecasts.

## Product Scope

The core product must implement:

1. Farm location
2. Field information
3. Crop history/current rotation
4. Farmer constraints
5. Farmer priorities
6. NASA environmental profile
7. Rotation generation
8. Rotation comparison
9. Explainability
10. Historical climate stress testing
11. Missing-information / uncertainty handling
12. Water Commons
13. Printable/shareable plan
14. Methodology and NASA data transparency pages

## Water Commons

Water Commons coordinates several farms sharing irrigation capacity.

It should:

- combine estimated irrigation demand,
- detect peak-demand conflicts,
- preserve farmer constraints,
- suggest feasible timing and/or crop changes,
- compare before vs after peak demand.

Do not claim that planting-date shifts reduce total water consumption unless the underlying water requirement changes.

## UX

The approved Stitch designs are the visual source of truth.

Preserve their:

- typography
- spacing
- colors
- cards
- navigation
- crop timeline language
- NASA-data presentation
- chart style

Public pages use a top navbar.

The planning workflow uses a compact sidebar or stepper.

Design principle:

"NASA complexity underneath, farmer simplicity above."

## Engineering

Prefer simple, inspectable architecture over unnecessary complexity.

Do not add AI/LLM features unless they materially improve the core crop-rotation decision problem.

Avoid premature optimization.

Keep scientific logic separate from presentation logic.

Keep NASA data ingestion separate from agronomic knowledge.

Make all important scoring logic testable.

## Validation

Important logic must have tests.

At minimum test:

- location sensitivity
- farmer-priority sensitivity
- soil sensitivity
- crop-history sensitivity
- climate-stress sensitivity
- hard-constraint enforcement

## Workflow

For significant implementation work:

1. inspect relevant project context,
2. produce or update the implementation plan,
3. identify assumptions and blockers,
4. implement in a contained phase,
5. run tests,
6. verify behavior,
7. summarize what changed.

Do not rewrite unrelated parts of the project while completing a focused task.

## Deadline

Internal target:

November 1, 2026 — complete working site.

The product should be feature-complete by then so later time can be used for validation, documentation, presentation, and polish.
