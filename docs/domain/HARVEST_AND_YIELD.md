# Harvest and yield

Harvest is how the business learns what a cultivation cycle produced. Commercial packing is in [COMMERCIAL_TRACEABILITY.md](COMMERCIAL_TRACEABILITY.md).

## Confirmed

Harvesting is the exception to vidriera-level operations. A harvest event records a variety inside a cultivation cycle, together with the cantero when that physical origin is known.

The same variety and cantero may be harvested on many dates. Each event is independent. Harvesting one variety does not complete the cantero or the cycle. A harvested portion stays empty until a later planting cycle. The system does not infer emptiness from a progress note.

Origin on a production harvest is exact or partial. Exact names the cantero. Partial keeps the cycle and variety and leaves the cantero empty, without spreading the quantity across beds. Unknown vidriera is a commercial fact, not a field harvest. A medianero identifier does not supply the missing origin.

A harvest may also reference one crop allocation when that placement is reliably known. The allocation is a variety's placement in one cycle and cantero. Repeated cuts may cite the same allocation. If the known origin does not identify an allocation, the reference stays empty. The system does not invent one, and the missing reference does not block the harvest.

A harvest record is expected to be able to hold:

| Information | Notes |
| --- | --- |
| Date | When the cut happened. |
| Vidriera | The section. |
| Cultivation cycle | The cycle of that vidriera. |
| Cantero | Required when origin is exact. Absent when origin is partial. |
| Variety | The cultivated variety being cut. |
| Crop allocation | Optional. Set only when one existing placement is known. |
| Harvested portion or progress | Optional. The meaning of a percentage is not confirmed. |
| Quantity, unit, and exact or estimated status | From the unit catalog. Ramo and vara are separate. |
| Commercial size, color, and presentation | Optional harvest grades. Size is not taken from planting. |
| Quality classification | The classes in use are not confirmed. |
| Discarded amount | Distinguished from commercially acceptable quantity. |
| Observations | Optional notes. |

Several harvest events may exist for the same cantero in the same cycle. They accumulate. A later event does not replace an earlier one.

Yield comparison is a primary reason to keep this history. Comparisons must show variety, conditions, and management alongside the numbers. An association between a practice and a result is not a causal claim.

Commercially acceptable production is the harvested quantity that remains after recorded discards, in a compatible unit.

## Working assumptions

- A harvest event always names a cycle. Harvest is an outcome of a cycle, unlike a preparation operation, which may sit outside a cycle.
- The progress or percentage field may be stored as entered, with its interpretation marked unconfirmed, until [OQ-03](../OPEN_QUESTIONS.md#oq-03) is answered. The software does not treat that number as area, plant count, and informal progress at the same time.
- The software does not mark a cantero empty just because entered percentages add up to 100. Emptiness is a physical consequence the business understands; the automatic rule is not known.
- Quality classes are a user-maintained catalog. No class names are seeded. A measurement may be saved with quality explicitly unset.
- Discarded quantity uses the same dimension as the harvested quantity and the same measurement. When it is present, it is at least zero and no greater than the harvested quantity. A missing discard does not become zero. A loss outside the harvested quantity is a separate measurement or event.
- Area-based indicators appear only when a measured area is stored on the cantero or vidriera.
- Vara (stem), ramo (bunch), and plants stay in the unit in which they were recorded. A presentation may declare an explicit number of varas per ramo. That factor applies only to measurements that cite the presentation, and the derived figure is labeled as derived.

## Unknowns

- How precisely partial harvest progress is defined ([OQ-03](../OPEN_QUESTIONS.md#oq-03)).
- Which measurements are practical during harvest ([OQ-04](../OPEN_QUESTIONS.md#oq-04)).
- Which quality classifications are actually used ([OQ-05](../OPEN_QUESTIONS.md#oq-05)).
- Which commercial presentations exist, and which of them declare varas per ramo ([OQ-26](../OPEN_QUESTIONS.md#oq-26)).
- Whether flowers from different vidrieras are mixed before they are boxed ([OQ-15](../OPEN_QUESTIONS.md#oq-15)).

<a id="indicator-definitions"></a>

## Indicator definitions

Stage 2 publishes the definition next to every figure.

| Indicator | Definition | Shown as missing when |
| --- | --- | --- |
| Harvested quantity | Sum of harvest measurements in one unit. | Measurements use units that do not convert. The UI shows the separate unit totals instead of a false single sum. |
| Discarded quantity | Sum of discard measurements in one unit. | No discard was recorded. This is not shown as zero. |
| Commercially acceptable quantity | Harvested minus discarded, same unit. | Either side is missing, or the units differ. |
| Quantity per square meter | Commercially acceptable quantity divided by recorded area. | Area is absent, or the acceptable quantity is missing. |
| Cycle comparison | The indicators above for two or more cycles, with variety allocation, dates, and quinta. | A cycle lacks an input. The comparison still lists the cycle and marks the gap. |

No indicator invents a global vara count per ramo, a default bed area, or a quality class. Compatible units and compatible flower classifications are aggregated separately.
