# Monteiro OS

Monteiro OS is the internal production-management platform for Monteiro, a family-owned wholesale flower business in the La Plata region of Buenos Aires, Argentina.

The business needs a reliable record of what happened in each production section: which practices were used, which products were applied, what was harvested, and, later, what that production cost and what it sold for. The first goal is operational traceability. Later stages add harvest measurement, inventory, cost, and wholesale commercialization.

This repository is the functional source of truth for that product. The development foundation and the first production hierarchy are in the repository. Harvest, inventory, and commercial modules are specified and not yet built. PROD-01 is in progress on its feature branch until its acceptance criteria are verified.

## Current implementation

The running system is a modular monolith:

- A FastAPI application exposes `GET /health` and the Production API under `/api/production`. Health returns `{"status": "ok"}` when PostgreSQL accepts `SELECT 1`, including when the production tables do not exist yet. It returns `503` when PostgreSQL does not respond.
- Production routes create and edit quintas, vidrieras, and canteros. SQLAlchemy models `Quinta`, `Vidriera`, and `Cantero` live in `backend/app/modules/production/models.py`. Primary keys are server-generated UUIDs. Operational codes are separate unique columns, not keys.
- Alembic revision `0001_production_hierarchy` creates `quintas`, `vidrieras`, and `canteros`, with foreign keys and the uniqueness and check constraints for codes, names, and cantero numbers. It does not insert business records. Revision `0002_production_boundaries` adds a nullable JSONB `boundary` to quintas and vidrieras. Existing rows keep a null boundary.
- If that revision has not been applied, a Production request returns `503` and tells the operator to run `alembic upgrade head`. The response does not include SQL and is not an empty quinta list.
- A Next.js application renders a single-user desktop shell in Spanish. Inicio and Producción are working destinations. The other modules stay listed as not available. Producción lists quintas, opens one quinta, creates a vidriera with four canteros, edits descriptive data, and opens a satellite map for one quinta.
- Docker Compose runs PostgreSQL 18, the API, and the web app together. Compose does not apply Alembic.
- GitHub Actions runs backend lint, format, and pytest, plus frontend lint and production build.

There is no seeded business data and no logo. The shell uses a small set of interface colors, including a green accent, and is not a brand system. The MVP is single-user and desktop-first. It does not add accounts or a mobile client.

### Production API

| Method | Path | Purpose |
| --- | --- | --- |
| `GET`, `POST` | `/api/production/quintas` | List or create quintas |
| `GET`, `PATCH` | `/api/production/quintas/{quinta_id}` | Read or edit a quinta |
| `GET` | `/api/production/quintas/{quinta_id}/vidrieras` | List vidrieras in a quinta |
| `GET` | `/api/production/quintas/{quinta_id}/vidrieras/next-code` | Suggest the next vidriera code |
| `POST` | `/api/production/quintas/{quinta_id}/vidrieras` | Create a vidriera and its four canteros |
| `GET`, `PATCH` | `/api/production/vidrieras/{vidriera_id}` | Read or edit a vidriera |
| `PATCH` | `/api/production/canteros/{cantero_id}` | Edit a cantero name or active flag |
| `GET` | `/api/production/quintas/{quinta_id}/map` | Read a quinta and its vidrieras for the map |
| `GET`, `PUT`, `DELETE` | `/api/production/quintas/{quinta_id}/boundary` | Read, save, or remove the quinta boundary |
| `GET`, `PUT`, `DELETE` | `/api/production/vidrieras/{vidriera_id}/boundary` | Read, save, or remove one vidriera boundary |

An existing record with no boundary returns `200` and `geometry: null`. A missing record returns `404`. `DELETE` returns `204` and leaves the production record in place. `PUT` can return warnings for overlap or a small overflow. Those warnings are not validation errors.

Lists omit inactive records unless `include_inactive=true`. There is no route that deletes a quinta, vidriera, or cantero.

### Production screens

- `/produccion` lists quintas.
- `/produccion/quintas/nueva` creates a quinta.
- `/produccion/quintas/{quintaId}` shows that quinta and its vidrieras.
- `/produccion/quintas/{quintaId}/vidrieras/nueva` suggests a code and creates a vidriera.
- `/produccion/vidrieras/{vidrieraId}` shows the vidriera and canteros `C1` through `C4`.
- Edit routes under those paths change descriptive data. A cantero edit cannot change its number or its vidriera.
- `/produccion/quintas/{quintaId}/mapa` opens that quinta on a map. Saved polygons are drawn when they exist. A quinta without a boundary remains valid.

### Satellite imagery

The map uses [Esri World Imagery](https://developers.arcgis.com/rest/basemap-styles/service-data/) through the authenticated ArcGIS Location Platform service:

`https://ibasemaps-api.arcgis.com/arcgis/rest/services/World_Imagery/MapServer`

An API key is required. The unauthenticated `services.arcgisonline.com` World Imagery endpoint is not used. Esri documents that service as requiring an ArcGIS license, and a request to the Location Platform tile URL without a token returns an error body (`Token Required`), even when the HTTP status is 200.

Create a free [ArcGIS Location Platform](https://location.arcgis.com/) account and an API key with **Basemaps** and **Geocoding** privileges. Put it in `ESRI_API_KEY`. The Next.js server sends it as `Authorization: Bearer` when it proxies tiles and place search. The browser only calls `/api/imagery/...` on the same origin. Do not prefix the variable with `NEXT_PUBLIC_`.

Place search uses the ArcGIS Geocoding service `findAddressCandidates` with `forStorage=false`, biased toward the La Plata area, so names such as Villa Elisa and Arturo Seguí can be found. Results are not stored.

Attribution has to stay visible. The map shows `Powered by Esri` plus the `copyrightText` returned by the World Imagery service. If that metadata call fails, the fallback text is the attribution Esri publishes for this service: Esri, Maxar, Earthstar Geographics, and the GIS User Community. Leaflet's own attribution stays as well.

Published Location Platform allowances, from [the pricing page](https://location.arcgis.com/pricing/) and the [Static Basemap Tiles](https://developers.arcgis.com/rest/static-basemap-tiles/) and [Geocoding](https://developers.arcgis.com/rest/geocode/) references checked for this feature: 2,000,000 basemap tiles per month, then $0.15 per 1,000 tiles; 20,000 geocodes that are not stored, then $0.50 per 1,000. Confirm the current figures before relying on them. The service is the current World Imagery map tile service in Esri's developer documentation, not a deprecated API. This repository has not visually confirmed greenhouse-level detail around Villa Elisa or Arturo Seguí, because that requires a key and a look at the imagery.

Polygons are GeoJSON in WGS84. Replacing the imagery provider does not require redrawing them.

### Access boundary

Local Compose publishes the database, API, and web app on `127.0.0.1` only. `APP_ACCESS_SECRET` is optional. When it is set, backend routes other than `GET /health` require the header `X-Monteiro-Access`. The Next.js server reads that secret from its own environment and attaches the header. The browser bundle does not receive it. Do not put it in a `NEXT_PUBLIC_` variable. See `.env.example` and [CORE-01](docs/features/CORE-01-application-foundation.md).

The secret protects the API. It does not protect the web application. Pages and server actions call the API with the secret, so anyone who can open the frontend can use Production. The local loopback binding is what keeps that frontend private. An externally exposed frontend needs its own deployment protection, such as a network restriction or an equivalent control in front of the web app. Publishing the API beyond loopback without the secret is not a supported deployment. Publishing the frontend beyond loopback without its own restriction is not a supported deployment either.

Database backup and restore use `pg_dump` and `pg_restore` through the Compose database service. The procedure and its safety rules are in [backup and restore](docs/development/BACKUP.md).

## Product scope

Four committed stages:

1. **Production registration and traceability.** Record farms, production sections, approximate map boundaries, cultivation cycles, and operations, then reconstruct that history.
2. **Harvesting and yield.** Record partial harvests and compare cultivation cycles.
3. **Inventory and production costs.** Track supplies and calculate production cost without assuming a complete opening inventory.
4. **Market and commercial management.** Connect harvests to boxes, dispatch, sales, and unit economics.

Locating quintas and vidrieras on a satellite or aerial map is part of Stage 1 ([PROD-06](docs/features/PROD-06-farm-visual-mapping.md)). Sensors, automation control, voice capture, forecasting, richer satellite analysis, and multi-farm SaaS remain future options. They are not part of the committed roadmap.

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

### Database schema

Compose starts PostgreSQL without the production tables. Start the database with the commands in the next section, then apply the schema before using the Production screens:

```bash
cd backend
uv sync
uv run alembic upgrade head
```

`make migrate` runs the same upgrade. From a running backend container:

```bash
docker compose exec backend uv run alembic upgrade head
```

The upgrade creates empty `quintas`, `vidrieras`, and `canteros` tables. It does not load business records. `docker compose up` does not run it. Until it has run, `GET /health` can still succeed, and Producción reports that the schema is missing instead of showing an empty farm.

Use the same `DATABASE_URL` or `POSTGRES_*` values the API uses. Do not run `alembic downgrade` against a database that already holds business records.

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

`docker compose down` keeps the PostgreSQL volume. `docker compose down -v` deletes it. The volume is mounted at `/var/lib/postgresql` because the PostgreSQL 18 image stores each major version in its own subdirectory and rejects a mount directly on `/var/lib/postgresql/data`.

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

`uv run alembic upgrade head` is required before the Production screens. It applies `0001_production_hierarchy` and creates empty tables. It does not load business records.

Create a later revision when another model exists:

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

`npm run dev` is only needed to run the web app outside Docker. It calls the API at `BACKEND_URL`, or `http://127.0.0.1:8000` when that variable is empty. `npm test` runs the shell unit tests.

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

The Production module lives inside this backend and this frontend. Later modules will too. They are not separate services. See [architecture overview](docs/architecture/OVERVIEW.md).

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
