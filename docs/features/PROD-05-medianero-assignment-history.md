# PROD-05 — Medianero Assignment History

## Metadata
- ID: PROD-05
- Module: Production
- Stage: 1
- Status: Planned
- Priority: P1
- Domains: `FRONTEND` `BACKEND` `DATABASE`
- Dependencies: CORE-03, PROD-01

## Objective

Record which medianero is responsible for a vidriera over time, without erasing previous assignments.

## Business Value

Box letters and later cost questions refer to the medianero of an area. Responsibility changes, and past operations must still show who was assigned then.

## Functional Description

On a vidriera, the user either assigns a person who currently holds the medianero role or marks the vidriera as directly managed by Monteiro. Both are explicit. Direct management does not create a person named Monteiro or a fictitious medianero.

An assignment has a start date and an optional end date. Ending an assignment closes it. Assigning someone else, or switching to direct management, creates a new interval. The previous interval remains. A vidriera has at most one open responsibility interval. Assignments are independent of cultivation cycles. Production recorded during an interval stays attributable to that interval after a later change.

## Expected Behavior

- The vidriera detail shows the current medianero, or that it is directly managed, when an open interval exists.
- A history list shows closed assignments with start and end.
- Assigning a person who does not hold the medianero role is rejected.
- A second open assignment for the same vidriera is rejected.
- Ending an assignment does not delete it.
- Changing the current medianero does not alter the name stored on the closed interval.

## Business Rules

- Historical assignments are not overwritten. See [PEOPLE_AND_RESPONSIBILITIES.md](../domain/PEOPLE_AND_RESPONSIBILITIES.md) and [ADR 0006](../decisions/0006-medianero-financial-rules-deferred.md).
- The assignment does not encode payment, product supply, or a revenue share.
- A vidriera is either assigned to one medianero or directly managed. It is not both, and it does not require a placeholder person.
- The assignment does not copy itself onto harvest quantities or infer who pays for inputs.

## Data Requirements

| Fact | Required |
| --- | --- |
| Vidriera | Yes |
| Person with the medianero role | Required for a medianero interval; absent for direct management |
| Start date | Yes |
| End date | No, while open |

## User Interactions

- From the vidriera, choose a medianero and a start date.
- End the assignment.
- Read the history.

## Acceptance Criteria

- [ ] A vidriera can be assigned to a medianero.
- [ ] A person without the medianero role cannot be assigned.
- [ ] A vidriera can be marked directly managed without creating a person.
- [ ] A second open responsibility interval on the same vidriera is rejected.
- [ ] Ending an assignment keeps it in history with the end date and allows a new assignment or direct management.
- [ ] Assignment changes preserve historical responsibility: the closed interval still shows the original medianero.
- [ ] Two vidrieras may have different open medianeros at the same time.
- [ ] No cost share or settlement field is required or defaulted.
- [ ] Business persons do not require software accounts.

## Edge Cases & Validation

- An end date before the start date is rejected.
- An assignment that overlaps a closed interval on the same vidriera is rejected.
- Deactivating the person after assignment leaves the history readable and blocks a new assignment of that person.

## Out of Scope

- More than one medianero at the same time. [OQ-22](../OPEN_QUESTIONS.md#oq-22) is resolved against that case.
- Copying the assignment onto each operation or cycle.
- Box letters (COMM-01).

## Dependencies & Integration Points

- CORE-03 for people and the medianero role.
- PROD-01 for the vidriera.
- COMM-01 may display the medianero associated with a box; it does not read this assignment as proof of cultivation origin.

## Open Questions

- [OQ-12](../OPEN_QUESTIONS.md#oq-12) is non-blocking. Extra profile fields wait for that answer.
- [OQ-22](../OPEN_QUESTIONS.md#oq-22) is resolved: one medianero, or direct management, never both at once.
