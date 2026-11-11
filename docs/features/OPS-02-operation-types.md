# OPS-02 — Operation Types & Structured Data

## Metadata
- ID: OPS-02
- Module: Operations
- Stage: 1
- Status: Planned
- Priority: P1
- Domains: `FRONTEND` `BACKEND` `DATABASE`
- Dependencies: OPS-01, CORE-02, INV-01

## Objective

Capture the fields that make each operation type useful, without treating a program or a note as proof that something else happened.

## Business Value

A generic note cannot answer how long irrigation ran or which product was applied. Structured fields make those answers queryable.

## Functional Description

The operation form changes with the type. Existing OPS-01 operations remain valid when the structured fields are empty. New records of a type enforce that type's required fields.

| Type | Required structured data | Optional |
| --- | --- | --- |
| Irrigation | Duration, or a start and an end | Water volume and a volume unit, when known |
| Artificial lighting | A flag that the record is either a program or an observed occurrence, plus the intended or observed on/off interval | Notes |
| Black nylon covering | An action of raise or lower, or a covered/exposed interval | Notes |
| Heating (*dar fuego*) | Activation time and duration | Environmental note |
| Product application | At least one line with a product, a quantity, and a unit | Notes |
| Manual labor | A task description | Duration |
| Observation | A condition description | Notes beyond that description |

Application lines use the product catalog. The user searches, sees matches, and can create a product without losing the lines already entered. Units come from CORE-02 and must fit the quantity being expressed: a duration uses a time unit, an application quantity uses a unit of mass, volume, or rate.

A lighting program is stored as a program. It does not create an observed occurrence.

Workers on a labor record are not entered here. OPS-04 attaches people.

## Expected Behavior

- Choosing irrigation asks for time in a time unit and rejects a mass unit.
- Choosing application allows several products on one operation.
- A lighting record saved as a program does not appear as an observed occurrence in history labels.
- An observation can be saved with a description and no performer.
- Manual labor can be saved with a task and no worker.

## Business Rules

- One operation remains one record. Structured fields do not fan out per cantero.
- A configured program is not an observed operation. See [OPERATIONS_MODEL.md](../domain/OPERATIONS_MODEL.md).
- Observations are operations. See [ADR 0007](../decisions/0007-observations-as-operations.md).
- The feature does not encode hardware schedules beyond the fields in the table.

## Data Requirements

The common OPS-01 facts stay. In addition:

| Type | Facts |
| --- | --- |
| Irrigation | Start and end, or duration and a time unit. End is not before start. |
| Lighting | Record kind: program or observed. Interval start and end. |
| Nylon | Either an event (raise or lower) and a time, or an interval with a state of covered or exposed. |
| Heating | Activation time, duration, time unit. Environmental note optional. |
| Application | One or more lines: product, quantity greater than zero, unit. |
| Labor | Task description. Optional duration and time unit. |
| Observation | Description text. |

## User Interactions

- Select the type and complete the fields the type requires.
- On an application, search products, pick one, or create one inline after reviewing duplicates.
- Add another application line.
- Save an observation that will later accept photographs in TRACE-02.

## Acceptance Criteria

- [ ] An irrigation cannot be saved with a duration unit that is not a time unit.
- [ ] An irrigation can be saved with a duration and no water volume.
- [ ] A product application can reference catalog products and standardized quantities.
- [ ] An irrigation with an end before its start is rejected.
- [ ] A lighting record requires the program-or-observed flag, and a program is labeled as a program wherever the operation is shown.
- [ ] A nylon record requires either a raise or lower event or a covered/exposed interval.
- [ ] A heating record requires an activation time and a duration.
- [ ] An application can reference multiple catalog products on one operation.
- [ ] An application without a product line is rejected.
- [ ] A product search presents existing matches before offering product creation, and creation returns to the application with the new product selected.
- [ ] An application quantity cannot be saved with a unit from an incompatible dimension.
- [ ] A labor record can be saved with a task description and no participant.
- [ ] An observation can be saved with a description and is included in the operation list.
- [ ] An OPS-01 operation that predates structured fields still opens and can receive structured data later.

## Edge Cases & Validation

- A quantity of zero or less is rejected on an application line.
- An inactive product cannot be added to a new line and remains on a line already saved.
- Rate units are accepted on an application line. They are not converted into a total volume by this feature.

## Out of Scope

- Proving that a controller executed a program.
- Stock withdrawal when an application is saved.
- Photographs (TRACE-02).
- Multiple vidrieras (OPS-03).
- Naming extra labor types beyond free text (OQ-11).

## Dependencies & Integration Points

- OPS-01 for the operation.
- CORE-02 for units and INV-01 for products.
- COST-01 later reads application lines. It does not change them.
- Domain rules: [OPERATIONS_MODEL.md](../domain/OPERATIONS_MODEL.md).

## Open Questions

- [OQ-06](../OPEN_QUESTIONS.md#oq-06), [OQ-09](../OPEN_QUESTIONS.md#oq-09), [OQ-10](../OPEN_QUESTIONS.md#oq-10), [OQ-11](../OPEN_QUESTIONS.md#oq-11), and [OQ-25](../OPEN_QUESTIONS.md#oq-25) are non-blocking for the fields in this specification. Volume stays optional when it was not measured.
- [OQ-07](../OPEN_QUESTIONS.md#oq-07) and [OQ-08](../OPEN_QUESTIONS.md#oq-08) block device integration and block treating a program as an occurrence. They do not block the manual record defined here.
