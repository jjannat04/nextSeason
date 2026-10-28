# Production gate verification — 28 October 2026

**Historical strict-gate assessment, superseded by the user-authorized prototype strategy.** The source findings below remain unchanged; they are no longer a blanket release block. Aman, maize and sunflower now qualify with provisional evidence under [prototype methodology](prototype-methodology.md). `prototype_crop_subset.csv` is the active decision file; the earlier production subset is retained as an audit record.

**Decision: production recommendations remain disabled. No crop currently passes all four required release dimensions.** This pass supplies new Bangladesh evidence; it does not activate a scientifically unsupported runtime release. Raw CSVs, staging, `slice.json`, application code and fixture permissions remain unchanged.

## Deliverables and interpretation

- `data/normalized/crop_calendar_verified.csv`: 13 records, with complete original calendar rows preserved as JSON, new source statements, region/season/variety, precision, locators, confidence and verification/classification fields.
- `data/normalized/crop_rotation_rules_verified.csv`: all 16 directed pairs among the four crops, plus two narrower BRRI leads. Each pair preserves every matching raw rule, including its named cultivars and original claims. There are no invented weights or numeric minimum gaps.
- `data/normalized/production_crop_subset.csv`: four crop-level release decisions, with separate required and optional dimensions.
- `data/normalized/production_verification_manifest.json`: sources, access limitations, PDF checksums, original-file checksums and deliverable checksums.

`verified_source_statement` means the specified source statement was checked. It does not approve a named cultivar, a specific coastal field or an executable rotation. National references are labelled `reference_support=verified_national_calendar` but their calendar classification remains **provisional for the intended local production release**. Eleven calendar records are provisional and two unresolved; none is classified production_safe. `production_activation_allowed=false` is intentional in every evidence row. Only `production_recommendation_allowed` in the subset file expresses the crop release decision. Blank scientific fields mean unknown/not established, never zero. Source years distinguish publication year from reference year or metadata dates.

## A. Calendar findings

| Crop/system | Supported calendar facts | Classification and remaining issue |
|---|---|---|
| HYV transplanted Aman | Planting: June (late)–August (middle); harvest: December–January (early), crossing years | Verified national reference; local release provisional. Not verification of CAL01's July 10/August 20/November 20/December 31 dates or 133-day field occupation |
| Local transplanted Aman | June (end)–September (early); December–January (early) harvest | Verified separate national reference; local release provisional. Cannot merge with HYV or named BRRI cultivar calendars |
| Rabi maize | October (middle)–December (late); April (early)–May (end) harvest | Verified national reference; local release provisional. January sowing in CAL04 unsupported by this source |
| Winter sunflower | November (middle)–December (middle); February (late)–March (middle) harvest | Verified national reference; local release provisional. CAL05's January sowing/May harvest and Hysun-33 applicability not established |
| Mungbean, August–September sowing | August (middle)–September (middle); November (middle)–December (middle) harvest | Verified national reference; local release provisional. Season inferred from months, distinct from CAL06's late-Rabi crop |
| Mungbean, late Rabi/spring | BARC gives southern late-Rabi January (middle)–February (middle), and Kharif-I February (last part)–March (middle) sowing | `provisional` as complete calendars: harvesting is given as 55–70 days after emergence, not a verified sowing-to-final-field-clearance interval |

These are month-level evidence records with qualitative boundaries. No first/15th/last calendar dates have been fabricated from words such as “mid”. The BARC mungbean variety table's BARI Mung-6 life cycle of 55–60 days is retained separately from general 55–70 DAE harvesting guidance. Emergence lag, repeated pod picking and field clearance must not silently be collapsed into an invented exact harvest date.

**Exact primary calendar sources:**

1. BARC, *Hand Book of Agricultural Technology*, May 2013, ISBN 978-984-500-018-5. Maize sowing: printed p31 / PDF p46, §3.2. Mungbean sowing and BARI Mung-6 table: printed p62 / PDF p77. Mungbean harvest: printed p67 / PDF p82. [Official BARC-hosted PDF](https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-barc/2024/12/053a0722429448d4903412ce683a7d06.pdf).
2. BBS, *Yearbook of Agricultural Statistics-2024*, 36th series, **published June 2025**. §1.8: printed p24 / PDF p39, Aman rows 2(a)/2(c) and Rabi maize row 5; printed p25 / PDF p40, sunflower row 19 and mungbean row 24. [Official BBS-hosted PDF](https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-bbs/2024/12/58f325576f9a47cc91e7d227e336e40f.pdf).

The full PDFs were downloaded, target text extracted and tables visually inspected. BARC takes priority for its actual seasonal sowing guidance; BBS supplies separate complete national planting/harvest references. These publications do not establish cultivar-by-cultivar coastal timing.

**DAE/BAMIS regional cross-checks, all PDF p1:**

- [Khulna Aman chart](https://www.bamis.gov.bd/res/public/calendars/2019/08/23/5083.pdf): nursery and transplant phases are distinct. Month headings place transplanting in August and final harvest in December, but standard-week numbers disagree with month headings. `unresolved`; 133 days cannot be assumed to mean post-transplant occupation.
- [Khulna Rabi maize chart](https://www.bamis.gov.bd/res/public/calendars/2019/08/23/5127.pdf): December establishment, March harvest and 112-day duration. `provisional`; cultivar/system explanation for the national harvest difference is absent. A regional illustration is not automatically wrong because it differs, but the two contexts cannot be merged.
- [Khulna Kharif-I mungbean chart](https://www.bamis.gov.bd/res/public/calendars/2019/12/30/10934.pdf): April–June headings disagree with standard weeks 20–29. `unresolved`; germination is not an explicit sowing window. Do not auto-correct the headings or use their temperature/water tables as calibrated thresholds.

The BAMIS year 2019 comes from PDF metadata and hosting paths, not an explicit publication statement. No unverified trial date or generic global calendar was substituted for Bangladesh evidence.

## B. Sequence findings

**Direct institutional evidence:** IRRI Rice Today, 1 March 2021, [*Crop diversification in rice-based systems in the polders of Bangladesh: Yield stability, profitability, and associated risk*](https://ricetoday.irri.org/crop-diversification-in-rice-based-systems-in-the-polders-of-bangladesh-yield-stability-profitability-and-associated-risk/), results/conclusion and discussion of drainage, wet-season rice harvest and dry-season establishment. This is the research institution's summary of Assefa et al., *Agricultural Systems* 187, DOI [10.1016/j.agsy.2020.102986](https://doi.org/10.1016/j.agsy.2020.102986). The linked journal full text could not be inspected; the repository records this limitation rather than claiming to verify its methods or cultivar tables.

| Relationship | Evidence class | What it permits |
|---|---|---|
| Aman → maize | `acceptable`, conditional system evidence | Recognizes a reported system; no guaranteed productivity/income or exact hybrid-pair approval |
| Aman → sunflower | `acceptable`, conditional system evidence | Same limits; dry-season establishment depends on field and water conditions |
| Aman → mungbean | `acceptable`, conditional system evidence | Recognizes a cereal–legume system; no fixed nitrogen credit or universal preference |
| Maize/sunflower/mungbean → Aman | `acceptable`, **provisional derived annual return** | Documents an annual-cycle interpretation; not separately tested directional pair evidence |
| Four self-pairs and six dry-crop → dry-crop pairs | `unresolved` | No automatic neutral/acceptable classification; not eligible for generation |

“Highest yielding in the examined study” is not a universal `strongly_preferred` compatibility rule. No adequate crop-pair evidence was verified here for `discouraged`, `avoid` or a numeric minimum gap. These classes remain available in the schema without fabricated rows. All `hard_constraint` values are false because no pair-specific biological prohibition has been verified. A farmer constraint or actual calendar overlap remains a separate hard feasibility check.

Same-family membership cannot create a blanket prohibition: Aman and maize are both Poaceae, and their system is reported. Conversely, a legume label alone does not prove every cereal transition beneficial. Family strings in these evidence records preserve botanical context; this pass does not activate a family-diversity health score.

**Higher-priority BRRI leads, retained provisionally:** [ধান ভিত্তিক খামার বিন্যাস বিভাগের সাফল্য](https://brri.gov.bd/pages/static-pages/6922dc9b933eb65569e1140d), section (খ), item16, lists hybrid maize → BRRI dhan39 for irrigated high land with clay-loam/loam soil; section (ঝ), item43, lists BARI Mung-6 → fallow → BRRI dhan44 for a non-saline tidal ecosystem. Official indexed text was readable, but full-page access failed. Publication year is unknown. These are not verified substitutes for the raw BRRI dhan51/52/54 pairs, and fallow is not an invented number of gap days.

BARI technology-library entries and the 2019 handbook were investigated as leads. Full authoritative detail was not consistently accessible; search snippets and third-party copies were not promoted into verified production records. The accessible BARC publication remains the higher-priority source for the mungbean sowing facts above.

## C. Required versus optional production dimensions

| Dimension | Current result | Release implication |
|---|---|---|
| Calendar | Supported national references; incomplete selected coastal cultivar/system alignment | Required gate not passed for the intended local release |
| Climate compatibility | Verified global species temperature references; only period-mean reference comparison authorized | Local/seasonal recommendation applicability and comparison method remain unestablished; do not relabel a reference as validated suitability |
| Soil compatibility | Verified global optimum-pH references; incomplete measurement-method, drainage and local applicability | Core gate remains partial. BARC's mungbean preferred pH 6.2–7.2 differs from the existing global optimum 5.5–6.2; preserve scopes and seek method/applicability resolution, do not average or overwrite |
| Sequence | Three conditional forward systems; inferred return phases; narrower cultivar-specific BRRI leads | No complete executable location/cultivar sequence set approved |
| Water, salinity, stage sensitivity | `insufficient_data` for calibrated evaluation | **Optional scoring gaps do not independently block release.** Explicit management prerequisites of a selected cropping system still matter |

No release flag was changed merely to make a demo work. No exact-day requirement has been imposed on source evidence: a future released planner can operate on conservative month intervals with explicit uncertainty and fallow. The existing dated fixture algorithm is not suitable for silently consuming these records. Its duration/turnaround fields must not be populated with guessed numbers.

## D. Smallest practical unblock path

1. Start with **Aman + BARI Mung-6** as the smallest research target, not an approved production subset. Select one ecosystem and matching Aman cultivar. Do not combine Polder 30, general southern late Rabi and BRRI's non-saline tidal recommendation as though they were the same trial.
2. Obtain full source detail for that system, including nursery/transplant basis, final mungbean field-clearance interval or explicit harvest months, source-required fallow, drainage and establishment conditions. A month-level answer is sufficient; a numeric minimum gap is only needed if the evidence actually requires one.
3. Establish the intended climate and soil comparison method/applicability for a recommendation. Keep global reference results labelled as references; resolve the mungbean pH scope difference. Do not demand complete water/salinity/stage models as a precondition.
4. Only after these core conditions pass, implement an explicit release allowlist, region/cultivar/management applicability checks and month-interval scheduling. Preserve separate fixtures. Test successful production candidates and rejected unverified, wrong-scope and uncertain overlapping transitions using independently supported cases.

**Task D condition is not satisfied in this pass.** Production remains `blocked_scientific_data`, with no recommendations and no fixture fallback. Evidence-review files are deliberately not imported by requests. No new product feature has been started.

## Validation performed

All 34 Python tests pass, including five new tests for unchanged-original provenance/checksums, day/emergence precision, complete pair coverage and unresolved semantics, preservation of raw cultivar-rule evidence, and the blocked production boundary. All three frontend safety tests, the frontend production build and Django system checks pass. The frontend test runner initially could not rename a sandbox temp-cache file; setting TEMP/TMP to the existing workspace `.runtime/test-tmp` resolved that environment restriction. No application change was needed.
