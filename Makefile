# ──────────────────────────────────────────────────────────────
# Overdue – Makefile
# ──────────────────────────────────────────────────────────────
SHELL      := /bin/sh
PYTHON     := python3
VENV       := .venv
COMPOSE    := docker compose

.DEFAULT_GOAL := help

# ──────────────────────────────────────────────────────────────
# Editor tooling
# ──────────────────────────────────────────────────────────────

.PHONY: venv
venv: $(VENV)/.installed ## Create a local venv for editor intelligence (autocomplete, go-to-def)

$(VENV)/.installed: pyproject.toml
	@echo "⟳  Syncing editor venv…"
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/pip install --quiet --upgrade pip
	$(VENV)/bin/pip install --quiet -e ".[dev]"
	@touch $@

.PHONY: venv-clean
venv-clean: ## Remove the local editor venv
	rm -rf $(VENV)

# ──────────────────────────────────────────────────────────────
# Docker
# ──────────────────────────────────────────────────────────────

.PHONY: build
build: ## Build the Docker image
	$(COMPOSE) build

.PHONY: up
up: ## Start the app in the background
	$(COMPOSE) up -d

.PHONY: down
down: ## Stop and remove containers
	$(COMPOSE) down

.PHONY: restart
restart: down up ## Restart containers

.PHONY: logs
logs: ## Tail container logs
	$(COMPOSE) logs -f

.PHONY: shell
shell: ## Open a shell inside the running container
	$(COMPOSE) exec overdue /bin/bash

# ──────────────────────────────────────────────────────────────
# Quality (runs inside Docker)
# ──────────────────────────────────────────────────────────────

.PHONY: lint
lint: ## Run ruff linter
	$(COMPOSE) exec overdue ruff check src/

.PHONY: format
format: ## Run ruff formatter
	$(COMPOSE) exec overdue ruff format src/

.PHONY: typecheck
typecheck: ## Run mypy type checker
	$(COMPOSE) exec overdue mypy src/

.PHONY: test
test: ## Run the test suite
	$(COMPOSE) exec overdue pytest

.PHONY: check
check: lint typecheck test ## Run lint + typecheck + tests

# ──────────────────────────────────────────────────────────────
# Assets
# ──────────────────────────────────────────────────────────────

.PHONY: icons
icons: ## Rebuild pixel art icon and avatar SVGs
	$(COMPOSE) exec overdue python scripts/build_icons.py

# ──────────────────────────────────────────────────────────────
# Help
# ──────────────────────────────────────────────────────────────

.PHONY: help
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'
