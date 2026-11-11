# COMM-03 — Truck Loading & Dispatch

## Metadata
- ID: COMM-03
- Module: Commercial
- Stage: 4
- Status: Planned
- Priority: P3
- Domains: `FRONTEND` `BACKEND` `DATABASE`
- Dependencies: COMM-01

## Objective

Record which boxes were loaded for a delivery and identify the transport in the terms the business already uses.

## Business Value

Dispatch is the moment a box leaves the farm. Sales and traceability need to know whether a box actually went.

## Functional Description

A dispatch has a date, a transport label the user types, optional notes, and the boxes loaded onto it. The transport label is free text, such as a truck name the business already uses. There is no vehicle registry.

A box can be on at most one dispatch. The user can remove a box before the dispatch is marked departed. After departure, removal is a correction that stays visible: the box leaves the dispatch and the dispatch shows that the box was removed, with the time and the user.

An optional link to an order records intent. Loading does not require an order and does not create a sale.

## Expected Behavior

- Adding a box to a dispatch shows the box as loaded.
- Adding that box to a second dispatch is rejected.
- Marking the dispatch departed freezes the casual remove action and requires an explicit correction.
- A box that is not on a dispatch remains available to load.

## Business Rules

- Loading is not a sale. See [COMMERCIAL_TRACEABILITY.md](../domain/COMMERCIAL_TRACEABILITY.md).
- One physical box is not loaded twice.

## Data Requirements

| Fact | Required |
| --- | --- |
| Dispatch date | Yes |
| Transport label | Yes |
| Notes | No |
| Linked order | No |
| Departed time | No, until departed |
| Boxes currently loaded | No, although a departed dispatch with zero boxes is rejected |
| Correction note when a box is removed after departure | Yes, on that correction |

## User Interactions

- Create a dispatch, add boxes, and mark it departed.
- Remove a box before departure.
- Correct a departed dispatch by removing a box with a reason.

## Acceptance Criteria

- [ ] A user can create a dispatch with a date and a transport label and add a box.
- [ ] The same box cannot be added to two dispatches.
- [ ] Removing a box before departure leaves the box unloaded and the dispatch without that box.
- [ ] A departed dispatch rejects a silent removal and accepts a removal that stores a correction note, the user, and the time.
- [ ] Creating a dispatch does not create a sale or change harvest quantities.
- [ ] A box with origin unknown can be loaded.

## Edge Cases & Validation

- Marking departure with no boxes is rejected.
- A cancelled order cannot be linked.
- Duplicate adds of the same box on one dispatch are ignored as a single load.

## Out of Scope

- Route planning, GPS, and a fleet register.
- Customer signatures.
- Automatic sale creation on departure.

## Dependencies & Integration Points

- COMM-01 boxes. COMM-02 orders are an optional link and not a hard dependency for the first version of loading; the data requirement allows the link when COMM-02 exists.
- COMM-04 may cite the dispatch.

## Open Questions

None specific to loading. Origin precision remains [OQ-16](../OPEN_QUESTIONS.md#oq-16).
