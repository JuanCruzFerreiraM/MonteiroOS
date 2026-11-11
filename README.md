# Monteiro OS

Monteiro OS is the internal production-management platform for Monteiro, a family-owned wholesale flower business in the La Plata region of Buenos Aires, Argentina.

The business needs a reliable record of what happened in each production section: which practices were used, which products were applied, what was harvested, and, later, what that production cost and what it sold for. The first goal is operational traceability. Later stages add harvest measurement, inventory, cost, and wholesale commercialization.

This repository is the functional source of truth for that product. It currently contains the development foundation only. Production, harvest, inventory, and commercial modules are specified and not yet built.

## Current implementation

The running system is a modular monolith foundation:

- A FastAPI application exposes `GET /health`. The endpoint returns `{"status": "ok"}` when PostgreSQL accepts `SELECT 1`, and `503` when it does not.
- A Next.js application renders a single placeholder page. It has no business navigation, screens, or API calls.
- SQLAlchemy and Alembic are configured. There are no domain models and no migration revisions.
- Docker Compose runs PostgreSQL 18, the API, and the web app together.
- GitHub Actions runs backend lint, format, and pytest, plus frontend lint and production build.

There is no domain data and no brand asset or color system in the repository. The UI copy on the placeholder page is Spanish. The planned MVP is single-user and desktop-first. It does not add accounts or a mobile client.

## Product scope

Four committed stages:

1. **Production registration and traceability.** Record farms, production sections, cultivation cycles, and operations, then reconstruct that history.
2. **Harvesting and yield.** Record partial harvests and compare cultivation cycles.
3. **Inventory and production costs.** Track supplies and calculate production cost without assuming a complete opening inventory.
4. **Market and commercial management.** Connect harvests to boxes, dispatch, sales, and unit economics.

Interactive maps, sensors, automation control, voice capture, forecasting, and multi-farm SaaS are future options. They are not part of the committed roadmap.

## Documentation

Start here:

| Document | Purpose |
| --- | --- |
| [FEATURES.md](FEATURES.md) | Feature index, status, and implementation sequence |
| [Product vision](docs/product/VISION.md) | Problem, users, principles, and boundaries |
| [Roadmap](docs/product/ROADMAP.md) | Stages and uncommitted future work |
| [Glossary](docs/product/GLOSSARY.md) | Domain terms |
| [Documentation map](docs/README.md) | Full document index |
| [Open questions](docs/OPEN_QUESTIONS.md) | Decisions that still need the business |
| [Contributing](CONTRIBUTING.md) | How to implement a feature |

Domain language keeps the Spanish operational terms *quinta*, *vidriera*, *cantero*, and *medianero*. Definitions are in the glossary.

## Local development

These instructions match the repository configuration (`docker-compose.yml`, `Makefile`, manifests, and CI). They were established with the project bootstrap.

### Requirements

- Git
- Docker, running
- [uv](https://docs.astral.sh/uv/) 0.12 or newer, for host-side tests and migrations
- Node.js 22.13 or newer and npm, for host-side frontend lint and build
- Make, optional

### Setup

```bash
git clone https://github.com/JuanCruzFerreiraM/MonteiroOS.git
cd MonteiroOS
git checkout develop
cp .env.example .env
```

`.env` is optional when the defaults are acceptable. It is not committed. Variables are explained in `.env.example`.

### Run and stop

```bash
docker compose up --build
```

- Web app: http://localhost:3000
- API health: http://localhost:8000/health
- API docs: http://localhost:8000/docs

```bash
docker compose logs -f
docker compose ps
docker compose down
```

`docker compose down` keeps the PostgreSQL volume. `docker compose down -v` deletes it.

If port 5432 is already in use, change `POSTGRES_PORT` in `.env` before starting Compose. The backend container still connects to the `db` service. The published port matters only for tools running on the host.

Make equivalents: `make up`, `make up-d`, `make logs`, `make down`.

The API reloads when files under `backend/app` change. The web app reloads when the frontend changes. Rebuild after Python dependency changes: `docker compose up --build`. If `frontend/package-lock.json` changes, the frontend container runs `npm ci` on startup.

### Backend

From `backend/`, with PostgreSQL running:

```bash
uv sync
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run alembic upgrade head
```

`alembic upgrade head` applies no domain schema today because there are no revisions. It confirms that Alembic can reach the database.

Create a revision only when a real model exists:

```bash
uv run alembic revision --autogenerate -m "short description"
uv run alembic upgrade head
```

### Frontend

From `frontend/`:

```bash
npm ci
npm run lint
npm run format:check
npm run build
npm run dev
```

`npm run dev` is only needed to run the web app outside Docker.

### Pre-commit

```bash
uv tool install pre-commit
pre-commit install
pre-commit run --all-files
```

Hooks cover repository hygiene, Ruff, and frontend lint and format. They do not run pytest or the Next.js build.

## Stack

| Layer | Technology |
| --- | --- |
| Frontend | Next.js 16, React 19, TypeScript, Tailwind CSS 4, ESLint, Prettier |
| Backend | Python 3.13, FastAPI, SQLAlchemy 2, Alembic, uv, Ruff, pytest |
| Data | PostgreSQL 18 |
| Environment | Docker Compose |
| CI | GitHub Actions, jobs `backend` and `frontend` |

Domain modules will live inside this backend and this frontend. They will not be separate services. See [architecture overview](docs/architecture/OVERVIEW.md).

## Repository layout

```text
MonteiroOS/
├── backend/          API, configuration, Alembic, tests
├── frontend/         Next.js application
├── docs/             Product, domain, architecture, features, workflow
├── .github/workflows CI
├── docker-compose.yml
├── Makefile
├── FEATURES.md
└── CONTRIBUTING.md
```
