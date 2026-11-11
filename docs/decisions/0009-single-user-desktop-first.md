# ADR 0009 — Single-user, desktop-first MVP

- Status: Accepted
- Date: 2026-11-11

## Decision

The first version of Monteiro OS is a single-user, desktop-first web application on the existing Next.js and FastAPI stack. It does not introduce accounts, role-based access, mobile-specific workflows, or a native desktop client.

Business people, including employees and medianeros, are records in the people registry. They are not software users.

Basic protection of a deployment may use one shared secret or a network restriction. That secret does not identify a person.

Multi-user access and mobile interfaces remain future evolution. They are not part of Stages 1–4.

## Consequences

- CORE-01 does not create a user directory.
- CORE-03 does not link people to accounts.
- Operation and harvest records may name a person from the registry. They do not require a logged-in account.
- Acceptance of MVP screens targets a desktop window. A separate mobile layout is out of scope.
