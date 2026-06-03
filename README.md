# vast-migration
Script for creating views in Vast in preparation for data migration from Unifiles

## Setup

### 1. Install uv

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS / Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Or via pip if you prefer: `pip install uv`

### 2. Install and pin Python 3.14

```bash
uv python install 3.14
uv python pin 3.14
```

### 3. Create a virtual environment and install dependencies

```bash
uv sync --extra dev
```

This creates a `.venv` in the project root, installs all runtime and dev dependencies, and pins versions in `uv.lock`.


## Usage

### 1. Set environment variables
Create a `.env` file in the project root with the following content:

```env
VAST_HOST=your_vast_host
VAST_TOKEN=your_vast_token
PROJECT_DB_API_KEY=your_project_db_api_key
```

### 2. Run the script

```bash
uv run python main.py
```

## Testing

### 1. Run tests

```bash
uv run pytest
```

### 2. Run tests with coverage

```bash
uv run pytest --cov=vast_migration tests/
```

## Linting & Formatting

This project uses [Ruff](https://docs.astral.sh/ruff/) for linting and formatting.

```bash
uv run ruff check .          # lint
uv run ruff check . --fix    # lint and auto-fix
uv run ruff format .         # format
```
