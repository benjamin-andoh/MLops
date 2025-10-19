PY=python
PIP=$(PY) -m pip

.PHONY: precommit-install
precommit-install:
	@echo "Installing dev dependencies and pre-commit hooks..."
	$(PIP) install -r requirements-dev.txt
	@echo "Installing git hooks via pre-commit"
	pre-commit install
	@echo "Running pre-commit on all files"
	pre-commit run --all-files

.PHONY: help
help:
	@echo "Makefile targets:"
	@echo "  precommit-install  - install dev deps and enable pre-commit hooks"
C:\Users\user\Desktop\MLops
