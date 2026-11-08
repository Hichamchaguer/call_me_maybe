# ============================================================================ #
#  Call Me Maybe — Makefile                                                    #
# ============================================================================ #

PYTHON     ?= python3
UV         ?= uv
SRC_DIR    := src
INPUT_DIR  := data/input
OUTPUT_DIR := data/output

# Default files (can override: make run INPUT_FILE=path/to/x.json)
FUNCS_FILE := $(INPUT_DIR)/functions_definition.json
TESTS_FILE := $(INPUT_DIR)/function_calling_tests.json
OUT_FILE   := $(OUTPUT_DIR)/function_calling_results.json

.PHONY: all install run debug clean lint lint-strict sync help

all: help

## install: Install project dependencies with uv (uv sync)
install: sync

## sync: uv sync (creates .venv from pyproject.toml + uv.lock)
sync:
	@$(UV) sync

## run: Execute the main program
run:
	@$(UV) run $(PYTHON) -m $(SRC_DIR) \
		--functions_definition $(FUNCS_FILE) \
		--input  $(TESTS_FILE) \
		--output $(OUT_FILE)

## debug: Run the main script under pdb
debug:
	@$(UV) run $(PYTHON) -m pdb -m $(SRC_DIR) \
		--functions_definition $(FUNCS_FILE) \
		--input  $(TESTS_FILE) \
		--output $(OUT_FILE)

## clean: Remove caches and temp files
clean:
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache"  -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache"  -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc"        -delete 2>/dev/null || true
	@rm -rf $(OUTPUT_DIR)
	@echo "clean: done"

## lint: flake8 + mypy (mandatory flags)
lint:
	@$(UV) run flake8 .
	@$(UV) run mypy . \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs

## lint-strict: flake8 + mypy --strict
lint-strict:
	@$(UV) run flake8 .
	@$(UV) run mypy . --strict

## help: Show this help
help:
	@echo "Usage: make <target>"
	@echo
	@grep -E '^## ' $(MAKEFILE_LIST) | sed 's/^## /  /'