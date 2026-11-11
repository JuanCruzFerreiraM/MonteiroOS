# PROD-04 — Crop Allocation Within a Cycle

## Metadata
- ID: PROD-04
- Module: Production
- Stage: 1
- Status: Planned
- Priority: P1
- Domains: `FRONTEND` `BACKEND` `DATABASE`
- Dependencies: PROD-02, PROD-03

## Objective

Record which varieties occupy each cantero during one cultivation cycle, including more than one variety in the same bed.

## Business Value

Harvest and later sales need the planted identity of a bed. A cantero is not limited to a single variety, and the planting must stay attached to the cycle that produced it.

## Functional Description

On a cycle, the user allocates a variety to a cantero of that cycle's vidriera. A cantero may receive several allocations. Different canteros may differ. A cantero may have none.

Each allocation stores the variety and, when known at planting, a color. Commercial size, quality, and presentation are not asked and cannot be stored here. A single allocation may later be harvested as more than one size or quality.

An optional portion note may be stored. Its meaning is not calculated until [OQ-02](../OPEN_QUESTIONS.md#oq-02) is answered. The note is not treated as area, length, or plant count.

Allocations belong to the cycle. Changing the active cycle does not change a finalized cycle. The cantero itself does not keep the current variety as its only history.

## Expected Behavior

- The cycle shows each cantero and every variety allocated to it.
- Two varieties can be saved on one cantero in one cycle.
- A color can be set or left empty.
- The form does not offer commercial size.
- An allocation cannot point at a cantero from another vidriera.
- Finalized cycles show the allocations they had. This feature does not edit them.

## Business Rules

- A cantero can contain multiple varieties in one cycle. See [PRODUCTION_MODEL.md](../domain/PRODUCTION_MODEL.md).
- A vidriera's four canteros may each hold their own mix.
- Cultivated identity is flower type, variety, and color when known.
- Commercial size is not required to start or describe a cycle.

## Data Requirements

| Fact | Required |
| --- | --- |
| Cultivation cycle | Yes |
| Cantero of that cycle's vidriera | Yes |
| Variety | Yes |
| Color | No |
| Portion note | No |

Commercial size, quality, and presentation are absent.

## User Interactions

- From the cycle, add a variety to a cantero, optionally choose a color, and save.
- Add another variety to the same cantero.
- Search varieties and create a missing one without losing the form.
- Clear one allocation on the active cycle.

## Acceptance Criteria

- [ ] One cantero can contain multiple varieties within a single cultivation cycle.
- [ ] A vidriera can contain varieties distributed among its four canteros.
- [ ] A second variety on the same cantero and cycle is saved beside the first.
- [ ] An allocation that references a cantero outside the vidriera is rejected.
- [ ] Color can be saved on an allocation and can also be left empty.
- [ ] Commercial size is not required when starting a cultivation cycle or when saving an allocation.
- [ ] Allocations remain associated with their original cycle after that cycle is finalized.
- [ ] A newer cycle's allocations do not replace the finalized cycle's allocations.
- [ ] The variety picker presents search matches before variety creation.
- [ ] A portion note, when entered, is stored as text and is not converted into area or plant count.

## Edge Cases & Validation

- The same variety and the same color cannot be allocated twice to the same cantero in the same cycle. A different color is a separate allocation.
- An inactive variety cannot be newly allocated and remains visible if it was allocated before deactivation.
- Clearing the last allocation leaves the cycle in place.

## Out of Scope

- A measured share of the bed (area, linear meters, or plant count) until OQ-02 is answered.
- Copying the previous cycle's allocations automatically.
- Harvest quantities and commercial grades.

## Dependencies & Integration Points

- PROD-02 for varieties and colors. PROD-03 for the cycle.
- HARV-01 uses these allocations as the planted origin of a cut. A harvest may still record a grade that the allocation does not have.

## Open Questions

- [OQ-02](../OPEN_QUESTIONS.md#oq-02) is non-blocking. Allocations are valid without a measured portion.
