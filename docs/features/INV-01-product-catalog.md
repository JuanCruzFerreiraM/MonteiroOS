# INV-01 — Product Catalog

## Metadata
- ID: INV-01
- Module: Product catalog
- Stage: 1
- Status: Planned
- Priority: P1
- Domains: `FRONTEND` `BACKEND` `DATABASE`
- Dependencies: CORE-01, CORE-02

## Objective

Maintain a reusable catalog of cultivation products that applications can search and extend during data entry.

## Business Value

Product names typed differently on each application cannot be compared or costed. A catalog gives every application the same identity.

## Functional Description

Users search products by commercial name. If none fits, they can create one without discarding the form they started from. Before creation, possible duplicates are shown.

A product stores the commercial name, an optional manufacturer, a category, an optional formulation, an optional presentation, a standard unit, optional identification text, and an active flag. Categories are an extensible list. Fertilizer and crop protection are available as initial category labels, not as a regulatory scheme.

The catalog stores no on-hand quantity, location, or purchase price.

## Expected Behavior

- Search shows matches before the create action.
- Creating a product with the same commercial name and an empty manufacturer as an existing product is rejected after the duplicate is shown.
- The same commercial name with a different manufacturer can be saved after the user confirms it is not a duplicate.
- An inactive product remains on past applications and is omitted from the default search.
- Identification text is optional. The form does not require a registration number.

## Business Rules

- A product is not stock. See [ADR 0005](../decisions/0005-product-catalog-separate-from-stock.md) and [INVENTORY_MODEL.md](../domain/INVENTORY_MODEL.md).
- The system stores identification text the user supplies and does not check it against a regulator.
- The standard unit comes from CORE-02.

## Data Requirements

| Fact | Required |
| --- | --- |
| Commercial name | Yes |
| Manufacturer | No |
| Category | Yes |
| Formulation or composition | No |
| Presentation | No |
| Standard quantity unit | Yes |
| Identification or regulatory text | No |
| Active flag | Yes |

## User Interactions

- Search and create from the catalog screen.
- The same search and create is available inside an application form in OPS-02, without losing entered lines.

## Acceptance Criteria

- [ ] A product search presents existing matches before offering creation.
- [ ] A product can be saved with a name, a category, and a standard unit, leaving manufacturer, formulation, presentation, and identification empty.
- [ ] Saving a duplicate commercial name with no manufacturer is rejected and the existing product is shown.
- [ ] A quantity unit that is not in the unit catalog is rejected.
- [ ] Deactivating a product hides it from default search and leaves a historical reference readable.
- [ ] The product screen does not ask for or display a stock quantity.

## Edge Cases & Validation

- An empty name or a missing category is rejected.
- Category labels can be added. A product cannot be saved with an empty category.
- Deleting a referenced product is rejected.

## Out of Scope

- Storage locations, stock, suppliers, and prices (INV-02, INV-03, INV-04, COST-01).
- Application recommendations or dose checks.
- A regulatory compliance workflow.

## Dependencies & Integration Points

- CORE-02 for the standard unit.
- OPS-02 application lines reference products.
- Domain rules: [INVENTORY_MODEL.md](../domain/INVENTORY_MODEL.md).

## Open Questions

- [OQ-06](../OPEN_QUESTIONS.md#oq-06) is non-blocking. The standard unit is whatever the user selects from the catalog.
