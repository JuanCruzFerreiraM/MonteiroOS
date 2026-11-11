# COMM-01 — Harvest Lots & Boxes

## Metadata
- ID: COMM-01
- Module: Commercial
- Stage: 4
- Status: Planned
- Priority: P3
- Domains: `FRONTEND` `BACKEND` `DATABASE`
- Dependencies: HARV-01, PROD-02, CORE-03

## Objective

Group harvest events into lots and record the boxes prepared for the wholesale market, including mixed or unknown origin.

## Business Value

The market currently sees a box letter tied to a medianero. The business needs that commercial identity and, when it knows more, the harvests inside the box.

## Functional Description

A harvest lot groups one or more harvest events. A lot may also exist with no events yet, as a packing placeholder, and events can be attached later.

A box has an identifier, an optional associated medianero, and one or more content lines. A content line has a variety, a quantity, a unit, and either one or more harvest lots, or an explicit origin of unknown. The identifier can be the letter used today. Letters are not assumed unique across time; uniqueness is the box record itself. The user may reuse a letter on a new box.

The medianero on the box is a commercial mark. The screen does not present it as the vidriera that grew the flowers.

Creating a box does not change harvest measurements.

## Expected Behavior

- A box can be saved with a letter, a medianero, a variety, a quantity, and origin unknown.
- A content line can reference two lots from different vidrieras.
- A content line cannot reference a lot and simultaneously say the origin is unknown.
- Harvest events remain unchanged after they are added to a lot.

## Business Rules

- Medianero identification alone does not establish cultivation origin. See [COMMERCIAL_TRACEABILITY.md](../domain/COMMERCIAL_TRACEABILITY.md).
- Origin status on a content line is exact, partial, or unknown. Exact origin cites harvest events that identify the cycle, variety, and cantero. Partial origin cites what is known and leaves the rest empty. Unknown origin cites nothing.
- The quantity on a partial or unknown line is not divided across vidrieras.
- A medianero letter does not fill origin.
- A content line may also carry commercial size, color, and presentation. Those are independent of the planting allocation.

## Data Requirements

| Fact | Required |
| --- | --- |
| Lot identifier | Yes |
| Harvest events on a lot | No |
| Box identifier | Yes |
| Associated medianero | No |
| Content variety | Yes |
| Content quantity and unit | Yes |
| Origin status: exact, partial, or unknown | Yes |
| Linked harvest events | Required for exact origin; optional for partial; absent for unknown |
| Commercial size, color, and presentation | No |

## User Interactions

- Create a lot and attach harvest events.
- Create a box, enter the letter, optionally pick a medianero, and add content lines.
- Mark a line's origin unknown, or search lots to attach.

## Acceptance Criteria

- [ ] A box can be saved with an identifier and one content line whose origin is unknown.
- [ ] A content line can record exact origin through harvest events that name the cycle, variety, and cantero.
- [ ] A content line can record partial origin without assigning its quantity to every vidriera in a quinta.
- [ ] A content line is not both unknown and linked to a harvest event.
- [ ] Selecting a medianero does not set the vidriera, cycle, or cantero.
- [ ] Commercial size, color, and presentation can be stored on a line and can differ from the planting allocation.
- [ ] The box screen states that the medianero mark does not identify the cultivation origin.
- [ ] Reusing an identifier string on a second box is allowed, and the two boxes remain distinct records.
- [ ] Attaching a harvest event to a lot does not change that event's measurements.
- [ ] A content quantity requires a catalog unit.

## Edge Cases & Validation

- A box with no content lines is rejected.
- A lot can include events from more than one cycle.
- An inactive variety cannot be added to a new line.

## Out of Scope

- Customers and orders (COMM-02).
- Loading a truck (COMM-03).
- Prices (COMM-04).
- Requiring a vidriera on every box.

## Dependencies & Integration Points

- HARV-01 events, PROD-02 varieties, CORE-02 units, CORE-03 people for the optional medianero.
- PROD-05 assignment history is not copied onto the box. The user selects the medianero associated with the letter.
- COMM-05 reads these links.

## Open Questions

- [OQ-15](../OPEN_QUESTIONS.md#oq-15) and [OQ-16](../OPEN_QUESTIONS.md#oq-16) block a mandatory single origin.
- [OQ-24](../OPEN_QUESTIONS.md#oq-24) is non-blocking while the identifier is an explicit string.
- [OQ-12](../OPEN_QUESTIONS.md#oq-12) is non-blocking.
