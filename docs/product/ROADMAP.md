# Roadmap

This roadmap commits to four product stages. It is not a schedule and it does not assign dates or effort. The feature index, status, and recommended build order live in [FEATURES.md](../../FEATURES.md).

Nothing in these stages is implemented. The repository contains only the application foundation described in the [architecture overview](../architecture/OVERVIEW.md).

## Stage 1 — Production registration and traceability

**Goal.** Register operations and reconstruct the operational history of every vidriera and cultivation cycle.

The first usable release is a vertical slice, not the whole stage:

create a vidriera, start a cultivation cycle, register an operation, review its history.

That slice is CORE-01, PROD-01, PROD-03, OPS-01, and TRACE-01. The rest of the stage makes the record precise enough to trust: units, crops, products, structured operation types, people, responsibilities, shared operations, and photographs.

| ID | Name |
| --- | --- |
| [CORE-01](../features/CORE-01-application-foundation.md) | Application Foundation |
| [CORE-02](../features/CORE-02-units-of-measurement.md) | Units of Measurement |
| [CORE-03](../features/CORE-03-people-and-roles.md) | People & Roles Registry |
| [PROD-01](../features/PROD-01-farms-vidrieras-beds.md) | Farms, Vidrieras & Beds |
| [PROD-02](../features/PROD-02-crop-variety-catalog.md) | Flower Type, Variety & Classifications |
| [PROD-03](../features/PROD-03-cultivation-cycles.md) | Cultivation Cycle Management |
| [PROD-04](../features/PROD-04-crop-allocation.md) | Crop Allocation Within a Cycle |
| [PROD-05](../features/PROD-05-medianero-assignment-history.md) | Medianero Assignment History |
| [INV-01](../features/INV-01-product-catalog.md) | Product Catalog |
| [OPS-01](../features/OPS-01-operation-registration.md) | Operation Registration |
| [OPS-02](../features/OPS-02-operation-types.md) | Operation Types & Structured Data |
| [OPS-03](../features/OPS-03-multi-vidriera-operations.md) | Multi-Vidriera Operations |
| [OPS-04](../features/OPS-04-operation-participants.md) | Operation Participants & Responsibilities |
| [TRACE-01](../features/TRACE-01-production-activity-history.md) | Production Activity History |
| [TRACE-02](../features/TRACE-02-observations-attachments.md) | Observations & Attachments |

## Stage 2 — Harvesting and yield measurement

**Goal.** Measure production outcomes and compare cultivation cycles.

This stage follows Stage 1 promptly. Harvest quantity and productivity comparison are a primary business objective, not a distant analytics project.

| ID | Name |
| --- | --- |
| [HARV-01](../features/HARV-01-partial-harvest.md) | Partial Harvest Registration |
| [HARV-02](../features/HARV-02-harvest-measurements-quality.md) | Harvest Measurements & Quality Classification |
| [HARV-03](../features/HARV-03-yield-indicators.md) | Yield & Productivity Indicators |
| [HARV-04](../features/HARV-04-cycle-comparison.md) | Cultivation Cycle Comparison |

Indicators must expose missing data and the definition used. They must not present correlation as causation.

## Stage 3 — Inventory and production costs

**Goal.** Manage agricultural resources and progressively calculate production cost.

Stage 3 extends the production history. It does not create a second, parallel record of applications or harvests.

| ID | Name |
| --- | --- |
| [INV-02](../features/INV-02-storage-locations.md) | Storage Locations |
| [INV-03](../features/INV-03-stock-movements.md) | Stock & Inventory Movements |
| [INV-04](../features/INV-04-suppliers-purchasing.md) | Suppliers & Purchasing |
| [COST-01](../features/COST-01-product-consumption-costs.md) | Agricultural Product Consumption Costs |
| [COST-02](../features/COST-02-production-cost-allocation.md) | Production Cost Allocation |

Catalog products, physical stock, recorded application quantities, and confirmed stock withdrawals remain different facts. Direct and indirect costs remain different facts. Physical consumption and economic responsibility remain different facts. Medianero cost-sharing rules stay unconfigured until the business validates them.

The stage does not assume that an accurate opening inventory already exists.

## Stage 4 — Market and commercial management

**Goal.** Connect cultivation and harvesting to preparation, delivery, sales, and profitability.

| ID | Name |
| --- | --- |
| [COMM-01](../features/COMM-01-harvest-lots-boxes.md) | Harvest Lots & Boxes |
| [COMM-02](../features/COMM-02-customers-orders.md) | Customers & Orders |
| [COMM-03](../features/COMM-03-truck-loading-dispatch.md) | Truck Loading & Dispatch |
| [COMM-04](../features/COMM-04-sales-receipts.md) | Sales & Receipts |
| [COMM-05](../features/COMM-05-commercial-traceability.md) | Commercial Traceability |
| [COST-03](../features/COST-03-unit-economics.md) | Unit Economics & Profitability |

The stage covers medianero box letters, variety identification, harvest origin when it is known, customer orders, truck loading, sales quantities and prices, basic customer receipts, and cost and margin per bunch.

It is not a general ledger, tax system, or payroll system. Medianero settlement rules are unknown and are excluded until [OQ-14](../OPEN_QUESTIONS.md#oq-14) and [OQ-17](../OPEN_QUESTIONS.md#oq-17) are answered.

## Future evolution — not committed

These items have no feature specification and no delivery commitment. Descriptions state the capability and what it would depend on.

| Capability | Depends on | Notes |
| --- | --- | --- |
| Multi-user access | CORE-01, CORE-03 | Accounts and authorization after the single-user MVP. People remain business records. |
| Mobile interfaces | The desktop MVP | A phone layout and field entry. Not required for Stages 1–4. |
| Interactive production map | PROD-01 | Navigation across physical areas. Not required for Stage 1. |
| Spatial geometry of vidrieras and beds | PROD-01 | Shapes and coordinates. Area used for yield can exist as a measured number before geometry exists. |
| Agricultural experiment management | PROD-03, OPS-01, HARV-04 | Name a trial, the cycles it covers, and the practice being compared. |
| Statistical production analysis | HARV-04 | Formal analysis beyond the Stage 2 comparison. Must still separate association from causation. |
| IoT sensors | OPS-01, TRACE-01 | Store sensor readings as observations. A reading is not automatically an operation. |
| Irrigation and lighting integration | OPS-02 | Import device events. A configured schedule still does not prove the operation occurred. |
| Automated environmental monitoring | Observations, future sensors | Time series of conditions. No control loop. |
| Supervised control systems | Monitoring plus validated operating procedures | Human confirmation before an actuation is treated as an operation. |
| WhatsApp-assisted order management | COMM-02 | Capture order intent from WhatsApp. A message is not a confirmed order until a person accepts it. |
| Audio transcription and structured order extraction | COMM-02 | Turn speech into a draft order for review. |
| Production forecasting | HARV-03, PROD-03 | Project a cycle from historical yields. Requires enough comparable history. |
| Yield prediction | HARV-03 | Model expected yield. Same evidence bar as forecasting. |
| AI-powered decision support | Traceability, harvest, and cost history | Suggestions must cite the records they used. |
| Optimization and scenario simulation | COST-03, HARV-04 | Compare hypothetical practice or mix changes. Inputs and assumptions must be visible. |
| Multi-farm commercial SaaS | The single-business product in production use | A later product decision. The current architecture optimizes for Monteiro, not for tenant isolation. |

## Sequencing principle

Build the production record first. Measure it second. Attach costs and sales to that same record. Do not introduce a parallel book for harvests, applications, or sales that cannot point back to a vidriera and a cultivation cycle.
