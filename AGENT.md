# AGENT.md - Codebase Guide for AI Agents

## Commands
- **Build/Install**: `uv install` or `uv install --dev` (for dev dependencies)
- **Lint**: `uv run ruff check` or `uv run ruff check --fix`
- **Format**: `uv run ruff format`
- **Type check**: `uv run mypy cami`
- **Test all**: `uv run pytest`
- **Test single**: `uv run pytest tests/test_main.py::test_function_name`
- **Run server**: `uv run cami` or `uv run python -m cami.server`
- **Run with hypercorn**: `uv run hypercorn cami.server:app`

## Code Style
- **Python version**: 3.13+
- **Line length**: 100 characters
- **Quotes**: Double quotes (`"`)
- **Imports**: Standard library first, third-party, then local (ruff isort)
- **Naming**: snake_case for variables/functions, PascalCase for classes
- **Type hints**: Required for function signatures, use from `typing`
- **Error handling**: Use specific exceptions, log with context using `logging.getLogger(__name__)`
- **Models**: Use Pydantic BaseModel for data validation
- **Async**: Prefer async/await for I/O operations
- **Constants**: UPPER_SNAKE_CASE in config.py
