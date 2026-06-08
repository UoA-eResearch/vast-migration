import os


def _require(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise OSError(f"Required environment variable '{key}' is not set.")
    return value


VAST_HOST: str = _require("VAST_HOST")
VAST_TOKEN: str = _require("VAST_TOKEN")
PROJECT_DB_API_HOST: str = _require("PROJECT_DB_API_HOST")
PROJECT_DB_API_KEY: str = _require("PROJECT_DB_API_KEY")
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
WRITE_OUTPUT_FILES: bool = os.getenv("WRITE_OUTPUT_FILES", "false").lower() == "true"
RESEARCH_DRIVES_ROOT: str = os.getenv("RESEARCH_DRIVES_ROOT", "test-smb-view")
USE_TEST_DRIVES: bool = os.getenv("USE_TEST_DRIVES", "true").lower() == "true"
USE_TEST_GROUPS: bool = os.getenv("USE_TEST_GROUPS", "true").lower() == "true"