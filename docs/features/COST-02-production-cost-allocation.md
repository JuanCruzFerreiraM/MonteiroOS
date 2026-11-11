# COST-02 — Production Cost Allocation

## Metadata
- ID: COST-02
- Module: Cost
- Stage: 3
- Status: Planned
- Priority: P2
- Domains: `FRONTEND` `BACKEND` `DATABASE`
- Dependencies: COST-01, PROD-03

## Objective

Record direct and indirect production costs against a cycle, a vidriera, or a quinta, without inventing a split.

## Business Value

Product costs are only part of production cost. Labor, energy, water, and overhead have to be recorded as themselves, and shared costs have to stay shared until a method is chosen.

## Functional Description

The user records a cost with a category, an amount, a currency, a direct or indirect flag, an actual or estimate flag, and a scope. Categories are agricultural products, labor, water, energy, materials, packaging, transportation, and shared overhead.

Scope is one of: an operation, a cultivation cycle, a vidriera, a quinta, or several vidrieras. A product-consumption cost from COST-01 is already an operation-scoped agricultural-product cost and appears in this feature's totals. This feature does not duplicate it.

Each cost keeps three different facts:

- **Purchaser.** Who bought the input. The usual purchaser is the business, Monteiro. The form may offer that value, and the user can change it. A person is not created to represent the business.
- **Physical consumption.** Where or on which operation the input was used. This is the scope already stored for the cost or the application.
- **Economic responsibility.** Who bears the cost. It defaults to empty. The purchaser is not copied into it.

There is no percentage split. Monteiro generally purchases inputs; that fact does not decide the share a medianero bears.

An indirect cost can be allocated only when the user chooses a method and the inputs are stored with the result. The methods available in this feature are: leave unallocated, or allocate by equal share across a set of vidrieras the user explicitly selects. No method uses area, yield, or a medianero formula, because those bases are not validated. The equal-share result stores the vidriera list and the amount each received. Changing the source cost does not silently rewrite a stored allocation; the user reruns it.

Labor cost does not invent a wage from OPS-04 participants. The user enters an amount if they know it.

## Expected Behavior

- A direct energy cost on a cycle appears in that cycle's direct costs.
- An indirect overhead on a quinta appears as unallocated until the user allocates it.
- Equal share across two selected vidrieras stores half on each and shows the method.
- A cycle total lists known costs and a separate unknown count for application lines whose COST-01 status is unknown.
- Unknown is not added as zero.

## Business Rules

- Direct and indirect stay distinct. Purchaser, physical consumption, and economic responsibility stay distinct. See [INVENTORY_MODEL.md](../domain/INVENTORY_MODEL.md#costs) and [ADR 0006](../decisions/0006-medianero-financial-rules-deferred.md).
- Missing amounts stay missing.
- Currency is not converted. Totals are per currency.

## Data Requirements

| Fact | Required |
| --- | --- |
| Category | Yes |
| Amount and currency | Yes, on a cost the user enters |
| Direct or indirect | Yes |
| Actual or estimate | Yes |
| Scope | Yes |
| Purchaser: the business or a person | No. The form may offer the business and must not write that value into economic responsibility |
| Economic responsibility | No |
| Allocation method and inputs | Required only when an allocation result is stored |

## User Interactions

- Add a cost on a cycle or a vidriera.
- Record a quinta-level overhead and leave it unallocated.
- Allocate that overhead equally across chosen vidrieras and read the stored split.
- See COST-01 lines included in the cycle view.

## Acceptance Criteria

- [ ] A direct cost saved on a cycle appears in that cycle's direct total for its currency.
- [ ] An indirect cost saved on a quinta is excluded from a cycle's direct total and shown as unallocated.
- [ ] Allocating an indirect cost by equal share across two explicitly selected vidrieras stores both shares and the method.
- [ ] A cost with an empty economic responsibility can be saved.
- [ ] Setting the purchaser to Monteiro leaves economic responsibility empty.
- [ ] Physical consumption and economic responsibility are stored as separate facts.
- [ ] No cost is given a medianero percentage by default.
- [ ] Application lines with unknown COST-01 status are counted as unknown and are not summed as zero.
- [ ] Amounts in two currencies are not added together.
- [ ] A labor cost can be saved without an OPS-04 participant and without a wage rate catalog.

## Edge Cases & Validation

- An amount of zero is rejected. Unknown cost is represented by leaving the COST-01 line unknown, not by a zero row.
- An allocation that selects zero vidrieras is rejected.
- A negative amount is rejected.

## Out of Scope

- Medianero settlements and automatic shares based on yield or contract (OQ-14).
- Per-bunch margin (COST-03).
- A general ledger.
- Currency conversion.

## Dependencies & Integration Points

- COST-01 for product consumption. PROD-03 for cycles. PROD-01 for vidrieras and quintas.
- OPS-04 is not required. Participants may be cited in a note; they are not a cost engine.
- COST-03 reads the totals produced here.

## Open Questions

- [OQ-13](../OPEN_QUESTIONS.md#oq-13) and [OQ-14](../OPEN_QUESTIONS.md#oq-14) block default responsibility and any non-equal, unvalidated split.
