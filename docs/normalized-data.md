# Normalized data contract

**Current release: evidence-tiered prototype recommendations.** The separate offline `knowledge.prototype` builder creates `prototype_slice.json` and `prototype_crop_subset.csv` from the audited normalized calendar/rule CSVs and reference slice. Verified/provisional core evidence may participate; unresolved/missing fields are excluded from scientific logic. Original statuses, sources, scopes and raw values survive. Runtime reads only JSON and checks source fingerprints. See [prototype methodology](prototype-methodology.md). The strict `slice.json` and earlier production audit remain preserved as historical/reference artifacts; their old activation policy below does not govern the prototype.

The raw `research/csv/` directory is never rewritten. `data/normalized/` contains separate reproducible JSON artifacts, not a production database import. Request handling never opens the CSVs or full staging file.

## Artifacts

- `data/crosswalk/spec.json`: explicit reviewed-to-identity mapping specification. Maps master codes, legacy numeric codes, cultivar slugs and names. Identity mapping does not verify agronomic claims or transfer species evidence to a cultivar.
- `data/crosswalk/crops.json`: namespaced crosswalk for every observed identifier/name/token, plus exact unresolved file/record/column occurrences. Oryza's three ambiguous system-name occurrences and the Dhaincha/Rabi-crops tokens remain reported instead of guessed.
- `data/normalized/manifest.json`: original file SHA-256 and record counts.
- `data/normalized/staging.json`: all raw records and per-cell envelopes. Explicitly marked `RESEARCH_STAGING_NOT_FOR_SCORING`. Source titles/URLs remain unchanged; `source.normalized_urls` only trims delimiters/tracking parameters and preserves meaningful query IDs. Multiple sources remain a list rather than a synthetic single citation.
- `data/normalized/conflicts.json`: disputed claims, corresponding evidence-record pointers, reason and null resolution. Both sides remain in staging. No values are averaged or selected automatically.
- `data/normalized/slice.json`: only Aman, maize, sunflower and mungbean. Runtime reads this small projection. Only independently checked temperature/optimal-pH claims permit `global_species_reference_comparison`; no calendars or sequence rules are active.

Regenerate from repository root with `PYTHONPATH=backend` and `python -m next_season.knowledge.normalize`. The command reports invalid values instead of coercing them to zero; it checks that original CSV hashes remain unchanged during the run. Outputs are deterministic for unchanged source bytes/code/specification.

## Evidence field

```json
{
  "raw_value": "N/A",
  "normalized_value": null,
  "verification": "missing",
  "missing_reason": "unspecified_missing",
  "source": {
    "source_title": "original title or null",
    "source_url": "original URL string or null",
    "normalized_urls": [],
    "source_year": "original year string or null"
  },
  "confidence": null,
  "notes": null,
  "geographic_applicability": null,
  "provenance": {"file": "original.csv", "record": 2, "column": "property", "sha256": "original asset checksum"},
  "unit": null,
  "allowed_uses": []
}
```

States: `verified`, `provisional`, `conflicting`, `missing`, `not_applicable`. An N/A token whose meaning is unspecified stays missing rather than assuming not-applicable. An intentional false/zero remains false/zero. Normalization does not automatically upgrade verification. Status prose remains raw evidence rather than an executable rule.

Crop IDs normalize in `fields.crop_id.normalized_value` and sequence predecessor/successor fields. `identity_mapping` retains namespace, canonical ID and variety ID; `raw_value` always retains the original token. Species-level maize and its several hybrids share a canonical crop ID while preserving different `variety_id`s. Rice systems have separate canonical IDs; `Oryza sativa L.` alone cannot identify a system. Fallow is a land-use activity, not a crop.

Temperature uses °C (`degC`), annual rainfall uses mm/year, Kc is dimensionless, soil pH retains unknown test basis, salinity ECe uses dS/m, and loss slope uses relative-yield percentage points per dS/m. Source `dS_per_m` spellings normalize without claiming EC/ECe equivalence. Missing periods/area denominators are explicitly retained (e.g. `m3/ha_period_unspecified`). Unit normalization never converts annual climate bounds to seasonal irrigation or grain yield from a fresh-ear response.

## Activating future calendars

Calendar records are independently gated by `verification=verified` and all four required fields carrying `rotation_feasibility` allowed use:

- `planting_start`, `planting_end`: ISO dates;
- `duration_days`: positive integer with approved establishment/occupancy meaning;
- `turnaround_days`: positive integer (this pilot does not support same-day/relay establishment).

Each activated record has an explicit slot (0–2), location/cultivar applicability and source evidence. Before generalizing beyond a reviewed slice, add executable location/cultivar scope validation; **do not simply flip the research JSON's flags**. Current runtime production release has no active calendar records. Sequence records similarly need separately approved `previous`, `next`, rule ID, `rotation_feasibility` and provenance. Current source rules remain staged evidence, not executable production rules.

No reviewer upload API or field editing endpoint exists. A future evidence release must be code-reviewed and versioned with its associated tests; changing readiness flags is not scientific review.

## Source checks, October 28

The official EcoCrop Ecology tables for rice ID 1574, maize ID 238663, sunflower ID 1191 and mungbean ID 2150 were inspected. Only the exact temperature envelope and optimal pH already present in the researcher data were checked. The normalizer requires both matching numeric value and exact source URL before attaching the narrow source-transcription review. The verified source claims apply globally at species level, not specifically to Aman timing, named cultivars or the selected Bangladesh farm. General crop-cycle ranges shown by those pages were deliberately not imported as local calendars.
