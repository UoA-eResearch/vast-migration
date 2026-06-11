# vast-migration
Script for creating views in Vast as part of data migration from Unifiles.

Drives to be processed must be provided in a CSV file containing the names of the research drives (e.g. `ressci202300019-testresearchdrive`). This allows us to process drives in batches rather than all at once.

The script will read the list of drive names from the CSV, fetch the corresponding drive info and group names from the Centre for eResearch ProjectDB API, and then create views in Vast with the appropriate ACLs and quotas.

Quotas are determined based on the allocated GB for the drive in ProjectDB, with adjustments if there is archived data usage that should be included in the view quota.

Once a view is successfully created for a research drive, the script also updates the associated project notes in ProjectDB to indicate this.

Additionally, there is a dry-run mode to verify what the script would do without making any changes in Vast or the ProjectDB.


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
| `VAST_ADDRESS` | Address of the Vast Data API |
| `VAST_TOKEN` | API token for Vast Data |
| `PROJECT_DB_API_HOST` | Hostname of the ProjectDB API |
| `PROJECT_DB_API_KEY` | API key for the ProjectDB API |
| `RESEARCH_DRIVES_ROOT` | Root directory in Vast where the views will be created |
| `LOG_LEVEL` | (optional) Logging level (e.g. DEBUG, INFO, WARNING) |
| `WRITE_OUTPUT_FILES` | (optional) Whether to write output files with the results (true/false) |

### 2. Prepare the input CSV file

Create a CSV file with a list of research drive names, one per line. See `input\drives-to-process.example.csv` for the expected format.

### 3. Obtain the Archived data usage CSV file

Get a recent CSV export of the archived data usage for research drives. This file is used to determine if there is archived data that should be included in the view quotas. See `input\drives-archived-data.example.csv` for the expected format.

### 4. Run the script

```bash
uv run --env-file .env.prod python main.py --drives-file input/drives-to-process.csv --archived-data-file input/drives-archived-data.csv  # production
uv run --env-file .env.test python main.py --drives-file input/drives-to-process.csv --archived-data-file input/drives-archived-data.csv   # test
```

#### Dry run

To verify what the script _would_ do without making any changes in Vast, use the `--dry-run` flag. It will fetch research drives from ProjectDB and check for existing views, but will not create any new views or update the project notes in ProjectDB.

```bash
uv run --env-file .env.prod python main.py --drives-file input/drives-to-process.csv --archived-data-file input/drives-archived-data.csv --dry-run
```

#### Results output
If `WRITE_OUTPUT_FILES` is set to `true` (default), the script will write output CSV files to the `./output` folder with details of the created views, skipped views, and error cases.

- Skipped views are drives that already had a view in Vast. These should still be reviewed to ensure they have the correct ACLs and quotas set in Vast.
- Error cases include any drive for which the script attempted to create a view but encountered an error (e.g. due to API issues, required drive or group details not found in CeR ProjectDB etc.). These should be reviewed and remediated as needed (e.g. by manually creating the view in Vast, fixing drive details in ProjectDB, etc.).


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
