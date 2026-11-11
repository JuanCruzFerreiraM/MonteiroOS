# OPS-03 — Multi-Vidriera Operations

## Metadata
- ID: OPS-03
- Module: Operations
- Stage: 1
- Status: Planned
- Priority: P1
- Domains: `FRONTEND` `BACKEND` `DATABASE`
- Dependencies: OPS-01

## Objective

Let one operation apply to several vidrieras and remain a single record.

## Business Value

Shared irrigation or a shared application should not be entered four or five times. Duplicate entry creates false history.

## Functional Description

The user adds one or more additional vidrieras to an operation's scope. The operation is stored once and appears in each selected vidriera's history. Removing a vidriera from the scope removes it from that history and leaves the others.

Each scoped vidriera may reference that vidriera's cultivation cycle, or none. The form defaults each active vidriera to its own active cycle. It does not copy one cycle onto every target.

Structured fields from OPS-02, when present, stay on the shared operation. This feature does not require OPS-02.

## Expected Behavior

- An operation saved for vidriera A and vidriera B has one identity.
- Opening the history of A and of B shows that same operation.
- Editing the notes changes what both vidrieras show.
- A cycle selected for A cannot be a cycle of B.
- Clearing B's cycle leaves A's cycle intact.

## Business Rules

- Physical scope and yield beds are different. The operation is not split by cantero. See [ADR 0004](../decisions/0004-operation-scope-separate-from-yield.md).
- Scope contains at least one vidriera.

## Data Requirements

| Fact | Required |
| --- | --- |
| Operation | Yes |
| One or more vidriera targets | Yes |
| Cycle for each target | No, and only a cycle of that vidriera |

## User Interactions

- While recording or editing an operation, search and add vidrieras.
- Review the cycle default per vidriera before saving.
- Remove a target.

## Acceptance Criteria

- [ ] An operation targeting multiple vidrieras is stored as one logical operation.
- [ ] A shared operation is stored once and remains visible from all affected vidrieras.
- [ ] The shared operation is not duplicated for every cantero or variety inside those vidrieras.
- [ ] The history entry on each vidriera links to the same operation identity.
- [ ] Updating the operation notes is visible from every targeted vidriera without a second edit.
- [ ] Removing one vidriera from the scope hides the operation from that vidriera and leaves it on the others.
- [ ] A scope with zero vidrieras is rejected.
- [ ] A cycle that does not belong to the targeted vidriera is rejected.
- [ ] Two targeted vidrieras can point at two different cycles, or at none.
- [ ] The operation is still not duplicated per cantero.

## Edge Cases & Validation

- Adding the same vidriera twice does not create two targets.
- An inactive vidriera cannot be newly added and remains if it was already in scope.
- An operation that was created for one vidriera under OPS-01 can gain a second vidriera.

## Out of Scope

- Splitting quantities across vidrieras.
- Applying an operation to a subset of canteros.
- A map-based multi-select.

## Dependencies & Integration Points

- OPS-01 for the operation. PROD-01 and PROD-03 are reached through that feature.
- TRACE-01 must list the shared operation on each vidriera once OPS-03 exists. The TRACE-01 specification includes that case.

## Open Questions

None.
