# Contributing

Monteiro OS is built by a small team with Cursor. The repository documentation is the functional source of truth. There is no separate task tracker.

Read [FEATURES.md](FEATURES.md) and the feature specification before changing product behavior. The day-to-day commands, branching rules, and review expectations are in [docs/development/WORKFLOW.md](docs/development/WORKFLOW.md).

## Implement a feature

1. Choose a `Planned` feature from [FEATURES.md](FEATURES.md).
2. Read its specification and the domain documents it depends on.
3. Resolve any open question marked as blocking for that feature in [docs/OPEN_QUESTIONS.md](docs/OPEN_QUESTIONS.md).
4. Inspect the existing implementation before adding structure.
5. Branch from `develop` using `feat/<ID>-<short-name>` or `fix/<short-name>`.
6. Implement the smallest change that satisfies the specification.
7. Add or update tests, and verify the acceptance criteria.
8. Update technical documentation when the change alters setup, architecture, or feature status.
9. Open a pull request to `develop`.

A feature may take more than one pull request. Do not split work into pull requests that only create an empty table, route, or component.

## Status

Use only `Planned`, `In Progress`, `Implemented`, and `Deferred`.

`Implemented` means the feature is integrated and its acceptance criteria have been verified. Generated code that has not been checked against those criteria stays `In Progress`.

## Rules that keep the product coherent

- Preserve the current stack and the modular monolith. See [ADR 0001](docs/decisions/0001-modular-monolith.md) and [ADR 0002](docs/decisions/0002-technology-stack.md).
- Keep Spanish domain terms (`quinta`, `vidriera`, `cantero`, `medianero`) in the conceptual model.
- Do not turn an open question into a business rule inside code or documentation.
- Do not invent operational data, prices, yields, employee identities, or regulatory requirements.
- Do not commit secrets.

## Definition of done

A feature is done only when it meets [docs/development/DEFINITION_OF_DONE.md](docs/development/DEFINITION_OF_DONE.md).

New or substantially changed specifications follow [docs/development/FEATURE_TEMPLATE.md](docs/development/FEATURE_TEMPLATE.md).
