# COST-01 — Agricultural Product Consumption Costs

## Metadata
- ID: COST-01
- Module: Cost
- Stage: 3
- Status: Planned
- Priority: P2
- Domains: `FRONTEND` `BACKEND` `DATABASE`
- Dependencies: OPS-02, INV-01, CORE-02

## Objective

Attach a cost to the products recorded on an application, and show whether that cost is actual or estimated.

## Business Value

Application quantities become production cost only when a price is known and labeled. A missing price must stay missing so margin is not understated.

## Functional Description

For each application line, the user can record a unit cost and a currency, or select a purchase line from INV-04 as the price source when that feature exists. A cost that comes from a purchase line is marked actual. A cost typed without a purchase source is marked estimate. The user can also leave the cost unknown.

The consumption quantity is the application quantity. Creating the cost does not create a stock withdrawal and does not change the application.

The line cost is the application quantity converted to the unit the price uses, when CORE-02 allows the conversion. If conversion is impossible, the cost stays uncalculated and the screen says why.

No cost is allocated to a medianero.

## Expected Behavior

- An application line with no price shows cost unknown.
- An estimated unit cost shows the line total and the estimate label.
- An actual unit cost from a purchase shows the line total and the actual label.
- Two products on one application produce two cost lines.
- Changing the application quantity recalculates the cost from the stored unit cost; it does not rewrite the purchase.

## Business Rules

- Actual and estimate are different. Unknown is not zero. See [INVENTORY_MODEL.md](../domain/INVENTORY_MODEL.md#costs).
- Physical consumption recorded here is the application quantity, not a warehouse withdrawal.
- Economic responsibility is out of scope for this feature.

## Data Requirements

| Fact | Required |
| --- | --- |
| Application line | Yes |
| Cost status: unknown, estimate, or actual | Yes |
| Unit cost and currency | Required for estimate and actual; absent for unknown |
| Price source | Required for actual: a purchase line or another source the user names as a recorded purchase reference |
| Computed line amount | Present only when quantity and unit cost convert |

## User Interactions

- Open an application and set a unit cost, or link a purchase line.
- Leave a line unknown.
- Read the application with costs labeled.

## Acceptance Criteria

- [ ] An application line with no cost record is displayed as cost unknown, not as zero.
- [ ] Entering a unit cost without a purchase source saves it as an estimate and shows the line amount when the units convert.
- [ ] Linking a purchase line saves the cost as actual and shows that purchase as the source.
- [ ] An application with two products shows two independent cost lines.
- [ ] A unit cost whose unit does not convert to the application quantity is stored without a computed amount, and the screen states that the amount is not calculated. It is not stored as zero.
- [ ] Saving a cost does not create an inventory movement and does not change the application quantity.
- [ ] No field assigns the cost to a medianero.

## Edge Cases & Validation

- A negative unit cost is rejected.
- A currency is required whenever a unit cost is present.
- An inactive product's historical line can still receive a cost.

## Out of Scope

- Labor, water, energy, and overhead (COST-02).
- Margin (COST-03).
- Splitting the cost across vidrieras when the operation is shared. Until COST-02, a shared operation's product cost stays on the operation and is visible from each vidriera without being divided.

## Dependencies & Integration Points

- OPS-02 application lines, INV-01 products, CORE-02 conversions.
- INV-04 is an optional price source. COST-01 can ship with manual estimates before purchases exist.
- Domain rules: [INVENTORY_MODEL.md](../domain/INVENTORY_MODEL.md#costs).

## Open Questions

- [OQ-06](../OPEN_QUESTIONS.md#oq-06) is non-blocking.
- [OQ-13](../OPEN_QUESTIONS.md#oq-13) blocks a default payer and does not block an explicit cost on the line.
