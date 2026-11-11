# COST-03 — Unit Economics & Profitability

## Metadata
- ID: COST-03
- Module: Cost
- Stage: 4
- Status: Planned
- Priority: P3
- Domains: `FRONTEND` `BACKEND` `ANALYTICS`
- Dependencies: COST-02, COMM-04, HARV-02

## Objective

Show production cost, commercial cost, revenue, and margin for a cycle or a bunch when the underlying records exist.

## Business Value

The long-term question is what a bunch cost and what it returned. The answer is usable only when missing costs and missing revenue stay visible.

## Functional Description

For a cultivation cycle, the view lists:

- production costs from COST-02, grouped as direct and indirect, per currency;
- commercial costs in the categories packaging and transportation, per currency, when they were recorded on that cycle or on boxes linked to it;
- harvested quantities by unit from HARV-02;
- revenue from sale lines whose boxes or lots link to the cycle, per currency.

Margin is revenue minus known cost in the same currency. It is shown only when the user can see which costs were included. If any included application line is still cost-unknown, or revenue is absent, margin is incomplete rather than a number.

Per bunch uses harvested or sold quantities recorded in bunches. The view does not convert stems to bunches. Per square meter uses the HARV-03 rule and only a recorded area.

Production costs and commercial costs are separate subtotals. A packaging cost is not presented as a growing cost.

No medianero profit share is calculated.

The screen states that the figures describe recorded history. It does not claim a practice caused the margin.

## Expected Behavior

- A cycle with known costs and no linked sales shows cost and marks revenue and margin incomplete.
- A cycle with sales in ARS and costs in ARS shows margin in ARS.
- Costs in two currencies stay in two columns.
- A bunch indicator appears only for bunch quantities.
- Unallocated indirect costs are listed outside the cycle margin unless a COST-02 allocation assigned them to the cycle.

## Business Rules

- Definitions follow [COMMERCIAL_TRACEABILITY.md](../domain/COMMERCIAL_TRACEABILITY.md#cost-and-margin) and [INVENTORY_MODEL.md](../domain/INVENTORY_MODEL.md#costs).
- Unknown amounts are not zero.
- No stems-per-bunch factor is applied.
- Medianero settlement is not part of margin.

## Data Requirements

No new stored facts. The view reads COST-02 costs and allocations, COST-01 unknown counts, HARV-02 measurements, HARV-03 area rules, COMM-04 sales, and COMM-01 links from boxes to cycles.

## User Interactions

- Open a cycle's unit economics.
- See which sales and which costs were included.
- Switch the quantity basis between the units actually recorded.

## Acceptance Criteria

- [ ] A cycle with an ARS production cost and no linked sale shows the cost and marks revenue and margin incomplete.
- [ ] A cycle with ARS costs of a known amount and ARS revenue of a known amount shows margin as revenue minus those costs, and lists the costs included.
- [ ] An unknown COST-01 line on the cycle forces margin to incomplete even if other costs exist.
- [ ] Packaging and transportation costs are subtotaled separately from agricultural-product, labor, water, and energy costs.
- [ ] Amounts in different currencies are not combined into one margin.
- [ ] A per-bunch figure is shown only when a bunch quantity is recorded, and stems are not converted into bunches.
- [ ] A per-square-meter cost is omitted when area is missing.
- [ ] Unallocated indirect cost is visible and is excluded from the cycle margin.
- [ ] The view does not calculate a medianero share.
- [ ] The view does not state that a management practice caused the margin.

## Edge Cases & Validation

- A sale linked to boxes from two cycles does not assign the full revenue to both. Revenue is included only when the sale line's boxes link solely to the cycle being viewed, or the line is marked revenue not attributable and excluded. The screen says which rule applied.
- A voided sale is excluded from revenue.
- A cycle with no harvest and no cost shows an empty state.

## Out of Scope

- Financial statements, tax, and currency conversion.
- Medianero settlements (OQ-14, OQ-17).
- Forecast profit.
- Allocating one sale line across cycles by a guessed ratio.

## Dependencies & Integration Points

- COST-02 for costs, COMM-04 for revenue, HARV-02 for quantities, COMM-05 paths for linking boxes to cycles.
- HARV-03 area rules are reused and not redefined.

## Open Questions

- [OQ-04](../OPEN_QUESTIONS.md#oq-04) blocks any stem-to-bunch conversion.
- [OQ-14](../OPEN_QUESTIONS.md#oq-14) and [OQ-17](../OPEN_QUESTIONS.md#oq-17) block medianero profit. They do not block cycle margin from explicit costs and sales.
