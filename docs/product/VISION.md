# Vision

## The business

Monteiro is a family-owned wholesale flower production business in the La Plata region of Buenos Aires, Argentina. Production currently takes place on two properties: Villa Elisa and Arturo Seguí.

The business grows several kinds of flowers, including chrysanthemums and other commercially recognized varieties. Some varieties are known by informal local names. The software must accept those names without requiring a botanical classification.

Work is done by the owner and employees, and production responsibility for some areas is assigned to *medianeros*. A medianero is a production partner responsible for assigned areas. The financial and contractual terms of that arrangement are not documented yet. A medianero is not modeled as an ordinary employee.

## The problem

The business experiments and changes practices from experience. That history is not kept in a structured, queryable system. It is therefore difficult to answer:

- What was done in a particular production area?
- Which products were applied?
- When was an irrigation performed?
- What conditions and management practices were used?
- Who performed an operation?
- How much did a crop produce?
- How much of that production was commercially acceptable?
- How do cultivation cycles compare?
- What was the production cost per bunch?
- Which practices appear associated with better results?

The first objective is reliable operational traceability. The longer-term objective is to improve productivity, consistency, product quality, and profitability. The application is the intended long-term source of truth for production information. It should move the operation toward standardized, measurable records, while the first release still accepts incomplete details.

## Optimization objective

The business wants to increase commercially acceptable flower production per unit of cultivated area, while maintaining or improving quality.

Long-term indicators may include commercially acceptable stems per square meter, quality distribution, losses and discard, production per cycle, production cost per bunch, gross margin per square meter, and differences across varieties, seasons, and practices.

Comparisons must show the variety, conditions, and management that differ between cycles. A historical association is not proof that a practice caused a result.

## What Monteiro OS is

Monteiro OS is a specialized production-management and decision-support platform for this business. It is not intended to start as a general ERP.

It should grow in this order:

1. Record operations and reconstruct the history of every vidriera and cultivation cycle.
2. Measure harvests and compare cycle performance.
3. Account for supplies and production cost.
4. Connect production to boxes, dispatch, sales, and margin.

The product principles are:

- Operational simplicity for a single internal operator.
- A desktop-first layout. Mobile and multi-user access are future evolution, not the MVP.
- Reliable structured data and controlled measurement units.
- Minimal repeated entry, with reusable product, crop, and people catalogs.
- Clear traceability from an action back to a place, a cycle, and the people involved.
- Modular delivery inside one application.
- Extension toward inventory, commerce, analytics, and IoT only after the operational record exists.
- No premature AI features or extra infrastructure.

## Users

The first software operator is one internal user at a desktop. Employees and medianeros are business people in the registry. They do not receive logins in the MVP. See [ADR 0009](../decisions/0009-single-user-desktop-first.md).

## Boundaries

In scope for the committed roadmap: production structure, cultivation cycles, operations, observations, harvest measurement, a product catalog, inventory, production cost, and wholesale commercialization through delivery and basic receipts.

Out of scope until a later explicit requirement:

- A full accounting system, tax engine, or payroll system.
- Automated recommendations for crop-protection products.
- Treating a lighting or irrigation schedule as proof that the operation happened.
- Encoding medianero profit-sharing rules that have not been validated.
- Multi-farm SaaS, sensor control, forecasting, and voice ordering. Those items are listed under future evolution in the [roadmap](ROADMAP.md).

## How the product should learn

Confirmed operating facts in [the domain documents](../README.md) are safe to model. Working assumptions are labeled and may be implemented only where the related specification says they are safe. Unknowns stay in [OPEN_QUESTIONS.md](../OPEN_QUESTIONS.md).

Earlier project documents postponed all domain modeling until discovery was finished. That posture is superseded for the model now written down. It still applies to any process that is not described there.
