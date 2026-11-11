# TRACE-01 — Production Activity History

## Metadata
- ID: TRACE-01
- Module: Operations
- Stage: 1
- Status: Planned
- Priority: P0
- Domains: `FRONTEND` `BACKEND` `DATABASE`
- Dependencies: OPS-01

## Objective

Show the operational history of a vidriera and of a cultivation cycle from the records already stored.

## Business Value

The reason to register an operation is to reconstruct what happened. The history view is that reconstruction.

## Functional Description

The vidriera detail lists operations in reverse chronological order. Filters narrow by type and by date range. Each entry shows the type, time, cycle or an explicit "outside a cycle" label, the recording person when one was set, and notes when present. The entry does not list varieties as the scope of the operation. Opening an entry shows the full operation.

A cycle view lists the operations linked to that cycle. An operation with no cycle appears on the vidriera and not on a cycle.

When OPS-03 is implemented, a shared operation appears once in each targeted vidriera and uses the same identity. This feature's first release, before OPS-03, lists the single-vidriera operations from OPS-01.

The history is read-only. Corrections happen by editing the operation.

## Expected Behavior

- Recording an operation and opening the vidriera shows it without a second entry step.
- Finalized cycles still have a history view.
- Filters do not hide the fact that an empty result is caused by the filter.
- A shared operation, once OPS-03 exists, is not shown twice on the same vidriera.

## Business Rules

- History reads operations. It does not create a second copy. See [DATA_MODEL.md](../architecture/DATA_MODEL.md).
- Operations outside a cycle stay visible on the vidriera.
- The view does not compute yield or cost.

## Data Requirements

No new business facts. The view reads operations, scopes, cycles, and vidrieras. When later features exist, it also shows structured summaries, participants, and attachment counts without owning those records.

## User Interactions

- From the vidriera, scan history, filter, and open an operation.
- From a cycle, open the operations linked to it.
- Clear filters to return to the full list.

## Acceptance Criteria

- [ ] After an operation is saved for a vidriera, that vidriera's history lists it with type and time.
- [ ] The history entry does not repeat the operation once per cantero or variety.
- [ ] An operation saved with no cycle is labeled as outside a cycle and does not appear on any cycle's history.
- [ ] An operation linked to a cycle appears on that cycle's history.
- [ ] A finalized cycle's history remains available and unchanged after a newer cycle starts.
- [ ] Filtering by type shows only that type, and clearing the filter restores the other operations.
- [ ] A vidriera with no operations shows an empty state that points back to recording an operation.
- [ ] Once OPS-03 is in place, an operation that targets two vidrieras is listed once on each vidriera, and both entries open the same operation.

## Edge Cases & Validation

- A date filter with the end before the start is rejected.
- Operations are ordered by occurrence time, not by edit time.
- Notes that are empty do not show a blank section title.

## Out of Scope

- Editing from inside a read-only summary beyond a link to the operation form.
- Harvest totals, costs, and photographs. Attachment counts may appear after TRACE-02 without this feature storing files.
- Cross-vidriera analytics.

## Dependencies & Integration Points

- OPS-01 writes the records this feature reads. PROD-01 and PROD-03 provide the pages that host the lists.
- OPS-02, OPS-03, OPS-04, and TRACE-02 enrich the same entries when they are implemented.

## Open Questions

- [OQ-23](../OPEN_QUESTIONS.md#oq-23) is non-blocking. The label for a missing cycle is "outside a cycle" until the business prefers another phrase.
