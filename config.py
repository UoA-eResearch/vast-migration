import os


def _require(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise OSError(f"Required environment variable '{key}' is not set.")
    return value


VAST_ADDRESS: str = _require("VAST_ADDRESS")
VAST_TOKEN: str = _require("VAST_TOKEN")
PROJECT_DB_API_HOST: str = _require("PROJECT_DB_API_HOST")
PROJECT_DB_API_KEY: str = _require("PROJECT_DB_API_KEY")
RESEARCH_DRIVES_ROOT: str = _require("RESEARCH_DRIVES_ROOT") # Root level directory in Vast
VIEW_POLICY_NAME: str = _require("VIEW_POLICY_NAME")

LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
WRITE_OUTPUT_FILES: bool = os.getenv("WRITE_OUTPUT_FILES", "true").lower() == "true"
