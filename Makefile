PYTHON := python3
BACKEND_DIR := backend
VENVDIR := .venv
LOCAL_DB_URL := postgresql+psycopg://postgres:postgres@localhost:5433/chatbot
USE_LOCAL := $(shell [ -d $(VENVDIR) ] && echo 1 || echo 0)
ACTIVATE := . $(VENVDIR)/bin/activate &&
API_PORT ?= 9000

.PHONY: install dev-install run test lint fmt compose-up compose-down migrate seed \
	lint-local test-local migrate-local seed-local

install:
	$(PYTHON) -m pip install -r $(BACKEND_DIR)/requirements.txt

dev-install:
	if [ ! -d $(VENVDIR) ]; then $(PYTHON) -m venv $(VENVDIR); fi
	$(ACTIVATE) pip install --upgrade pip
	$(ACTIVATE) pip install -r $(BACKEND_DIR)/requirements-dev.txt

run:
ifeq ($(USE_LOCAL),1)
	$(ACTIVATE) uvicorn app.main:app --host 0.0.0.0 --port $(API_PORT) --app-dir $(BACKEND_DIR) --reload
else
	docker compose up api
endif

lint:
ifeq ($(USE_LOCAL),1)
	$(MAKE) lint-local
else
	docker compose exec api env PYTHONPATH=/app ruff check app tests
endif

lint-local:
	$(ACTIVATE) cd $(BACKEND_DIR) && PYTHONPATH=. ruff check app tests

fmt:
ifeq ($(USE_LOCAL),1)
	$(ACTIVATE) cd $(BACKEND_DIR) && PYTHONPATH=. black app tests
else
	docker compose exec api env PYTHONPATH=/app black app tests
endif

test:
ifeq ($(USE_LOCAL),1)
	$(MAKE) test-local
else
	docker compose exec api env PYTHONPATH=/app pytest
endif

test-local:
	$(ACTIVATE) cd $(BACKEND_DIR) && PYTHONPATH=. pytest

migrate:
ifeq ($(USE_LOCAL),1)
	$(MAKE) migrate-local
else
	docker compose exec api env PYTHONPATH=/app alembic upgrade head
endif

migrate-local:
	$(ACTIVATE) cd $(BACKEND_DIR) && PYTHONPATH=. DATABASE_URL=$(LOCAL_DB_URL) alembic upgrade head

seed:
ifeq ($(USE_LOCAL),1)
	$(MAKE) seed-local
else
	docker compose exec api env PYTHONPATH=/app python -m app.seeds.seed_demo
endif

seed-local:
	$(ACTIVATE) cd $(BACKEND_DIR) && PYTHONPATH=. DATABASE_URL=$(LOCAL_DB_URL) python -m app.seeds.seed_demo

compose-up:
	docker compose up --build

compose-down:
	docker compose down
