# OPS-01 — Operation Registration

## Metadata
- ID: OPS-01
- Module: Operations
- Stage: 1
- Status: In Progress
- Priority: P0
- Domains: `FRONTEND` `BACKEND` `DATABASE`
- Dependencies: PROD-01, PROD-03

## Objective

Record a cultivation operation against one vidriera so the business can say what was done and when.

## Business Value

This is the first useful production record: a vidriera, a cycle, and an operation that can be reviewed later.

## Functional Description

From the vidriera detail, the user records an operation. The record stores the operation type, the time, the vidriera, an optional cultivation cycle, and notes. The user does not choose varieties or canteros. An optional recording person may be selected once CORE-03 exists; the operation does not require a software account.

The type list is the initial catalog: irrigation, artificial lighting, black nylon covering, cold-protection heating, product application, manual labor, and observation. Type-specific fields are not required in this feature. Notes carry the detail until OPS-02.

If the vidriera has an active cycle, the form defaults to that cycle. The user can choose no cycle, which is how preparation between cycles is stored. The user can explicitly select a finalized cycle of the same vidriera for backfill. The default is never a finalized cycle.

One save creates one operation. It is not copied onto the four canteros or onto each variety planted in them. Agricultural operations default to vidriera scope.

## Expected Behavior

- Saving from a vidriera shows the operation on that vidriera.
- The operation does not ask for a variety or a cantero.
- A cycle belonging to another vidriera is rejected.
- Two saves create two operations; the second does not overwrite the first.
- An operation with no cycle is accepted.

## Business Rules

- Scope at this stage is a single vidriera. See [ADR 0004](../decisions/0004-operation-scope-separate-from-yield.md).
- OPS-01 records an operation that already happened. It does not record a plan.
- A recurring schedule is [OPS-AUTO-01](OPS-AUTO-01-recurring-operation-scheduling.md). It is not evidence that work happened, and saving a manual lighting or nylon operation does not convert it into a scheduled occurrence.
- The optional cycle is stored on the operation while the operation belongs to one vidriera. OPS-03 may move that link onto a scope row. The selected cycle must belong to the same vidriera.
- The recorder, when named, is a person from the registry and may differ from a performer. Performers are OPS-04, so this feature does not require one. There is no software account on the operation.

## Data Requirements

| Fact | Required |
| --- | --- |
| Operation type, from the initial catalog | Yes |
| Time the operation occurred | Yes. Not in the future, aside from a five-minute clock tolerance |
| Vidriera | Yes. It cannot be changed after creation |
| Cultivation cycle of that vidriera | No |
| Notes | No |
| Actual start and end, for lighting and black nylon | No. Both ends, or neither. The end is after the start and is not in the future beyond the same tolerance |
| Origin | Yes. `manual` for this feature |
| Recording person | No |
| Recorded-at timestamp | Yes |

## User Interactions

- On the vidriera detail, choose a type, confirm the time and the cycle default, add optional notes, and save. Lighting and nylon may also include an actual interval.
- Correct the type, the occurrence time, the cycle, and the notes of a manual operation. Clearing the cycle is explicit. The vidriera stays the same, the identifier stays the same, and the record is not deleted.
- A confirmed scheduled operation keeps the type of its schedule. Its occurrence time is the actual interval start, so those two values are saved together. The expected interval stays on the resolution.

## Acceptance Criteria

- [ ] An operation can be recorded against a vidriera without selecting individual varieties or canteros.
- [ ] A user can save an operation for a vidriera with a type and a time, and see it on that vidriera.
- [ ] When the vidriera has an active cycle, the saved operation uses that cycle unless the user cleared it.
- [ ] The user can save an operation with no cycle while an active cycle exists.
- [ ] The user cannot save an operation against a cycle that belongs to a different vidriera.
- [ ] A finalized cycle is used only when the user explicitly selects it.
- [ ] Saving two operations creates two records and leaves both readable.
- [ ] The operation is stored once and is not duplicated for every cantero or variety.
- [ ] Saving an operation does not require a software account.
- [ ] An occurrence time in the future is rejected when the operation is recorded as completed.
- [ ] The form does not offer a planned or scheduled state.

## Edge Cases & Validation

- A missing type or time is rejected.
- An occurrence time later than the current time, beyond ordinary clock tolerance, is rejected. There is no 24-hour grace period.
- Editing type, time, cycle, notes, or a lighting/nylon interval does not create a second operation.
- An interval with only one end is rejected. Duration is not inferred when the end is missing.

## Out of Scope

- Structured payloads (OPS-02).
- Several vidrieras (OPS-03).
- Participants (OPS-04).
- Photographs (TRACE-02).
- Recurring schedules and their confirmation. That is [OPS-AUTO-01](OPS-AUTO-01-recurring-operation-scheduling.md). A manual operation remains available beside a schedule.
- The history browser beyond showing the new operation on the vidriera (TRACE-01).

## Dependencies & Integration Points

- PROD-01 for the vidriera and PROD-03 for cycles.
- CORE-01 for the shell. CORE-03, when present, supplies an optional recording person.
- TRACE-01 reads these records.
- Domain rules: [OPERATIONS_MODEL.md](../domain/OPERATIONS_MODEL.md).

## Open Questions

- [OQ-23](../OPEN_QUESTIONS.md#oq-23) is non-blocking. The safe behavior is an operation with no cycle.
