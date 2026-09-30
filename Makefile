.PHONY: up up-d down logs ps test lint format format-check migrate frontend-lint frontend-format frontend-build pre-commit

up:
	docker compose up --build

up-d:
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f

ps:
	docker compose ps

test:
	cd backend && uv run pytest

lint:
	cd backend && uv run ruff check .

format:
	cd backend && uv run ruff format .

format-check:
	cd backend && uv run ruff format --check .

migrate:
	cd backend && uv run alembic upgrade head

frontend-lint:
	cd frontend && npm run lint

frontend-format:
	cd frontend && npm run format

frontend-build:
	cd frontend && npm run build

pre-commit:
	pre-commit run --all-files
