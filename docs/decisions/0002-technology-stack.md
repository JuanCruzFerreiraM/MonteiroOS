# ADR 0002 — Keep the bootstrapped technology stack

- Status: Accepted
- Date: 2026-10-28
- Source: Repository bootstrap. See root README and `docker-compose.yml`.

## Decision

Keep the stack that is already wired and tested:

- Next.js, React, TypeScript, Tailwind CSS, ESLint, Prettier
- Python 3.13, FastAPI, SQLAlchemy 2, Alembic, uv, Ruff, pytest
- PostgreSQL 18
- Docker Compose and GitHub Actions

## Consequences

- Documentation and feature work do not replace the framework, ORM, or database.
- New runtime dependencies require a feature that uses them and a lockfile update through the existing package managers.
- The documentation reset does not add runtime dependencies.
