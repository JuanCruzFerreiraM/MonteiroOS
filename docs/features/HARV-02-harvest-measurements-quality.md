# HARV-02 — Harvest Measurements & Quality Classification

## Metadata
- ID: HARV-02
- Module: Harvest
- Stage: 2
- Status: Planned
- Priority: P1
- Domains: `FRONTEND` `BACKEND` `DATABASE`
- Dependencies: HARV-01, CORE-02

## Objective

Record how much a harvest produced, in a controlled unit, and how much was discarded or placed in a quality class.

## Business Value

Commercially acceptable production cannot be computed from an unlabeled count. Quantity, unit, and discard have to be explicit.

## Functional Description

On a harvest event, the user adds measurements. Each measurement has a quantity, a unit, and a status of exact or estimated. It may also have a commercial size, a color, a presentation, a quality class, and a discarded quantity in the same dimension.

Ramo (bunch) and vara (stem) are both valid units. Choosing one does not fill the other. A presentation's explicit stem count is not applied unless that presentation is selected on the measurement, and even then the recorded quantity stays in the unit that was entered. Size, color, quality, and presentation are harvested or commercial attributes. They are not required to match the planting allocation, and one cycle may produce several sizes.

Quality classes come from a catalog the business maintains. The catalog starts empty. No class names are seeded. A measurement can be saved with quality unset, and the unset state is shown as missing rather than as a default class.

Discarded quantity is separate from quality. A missing discard is missing, not zero. When a discard is entered, it is a subset of that measurement's harvested quantity: zero or greater, and no larger than the harvested quantity. Both quantities use compatible units and the same measurement. A loss that is not part of the harvested quantity is a separate measurement or event. It is not entered by making the discard larger than the harvest.

Plants, stems, and bunches do not convert into each other.

## Expected Behavior

- A harvest event can carry more than one measurement, for example a stem count and a bunch count, without merging them.
- Selecting bunches does not ask for or apply a stem factor.
- Adding a quality class is a catalog action with duplicate warning, then the class is selectable.
- Deactivating a class hides it from new measurements and leaves old measurements readable.

## Business Rules

- Units come from CORE-02. See [ADR 0008](../decisions/0008-controlled-measurement-units.md).
- Commercially acceptable quantity is defined only when both the harvested quantity and the discard are present in a compatible unit. The definition is applied in HARV-03; this feature stores the inputs.
- For one measurement, `0 <= discarded_quantity <= harvested_quantity`. The two quantities share a dimension and that measurement's scope.
- Quality class names are business data. See [OQ-05](../OPEN_QUESTIONS.md#oq-05).

## Data Requirements

| Fact | Required |
| --- | --- |
| Harvest event | Yes |
| Quantity, greater than zero | Yes |
| Unit | Yes |
| Quantity status: exact or estimated | Yes |
| Commercial size for the variety's flower type | No |
| Color | No |
| Commercial presentation | No |
| Quality class | No |
| Discarded quantity | No |
| Discard unit | Required when a discard is entered; same dimension as the quantity |

Quality class catalog: name required, active flag required, description optional.

## User Interactions

- Open a harvest event, add a quantity and a unit, optionally a discard and a class.
- Add a quality class from the measurement form after search shows no match.
- Leave quality empty and save.

## Acceptance Criteria

- [ ] A measurement cannot be saved without a quantity and a catalog unit.
- [ ] A quantity cannot be saved with a unit that is inactive or unknown.
- [ ] A discarded amount in a different dimension from the harvested quantity is rejected.
- [ ] A discarded quantity greater than that measurement's harvested quantity is rejected.
- [ ] A discarded quantity of zero is accepted and is distinct from a missing discard.
- [ ] A measurement with no discard shows the discard as missing, and the stored discard is not zero.
- [ ] A measurement with no quality class is accepted and displayed as quality not recorded.
- [ ] The quality catalog has no seeded classes in a fresh database.
- [ ] A user can add a quality class, and a later measurement can reference it.
- [ ] Harvest measurements can distinguish exact quantities from estimates.
- [ ] A measurement in ramos is not given a vara quantity.
- [ ] Bunches are not automatically converted to stems.
- [ ] Commercial size may differ across harvested output from the same cultivation cycle.
- [ ] Size, color, quality, and presentation remain readable on the measurement after the cycle is finalized.
- [ ] Two measurements on one event are both retained.

## Edge Cases & Validation

- A discard greater than the harvested quantity is rejected. Confirmation does not override the subset rule.
- A negative discard is rejected.
- Zero and negative quantities are rejected.
- Deleting a class that is in use is rejected.

## Out of Scope

- Per-square-meter indicators (HARV-03).
- Packing those quantities into boxes (COMM-01).
- A fixed list of commercial grades.

## Dependencies & Integration Points

- HARV-01 for the event and CORE-02 for units.
- HARV-03 reads these measurements.
- Domain rules: [HARVEST_AND_YIELD.md](../domain/HARVEST_AND_YIELD.md).

## Open Questions

- [OQ-04](../OPEN_QUESTIONS.md#oq-04) and [OQ-05](../OPEN_QUESTIONS.md#oq-05) are non-blocking. Units stay explicit, and quality classes are not seeded.
- [OQ-26](../OPEN_QUESTIONS.md#oq-26) is non-blocking. A presentation is optional until the business defines one.
