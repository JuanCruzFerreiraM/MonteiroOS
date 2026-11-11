# ADR 0001 — Use a modular monolith

- Status: Accepted
- Date: 2026-10-28
- Source: Preserved from the bootstrap architecture note and restated for the product model.

## Decision

Monteiro OS has one backend process and one web application. Domain areas are modules in those codebases. They share one PostgreSQL database, one configuration scheme, and one deployment.

## Consequences

- Features add modules inside `backend/app` and the Next.js app.
- The browser calls the HTTP API. It does not open a second path to the database.
- Queues, separate services, and event brokers are out of scope until a concrete feature cannot be delivered without them. None of the four committed stages need them.
