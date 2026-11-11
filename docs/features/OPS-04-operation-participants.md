# OPS-04 — Operation Participants & Responsibilities

## Metadata
- ID: OPS-04
- Module: Operations
- Stage: 1
- Status: Planned
- Priority: P1
- Domains: `FRONTEND` `BACKEND` `DATABASE`
- Dependencies: OPS-01, CORE-03

## Objective

Record who performed an operation and who was responsible for it, separately from who entered it.

## Business Value

The person at the keyboard is often not the person who did the work. Traceability that assumes otherwise attributes work to the wrong people.

## Functional Description

On an operation, the user may add participants. Each participant is a person and a kind: performer or responsible. The same person may be both, as two links or one link with both kinds, as long as the operation shows both facts. Several performers are allowed. Zero participants are allowed.

The recording person, when OPS-01 has one, is displayed and is not automatically added as a performer. There is no software account to copy onto the operation.

## Expected Behavior

- Saving an operation with no participants succeeds.
- Saving three performers shows all three.
- The recording person, when set, remains even when a different performer is selected.
- A deactivated person cannot be newly added and stays visible if already linked.
- Removing a participant does not delete the person or the operation.

## Business Rules

- Performer, responsible person, and recording person are different relationships. See [PEOPLE_AND_RESPONSIBILITIES.md](../domain/PEOPLE_AND_RESPONSIBILITIES.md).
- Not every activity has a human executor.
- Participants do not assign a wage or a cost share.

## Data Requirements

| Fact | Required |
| --- | --- |
| Operation | Yes |
| Person | Yes, on each participant link |
| Kind: performer, responsible, or both | Yes, on each link |

Zero links are valid.

## User Interactions

- Search people and add them as performer or responsible.
- Remove a participant.
- See the recording person, when set, as context distinct from performers.

## Acceptance Criteria

- [ ] An operation can be saved with no performer and no responsible person.
- [ ] An operation can list multiple performers.
- [ ] The same person can be marked performer and responsible on one operation.
- [ ] The recording person is not added as a performer unless explicitly selected.
- [ ] A Monteiro employee and a medianero can both be performers on one operation.
- [ ] Multiple people can be recorded on one operation.
- [ ] Performer, responsible person, and recording person stay distinguishable.
- [ ] Business persons do not require software accounts.
- [ ] Removing one performer leaves the other participants and the operation in place.

## Edge Cases & Validation

- The same person cannot be added twice for the same kind.
- An empty participant row is rejected rather than stored as a blank name.

## Out of Scope

- Labor cost and wages (COST-02).
- Medianero assignment (PROD-05), which is about the vidriera rather than one operation.
- Requiring an employee role. Any person in the registry may participate. The employee role remains available for filtering, not as a gate.

## Dependencies & Integration Points

- OPS-01 for the operation and the optional recording person.
- CORE-03 for people.
- TRACE-01 displays participants when this feature is present.

## Open Questions

None.
