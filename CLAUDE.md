# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Flask-based deployment automation service for Blindern infrastructure. Exposes a POST /deploy JSON API that triggers Ansible playbook runs. Uses GitHub App auth for git, git-crypt for secrets, and per-service locking to prevent concurrent deploys.

## Commands

```bash
uv sync                              # Install deps
uv run flask run                     # Dev server (port 5000)
uv run pytest                        # Run all tests
uv run pytest tests/test_app.py      # Run single test file
uv run pytest -k test_name           # Run specific test
uv run pre-commit run --all-files    # Lint + format + type check
uv run ruff check --fix .            # Lint (with auto-fix)
uv run ruff format .                 # Format
uv run ty check                      # Type check
```

## Architecture

**Request flow**: POST /deploy → Bearer token auth → validate service/attributes → acquire per-service lock → clone repo (GitHub App HTTPS token) → git-crypt unlock → patch deployer.json → run Ansible playbook → commit & push (retry up to 4x on race).

Dependency injection via Flask-Injector (`injector.py`): Config, Deployer, ServiceLocks as singletons.

**Deployment**: Blue-green — CI deploys deployer-secondary first, then deployer-primary from secondary.

## Configuration

See `.env.template` for required env vars. Tests set most env vars in `conftest.py`.
