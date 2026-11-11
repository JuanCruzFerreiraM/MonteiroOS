# COMM-05 — Commercial Traceability

## Metadata
- ID: COMM-05
- Module: Commercial
- Stage: 4
- Status: Planned
- Priority: P3
- Domains: `FRONTEND` `BACKEND` `ANALYTICS`
- Dependencies: COMM-01, HARV-01, PROD-03

## Objective

Show the path from a box back to harvests and cycles when the links exist, and show the gap when they do not.

## Business Value

The medianero letter is the traceability the business has today. This view adds cultivation origin where packing recorded it, and refuses to invent it otherwise.

## Functional Description

From a box, the user sees the identifier, the associated medianero if any, each content line, and for every linked lot the harvest events, canteros, vidrieras, cycles, and quintas. Lines marked origin unknown say so. A line with several lots lists every origin.

From a cultivation cycle, the user sees the boxes whose lots include harvest events of that cycle. A box that also contains another cycle shows both.

The medianero letter is labeled as a commercial mark.

The view is read-only and does not copy origin onto the box.

## Expected Behavior

- A box linked to one harvest shows that harvest's vidriera and cycle.
- A box with two lots from two vidrieras shows both.
- A box with origin unknown shows unknown origin and no guessed vidriera.
- A cycle page lists only boxes actually linked to it.

## Business Rules

- Unknown and multiple origins stay explicit. See [COMMERCIAL_TRACEABILITY.md](../domain/COMMERCIAL_TRACEABILITY.md).
- The medianero on the box is not displayed as the growing location.

## Data Requirements

No new stored facts. The view reads boxes, content lines, lots, harvest events, canteros, vidrieras, cycles, quintas, and the optional medianero.

## User Interactions

- Open a box and read its origins.
- Open a cycle and read the boxes linked to it.
- Jump from an origin line to the harvest event.

## Acceptance Criteria

- [ ] A box whose content links to one harvest event shows that event's cantero, vidriera, cycle, and quinta.
- [ ] A box whose content links to harvest events from two vidrieras shows both vidrieras.
- [ ] A content line marked origin unknown displays origin unknown and does not display a vidriera.
- [ ] The medianero associated with the box is visible and described as a commercial mark.
- [ ] A cycle lists a box that links to it and omits a box that does not.
- [ ] A box that links to two cycles appears on both cycle views.
- [ ] Editing is not offered on the traceability view; links open the underlying records.

## Edge Cases & Validation

- A lot with no harvest events shows the lot and states that no harvest is attached.
- A harvest whose cantero was later deactivated still resolves to that cantero's name.
- A box on a dispatch shows the dispatch link when COMM-03 exists, without requiring it for origin.

## Out of Scope

- Inferring origin from the medianero assignment history.
- QR codes and printed labels.
- Changing lots from this screen.

## Dependencies & Integration Points

- COMM-01 for boxes and lots, HARV-01 for events, PROD-01 and PROD-03 for place and cycle names.
- COMM-03 dispatch status is optional context.

## Open Questions

- [OQ-15](../OPEN_QUESTIONS.md#oq-15) and [OQ-16](../OPEN_QUESTIONS.md#oq-16) are already reflected by allowing many origins and unknown origin. They block any feature that would fill a missing origin automatically.
