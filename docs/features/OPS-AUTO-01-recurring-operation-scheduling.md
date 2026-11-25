# OPS-AUTO-01 — Recurring Operation Scheduling

## Metadata
- ID: OPS-AUTO-01
- Module: Operations
- Stage: 1
- Status: In Progress
- Priority: P0
- Domains: `FRONTEND` `BACKEND` `DATABASE`
- Dependencies: OPS-01, PROD-03

## Objective

Record the lighting and black-nylon intervals that a vidriera is expected to follow, and let a person confirm what actually happened, without operating equipment or filling one form per night.

## Business Value

Most lighting and nylon work repeats. The schedule keeps the expected interval. Confirmation, including an explicit "it did not happen", is the historical evidence. The two facts stay separate so later analysis can compare the plan with the confirmed interval.

## Schedule model

A schedule belongs to one vidriera and to one operation type: artificial lighting or black nylon. It is a series of revisions that share a stable series identifier.

Each revision stores:

- Effective start and end dates.
- Selected weekdays, Monday = 1 through Sunday = 7.
- Civil start and end clock times.
- Optional notes.
- Status: active, paused, or ended.
- Whether the revision generates occurrences. A pause does not.

An overnight interval is one occurrence. It belongs to the calendar day of the start and ends the next day. Example: 22:00–02:00 on 1 December starts that evening and ends at 02:00 on 2 December. Equal clock times are rejected. An empty weekday selection is rejected. The end date cannot precede the start date.

Periods of the same vidriera and type cannot overlap. Creating or editing a schedule does not replace another one silently. A conflicting period is rejected.

The schedule is not permanently tied to a cultivation cycle. Cycle association happens on the confirmed operation.

## Occurrence lifecycle

Occurrences are calculated for a requested date range of at most 62 days. The application does not store every future night and does not use a background worker.

| State | Meaning |
| --- | --- |
| Scheduled | The expected window has not ended. It is not completed work. |
| Unverified | The window has ended and nobody has resolved it. It is not completed work. |
| Confirmed | A person confirmed it. The result is an OPS-01 operation with origin `scheduled`. |
| Not occurred | A person recorded that it did not happen. There is no operation. |

The identity of an occurrence is the schedule series plus the start date. Revisions of the same series do not create a second identity for that date.

A window can be confirmed only after it has ended, with the same five-minute clock tolerance used by OPS-01. A future occurrence cannot be marked completed.

## Confirmation

One occurrence can be confirmed or marked as not occurred. Several unverified occurrences can be confirmed together, or marked as not occurred together.

A batch runs in one database transaction. Each item uses a savepoint. Items that succeed are kept together. A conflict or a validation error rolls back only that item. The response lists each item as confirmed, not occurred, unchanged, conflict, or invalid. HTTP 200 means the batch was processed, not that every item succeeded. An empty batch is rejected. A batch is limited to 31 occurrences.

Repeating the same outcome is idempotent and does not create another operation. A different outcome for an occurrence that was already resolved is a conflict and does not overwrite the first decision.

The default actual interval in a batch may copy the expected interval. That copy is stored as `assumed_from_schedule`. It is a value the operator accepted, not a measurement and not a sensor reading. If the operator enters different start and end times, the basis is `operator_entered`. Confirmation method for this version is `manual`, with the time of the confirmation.

Later correction of the actual interval, the cycle, and the notes uses the OPS-01 operation. The operation keeps the schedule type: changing lighting into nylon, or the reverse, is rejected. The occurrence time is stored as the same instant as the actual start. Sending a different occurrence time is rejected. An unchanged actual interval keeps its timing basis, `assumed_from_schedule` or `operator_entered`. The correction does not change the expected timestamps stored on the resolution.

## Scheduled and actual timestamps

Expected start and end are copied onto the resolution at confirmation and then left alone. Actual start and end live on the resolution and on the operation interval. Both pairs remain available. Example: nylon expected 18:00–08:00 the next day, actual 18:30–07:45 the next day.

A manual lighting or nylon operation can still be recorded while a schedule exists. It has origin `manual` and no resolution. It is not silently attached to an occurrence.

## Historical revisions

Editing times, weekdays, notes, or the end date applies from an effective date that is today or later. If today's window has already ended, the change starts tomorrow. The previous revision keeps its clock times and ends the day before the new revision.

Previously resolved occurrences keep their expected timestamps and outcomes. A change that would start on a day that already has a resolution is rejected. Ending a schedule can shorten the future part of the period. It cannot drop days that have already passed, and it cannot extend the period. Extending or changing times is a new revision.

Pausing stops generation from the effective date. Resuming starts it again from a later date. The paused days are not turned into expected work.

## Timezone

Calendar days and clock times are interpreted in America/Argentina/Buenos_Aires. That timezone is not stored on each row. Persisted instants are timezone-aware. Naive timestamps are rejected.

## Deduplication and errors

- Two manual saves remain two operations.
- Two confirmations of the same occurrence do not create two operations. A concurrent pair is settled by the unique constraint on series and date: one succeeds and the other is a conflict.
- Overlapping schedule periods return a conflict and leave the existing schedule unchanged.
- A cycle on confirmation must belong to the vidriera. The active cycle of today is not applied to a past occurrence. If one cycle contains the occurrence date, the form may suggest it. The user can clear it. No cycle is a valid result.

## MVP limitations

- No timer, PLC, sensor, or equipment control.
- No electricity, dose, worker assignment, harvest, cost, or forecast.
- No background job. Occurrences exist when a bounded range is queried, plus the explicit resolutions.
- Nylon is one coverage interval, not separate mandatory raise and lower operations.
- A confirmed scheduled operation keeps the type of its schedule revision. The database requires that type on the operation, the resolution, and the revision together, and requires the occurrence time to equal the actual start.
- TRACE-01's full history browser is not part of this feature. The stored operations, resolutions, and calculated occurrences are enough for it to distinguish expected work from confirmed work.
