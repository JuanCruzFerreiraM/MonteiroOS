# INV-04 — Suppliers & Purchasing

## Metadata
- ID: INV-04
- Module: Inventory
- Stage: 3
- Status: Planned
- Priority: P2
- Domains: `FRONTEND` `BACKEND` `DATABASE`
- Dependencies: INV-01, INV-03

## Objective

Record who supplies cultivation products and what was purchased, separately from the stock receipt.

## Business Value

A purchase is the commercial acquisition. A receipt is the physical arrival. Keeping them apart lets the business record a bill before the goods are in a location, or a count that does not match the bill.

## Functional Description

Users maintain suppliers with a name, optional contact, and an active flag. A purchase has a supplier, a date, and lines. Each line has a product, a quantity, a unit, and an optional price with a currency. The currency defaults to ARS and can be changed. No prices are seeded.

Confirming a purchase does not increase stock. The user can create a receipt movement from a purchase line, and the receipt stores the link. The received quantity may differ from the purchased quantity. Both remain visible.

## Expected Behavior

- A purchase with a price stores the price and currency.
- A purchase line without a price is valid, and the price is shown as unknown.
- Creating a linked receipt increases stock by the received quantity only.
- The purchase line still shows the purchased quantity after the receipt.

## Business Rules

- Supplier, purchase, and stock receipt are different records. See [INVENTORY_MODEL.md](../domain/INVENTORY_MODEL.md).
- Economic responsibility for medianero vidrieras is not defaulted from the supplier. See [ADR 0006](../decisions/0006-medianero-financial-rules-deferred.md).

## Data Requirements

| Fact | Required |
| --- | --- |
| Supplier name | Yes |
| Supplier contact | No |
| Supplier active flag | Yes |
| Purchase supplier and date | Yes |
| Line product, quantity, unit | Yes |
| Line price and currency | No; currency is required when a price is present |

## User Interactions

- Create a supplier, then a purchase with lines.
- From a line, record a receipt into a location for a quantity the user enters.
- Leave a line unreceived.

## Acceptance Criteria

- [ ] A supplier can be saved with only a name.
- [ ] A purchase line can be saved without a price, and the price is displayed as unknown.
- [ ] A price without a currency is rejected.
- [ ] Saving a purchase does not change any stock balance.
- [ ] Recording a receipt from a purchase line creates an INV-03 receipt linked to that line and changes stock only by the received quantity.
- [ ] The purchased quantity remains unchanged when the received quantity differs.
- [ ] An inactive supplier cannot be used on a new purchase and remains on old purchases.

## Edge Cases & Validation

- A duplicate supplier name is shown before save and rejected when it matches an existing active supplier, ignoring case.
- A line quantity of zero or less is rejected.
- Two receipts may be linked to one line. The purchase does not silently close.

## Out of Scope

- Accounts payable beyond the purchase record.
- Who pays on behalf of a medianero (OQ-13).
- Sales of flowers (COMM-04).

## Dependencies & Integration Points

- INV-01 for products and INV-03 for the optional receipt.
- COST-01 may use a purchase unit price as an actual cost source.

## Open Questions

- [OQ-13](../OPEN_QUESTIONS.md#oq-13) blocks a default payer. It does not block recording a supplier and a purchase.
- [OQ-18](../OPEN_QUESTIONS.md#oq-18) blocks treating old papers as imported purchases unless the user enters them explicitly.
