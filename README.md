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

Copy `.env.example` to create environment-specific files:

```bash
cp .env.example .env.prod
cp .env.example .env.test
```

Fill in the values for each environment. These files are git-ignored — never commit them.

| Variable | Description |
|---|---|
| `VAST_HOST` | Hostname of the Vast Data API |
| `VAST_TOKEN` | API token for Vast Data |
| `PROJECT_DB_API_HOST` | Hostname of the ProjectDB API |
| `PROJECT_DB_API_KEY` | API key for the ProjectDB API |
| `RESEARCH_DRIVES_ROOT` | Root directory in Vast where the views will be created |
| `LOG_LEVEL` | (optional) Logging level (e.g. DEBUG, INFO, WARNING) |
| `WRITE_OUTPUT_FILES` | (optional) Whether to write output files with the results (true/false) |

### 2. Run the script

```bash
uv run --env-file .env.prod python main.py   # production
uv run --env-file .env.test python main.py   # test
```

### Dry run

To verify what the script _would_ do without making any changes in Vast, use the `--dry-run` flag. It will fetch research drives from ProjectDB and check for existing views, but will not create any new views.

```bash
uv run --env-file .env.prod python main.py --dry-run
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
