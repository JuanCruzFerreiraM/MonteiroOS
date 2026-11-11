# HARV-04 — Cultivation Cycle Comparison

## Metadata
- ID: HARV-04
- Module: Harvest
- Stage: 2
- Status: Planned
- Priority: P1
- Domains: `FRONTEND` `BACKEND` `ANALYTICS`
- Dependencies: HARV-03, PROD-02

## Objective

Compare cultivation cycles on the same indicators while showing the context that makes the comparison interpretable.

## Business Value

A single cycle total does not tell the business whether a later cycle did better. The comparison has to keep variety, place, and data gaps in view.

## Functional Description

The user selects two or more cycles and sees the HARV-03 indicators for each, plus quinta, vidriera, start and end, and the varieties allocated to the cycle. Missing indicators stay visible as missing. The user can filter the cycle list by crop or variety before selecting.

The screen does not rank a cycle as caused by a practice, and it does not hide a cycle because data is incomplete.

## Expected Behavior

- Two cycles of different vidrieras can be compared.
- A cycle with no measurements appears with its context and empty indicators.
- Filtering by a variety lists cycles that allocated that variety, including cycles that also allocated others.
- Changing a measurement changes the comparison because the comparison reads HARV-03 outputs rather than a stored snapshot.

## Business Rules

- Comparisons consider variety, conditions, and management differences by showing the recorded context. They do not claim causation. See [VISION.md](../product/VISION.md).
- Management context is the operation history link for each cycle, not a scored practice index.

## Data Requirements

No new stored facts. The view reads cycles, allocations, varieties, quintas, vidrieras, and HARV-03 indicators.

## User Interactions

- Filter cycles, select at least two, and read the comparison.
- Open one cycle's operation history from the comparison.
- Remove a cycle from the selection.

## Acceptance Criteria

- [ ] A user can compare two finalized cycles and see each indicator beside the cycle's quinta, vidriera, dates, and varieties.
- [ ] A cycle with a missing per-square-meter input still appears, with that indicator marked missing.
- [ ] An active cycle can be included, and its open state is visible.
- [ ] Filtering by a variety excludes cycles that never allocated that variety.
- [ ] The comparison does not convert vara to ramo, or the reverse, without an explicit presentation factor on every measurement being converted.
- [ ] Totals that use different units, or different flower types, are not added into one number.
- [ ] Each cycle shows the varieties, units, and missing indicators used in the comparison.
- [ ] The comparison does not label a cycle as better because of a specific operation.
- [ ] Each cycle links to its operation history and to its harvest measurements.

## Edge Cases & Validation

- Selecting one cycle does not present a comparison; the UI asks for another cycle.
- Cycles with different unit mixes show totals per unit, matching HARV-03.
- A cycle with no allocation shows varieties as not recorded.

## Out of Scope

- Statistical significance, experiments, and forecasts.
- Cost or revenue comparison (COST-03).
- Editing harvests from the comparison grid.

## Dependencies & Integration Points

- HARV-03 for numbers and PROD-02 for variety filters. PROD-04 allocations are read through the cycle.
- TRACE-01 is the history destination.

## Open Questions

None beyond the measurement questions already handled by HARV-03.
