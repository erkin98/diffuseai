# Contributing to imggen

Thank you for your interest in contributing to imggen!

## Development Setup

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd diffuseai
   ```

2. **Install dependencies**
   ```bash
   # The dev.sh script will auto-install uv
   ./dev.sh --help
   ```

3. **Run tests**
   ```bash
   uv run pytest
   ```

## Architecture Guidelines

This project follows **Clean Architecture** principles. Please maintain the layered structure:

### Domain Layer (`src/imggen/domain/`)
- **Pure business logic** with zero external dependencies
- Only use Python standard library and Pydantic
- No database, HTTP, or framework code
- Contains: Entities, Value Objects, Domain Services, Exceptions

### Application Layer (`src/imggen/application/`)
- **Use cases** that orchestrate domain objects
- Interface-agnostic (works for CLI, API, SDK)
- Depends only on domain layer
- Receives infrastructure via dependency injection

### Infrastructure Layer (`src/imggen/infrastructure/`)
- **External adapters**: database, GPU providers, storage
- Implements abstract interfaces from domain/application
- Can use any external libraries
- Should be easily swappable (e.g., SQLite → Postgres)

### Interface Layer (`src/imggen/interfaces/`)
- **User interfaces**: CLI, REST API (future), Web UI (future)
- Thin layer that calls application use cases
- No business logic here

## Code Style

- **Format**: Use `ruff format`
- **Lint**: Use `ruff check`
- **Type hints**: Required (enforced by mypy strict mode)
- **Docstrings**: Use Google-style docstrings
- **Line length**: 100 characters

```bash
# Format code
uv run ruff format .

# Check linting
uv run ruff check .

# Type check
uv run mypy src/imggen
```

## Testing

- Write **unit tests** for domain logic
- Write **integration tests** for use cases
- Aim for high coverage of critical paths

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=imggen

# Run specific test file
uv run pytest tests/unit/test_crypto.py
```

## Security Guidelines

This is a security-focused project. Please:

- Never log sensitive data (passwords, keys, plaintext)
- Use constant-time comparisons for sensitive data
- Follow zero-knowledge principles (server never sees master key)
- Use secure random sources (`secrets` module)
- Properly handle encryption errors

## Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Write tests** for your changes

3. **Ensure tests pass**
   ```bash
   uv run pytest
   ```

4. **Format and lint**
   ```bash
   uv run ruff format .
   uv run ruff check .
   ```

5. **Submit PR** with clear description

## Commit Messages

Use clear, descriptive commit messages:

```
feat: add cloud GPU provider support
fix: resolve session timeout issue
docs: update architecture documentation
test: add tests for crypto service
refactor: simplify image repository
```

## Questions?

Open an issue for discussion before major changes.

Thank you for contributing! 🎉

