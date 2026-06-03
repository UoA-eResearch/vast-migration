from services.project_db_api import ProjectDBAPIClient
from services.vast_api import VastAPIClient


def main() -> None:
    project_db = ProjectDBAPIClient()
    vast = VastAPIClient()

    # Retrieve research drives from ProjectDB
    drives = project_db.get_research_drives()

    # TODO: Fetch information about archived data on tape, and adjust quotas accordingly.

    # For each research drive, create a matching view in Vast and apply the quota
    for drive in drives:
        vast.create_view(drive)
        vast.set_quota(drive)


if __name__ == "__main__":
    main()
