# Features

Functional roadmap for Monteiro OS. Behavior for each feature is specified under [docs/features/](docs/features/). Product stages are explained in [docs/product/ROADMAP.md](docs/product/ROADMAP.md).

## Product objective

Record what happens in each vidriera so the business can reconstruct a cultivation cycle, measure commercially acceptable production, and later attach cost and sales to that same history.

## Status legend

| Status | Meaning |
| --- | --- |
| Planned | Specified, not started |
| In Progress | Started, acceptance criteria not yet verified |
| Implemented | Integrated and acceptance criteria verified |
| Deferred | Intentionally postponed |

Every feature below is **Planned**. The repository does not yet implement any of them. The running health check, placeholder page, PostgreSQL connection, and Alembic setup are bootstrap infrastructure. They are evidence for CORE-01, not completion of it.

## Priority legend

| Priority | Meaning |
| --- | --- |
| P0 | First usable vertical slice |
| P1 | Rest of Stage 1, and all of Stage 2 |
| P2 | Stage 3 |
| P3 | Stage 4 |

## Stage overview

| Stage | Goal | Features | Priority |
| --- | --- | --- | --- |
| 1 | Operational history of every vidriera and cycle | 15 | P0 and P1 |
| 2 | Harvest measurement and cycle comparison | 4 | P1 |
| 3 | Supplies and production cost | 5 | P2 |
| 4 | Wholesale flow and unit economics | 6 | P3 |

Future evolution is listed in the [roadmap](docs/product/ROADMAP.md) and has no feature IDs.

## Stage 1 — Production registration and traceability

| ID | Name | Priority | Status | Domains | Specification |
| --- | --- | --- | --- | --- | --- |
| CORE-01 | Application Foundation | P0 | Planned | `FRONTEND` `BACKEND` `DATABASE` `INFRA` | [spec](docs/features/CORE-01-application-foundation.md) |
| CORE-02 | Units of Measurement | P1 | Planned | `FRONTEND` `BACKEND` `DATABASE` | [spec](docs/features/CORE-02-units-of-measurement.md) |
| CORE-03 | People & Roles Registry | P1 | Planned | `FRONTEND` `BACKEND` `DATABASE` | [spec](docs/features/CORE-03-people-and-roles.md) |
| PROD-01 | Farms, Vidrieras & Beds | P0 | Planned | `FRONTEND` `BACKEND` `DATABASE` | [spec](docs/features/PROD-01-farms-vidrieras-beds.md) |
| PROD-02 | Flower Type, Variety & Classifications | P1 | Planned | `FRONTEND` `BACKEND` `DATABASE` | [spec](docs/features/PROD-02-crop-variety-catalog.md) |
| PROD-03 | Cultivation Cycle Management | P0 | Planned | `FRONTEND` `BACKEND` `DATABASE` | [spec](docs/features/PROD-03-cultivation-cycles.md) |
| PROD-04 | Crop Allocation Within a Cycle | P1 | Planned | `FRONTEND` `BACKEND` `DATABASE` | [spec](docs/features/PROD-04-crop-allocation.md) |
| PROD-05 | Medianero Assignment History | P1 | Planned | `FRONTEND` `BACKEND` `DATABASE` | [spec](docs/features/PROD-05-medianero-assignment-history.md) |
| INV-01 | Product Catalog | P1 | Planned | `FRONTEND` `BACKEND` `DATABASE` | [spec](docs/features/INV-01-product-catalog.md) |
| OPS-01 | Operation Registration | P0 | Planned | `FRONTEND` `BACKEND` `DATABASE` | [spec](docs/features/OPS-01-operation-registration.md) |
| OPS-02 | Operation Types & Structured Data | P1 | Planned | `FRONTEND` `BACKEND` `DATABASE` | [spec](docs/features/OPS-02-operation-types.md) |
| OPS-03 | Multi-Vidriera Operations | P1 | Planned | `FRONTEND` `BACKEND` `DATABASE` | [spec](docs/features/OPS-03-multi-vidriera-operations.md) |
| OPS-04 | Operation Participants & Responsibilities | P1 | Planned | `FRONTEND` `BACKEND` `DATABASE` | [spec](docs/features/OPS-04-operation-participants.md) |
| TRACE-01 | Production Activity History | P0 | Planned | `FRONTEND` `BACKEND` `DATABASE` | [spec](docs/features/TRACE-01-production-activity-history.md) |
| TRACE-02 | Observations & Attachments | P1 | Planned | `FRONTEND` `BACKEND` `DATABASE` `STORAGE` | [spec](docs/features/TRACE-02-observations-attachments.md) |

## Stage 2 — Harvesting and yield measurement

| ID | Name | Priority | Status | Domains | Specification |
| --- | --- | --- | --- | --- | --- |
| HARV-01 | Partial Harvest Registration | P1 | Planned | `FRONTEND` `BACKEND` `DATABASE` | [spec](docs/features/HARV-01-partial-harvest.md) |
| HARV-02 | Harvest Measurements & Quality Classification | P1 | Planned | `FRONTEND` `BACKEND` `DATABASE` | [spec](docs/features/HARV-02-harvest-measurements-quality.md) |
| HARV-03 | Yield & Productivity Indicators | P1 | Planned | `FRONTEND` `BACKEND` `DATABASE` `ANALYTICS` | [spec](docs/features/HARV-03-yield-indicators.md) |
| HARV-04 | Cultivation Cycle Comparison | P1 | Planned | `FRONTEND` `BACKEND` `ANALYTICS` | [spec](docs/features/HARV-04-cycle-comparison.md) |

## Stage 3 — Inventory and production costs

| ID | Name | Priority | Status | Domains | Specification |
| --- | --- | --- | --- | --- | --- |
| INV-02 | Storage Locations | P2 | Planned | `FRONTEND` `BACKEND` `DATABASE` | [spec](docs/features/INV-02-storage-locations.md) |
| INV-03 | Stock & Inventory Movements | P2 | Planned | `FRONTEND` `BACKEND` `DATABASE` | [spec](docs/features/INV-03-stock-movements.md) |
| INV-04 | Suppliers & Purchasing | P2 | Planned | `FRONTEND` `BACKEND` `DATABASE` | [spec](docs/features/INV-04-suppliers-purchasing.md) |
| COST-01 | Agricultural Product Consumption Costs | P2 | Planned | `FRONTEND` `BACKEND` `DATABASE` | [spec](docs/features/COST-01-product-consumption-costs.md) |
| COST-02 | Production Cost Allocation | P2 | Planned | `FRONTEND` `BACKEND` `DATABASE` | [spec](docs/features/COST-02-production-cost-allocation.md) |

## Stage 4 — Market and commercial management

| ID | Name | Priority | Status | Domains | Specification |
| --- | --- | --- | --- | --- | --- |
| COMM-01 | Harvest Lots & Boxes | P3 | Planned | `FRONTEND` `BACKEND` `DATABASE` | [spec](docs/features/COMM-01-harvest-lots-boxes.md) |
| COMM-02 | Customers & Orders | P3 | Planned | `FRONTEND` `BACKEND` `DATABASE` | [spec](docs/features/COMM-02-customers-orders.md) |
| COMM-03 | Truck Loading & Dispatch | P3 | Planned | `FRONTEND` `BACKEND` `DATABASE` | [spec](docs/features/COMM-03-truck-loading-dispatch.md) |
| COMM-04 | Sales & Receipts | P3 | Planned | `FRONTEND` `BACKEND` `DATABASE` | [spec](docs/features/COMM-04-sales-receipts.md) |
| COMM-05 | Commercial Traceability | P3 | Planned | `FRONTEND` `BACKEND` `ANALYTICS` | [spec](docs/features/COMM-05-commercial-traceability.md) |
| COST-03 | Unit Economics & Profitability | P3 | Planned | `FRONTEND` `BACKEND` `ANALYTICS` | [spec](docs/features/COST-03-unit-economics.md) |

## Major dependencies

```text
CORE-01
  ├── PROD-01 ── PROD-03 ── OPS-01 ── TRACE-01
  │                 │          ├── OPS-02 ── COST-01 ── COST-02 ── COST-03
  │                 │          ├── OPS-03
  │                 │          └── OPS-04
  │                 └── PROD-04 ── HARV-01 ── HARV-02 ── HARV-03 ── HARV-04
  ├── CORE-02 ── INV-01 ── OPS-02
  │                 └── INV-03 ── INV-04
  ├── CORE-03 ── PROD-05
  │            └── OPS-04
  └── INV-02 ── INV-03

HARV-01 ── COMM-01 ── COMM-03 ── COMM-05
           └── COMM-04
CORE-01 ── COMM-02 ── COMM-04 ── COST-03
```

COMM-04 depends on both COMM-01 and COMM-02. COMM-03 can load a box without an order.

OPS-01 can store a typed operation with notes before CORE-02 and INV-01 exist. Structured quantities wait for those catalogs. Harvest comparison waits for measurements. Cost and commerce attach to records that already exist; they do not replace them.

## Recommended implementation sequence

The order is dependency-aware and not a schedule.

| Step | Feature | Outcome |
| --- | --- | --- |
| 1 | CORE-01 | Single-user application shell on the existing API and database |
| 2 | PROD-01 | Quintas, vidrieras, and canteros |
| 3 | PROD-03 | One active cultivation cycle per vidriera |
| 4 | OPS-01 | An operation recorded against that vidriera |
| 5 | TRACE-01 | The operation visible in vidriera and cycle history |

Steps 1–5 are the first usable flow. CORE-02 is part of the first MVP and comes immediately after that flow, before structured quantities. Stage 1 continues as follows:

| Step | Feature | Outcome |
| --- | --- | --- |
| 6 | CORE-02 | Controlled units, including ramo and vara with no global conversion |
| 7 | PROD-02 | Crops and varieties |
| 8 | INV-01 | Product catalog |
| 9 | OPS-02 | Structured fields per operation type |
| 10 | CORE-03 | People and roles |
| 11 | OPS-04 | Performers and responsible persons |
| 12 | PROD-05 | Medianero assignment history |
| 13 | PROD-04 | Variety allocation inside the cycle |
| 14 | OPS-03 | One operation covering several vidrieras |
| 15 | TRACE-02 | Photographs on observations and other operations |

Stage 2, in order: HARV-01, HARV-02, HARV-03, HARV-04.

Stage 3, in order: INV-02, INV-03, INV-04, COST-01, COST-02. COST-01 also depends on OPS-02, which is already in place after step 9.

Stage 4, in order: COMM-01, COMM-02, COMM-03, COMM-04, COMM-05, COST-03. COMM-02 can be built in parallel with COMM-01 after CORE-01, and it should still ship as part of Stage 4 so sales are not a disconnected list.

## Features that need business clarification

These features have a safe slice and a blocked extension. Details are in [docs/OPEN_QUESTIONS.md](docs/OPEN_QUESTIONS.md).

| Feature | Safe to build | Wait for |
| --- | --- | --- |
| PROD-01 | Four canteros per vidriera | Resolved by OQ-21 |
| PROD-04 | Several varieties per cantero, without a measured share | OQ-02 before area, length, or plant-count portions |
| PROD-05 | One medianero, or direct management | OQ-12 before extra required fields |
| OPS-02 | Manual structured records | OQ-07 and OQ-08 before device or schedule truth |
| HARV-01 | Partial events and an uninterpreted progress note | OQ-03 before using the percentage in math |
| HARV-02 | Quantities, units, user-defined quality classes | OQ-05 before seeding classes |
| INV-03 | Receipts and adjustments | OQ-18 before importing an opening balance |
| COST-02 | Explicit direct and indirect costs | OQ-13 and OQ-14 before any split |
| COMM-01 | Boxes with optional or multiple origins | OQ-15 and OQ-16 before requiring one origin |
| COMM-04 | Sales and receipts | OQ-17 before settlements |
| COST-03 | Margin when revenue and cost are both known | OQ-14 and OQ-17 before medianero profit |

## Planned and implemented

| Capability | State |
| --- | --- |
| Development foundation: Compose, CI, health check, empty Alembic, placeholder page | Present in the repository. Not a product feature. |
| Stage 1–4 features in the tables above | Planned |
| Maps, sensors, control systems, voice orders, forecasting, AI advice, multi-user access, mobile UX, multi-farm SaaS | Not committed. No specification. |
