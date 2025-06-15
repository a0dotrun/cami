# CAMI

A FastAPI-based application with background task processing using Dramatiq.

## Installation

Install dependencies using uv:

```bash
uv install
```

For development dependencies:

```bash
uv install --dev
```

## Running the Application

### Start the FastAPI Server

```bash
python bin/run.py
```

The server will be available at `http://localhost:8000`.

### Start Background Workers

```bash
python -m dramatiq --threads 1 --process 1 cami.workers.background
```

## Development

### Code Quality

```bash
# Lint code
uv run ruff check

# Auto-fix linting issues
uv run ruff check --fix

# Format code
uv run ruff format

# Type checking
uv run mypy cami
```

### Testing

```bash
# Run all tests
uv run pytest

# Run specific test
uv run pytest tests/test_main.py::test_function_name

# Run with coverage
uv run pytest --cov=cami
```

## Dependencies

- **FastAPI**: Web framework
- **Dramatiq**: Background task processing
- **Firebase Admin**: Firebase integration
- **PostgreSQL**: Database (psycopg2-binary)
- **Redis**: Caching and message broker
- **Pydantic**: Data validation

## Development Tools

- **Ruff**: Linting and formatting
- **MyPy**: Type checking
- **Pytest**: Testing framework
