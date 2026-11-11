# HARV-01 — Partial Harvest Registration

## Metadata
- ID: HARV-01
- Module: Harvest
- Stage: 2
- Status: Planned
- Priority: P1
- Domains: `FRONTEND` `BACKEND` `DATABASE`
- Dependencies: PROD-03, PROD-04

## Objective

Record each harvest cut by variety and cultivation cycle, including repeated partial cuts of the same variety and cantero.

## Business Value

Maturity varies inside a bed. One date and one quantity cannot represent the crop. Each cut has to stay visible, and cutting one variety must not close the bed or the cycle.

## Functional Description

The user records a harvest event with its own date, a cultivation cycle, a variety, an origin status, and optional observations. Quantities, units, size, color, and quality belong to HARV-02. The event can be saved before those measurements exist.

Origin status is either:

- **Exact.** The event names one cantero of the cycle's vidriera.
- **Partial.** The cycle and variety are known, and the cantero is not. The gap stays empty. The quantity is not spread across canteros.

Unknown vidriera is not a harvest event. Commercial quantities with unknown production origin are recorded in COMM-01.

When the chosen cantero has allocations, the variety picker prefers those varieties and still allows another variety from the same flower types only after the user confirms it is not one of the allocated varieties. A harvest does not create or edit an allocation.

A progress note may be stored. It is not interpreted as area, plants, or a completed percentage until [OQ-03](../OPEN_QUESTIONS.md#oq-03) is answered.

Several events may share a variety and a cantero. They are independent rows with their own dates. Saving one does not replace another, does not empty the cantero, and does not finalize the cycle.

## Expected Behavior

- Two cuts of the same variety and cantero on different dates both remain.
- A cut of one variety leaves the other varieties on that cantero in place.
- A partial-origin event can be saved without a cantero.
- An exact-origin event without a cantero is rejected.
- A cantero from another vidriera is rejected.
- The cycle status is unchanged after the save.

## Business Rules

- Harvest scope is the variety inside a cycle, with the cantero when it is known. See [HARVEST_AND_YIELD.md](../domain/HARVEST_AND_YIELD.md).
- Operation scope stays at vidriera level and is not how harvests are stored.
- Partial harvesting does not create a cultivation cycle and does not complete one.
- Harvested plants stay out of production until the next planting. This feature does not infer that state from progress notes.
- Origin is not inferred from a medianero.

## Data Requirements

| Fact | Required |
| --- | --- |
| Date | Yes |
| Cultivation cycle | Yes |
| Variety | Yes |
| Origin status: exact or partial | Yes |
| Cantero of that cycle's vidriera | Required when origin is exact; absent when partial |
| Progress note | No |
| Observations | No |
| Recording person | No |

## User Interactions

- From the cycle, add a harvest, choose the variety and the date, and set exact or partial origin.
- For an exact origin, choose the cantero.
- Save another cut of the same variety later without deleting the first.

## Acceptance Criteria

- [ ] The same variety and cantero can have multiple harvest events on different dates.
- [ ] Every harvest event records its own date.
- [ ] A harvest event requires a variety and a cultivation cycle.
- [ ] An exact-origin event requires a cantero of that cycle's vidriera.
- [ ] A partial-origin event is saved without a cantero and does not assign the cut to every cantero in the vidriera.
- [ ] A harvest that names a cantero from another vidriera is rejected.
- [ ] Partial harvesting does not complete the cultivation cycle automatically.
- [ ] Saving a harvest does not remove other variety allocations on that cantero.
- [ ] A progress note can be saved and is not displayed as square meters, plant counts, or a completed bed.
- [ ] Historical harvests remain queryable after the cycle is finalized.
- [ ] The event does not store a software account. A recording person is optional.

## Edge Cases & Validation

- A harvest date more than one day in the future is rejected.
- Unknown origin is not offered on this form. The user is directed to commercial recording when the vidriera is unknown.
- Deactivating a cantero blocks a new exact-origin harvest and leaves old events readable.

## Out of Scope

- Quantities, units, size, color, quality, and estimate status (HARV-02).
- Yield math (HARV-03).
- Boxes and unknown commercial origin (COMM-01).
- Marking a bed empty from percentages.
- Completing a cycle from harvest activity (PROD-03).

## Dependencies & Integration Points

- PROD-03 for the cycle and PROD-04 for allocations and varieties.
- HARV-02 adds measurements on the event created here.
- Domain rules: [HARVEST_AND_YIELD.md](../domain/HARVEST_AND_YIELD.md).

## Open Questions

- [OQ-03](../OPEN_QUESTIONS.md#oq-03) blocks interpreting the progress note. Storing it is allowed.
- [OQ-02](../OPEN_QUESTIONS.md#oq-02) blocks a measured share of the bed. It does not block the event.
