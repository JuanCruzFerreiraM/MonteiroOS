# Architecture decision records

Decisions that constrain implementation. Business rules stay in `docs/domain/`. Open choices stay in [OPEN_QUESTIONS.md](../OPEN_QUESTIONS.md).

| ID | Title | Status |
| --- | --- | --- |
| [0001](0001-modular-monolith.md) | Use a modular monolith | Accepted |
| [0002](0002-technology-stack.md) | Keep the bootstrapped technology stack | Accepted |
| [0003](0003-one-active-cultivation-cycle.md) | One active cultivation cycle per vidriera | Accepted |
| [0004](0004-operation-scope-separate-from-yield.md) | Separate operation scope from yield units | Accepted |
| [0005](0005-product-catalog-separate-from-stock.md) | Keep the product catalog separate from stock | Accepted |
| [0006](0006-medianero-financial-rules-deferred.md) | Do not encode medianero financial rules yet | Accepted |
| [0007](0007-observations-as-operations.md) | Record observations as operations | Accepted |
| [0008](0008-controlled-measurement-units.md) | Use a controlled unit catalog | Accepted |
| [0009](0009-single-user-desktop-first.md) | Keep the MVP single-user and desktop-first | Accepted |

An accepted decision can change through a new record that supersedes it. Do not silently contradict one in a feature pull request.
