# Documentation map

Monteiro OS documentation is written in English. The application will be used in Spanish; domain terms stay in Spanish where the business uses them.

The functional source of truth is [FEATURES.md](../FEATURES.md). Feature behavior lives in `docs/features/`. Other documents explain why the product exists, how the operation works, and how to change the code.

## Product

| Document | Contents |
| --- | --- |
| [VISION.md](product/VISION.md) | Problem, users, principles, and product boundaries |
| [ROADMAP.md](product/ROADMAP.md) | Four committed stages and uncommitted future work |
| [GLOSSARY.md](product/GLOSSARY.md) | Terms used in the domain and in the software |
| [UX.md](product/UX.md) | Experience principles and the current UI baseline |

## Domain

| Document | Contents |
| --- | --- |
| [PRODUCTION_MODEL.md](domain/PRODUCTION_MODEL.md) | Farms, sections, beds, crops, and cycles |
| [OPERATIONS_MODEL.md](domain/OPERATIONS_MODEL.md) | Shared cultivation operations |
| [PEOPLE_AND_RESPONSIBILITIES.md](domain/PEOPLE_AND_RESPONSIBILITIES.md) | People, roles, and medianero assignments |
| [INVENTORY_MODEL.md](domain/INVENTORY_MODEL.md) | Products, units, stock, and cost concepts |
| [HARVEST_AND_YIELD.md](domain/HARVEST_AND_YIELD.md) | Partial harvests and productivity |
| [COMMERCIAL_TRACEABILITY.md](domain/COMMERCIAL_TRACEABILITY.md) | Boxes, dispatch, sales, and origin |

Each domain document separates confirmed facts, working assumptions, and unknowns.

## Architecture and decisions

| Document | Contents |
| --- | --- |
| [OVERVIEW.md](architecture/OVERVIEW.md) | What runs today and the target modular monolith |
| [DATA_MODEL.md](architecture/DATA_MODEL.md) | Conceptual entities and relationships |
| [MODULE_DEPENDENCIES.md](architecture/MODULE_DEPENDENCIES.md) | Module boundaries and allowed dependencies |
| [decisions/](decisions/README.md) | Architecture decision records |

## Features

Individual specifications are in [docs/features/](features/). The index and the recommended build order are in [FEATURES.md](../FEATURES.md).

## Development

| Document | Contents |
| --- | --- |
| [WORKFLOW.md](development/WORKFLOW.md) | Branches, commits, CI, tests, and local commands |
| [FEATURE_TEMPLATE.md](development/FEATURE_TEMPLATE.md) | Required specification structure |
| [DEFINITION_OF_DONE.md](development/DEFINITION_OF_DONE.md) | Completion criteria |
| [OPEN_QUESTIONS.md](OPEN_QUESTIONS.md) | Business questions still unresolved |

## Documentation history

The bootstrap documents `docs/vision.md`, `docs/architecture.md`, `docs/development.md`, and root `ROADMAP.md` were replaced by this set.

Those documents said the domain was still undiscovered and that entities should not be modeled until each process had been observed. They also listed commercial work, finance, analytics, voice input, IoT, and prediction as an undifferentiated later list.

The confirmed operating model in `docs/domain/` supersedes that discovery-only posture for the processes described there. Anything still unconfirmed stays in [OPEN_QUESTIONS.md](OPEN_QUESTIONS.md) and must not be implemented as if it were a rule. Voice input, IoT, and prediction moved to the uncommitted future section of the roadmap.

Local development procedures from the bootstrap guide were kept and updated in [WORKFLOW.md](development/WORKFLOW.md) and the root [README](../README.md).
