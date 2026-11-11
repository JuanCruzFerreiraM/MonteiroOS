# Production model

This document describes how Monteiro's physical production and cultivation cycles work. Operation details are in [OPERATIONS_MODEL.md](OPERATIONS_MODEL.md). People are in [PEOPLE_AND_RESPONSIBILITIES.md](PEOPLE_AND_RESPONSIBILITIES.md).

## Confirmed

### Physical hierarchy

```text
Quinta (production property)
  └── Vidriera (production section)
        ├── Cantero 1 (bed)
        ├── Cantero 2 (bed)
        ├── Cantero 3 (bed)
        └── Cantero 4 (bed)
```

A **quinta** is an entire production property. The properties known today are Villa Elisa and Arturo Seguí.

A **vidriera** is the primary functional production unit. Each quinta contains multiple vidrieras. Crops in a vidriera are managed together. Irrigation, product applications, and several environmental operations are shared at vidriera level.

A **cantero** is a physical subdivision of a vidriera. Each vidriera has four canteros. A cantero can hold more than one variety at the same time. Canteros matter for where crops are placed, how harvesting progresses, and how performance is measured. Harvesting may cut part of a variety inside a cantero while other plants in that bed remain. A harvested portion stays empty until a later planting cycle. The cut does not open a new cultivation cycle.

The physical structure is independent from time. Renaming a bed or changing who is responsible does not rewrite past cycles.

### Cultivation cycles

A vidriera is planted as a whole at the start of a cultivation cycle.

A vidriera must not have two active top-level cultivation cycles at the same time.

One cycle may include more than one variety. Those varieties may share a cantero or occupy different canteros. The cycle keeps the planting date, the allocations, the operations, the harvests, the observations, and the completion status.

During a cycle the business records operations, observations, and repeated partial harvests. Partial harvesting does not finalize the cycle. When harvesting and the associated work are finished, a person can finalize it. Finalized cycles stay queryable.

Work that prepares a vidriera between cycles must be recordable without attaching it to an unrelated cycle.

### Flower classification

Cultivated identity and commercial classification are different.

| Cultivated identity | Harvested or commercial classification |
| --- | --- |
| Flower type | Commercial size |
| Variety | Quality |
| Color, when known at planting | Presentation and commercial unit |

A cycle does not need a commercial size. One allocation can later produce more than one size or quality. Flower types do not have to share the same size, color, or presentation lists.

Chrysanthemum, with varieties such as Snow and Palisade, sizes such as large, medium, and small, and colors such as white and yellow, is an example of combinations the model must represent. Those names are not a seeded catalog and are not a price list.

Local variety names are valid. Botanical classification is optional.

## Working assumptions

These are safe for the first implementation slices. They are not additional confirmed facts.

- Cantero and vidriera area may be stored when someone has measured it. Yield per square meter is withheld when area is absent. No area is inferred.
- A portion of a cantero occupied by one variety may be noted as text. It is not treated as area, linear meters, or plant count until [OQ-02](../OPEN_QUESTIONS.md#oq-02) is answered.
- A cycle is either active or finalized. Draft planning of a future cycle is not required for the first release.
- An operation recorded while a cycle is active is associated with that cycle unless the person recording it marks it as outside the cycle. See [OQ-23](../OPEN_QUESTIONS.md#oq-23).

## Unknowns

- How to measure one variety's share of a cantero ([OQ-02](../OPEN_QUESTIONS.md#oq-02)).
- The measured area of each vidriera and cantero. Absence of a number is not zero area.
- Names, counts, and internal codes of vidrieras beyond the two quintas. Those are entered by the business; they are not seeded.
- Which commercial presentations exist for each flower type ([OQ-26](../OPEN_QUESTIONS.md#oq-26)).

## Implications for the software

- Store quintas, vidrieras, and canteros as durable records. Store cycles as separate records that point at a vidriera.
- Enforce one active cycle per vidriera.
- Keep finalized cycles and their allocations.
- Do not copy an operation onto each cantero or variety.
- Allow more than one variety allocation on the same cantero in the same cycle.
- In the first version, store one logical allocation per variety and color on a cantero and cycle. That limit is a simplification. A later version may give physically separate portions their own allocation identities without rewriting history. Do not add geometry for that case now.
- Keep commercial size off the planting record.
