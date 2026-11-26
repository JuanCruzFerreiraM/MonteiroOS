# TRACE-01 — Production Activity History

## Metadata
- ID: TRACE-01
- Module: Operations
- Stage: 1
- Status: In Progress
- Priority: P0
- Domains: `FRONTEND` `BACKEND` `DATABASE`
- Dependencies: OPS-01

## Objective

Show the operational history of a vidriera and of a cultivation cycle from the records already stored.

## Business Value

The reason to register an operation is to reconstruct what happened. The history view is that reconstruction.

## Functional Description

The vidriera detail lists recent operations in reverse chronological order of the occurrence time, not the time the row was written or edited. The full history view adds server-side filters for type, an inclusive Argentine calendar range, and cycle. The cycle filter can select one cycle or the operations stored with no cycle. Clearing the filters returns to the unfiltered list. An empty filtered list says that the filter matched nothing.

Each entry shows the Spanish type label, the occurrence time, whether the record is manual or a confirmed scheduled occurrence, the cycle or "Sin ciclo", notes when present, and the actual interval when one was stored. The entry links to the existing operation page. It does not list varieties or canteros as the scope of the operation. There is one row per operation.

A cycle view lists the operations whose saved cycle reference is that cycle. Membership is not inferred from dates. An operation with no cycle appears on the vidriera and not on a cycle. A finalized cycle keeps this list.

The list is paginated in the database. Order is occurrence time descending, then operation identifier descending, so a timestamp tie does not skip or repeat a row. The page returns at most the requested limit and a cursor for the next, older page. The existing index on vidriera and occurrence time supports the query. No second history table is stored.

The history is read-only. Corrections happen by editing the operation through OPS-01. The vidriera of an operation stays fixed, and a scheduled operation keeps its type.

Recorded operations, schedule expectations, and occurrence resolutions are different facts:

- An operation is completed work. Manual records and confirmed scheduled occurrences are both operations. Only these rows appear in the history.
- A schedule revision says what was expected. TRACE-01 does not list it as work that happened.
- A resolution is a person's decision about one expected occurrence. Confirmation creates an operation and keeps the expected timestamps beside the actual ones. An explicit non-occurrence stays a resolution and is not shown as completed work. A scheduled or unverified occurrence is calculated and is not an operation.

The vidriera keeps the schedule summary and the link to the confirmation screen separate from the history list.

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
- [ ] An operation saved with no cycle is labeled "Sin ciclo" and does not appear on any cycle's history.
- [ ] An operation linked to a cycle appears on that cycle's history.
- [ ] A finalized cycle's history remains available and unchanged after a newer cycle starts.
- [ ] Filtering by type shows only that type, and clearing the filter restores the other operations.
- [ ] A vidriera with no operations shows an empty state that points back to recording an operation.
- [ ] Once OPS-03 is in place, an operation that targets two vidrieras is listed once on each vidriera, and both entries open the same operation.

## Edge Cases & Validation

- A date filter with the end before the start is rejected.
- A calendar day is inclusive in America/Argentina/Buenos_Aires. The bounds are the local midnight and the next local midnight, not UTC midnight. An overnight interval belongs to the day its actual start falls on.
- Operations are ordered by occurrence time, not by edit time. Equal timestamps stay in identifier order across pages.
- Notes that are empty do not show a blank section title.
- A cursor that cannot be read is rejected.

## Out of Scope

- Editing from inside a read-only summary beyond a link to the operation form.
- Harvest totals, costs, and photographs. Attachment counts may appear after TRACE-02 without this feature storing files.
- Cross-vidriera analytics.

## Dependencies & Integration Points

- OPS-01 writes the records this feature reads. PROD-01 and PROD-03 provide the pages that host the lists.
- OPS-02, OPS-03, OPS-04, and TRACE-02 enrich the same entries when they are implemented.

## Open Questions

- [OQ-23](../OPEN_QUESTIONS.md#oq-23) is non-blocking. The label for a missing cycle is "outside a cycle" until the business prefers another phrase.
