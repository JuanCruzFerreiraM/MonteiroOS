# OPS-01 — Operation Registration

## Metadata
- ID: OPS-01
- Module: Operations
- Stage: 1
- Status: Planned
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
- A schedule is not created here and is not evidence that work happened.
- The recorder, when named, is a person from the registry and may differ from a performer. Performers are OPS-04, so this feature does not require one. There is no software account on the operation.

## Data Requirements

| Fact | Required |
| --- | --- |
| Operation type, from the initial catalog | Yes |
| Time the operation occurred | Yes |
| Vidriera | Yes |
| Cultivation cycle of that vidriera | No |
| Notes | No |
| Recording person | No |
| Recorded-at timestamp | Yes |

## User Interactions

- On the vidriera detail, choose a type, confirm the time and the cycle default, add optional notes, and save.
- Correct notes or the cycle link on an existing operation.

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

## Edge Cases & Validation

- A missing type or time is rejected.
- An occurrence time more than 24 hours in the future is rejected.
- Editing notes does not create a second operation.

## Out of Scope

- Structured payloads (OPS-02).
- Several vidrieras (OPS-03).
- Participants (OPS-04).
- Photographs (TRACE-02).
- The history browser beyond showing the new operation on the vidriera (TRACE-01).

## Dependencies & Integration Points

- PROD-01 for the vidriera and PROD-03 for cycles.
- CORE-01 for the shell. CORE-03, when present, supplies an optional recording person.
- TRACE-01 reads these records.
- Domain rules: [OPERATIONS_MODEL.md](../domain/OPERATIONS_MODEL.md).

## Open Questions

- [OQ-23](../OPEN_QUESTIONS.md#oq-23) is non-blocking. The safe behavior is an operation with no cycle.
