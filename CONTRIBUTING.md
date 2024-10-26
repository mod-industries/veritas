# Contributing

Welcome, and thank you for considering contributing to the project!

## Getting Started

### System Dependencies

Several system dependencies are required to make contributions to the package.

- [`mise`](https://mise.jdx.dev/) - Runtime version management
- [`just`](https://just.systems/man/en/) - Project-specific command execution
- [`uv`](https://github.com/astral-sh/uv) - Modern Python package management

### Setup Development Environment

To setup the development environment, simply run the included `setup` command.

```bash
just setup
```

This should setup a virtual environment, install necessary development dependencies, and configure development tools.
You can activate the virtual environment by manually sourcing the `activate` script...

```bash
# Bash / Zsh
source .venv/bin/activate

# Fish
source .venv/bin/activate.fish
```

### Running Tests

All that should be necessary to run tests is to run the included `test` command.

```bash
just test
```
