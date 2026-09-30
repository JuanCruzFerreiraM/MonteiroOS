# Desarrollo

Guía práctica para trabajar en Monteiro OS después del bootstrap. El día a día está al final.

## Ramas

| Rama | Uso |
| --- | --- |
| `main` | Hitos estables y releases |
| `develop` | Integración. De acá sale el trabajo nuevo |
| `feature/<nombre>` | Funcionalidad |
| `fix/<nombre>` | Corrección |

El bootstrap inicial se hizo directo sobre `develop`. El trabajo posterior no se commitea directo a `develop` ni a `main`.

## Flujo de un cambio

1. Actualizar `develop` y crear la rama desde ahí.
2. Hacer el cambio en `feature/<nombre>` o `fix/<nombre>`.
3. Abrir un pull request hacia `develop`.
4. Esperar a que CI pase.
5. Revisar el PR y mergearlo en `develop`.
6. `main` se actualiza solo en un hito o release, mediante un PR desde `develop`.

No hay automatización extra de GitFlow.

## Commits

[Conventional Commits](https://www.conventionalcommits.org/) en inglés:

```text
feat: add backend health endpoint
fix: correct database connection configuration
docs: add project vision
test: add health endpoint tests
chore: configure backend development environment
ci: add continuous integration workflow
```

El asunto explica el porqué en una o dos oraciones cuando el título no alcanza. No se mezclan en un mismo commit un cambio de producto y un reordenamiento grande sin relación.

## Pull requests

- Base: `develop`, salvo un release hacia `main`.
- El PR tiene que poder leerse sin pedir el contexto por otro canal: qué cambia y cómo se probó.
- CI tiene que estar verde.
- Hace falta revisión antes del merge.

## CI

El workflow `.github/workflows/ci.yml` se llama **CI**. Corre en pull requests hacia `develop` o `main`, y en pushes a esas ramas.

Checks que tienen que pasar, y que deben marcarse como obligatorios en GitHub:

| Job | Qué ejecuta |
| --- | --- |
| `backend` | `uv sync --frozen`, Ruff lint, Ruff format `--check`, pytest contra PostgreSQL |
| `frontend` | `npm ci`, ESLint, build de producción |

No hay deploy, publicación de imágenes ni umbral de cobertura.

## Pre-commit

Instalación, una vez por máquina:

```bash
uv tool install pre-commit
```

Activar los hooks en este clon:

```bash
pre-commit install
```

Correr todo el conjunto a mano:

```bash
pre-commit run --all-files
```

Incluye espacios finales, fin de archivo, YAML, TOML, archivos grandes, conflictos, claves privadas, finales de línea LF, Ruff y, si hay archivos del frontend, Prettier y ESLint.

No corre pytest, el build de Next.js ni Docker. Eso lo hace CI, o los comandos de abajo cuando haga falta.

El hook del frontend usa el `npm` local y `frontend/node_modules`. Si todavía no instalaste dependencias, corré `npm ci` dentro de `frontend/`.

## Tests

Los tests del backend usan PostgreSQL de verdad. No mockean la base para evitar configurarla.

Con el stack levantado y `.env` presente (o los valores por defecto):

```bash
cd backend
uv run pytest
```

`GET /health` devuelve `{"status": "ok"}` solo si `SELECT 1` funciona. Si la base no responde, el endpoint responde `503`.

## Lint y formato

Backend:

```bash
cd backend
uv run ruff check .
uv run ruff format .
uv run ruff format --check .
```

Frontend:

```bash
cd frontend
npm run lint
npm run format
npm run format:check
npm run build
```

## Dependencias

- Python: `backend/pyproject.toml` y el lock `backend/uv.lock`. Agregar con `uv add` o `uv add --dev` desde `backend/`. CI instala con `uv sync --frozen`.
- Node: `frontend/package.json` y `frontend/package-lock.json`. Agregar con `npm install` desde `frontend/`. CI instala con `npm ci`.
- La versión de uv usada en Docker y en CI es 0.12.21. Python del proyecto: 3.13 (`.python-version`).
- Node.js 22.13 o superior. Next.js declara ese mínimo de forma indirecta a través de ESLint.

No se commitean `.venv` ni `node_modules`.

## Migraciones

Alembic está configurado en `backend/alembic` y lee la misma URL que la aplicación.

Estado actual, sin revisiones:

```bash
cd backend
uv run alembic upgrade head
uv run alembic heads
```

Cuando aparezca el primer modelo:

1. Importar el módulo del modelo en el entorno de Alembic para que `Base.metadata` lo vea. Hoy `target_metadata = Base.metadata` y no hay modelos.
2. `uv run alembic revision --autogenerate -m "describe the change"`.
3. Leer el archivo generado en `backend/alembic/versions`.
4. `uv run alembic upgrade head`.
5. Commitear la revisión junto con el modelo.

Dentro de Docker:

```bash
docker compose exec backend uv run alembic upgrade head
```

## Configuración de GitHub

Después de publicar el repositorio, configurar a mano:

1. **Default branch:** `develop`, para que los PR nuevos apunten a integración.
2. **Rulesets o branch protection** en `develop` y en `main`:
   - exigir pull request antes de mergear;
   - exigir los status checks `backend` y `frontend`;
   - exigir que la rama esté actualizada con la base;
   - no permitir force push;
   - no permitir que se mergee un PR con checks fallidos.
3. En `main`, no permitir pushes directos. Los cambios entran desde `develop` en un release.
4. No hace falta un environment de deploy: CI no despliega.

Los nombres exactos de los checks son `backend` y `frontend`.

## Día a día

### Primera vez en la máquina

```bash
git clone <url-del-repositorio>
cd monteiro-os
git checkout develop
cp .env.example .env
uv tool install pre-commit
pre-commit install
docker compose up --build
```

Abrí http://localhost:3000 y http://localhost:8000/health.

### Cada día

```bash
docker compose up --build
```

Cuando termines:

```bash
docker compose down
```

Logs de un servicio:

```bash
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f db
```

`docker compose down` no borra los datos de PostgreSQL. `docker compose down -v` sí borra el volumen. Usalo solo si querés una base vacía.

### Empezar un cambio

```bash
git checkout develop
git pull
git checkout -b feature/nombre-corto
```

Para un bug: `fix/nombre-corto`.

### Ver el efecto

- UI: guardar un archivo del frontend. El contenedor recarga solo.
- API: guardar un archivo en `backend/app`. Uvicorn recarga solo.
- Tests mientras la base está levantada:

```bash
cd backend
uv run pytest
```

### Commit y push

```bash
git status
git add <archivos>
git commit -m "feat: describe the change"
git push -u origin HEAD
```

El hook de pre-commit corre en el commit. Si modifica archivos, revisá el diff y volvé a commitear. Para correrlo antes:

```bash
pre-commit run --all-files
```

### Abrir el PR

Hacia `develop`. CI corre los checks `backend` y `frontend`. No se mergea en rojo ni sin revisión.

```bash
gh pr create --base develop --title "feat: describe the change" --body "Qué cambia y cómo se probó."
```

### Migración en el mismo cambio

Si el cambio agrega o modifica modelos:

```bash
cd backend
uv run alembic revision --autogenerate -m "describe the schema change"
uv run alembic upgrade head
```

La revisión entra en el mismo PR que el modelo. No hace falta una migración vacía para “dejar Alembic andando”: ya está configurado.
