# Monteiro OS

Monteiro OS es la plataforma interna de gestión, analítica y, más adelante, apoyo a decisiones de un negocio de floricultura en Argentina.

Hoy el repositorio contiene solo la base de desarrollo: API, aplicación web, PostgreSQL y las comprobaciones automáticas. El dominio de negocio todavía se está descubriendo con las personas que operan el negocio, así que no hay módulos de producción, comercial ni finanzas.

## Estado actual

- API con `GET /health`, conectada a PostgreSQL.
- Aplicación web que muestra que el frontend está en funcionamiento.
- Alembic listo para la primera migración real, sin tablas de negocio.
- Entorno de desarrollo con Docker Compose.
- Tests, lint y CI mínimos.

## Stack

| Capa | Tecnología |
| --- | --- |
| Frontend | Next.js, React, TypeScript, ESLint, Prettier |
| Backend | Python 3.13, FastAPI, SQLAlchemy 2, Alembic, uv, Ruff, pytest |
| Datos | PostgreSQL 18 |
| Entorno | Docker Compose |

## Estructura

```text
monteiro-os/
├── backend/          API, configuración, Alembic y tests
├── frontend/         Aplicación Next.js
├── docs/             Visión, arquitectura y flujo de trabajo
├── .github/workflows CI
├── docker-compose.yml
├── Makefile
└── .env.example
```

Los módulos de dominio futuros van a vivir dentro del backend, no como servicios separados. Ver [docs/architecture.md](docs/architecture.md).

## Requisitos

- Git
- Docker Desktop, en ejecución
- [uv](https://docs.astral.sh/uv/) 0.12 o superior, para tests y migraciones en el host
- Node.js 22.13 o superior y npm, para lint y build del frontend en el host
- Make, opcional. Los comandos de abajo también están escritos sin Make

En Windows, Git Bash sirve para los comandos de este documento. `uv` se instala con:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Configuración local

```bash
git clone <url-del-repositorio>
cd monteiro-os
cp .env.example .env
```

`.env` es opcional si se usan los valores por defecto. No se commitea. Las variables están explicadas en `.env.example`.

## Arrancar y detener

```bash
docker compose up --build
```

- Frontend: http://localhost:3000
- API: http://localhost:8000/health
- Documentación de la API: http://localhost:8000/docs

En otra terminal:

```bash
docker compose logs -f
docker compose ps
docker compose down
```

Si el puerto 5432 ya está ocupado por otro PostgreSQL, cambiá `POSTGRES_PORT` en `.env` antes de levantar Compose. El backend dentro de Docker sigue hablando con el servicio `db`; el puerto publicado solo afecta a las herramientas que corren en el host.

Equivalentes con Make, si está instalado: `make up`, `make logs`, `make down`. `make up-d` deja los servicios en segundo plano.

El backend recarga al cambiar código en `backend/app`. El frontend recarga al cambiar la aplicación. Si cambian dependencias de Python, volvé a construir la imagen: `docker compose up --build`. Si cambia `frontend/package-lock.json`, el contenedor ejecuta `npm ci` al iniciar.

## Backend

Desde `backend/`, con PostgreSQL en marcha (el puerto 5432 publicado por Compose alcanza):

```bash
uv sync
uv run pytest
uv run ruff check .
uv run ruff format .
uv run ruff format --check .
uv run alembic upgrade head
```

`alembic upgrade head` hoy no aplica migraciones de negocio: todavía no hay revisiones. Confirma que Alembic llega a la base.

Para crear la primera revisión, cuando exista un modelo real:

```bash
uv run alembic revision --autogenerate -m "short description"
uv run alembic upgrade head
```

## Frontend

Desde `frontend/`:

```bash
npm ci
npm run lint
npm run format
npm run build
npm run dev
```

`npm run dev` solo hace falta si querés el frontend fuera de Docker.

## Pre-commit

```bash
uv tool install pre-commit
pre-commit install
pre-commit run --all-files
```

Los hooks cubren higiene del repositorio, Ruff y el lint/formato del frontend. No ejecutan la suite de tests ni builds.

## Más documentación

- [Visión](docs/vision.md)
- [Arquitectura](docs/architecture.md)
- [Desarrollo día a día](docs/development.md)
- [Roadmap](ROADMAP.md)
