# COMM-04 — Sales & Receipts

## Metadata
- ID: COMM-04
- Module: Commercial
- Stage: 4
- Status: Planned
- Priority: P3
- Domains: `FRONTEND` `BACKEND` `DATABASE`
- Dependencies: COMM-02, COMM-01, PROD-02

## Objective

Record quantities sold, their prices, and the money received against those sales.

## Business Value

Revenue has to be a stored fact before any margin exists. Receipts show what was collected without turning the product into an accounting system.

## Functional Description

A sale has a customer, a date, a currency, and lines. Each line has a variety, a quantity, a unit, and a unit price. It may also name a commercial size, a color, and a presentation. Those attributes explain the price. They are not a second product master, and a price is not required to exist before the sale. Optional links point at an order and at boxes or a dispatch. The sale quantity is what was sold; it does not have to equal the order or the box quantity, and both stay visible when they differ.

A receipt records an amount of money, a currency, a date, and the sale it applies to. Several receipts may apply to one sale. The outstanding amount is the sale total minus receipts in the same currency. A receipt in another currency is shown separately and does not reduce the outstanding amount.

The customer view lists sales and the outstanding amount per currency. It does not post journals, taxes, or credit notes.

No medianero settlement is calculated.

## Expected Behavior

- A sale of 10 bunches at a unit price shows the extended amount.
- A partial receipt reduces the outstanding amount and leaves the sale open.
- Receipts that equal the sale total show the sale as settled.
- A receipt larger than the outstanding amount is rejected.
- Linking boxes does not change box contents.

## Business Rules

- A sale is not an invoice system. A receipt is not a ledger entry. See [COMMERCIAL_TRACEABILITY.md](../domain/COMMERCIAL_TRACEABILITY.md).
- Price may depend on variety, commercial size, color, presentation, and the unit. Two lines that differ in size may have different unit prices. The system does not invent a price list.
- Settlements with medianeros are excluded until OQ-17 is answered.

## Data Requirements

| Fact | Required |
| --- | --- |
| Customer, date, currency | Yes |
| Line variety, quantity, unit, unit price | Yes |
| Line commercial size, color, and presentation | No |
| Link to an order, dispatch, or boxes | No |
| Receipt amount, currency, date, sale | Yes, on a receipt |

## User Interactions

- Create a sale for a customer, add lines, optionally attach boxes.
- Record a receipt against the sale.
- Read the customer's outstanding amounts.

## Acceptance Criteria

- [ ] A sale line with quantity and unit price displays the extended amount in the sale currency.
- [ ] Two sale lines for the same variety can carry different commercial sizes and different unit prices.
- [ ] A sale line can record color and presentation without requiring those values on the cultivation cycle.
- [ ] A sale can be saved without an order and without boxes.
- [ ] Linking a box does not change the box quantity or the harvest.
- [ ] A receipt smaller than the sale total leaves an outstanding balance equal to the difference.
- [ ] Receipts that sum to the sale total show no outstanding balance in that currency.
- [ ] A receipt that exceeds the outstanding balance is rejected.
- [ ] A receipt in a different currency does not change the sale's outstanding balance and is listed on its own.
- [ ] The customer view does not offer a journal entry, tax line, or medianero settlement.

## Edge Cases & Validation

- A zero or negative price is rejected.
- A zero or negative receipt is rejected.
- A cancelled order cannot be linked to a new sale.
- Deleting a sale that has receipts is rejected. The user voids the sale with a reason, the void remains visible, and outstanding balance becomes zero only through that explicit void.

## Out of Scope

- Invoices, taxes, and a chart of accounts.
- Medianero settlements (OQ-17, OQ-14).
- Currency exchange rates.

## Dependencies & Integration Points

- COMM-02 customers. COMM-01 boxes are optional links. COMM-03 dispatches are optional links.
- COST-03 reads sale amounts.

## Open Questions

- [OQ-17](../OPEN_QUESTIONS.md#oq-17) blocks settlements and does not block sales and receipts as specified here.
