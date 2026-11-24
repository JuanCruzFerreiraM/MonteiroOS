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

The physical structure is independent from time, from who is responsible, and from any map. Renaming a display label or changing who is responsible does not rewrite past cycles.

### Identity and operational codes

Each quinta and each vidriera has an immutable technical identifier and a separate operational code. The code is what people use. The identifier is what other records point at.

A quinta code is a short unique business code, such as `VE` for Villa Elisa or `AS` for Arturo Seguí. Those examples are not seeded fixtures.

A vidriera code combines the quinta code with a sequence number that is unique inside that quinta: `VE-V001`, `VE-V002`, `AS-V001`. The number is assigned at creation, is not reused after deactivation, and does not claim a physical order on the ground. There is no fixed maximum.

A cantero is numbered 1 to 4 inside its vidriera. A display label such as `VE-V001-C1` can be derived from the parent code and that number. The cantero's technical identifier does not depend on the label.

A descriptive name or location note may change. The technical identifier and the operational code do not. Moving a vidriera to another quinta is not a descriptive edit. It would attach the section to a different property and would conflict with the code. The normal edit path does not do it.

### Geographic identification

A quinta and a vidriera may each have one approximate geographic boundary. The boundary is optional. It is not the record's identity, and it is not required to create the record.

Boundaries are stored as geographic coordinates so they survive a change of satellite imagery. Imagery itself is a basemap from an external provider. It does not need to be current. The operator does not supply the base image.

A drawn polygon should normally fall inside its quinta, but manual boundaries are approximate. Invalid shapes are rejected. A shape is not silently rewritten to look tidy. [OQ-30](../OPEN_QUESTIONS.md#oq-30) is resolved: overlap and a small extension past the quinta edge stay visible as warnings, and a polygon that does not meet the quinta is rejected.

Three areas stay distinct:

- The area computed from a polygon, which is only an approximate footprint.
- The measured physical area, entered when someone has measured it.
- The productive or cultivated area, which this model does not infer from the map.

Canteros are not given polygons in the first map. [PROD-06](../features/PROD-06-farm-visual-mapping.md) owns the mapping behavior. [PROD-01](../features/PROD-01-farms-vidrieras-beds.md) owns the records and the codes.

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
- The actual quinta codes, vidriera counts, and descriptive names. The code convention is defined. The values are entered by the business and are not seeded.
- Which commercial presentations exist for each flower type ([OQ-26](../OPEN_QUESTIONS.md#oq-26)).

## Implications for the software

- Store quintas, vidrieras, and canteros as durable records. Store cycles as separate records that point at a vidriera.
- Enforce one active cycle per vidriera.
- Keep finalized cycles and their allocations.
- Do not copy an operation onto each cantero or variety.
- Allow more than one variety allocation on the same cantero in the same cycle.
- In the first version, store one logical allocation per variety and color on a cantero and cycle. That limit is a simplification. A later version may give physically separate portions their own allocation identities without rewriting history. Do not add cantero geometry to represent those portions.
- Keep operational codes stable when a display name, a cycle, a crop, a medianero, or a descriptive location changes.
- Do not reuse an operational code after deactivation.
- Treat map geometry as optional and approximate. Do not copy a polygon's computed area into a measured area or a yield figure.
- Keep commercial size off the planting record.
