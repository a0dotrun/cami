# CAMI

Insurance Claim Assistant AI powered by Google ADK, built for Google ADK Hackathon Project.

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

Start the application:

```bash
python main.py
```

The server will be available at `http://localhost:8080`.

## Architecture

For detailed architecture overview, see [Architecture Documentation](assets/Cami-Architecture-Overview.pdf).

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
- **Firebase Admin**: Firebase integration
- **PostgreSQL**: Database (psycopg2-binary)
- **Pydantic**: Data validation

## Development Tools

- **Ruff**: Linting and formatting
- **Pyrefry**: Type checking
- **Pytest**: Testing framework
