# Next Season documentation index

Release operators: [deployment guide](deployment-guide.md) · [manual release checklist](release-checklist.md) · [final QA findings](final-readiness-report.md).

Start with the repository [README](../README.md) for a product and local-run overview. For a technical or scientific review, follow this path:

| Topic | Document |
|---|---|
| Challenge, project goals and scope | [Project context](../PROJECT_CONTEXT.md) |
| Current release model, calendars, constraints, suitability, ranking and evidence states | [Prototype methodology](prototype-methodology.md) |
| Three NASA products, live access paths, variables, cache/provenance and limits | [NASA data depth](nasa-data-depth.md) |
| Observed-year scenario selection and robustness | [Historical stress-testing methodology](stress-testing-methodology.md) |
| Shared irrigation-plan arithmetic, adjustments and limitations | [Water Commons methodology](water-commons-methodology.md) |
| Raw CSV quality and safe-use decisions | [CSV audit](csv-audit.md) |
| Canonical normalization and provenance | [Normalized data](normalized-data.md) |
| Bangladesh calendar and sequence source verification | [Production-gate verification](production-gate-verification.md) |
| Outstanding research and scientific limitations | [Research blockers](research-blockers.md) |
| Original NASA POWER adapter details | [NASA data](nasa-data.md) |
| Current deployment/manual QA checklist | [Final readiness report](final-readiness-report.md) |
| Implementation phases and decisions | [Plan](../PLANS.md) · [Decisions](decisions.md) |

## Major external references

- [NASA POWER daily API](https://power.larc.nasa.gov/docs/services/api/temporal/daily/)
- [SMAP SPL4SMGP version 8](https://nsidc.org/data/spl4smgp/versions/8)
- [GPM IMERG Final V07](https://doi.org/10.5067/GPM/IMERGDF/DAY/07)
- [BBS *Yearbook of Agricultural Statistics 2024*](https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-bbs/2024/12/58f325576f9a47cc91e7d227e336e40f.pdf), §1.8
- [IRRI crop diversification in Bangladesh rice-based systems](https://ricetoday.irri.org/crop-diversification-in-rice-based-systems-in-the-polders-of-bangladesh-yield-stability-profitability-and-associated-risk/)
- FAO EcoCrop species references: [rice](https://ecocrop.apps.fao.org/ecocrop/srv/en/dataSheet?id=1574), [maize](https://ecocrop.apps.fao.org/ecocrop/srv/en/dataSheet?id=238663), [sunflower](https://ecocrop.apps.fao.org/ecocrop/srv/en/dataSheet?id=1191)

Each live rotation result includes source-specific links and evidence status. This index summarizes where to review the methods; it does not replace the per-result provenance.
