_default:
    @just --list

_setup-pre-commit:
    #!/usr/bin/env bash
    source .venv/bin/activate
    pre-commit install
    pre-commit install --hook-type commit-msg

# Install the project dependencies
install:
    @uv pip install -e .[dev]

# Setup the development environment
setup:
    mise install
    uv venv
    @just install
    @just _setup-pre-commit

# Run linters against the project
lint *args:
    ruff check {{ args }}

# Run formatters against the project
format *args:
    ruff format {{ args }}

# Run the tests
test: lint format
    pytest

alias t := test

# Check dependency license compatibility for the project
licenses:
    licensecheck --format ansi --zero

# Check the project for linting and formatting issues
check:
    @just lint
    @just format --check

alias c := check

# Generate the changelog
changelog:
    @git cliff -o CHANGELOG.md
