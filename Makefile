.PHONY: help install install-dev test lint format clean build publish docs

# Default target
help:
	@echo "PDF Reader Package - Development Commands"
	@echo "=========================================="
	@echo ""
	@echo "Installation:"
	@echo "  install      - Install package in development mode"
	@echo "  install-dev  - Install package with development dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  test         - Run all tests"
	@echo "  test-cov     - Run tests with coverage report"
	@echo "  test-fast    - Run tests without coverage"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint         - Run all linting checks"
	@echo "  format       - Format code with black and isort"
	@echo "  type-check   - Run type checking with mypy"
	@echo ""
	@echo "Documentation:"
	@echo "  docs         - Build documentation"
	@echo "  docs-serve   - Serve documentation locally"
	@echo ""
	@echo "Package Management:"
	@echo "  clean        - Clean build artifacts"
	@echo "  build        - Build package distribution"
	@echo "  publish      - Publish to PyPI (requires credentials)"
	@echo ""
	@echo "Development:"
	@echo "  setup        - Complete development setup"
	@echo "  check-all    - Run all checks (lint, test, type-check)"

# Installation
install:
	pip install -e .

install-dev:
	pip install -e .[dev]

# Testing
test:
	pytest tests/ -v --cov=pdf_reader --cov-report=term-missing

test-cov:
	pytest tests/ --cov=pdf_reader --cov-report=html --cov-report=term-missing

test-fast:
	pytest tests/ -v

# Code Quality
lint:
	flake8 pdf_reader tests
	black --check pdf_reader tests
	isort --check-only pdf_reader tests

format:
	black pdf_reader tests
	isort pdf_reader tests

type-check:
	mypy pdf_reader

# Documentation
docs:
	cd docs && make html

docs-serve:
	cd docs && python -m http.server 8000

# Package Management
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build:
	python -m build

publish:
	twine upload dist/*

# Development Setup
setup: install-dev
	@echo "Setting up development environment..."
	@echo "Installing pre-commit hooks..."
	pre-commit install

check-all: lint type-check test
	@echo "All checks completed successfully!"

# Security
security:
	bandit -r pdf_reader/
	safety check

# Performance
profile:
	python -m cProfile -o profile.stats -m pytest tests/ -v
	python -c "import pstats; pstats.Stats('profile.stats').sort_stats('cumulative').print_stats(20)"

# Docker
docker-build:
	docker build -t pdf-reader .

docker-run:
	docker run -it pdf-reader

# Environment
venv:
	python -m venv venv
	@echo "Virtual environment created. Activate with: source venv/bin/activate"

# Git hooks
pre-commit:
	pre-commit run --all-files

# Release
release-patch:
	bump2version patch

release-minor:
	bump2version minor

release-major:
	bump2version major

# Utility
check-deps:
	pip list --outdated

update-deps:
	pip install --upgrade -r requirements.txt

# Development server
dev-server:
	python -m http.server 8000

# Backup
backup:
	tar -czf backup-$(shell date +%Y%m%d-%H%M%S).tar.gz pdf_reader/ tests/ *.py *.md *.txt *.toml

# Helpers
.PHONY: show-version show-info

show-version:
	@python -c "import pdf_reader; print(pdf_reader.__version__)"

show-info:
	@python -c "import pdf_reader; print(f'Version: {pdf_reader.__version__}'); print(f'Author: {pdf_reader.__author__}'); print(f'Description: {pdf_reader.__description__}')" 