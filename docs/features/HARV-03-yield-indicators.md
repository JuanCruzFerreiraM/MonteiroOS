# HARV-03 — Yield & Productivity Indicators

## Metadata
- ID: HARV-03
- Module: Harvest
- Stage: 2
- Status: Planned
- Priority: P1
- Domains: `FRONTEND` `BACKEND` `DATABASE` `ANALYTICS`
- Dependencies: HARV-02, PROD-01

## Objective

Show production indicators for a cantero and a cultivation cycle from recorded measurements, with the definition and the gaps visible.

## Business Value

The business wants more commercially acceptable flowers per cultivated area. That comparison is impossible while totals hide missing discards, missing area, or mixed units.

## Functional Description

For a cycle, and for each cantero in it, the product shows the indicators defined in [HARVEST_AND_YIELD.md](../domain/HARVEST_AND_YIELD.md):

- harvested quantity, summed only within a unit;
- discarded quantity, summed only within a unit;
- commercially acceptable quantity, harvested minus discarded when both exist in the same unit;
- quantity per square meter, only when a measured area is stored and the acceptable quantity exists.

Each figure shows the formula in plain language and the measurements that fed it. Mixed units are listed separately instead of being forced into one total. A missing discard, a missing area, or a missing measurement is labeled missing. It is not shown as zero.

Progress notes from HARV-01 are not inputs to these formulas.

The screen does not say that a practice caused a result.

## Expected Behavior

- A cycle with two stem measurements shows their sum in stems.
- A cycle with stems and bunches shows two totals.
- A cantero without area shows the quantity and marks per-square-meter as missing.
- A measurement without discard shows commercially acceptable quantity as incomplete for that line.
- The indicator updates when a measurement is added; it is not a separately edited number.

## Business Rules

- Definitions in the harvest domain document are the calculation contract.
- No global ramo-to-vara factor and no default area are applied.
- A derived vara figure is shown only when every measurement included in it cites a presentation with an explicit vara count, and the figure is labeled as derived from those presentations. The recorded ramo total remains beside it.
- Indicators display the unit they use. Ramo and vara totals are not added together.
- Correlation is not presented as causation.

## Data Requirements

No new stored facts. The view reads harvest measurements, units, cantero or vidriera area, and cycle identity. It does not persist a second official total.

## User Interactions

- Open a cycle and read the indicators.
- Open a cantero's contribution.
- Follow a total back to the measurements.

## Acceptance Criteria

- [ ] Two measurements of 10 stems and 5 stems on the same cycle display 15 stems, and the screen names the sum.
- [ ] A ramo measurement on that cycle is not added into the vara total.
- [ ] The indicator shows the unit of each total.
- [ ] A vara figure is not derived from ramos when any included measurement lacks a presentation with an explicit vara count.
- [ ] When every contributing measurement has a discard in the same unit, the commercially acceptable quantity equals harvested minus discarded.
- [ ] When a discard is missing, the commercially acceptable quantity for that measurement is shown as incomplete and is not treated as equal to the harvested quantity.
- [ ] Quantity per square meter is shown only when area is recorded, and the area value is visible next to the result.
- [ ] When area is absent, the per-square-meter indicator is explicitly missing.
- [ ] A progress percentage on the harvest event does not change any indicator.
- [ ] The screen does not contain a statement that a practice caused the result.

## Edge Cases & Validation

- A cycle with no measurements shows an empty indicator state rather than zeros.
- Area stored on the cantero is preferred for a cantero indicator. Vidriera area is not divided by four to invent a bed area.
- Negative results are shown if discards were confirmed above the harvested quantity, and the indicator is marked as inconsistent inputs.

## Out of Scope

- Side-by-side comparison of several cycles (HARV-04).
- Monetary value.
- Forecasts and statistical tests.

## Dependencies & Integration Points

- HARV-02 measurements and optional area from PROD-01.
- HARV-04 reuses these definitions.
- Domain definitions: [HARVEST_AND_YIELD.md](../domain/HARVEST_AND_YIELD.md#indicator-definitions).

## Open Questions

- [OQ-03](../OPEN_QUESTIONS.md#oq-03) blocks using progress notes in these formulas.
- [OQ-04](../OPEN_QUESTIONS.md#oq-04) may later add a measurement definition. Until then, units are not converted across stems, bunches, and plants.
