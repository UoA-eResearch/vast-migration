import logging

import httpx

from models.research_drive import ResearchDrive
from models.research_drive_groups import ResearchDriveGroups


class ProjectDBAPIClient:
    """Client for retrieving research drive information from the ProjectDB API."""

    def __init__(self, base_url: str = "", api_key: str = "") -> None:
        self.base_url = base_url
        self._client = httpx.Client(
            base_url=base_url,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "apikey": api_key,
            },
            timeout=30.0,
        )

    def get_research_drives(self) -> list[ResearchDrive]:
        """Return all Unifiles research drives with their associated quotas."""
        try:
            response = self._client.get("/researchdrive")
            response.raise_for_status()
            return [ResearchDrive.model_validate(drive) for drive in response.json()]
        except httpx.HTTPError as e:
            logging.error(f"Error fetching research drives from ProjectDB: {e}")
            raise

    def get_drive_groups(self, drive_id: int) -> ResearchDriveGroups:
        """Return the group information for a given research drive."""
        try:
            response = self._client.get(f"/researchdrive/{drive_id}/group")
            response.raise_for_status()
            return ResearchDriveGroups.model_validate(response.json())
        except httpx.HTTPError as e:
            logging.error(f"Error fetching drive groups from ProjectDB for drive ID {drive_id}: {e}")
            raise

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> ProjectDBAPIClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
