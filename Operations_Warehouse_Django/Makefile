PYTHON ?= python
PIP ?= pip
MANAGE = $(PYTHON) manage.py
PYTEST = pytest

.DEFAULT_GOAL := help

help:
	@echo ""
	@echo "Available commands:"
	@echo "  make install"
	@echo "  make migrate"
	@echo "  make test"
	@echo "  make test-fast"
	@echo "  make test-file FILE=..."
	@echo "  make test-name NAME=..."
	@echo "  make coverage"
	@echo ""

# --------------------------------------
# Docker testing
# --------------------------------------
docker-build-test:
	docker compose -f ./tests/compose.test.yml build

docker-test:
	docker compose -f ./tests/compose.test.yml run --rm test

docker-coverage:
	docker compose -f ./tests/compose.test.yml run --rm test \
		pytest --cov=resource_v4 --cov-report=term

install:
	$(PIP) install -r ./tests/requirements.txt
	$(PIP) install pytest pytest-django pytest-mock pytest-cov

migrate:
	$(MANAGE) migrate

test:
	$(PYTEST)

test-fast:
	$(PYTEST) --reuse-db

test-file:
	$(PYTEST) $(FILE)

test-name:
	$(PYTEST) -k $(NAME)

coverage:
	$(PYTEST) --cov=resource_v4 --cov-report=term --cov-report=html

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache htmlcov .coverage
