# CORE-03 — People & Roles Registry

## Metadata
- ID: CORE-03
- Module: People
- Stage: 1
- Status: Planned
- Priority: P1
- Domains: `FRONTEND` `BACKEND` `DATABASE`
- Dependencies: CORE-01

## Objective

Keep a reusable registry of people and the roles they hold, without treating every person as an employee or as a software user.

## Business Value

Operations, medianero assignments, and commercial marks all point at people. A single registry stops the same person from being retyped under conflicting names.

## Functional Description

Users create and search people. A person may hold one or more roles over a validity interval. The initial roles are medianero and employee. Roles are not mutually exclusive.

A person is not a software account. The MVP has no account to link. Deactivating a person removes them from new pickers and preserves history. Multi-user accounts, if they are ever added, must not replace this registry.

No real people are seeded.

## Expected Behavior

- Search by name returns active people and can include inactive people on request.
- Adding a role records a start date. Ending a role sets an end date and keeps the interval.
- A person can hold medianero and employee at the same time.
- A deactivated person still appears on operations and assignments already stored.
- The people screen does not create a login.

## Business Rules

- A medianero is not stored as an employee-only record. The role is explicit. See [PEOPLE_AND_RESPONSIBILITIES.md](../domain/PEOPLE_AND_RESPONSIBILITIES.md).
- Role history is not overwritten when a role ends.
- Business roles do not create a software account. The MVP does not have per-person logins. See [ADR 0009](../decisions/0009-single-user-desktop-first.md).

## Data Requirements

| Fact | Required |
| --- | --- |
| Person name | Yes |
| Contact details | No |
| Notes | No |
| Active flag | Yes |
| Role | Yes, on each role interval |
| Role start | Yes |
| Role end | No, while the role is current |
| Software account | Not stored. People are not application users. |

## User Interactions

- Create a person from the people list.
- Add or end a role.
- Search before creating a person, and show a similar name when one exists.

## Acceptance Criteria

- [ ] A person can be saved with only a name.
- [ ] The same person can have overlapping medianero and employee role intervals.
- [ ] Ending a role retains the start and end dates and the person record.
- [ ] A person can be selected as an operation participant without a software account.
- [ ] The registry exposes no sign-in, password, or account link.
- [ ] Deactivating a person hides them from the default search and leaves existing links readable.
- [ ] Creating a person shows a possible name match before the save completes.

## Edge Cases & Validation

- A role end before its start is rejected.
- An empty name is rejected.
- Deactivating a person does not remove historical operations or assignments.

## Out of Scope

- Vidriera assignments (PROD-05).
- Wages, settlements, and cost shares.
- Extra required profile fields beyond name. See OQ-12.
- Software accounts, including a future multi-user login. CORE-01 does not create them.

## Dependencies & Integration Points

- CORE-01 provides the shell only. It has no account to attach.
- PROD-05 requires the medianero role.
- OPS-04 selects people as participants.

## Open Questions

- [OQ-12](../OPEN_QUESTIONS.md#oq-12) is non-blocking for this feature. Additional required fields wait for that answer.
