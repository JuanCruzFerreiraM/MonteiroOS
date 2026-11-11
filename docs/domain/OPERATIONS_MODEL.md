# Operations model

Operations are the events and observations that explain what happened to a vidriera. The places they apply to are defined in [PRODUCTION_MODEL.md](PRODUCTION_MODEL.md).

## Confirmed

Agricultural operations are recorded at vidriera level by default. One irrigation can cover all four canteros and every variety in them. The system stores that operation once. It does not create a duplicate per cantero or per variety. Harvesting is not an operation of this kind. Harvest events are specified in [HARVEST_AND_YIELD.md](HARVEST_AND_YIELD.md).

An operation may later target more than one vidriera. The physical scope of the operation is not the same thing as the canteros used to measure yield.

The person who records an operation may be different from anyone who performed it. Some activities have no human executor.

A configured schedule does not prove that an operation physically happened. Lighting, in particular, must be able to represent a program and an observed state as different facts.

Preparation between cultivation cycles must be representable without assigning it to the wrong cycle.

### Initial operation catalog

| Type | What is known | What must stay explicit |
| --- | --- | --- |
| Irrigation | May be a timed operation. | Start and end, or a duration. |
| Artificial lighting | May involve scheduled or actual on/off states. | Whether the record is a program or an observation that it happened. |
| Black nylon covering | Raising and lowering, and the interval of exposure. | The event or interval. The field procedure is not documented. |
| Cold-protection heating (*dar fuego*) | Activation, duration, and environmental context may matter. | What was done, for how long, and any context the operator notes. |
| Product application | One or more catalog products, with a standardized quantity or dose. | Product identity and a unit from the unit catalog. |
| Manual labor | A task that may involve several workers. | The task. The workers are participants, not copies of the operation. |
| Observation | Describes conditions. Ideally includes photographs. | It is not assumed to be an intervention. |

Product applications use the [product catalog](INVENTORY_MODEL.md). Quantities use [controlled units](INVENTORY_MODEL.md#units).

## Working assumptions

- The first record of an operation can be stored with a type, a time, one vidriera, notes, and the user who entered it. Type-specific fields arrive with OPS-02 and are not required to save history for the earliest release.
- When a vidriera has an active cycle, a new operation defaults to that cycle. The user can mark it as outside any cycle.
- Backfilling onto a finalized cycle is allowed when the user explicitly selects that cycle. The default never selects a finalized cycle.
- For an operation that covers several vidrieras, each vidriera keeps its own cycle link. One cycle is not applied to every target.
- Observations are stored as operations of type observation so they appear in the same history. Photographs are attachments on that operation, specified in TRACE-02.
- Environmental context for heating is free text or a referenced observation. The system does not synthesize sensor readings.

## Unknowns

The operating procedures, schedules, and hardware behavior of lighting, nylon covering, and heating are not validated. See [OQ-07](../OPEN_QUESTIONS.md#oq-07), [OQ-08](../OPEN_QUESTIONS.md#oq-08), [OQ-09](../OPEN_QUESTIONS.md#oq-09), and [OQ-10](../OPEN_QUESTIONS.md#oq-10).

Also unresolved:

- How application quantities are written down today ([OQ-06](../OPEN_QUESTIONS.md#oq-06)).
- Which additional manual tasks are worth a named entry in the catalog ([OQ-11](../OPEN_QUESTIONS.md#oq-11)).
- How operators want to label work between cycles ([OQ-23](../OPEN_QUESTIONS.md#oq-23)).

Until those answers exist, the seven types above are the catalog, and their structured fields stay limited to the columns in the table.

## Implications for the software

- Persist one operation and a scope of one or more vidrieras.
- Keep type-specific data on that operation, validated per type.
- Never split one shared action into four bed-level operation rows.
- Do not mark a scheduled lighting program as completed unless a person records that it happened.
