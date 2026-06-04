import logging

from config import PROJECT_DB_API_HOST, PROJECT_DB_API_KEY, VAST_HOST, VAST_TOKEN, LOG_LEVEL
from services.project_db_api import ProjectDBAPIClient
from services.vast_api import VastAPIClient

logging.basicConfig(level=getattr(logging, LOG_LEVEL), format="%(asctime)s %(levelname)s %(message)s")


def main() -> None:
    # Retrieve research drives from ProjectDB
    with ProjectDBAPIClient(
        "https://" + PROJECT_DB_API_HOST, PROJECT_DB_API_KEY
    ) as project_db:
        drives = project_db.get_research_drives()
        logging.info(f"Retrieved {len(drives)} research drives from ProjectDB.")

    # TODO: Fetch information about archived data on tape, and adjust quotas accordingly.

    # Initialize Vast API client
    with VastAPIClient("https://" + VAST_HOST, VAST_TOKEN) as vast:
        # For each research drive, create a matching view in Vast and apply the quota
        for drive in drives:
            vast.create_view(drive)
            vast.set_quota(drive)


if __name__ == "__main__":
    main()
