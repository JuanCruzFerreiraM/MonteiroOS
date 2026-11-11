# Development workflow

Lightweight workflow for one engineer working with Cursor. The functional source of truth is the repository, starting at [FEATURES.md](../../FEATURES.md).

## Branches

| Branch | Use |
| --- | --- |
| `main` | Stable milestones and releases |
| `develop` | Integration. New work starts here. |
| `feat/<ID>-<short-name>` | A product feature, for example `feat/OPS-01-operation-registration` |
| `fix/<short-name>` | A correction |

The bootstrap landed directly on `develop`. Later work is not committed straight to `develop` or `main`.

A feature may contain several commits and more than one pull request. One commit per feature is not required.

## Feature flow

1. Select a `Planned` feature from [FEATURES.md](../../FEATURES.md). Prefer the recommended sequence unless a dependency forces a change.
2. Read the specification, the domain documents it cites, and any blocking question in [OPEN_QUESTIONS.md](../OPEN_QUESTIONS.md).
3. Inspect the current backend and frontend before adding packages or routes.
4. Plan the smallest change that satisfies the acceptance criteria.
5. Branch from an up-to-date `develop`.
6. Implement and add or update tests.
7. Check the acceptance criteria, including the failure cases.
8. Update the feature status in `FEATURES.md` when the state actually changes.
9. Open a pull request to `develop`.
10. Merge only after CI is green and the pull request has been reviewed.
11. Move `main` forward only at a milestone, through a pull request from `develop`.

There is no extra GitFlow automation and no external tracker.

## Status values

| Status | Meaning |
| --- | --- |
| `Planned` | Specified, not started. |
| `In Progress` | A branch or pull request exists and the acceptance criteria are not yet verified. |
| `Implemented` | Integrated, and the acceptance criteria have been verified. |
| `Deferred` | Intentionally postponed. The specification stays. |

Do not mark a feature `Implemented` because code was generated. The bootstrap shell does not satisfy CORE-01; that feature stays `Planned` until access and the application shell meet its criteria.

Technical completion and field validation are different. A feature can be `Implemented` in the product while [OPEN_QUESTIONS.md](../OPEN_QUESTIONS.md) still requires a business check, as long as the specification did not depend on that answer. Say so in the pull request.

## Commits

[Conventional Commits](https://www.conventionalcommits.org/) in English:

```text
feat: add vidriera registration
fix: reject a second active cultivation cycle
docs: specify harvest measurements
test: cover health endpoint database failure
chore: configure backend development environment
ci: add continuous integration workflow
```

The body explains why when the subject is not enough. A product change and an unrelated documentation move do not share a commit.

## Pull requests

- Base branch is `develop`, except a release into `main`.
- The description states what changed and how it was verified.
- CI is green.
- Someone reviews the pull request before merge. On a one-person project, the review still checks acceptance criteria, tests, and migrations rather than rubber-stamping.

## CI

`.github/workflows/ci.yml` is named **CI**. It runs on pull requests to `develop` or `main`, and on pushes to those branches.

| Job | What it runs |
| --- | --- |
| `backend` | `uv sync --frozen`, Ruff lint, Ruff format `--check`, pytest against PostgreSQL |
| `frontend` | `npm ci`, ESLint, production build |

There is no deploy, image publish, or coverage threshold. The check names to require in GitHub are `backend` and `frontend`.

## GitHub settings

Configure on the host after the repository is available:

1. Default branch: `develop`.
2. Branch protection or rulesets on `develop` and `main`:
   - require a pull request before merge;
   - require status checks `backend` and `frontend`;
   - require the branch to be up to date;
   - block force pushes;
   - block merge when checks fail.
3. `main` does not accept direct pushes. It updates from `develop` at a release.
4. No deployment environment is required.

## Pre-commit

Once per machine:

```bash
uv tool install pre-commit
pre-commit install
```

Run the hooks manually:

```bash
pre-commit run --all-files
```

Hooks cover trailing whitespace, end of file, YAML, TOML, large files, merge conflicts, private keys, LF line endings, Ruff, and, when frontend files change, Prettier and ESLint.

They do not run pytest, the Next.js build, or Docker. The frontend hook uses local `npm` and `frontend/node_modules`. Run `npm ci` in `frontend/` first.

If a hook modifies files, review the diff and create a new commit. Do not amend a commit that was not created in the current session, and do not skip hooks.

## Tests

Backend tests use PostgreSQL. They do not mock the database in order to avoid configuring it.

With the stack running and `.env` present, or with the default variables:

```bash
cd backend
uv run pytest
```

`GET /health` returns `{"status": "ok"}` only when `SELECT 1` succeeds. If the database is unreachable, the endpoint returns `503`.

Feature work adds tests for the acceptance criteria that can run automatically, including rejected duplicates, overlapping cycles, and incompatible units.

## Lint and format

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

## Dependencies

- Python: `backend/pyproject.toml` and `backend/uv.lock`. Add with `uv add` or `uv add --dev` from `backend/`. CI installs with `uv sync --frozen`.
- Node: `frontend/package.json` and `frontend/package-lock.json`. Add with `npm install` from `frontend/`. CI installs with `npm ci`.
- uv in Docker and CI is 0.12.21. Project Python is 3.13 (`backend/.python-version`).
- Node.js is 22.13 or newer.

`.venv` and `node_modules` are not committed. A documentation-only change does not add runtime dependencies.

## Migrations

Alembic lives in `backend/alembic` and uses the application database URL.

Today there are no revisions:

```bash
cd backend
uv run alembic upgrade head
uv run alembic heads
```

When a feature adds or changes a model:

1. Import the model module so Alembic sees `Base.metadata`. Today `target_metadata = Base.metadata` and no models are imported.
2. `uv run alembic revision --autogenerate -m "describe the change"`.
3. Read the generated file in `backend/alembic/versions`.
4. `uv run alembic upgrade head`.
5. Commit the revision with the model.

Inside Docker:

```bash
docker compose exec backend uv run alembic upgrade head
```

Do not add an empty revision just to exercise Alembic. It is already configured.

## Day to day

### First time on a machine

```bash
git clone https://github.com/JuanCruzFerreiraM/MonteiroOS.git
cd MonteiroOS
git checkout develop
cp .env.example .env
uv tool install pre-commit
pre-commit install
docker compose up --build
```

Open http://localhost:3000 and http://localhost:8000/health.

### Each session

```bash
docker compose up --build
```

When finished:

```bash
docker compose down
```

Logs:

```bash
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f db
```

`docker compose down -v` deletes the PostgreSQL volume. Use it only when a empty database is intended.

### Start a change

```bash
git checkout develop
git pull
git checkout -b feat/OPS-01-operation-registration
```

### See the effect

- UI: save a frontend file. The container reloads.
- API: save a file under `backend/app`. Uvicorn reloads.
- Tests, with the database up:

```bash
cd backend
uv run pytest
```

### Commit, push, and open the pull request

```bash
git status
git add <files>
git commit -m "feat: describe the change"
git push -u origin HEAD
gh pr create --base develop --title "feat: describe the change" --body "What changed and how it was verified."
```

## Documentation updates in the same change

- Behavior changes update the feature specification or the domain document that stated the old rule.
- A newly answered business question updates [OPEN_QUESTIONS.md](../OPEN_QUESTIONS.md) and the specifications that cited it.
- Status changes update [FEATURES.md](../../FEATURES.md).
- Setup changes update the root README and this workflow.
