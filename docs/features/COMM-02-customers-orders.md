# COMM-02 — Customers & Orders

## Metadata
- ID: COMM-02
- Module: Commercial
- Stage: 4
- Status: Planned
- Priority: P3
- Domains: `FRONTEND` `BACKEND` `DATABASE`
- Dependencies: CORE-01, PROD-02, CORE-02

## Objective

Keep wholesale customers and the quantities they request.

## Business Value

Orders are the demand the packing day tries to meet. They are not invoices and they are not a second harvest record.

## Functional Description

Users maintain customers with a name, optional contact, and an active flag. An order belongs to a customer and has a date, a status of draft, confirmed, or cancelled, and lines. A line has a variety, a quantity, and a unit.

Confirming an order does not create a sale, a dispatch, or a stock movement. Agricultural-product inventory is untouched. Cancelling a confirmed order keeps the order readable and sets the status to cancelled.

## Expected Behavior

- A draft order can be edited.
- A confirmed order can still have its lines corrected, and the correction is what later sales see if they link to it.
- A cancelled order cannot be dispatched later.
- Search finds customers by name before create.

## Business Rules

- An order is a request, not a sale and not a flower stock withdrawal. See [COMMERCIAL_TRACEABILITY.md](../domain/COMMERCIAL_TRACEABILITY.md).
- No tax, invoice number, or credit limit is required.

## Data Requirements

| Fact | Required |
| --- | --- |
| Customer name | Yes |
| Customer contact | No |
| Customer active flag | Yes |
| Order customer, date, status | Yes |
| Line variety, quantity, unit | Yes |

## User Interactions

- Create a customer and an order.
- Add lines, confirm, or cancel.
- Find a past order from the customer.

## Acceptance Criteria

- [ ] A customer can be saved with only a name.
- [ ] An order line requires a variety, a quantity greater than zero, and a catalog unit.
- [ ] Confirming an order does not create a sale, a dispatch, a harvest, or an inventory movement.
- [ ] A cancelled order remains readable and is not offered as a dispatch source.
- [ ] A duplicate customer name is shown before save.
- [ ] An inactive customer cannot be used on a new order and remains on old orders.

## Edge Cases & Validation

- An order with no lines cannot be confirmed.
- A draft order can exist with no lines.
- Cancelling is rejected if a sale already references the order, until the sale link is removed in COMM-04. Before COMM-04 exists, cancel is always available.

## Out of Scope

- Prices and payments (COMM-04).
- WhatsApp or voice capture of orders.
- Credit control and invoicing.

## Dependencies & Integration Points

- PROD-02 varieties and CORE-02 units.
- COMM-03 and COMM-04 may reference orders later.

## Open Questions

None. How orders are captured today may be refined by [OQ-17](../OPEN_QUESTIONS.md#oq-17) without blocking this record.
