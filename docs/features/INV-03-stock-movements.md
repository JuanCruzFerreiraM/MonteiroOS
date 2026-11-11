# INV-03 — Stock & Inventory Movements

## Metadata
- ID: INV-03
- Module: Inventory
- Stage: 3
- Status: Planned
- Priority: P2
- Domains: `FRONTEND` `BACKEND` `DATABASE`
- Dependencies: INV-01, INV-02, CORE-02

## Objective

Record how much of a catalog product is at a location, and every change to that quantity, starting from explicit movements rather than an assumed opening balance.

## Business Value

The business cannot cost or replenish products if on-hand quantities are guesses. An explicit movement history shows where a balance came from.

## Functional Description

Stock is the quantity of one product at one location, derived from movements. Movement kinds are receipt, withdrawal, transfer, and adjustment. Each movement stores the product, quantity, unit, date, locations, and an optional note. A transfer has a source and a destination. A receipt, withdrawal, or adjustment has one location.

There is no opening balance until a user records a receipt or an adjustment. An adjustment is labeled as an adjustment so it is not mistaken for a purchase or a field application.

Saving a product application in OPS-02 does not create a withdrawal. A user may optionally link a withdrawal to an operation. The link does not copy or change the application quantity.

A withdrawal or transfer that exceeds the recorded balance is rejected. The error tells the user that the recorded balance may be incomplete and that an adjustment can establish it. The system does not insert a silent adjustment.

Units must belong to the same dimension as the product's standard unit. Conversion within the dimension is allowed when CORE-02 defines it.

## Expected Behavior

- A new product and location show no stock, not zero presented as counted.
- A receipt of 10 L makes the on-hand quantity 10 L.
- A withdrawal of 12 L against that balance is rejected.
- An application of 2 L does not change the 10 L until a withdrawal is recorded.
- A transfer decreases one location and increases the other by the same quantity in the same unit dimension.

## Business Rules

- Catalog product and stock quantity are different. See [ADR 0005](../decisions/0005-product-catalog-separate-from-stock.md).
- Application quantity and stock withdrawal are different.
- No imported opening inventory until OQ-18 is answered and the business marks the figures as adjustments.

## Data Requirements

| Fact | Required |
| --- | --- |
| Movement kind | Yes |
| Product | Yes |
| Quantity greater than zero | Yes |
| Unit compatible with the product | Yes |
| Date | Yes |
| Location, or source and destination for a transfer | Yes |
| Note | No |
| Optional link to an operation or, later, a purchase | No |
| Recording user | Yes |

On-hand quantity is derived. It is not edited directly.

## User Interactions

- Record a receipt, withdrawal, transfer, or adjustment.
- Read the derived balance and the movement list for a product at a location.
- From a withdrawal, optionally cite an operation.

## Acceptance Criteria

- [ ] Before any movement, a product at a location shows that no balance has been recorded, not a counted zero.
- [ ] A receipt increases the derived balance by the converted quantity.
- [ ] A withdrawal that exceeds the derived balance is rejected and does not change the balance.
- [ ] An adjustment of a stated quantity sets the movement history so the derived balance matches that quantity, and the movement is labeled adjustment.
- [ ] A transfer reduces the source and increases the destination by the same dimensionally converted quantity.
- [ ] Saving an application does not create a movement.
- [ ] A withdrawal linked to an operation leaves the application's quantity unchanged.
- [ ] A unit in an incompatible dimension is rejected.
- [ ] Deactivating a product blocks a new movement and leaves old movements readable.

## Edge Cases & Validation

- A transfer with the same source and destination is rejected.
- A movement for an inactive location is rejected.
- Negative quantities are rejected. A downward adjustment is an adjustment to a lower stated balance, not a negative quantity field.

## Out of Scope

- Purchase prices (INV-04).
- Automatic replenishment.
- Importing a spreadsheet of opening stock before the business confirms it.
- Flower inventory. This feature tracks cultivation products.

## Dependencies & Integration Points

- INV-01 products, INV-02 locations, CORE-02 units.
- OPS-02 operations may be cited and are not modified.
- COST-01 does not require a movement in order to cost an application.

## Open Questions

- [OQ-18](../OPEN_QUESTIONS.md#oq-18) blocks imported opening balances. Explicit adjustments remain available.
