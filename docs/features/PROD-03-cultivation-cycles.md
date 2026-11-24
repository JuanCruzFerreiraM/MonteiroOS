# PROD-03 — Cultivation Cycle Management

## Metadata
- ID: PROD-03
- Module: Production
- Stage: 1
- Status: In Progress
- Priority: P0
- Domains: `FRONTEND` `BACKEND` `DATABASE`
- Dependencies: PROD-01

## Objective

Start, finalize, and retain the cultivation cycle of a vidriera.

## Business Value

Operations and harvests are meaningful only inside a cycle. The business also needs every past cycle to remain available for comparison.

## Functional Description

From the vidriera detail, a user starts a cultivation cycle. The vidriera may have only one active cycle. When work is finished, the user finalizes the cycle. Finalized cycles stay in a history list on the vidriera and remain readable.

Starting a cycle records the planting date and does not require varieties, colors, or a commercial size. Allocations arrive in PROD-04. A vidriera with no cycle is valid and is where preparation is recorded until a cycle starts.

Partial harvests do not open a second cycle and do not finalize the current one. The cycle stays active until a person finalizes it. Finalized cycles keep their planting date, allocations, operations, harvests, and observations.

## Expected Behavior

- Starting a cycle on a vidriera with no active cycle sets that cycle active and records its start.
- Starting a second cycle while one is active is rejected, and the existing cycle is identified in the error.
- Finalizing requires an end that is not before the start, and leaves the cycle queryable.
- After finalizing, a new cycle can start.
- Cycle periods for the same vidriera cannot overlap.

## Approved decisions

- The cycle starts on the actual planting date. That date is the cycle start. It ends only when an operator finalizes it and records the end date. A partial harvest does not finalize the cycle and does not start another one.
- Cleaning, preparation, and maintenance done before planting are not assigned to the next cycle. They can later be recorded on the vidriera with no cycle. This feature does not infer an owner, allocate cost, or attach that work to a future cycle. Cost attribution for preparatory work stays outside the MVP. [OQ-23](../OPEN_QUESTIONS.md#oq-23) remains open for the local name and for whether operators treat the work as part of the next crop.
- One vidriera has many historical cycles and at most one active cycle. Every cycle belongs to exactly one vidriera and covers that vidriera as a whole. Canteros do not have their own cycles.
- Starting a cycle does not require a flower type, variety, color, commercial size, crop allocation, or harvest quantity.
- Status is not stored. An empty end date means the cycle is active. A recorded end date means it is finalized, so the two facts cannot disagree.
- Dates are calendar dates. Ranges are inclusive: a cycle that ends on the day another starts overlaps, and the next calendar day does not. An open cycle occupies every later date.
- Dates and notes may be corrected in place. The correction keeps the cycle identifier and the vidriera, keeps an active cycle active, and keeps a finalized cycle finalized. It is rejected when the new period would overlap another cycle of the same vidriera. Previous values are not retained. An audit log is not part of this feature.

## Business Rules

- One active top-level cycle per vidriera. The vidriera is planted as a whole. See [ADR 0003](../decisions/0003-one-active-cultivation-cycle.md).
- Partial harvesting does not create or complete a cycle.
- Finalized cycles are not deleted by finalization.
- A cycle belongs to one vidriera.

## Data Requirements

| Fact | Required |
| --- | --- |
| Vidriera | Yes |
| Status: active or finalized | Yes. Derived from the end date. It is not a separate column. |
| Planting date, stored as the cycle start | Yes |
| End date | Required when finalized; empty while active |
| Notes | No |

## User Interactions

- On the vidriera detail, start a cycle and see it as the active cycle.
- Finalize it from the same view.
- Open a finalized cycle from the history list.

## Acceptance Criteria

- [ ] A user can start a cycle for a vidriera and see it on that vidriera's detail.
- [ ] A user cannot start a second active cycle for the same vidriera.
- [ ] A different vidriera can have its own active cycle at the same time.
- [ ] Finalizing a cycle keeps it listed under historical cycles and clears the active cycle.
- [ ] A historical cycle remains readable after finalization, including its start and end.
- [ ] An end date before the start date is rejected.
- [ ] A new cycle whose start overlaps the previous cycle's period is rejected.
- [ ] Starting a cycle does not require a commercial size, a variety, or a color.
- [ ] A harvest recorded against the active cycle leaves that cycle active.

## Edge Cases & Validation

- Finalizing an already finalized cycle is rejected.
- A vidriera with no cycle shows an empty state that offers start, and does not invent a cycle.
- Notes may be empty.

## Out of Scope

- Crop allocation (PROD-04).
- Automatically attaching operations, including pre-planting work (OPS-01 chooses the cycle at recording time).
- Cost attribution for preparation done without a cycle.
- Reopening a finalized cycle. Corrections to dates may be edited with validation; the status does not silently return to active.
- An audit log of the values replaced by a correction.
- Nested cycles inside canteros.

## Dependencies & Integration Points

- PROD-01 supplies the vidriera.
- OPS-01, TRACE-01, PROD-04, and HARV-01 reference cycles.
- Domain model: [PRODUCTION_MODEL.md](../domain/PRODUCTION_MODEL.md).

## Open Questions

- [OQ-23](../OPEN_QUESTIONS.md#oq-23) is non-blocking. A vidriera may exist with no active cycle, and preparatory work stays there until someone records it against a cycle on purpose.

## Implementation notes

The behaviors above are covered by the API, the database constraints, and the vidriera screen. The feature stays In Progress until that behavior is accepted. The acceptance item about a harvest leaving the cycle active waits for HARV-01, which is the feature that records a harvest.

Overlap is rejected in PostgreSQL with an exclusion constraint. It uses the `btree_gist` extension because the constraint compares the vidriera identifier with equality and a date range with overlap. Core GiST has no equality operator class for `uuid`. Downgrade drops the cycle table and leaves the extension installed.
