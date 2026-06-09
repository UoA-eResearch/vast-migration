import logging

import httpx

from models.research_drive import ResearchDrive
from models.research_drive_groups import ResearchDriveGroups
from models.research_drive_project import ResearchDriveProject


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

    def get_research_drive_by_name(self, drive_name: str) -> ResearchDrive:
        """Return a research drive by its name."""
        try:
            response = self._client.get(f"/researchdrive/{drive_name}")
            response.raise_for_status()
            drives = response.json()
            if not drives:
                raise ValueError(f"No research drive found with name {drive_name}")
            return ResearchDrive.model_validate(drives[0])
        except httpx.HTTPError as e:
            logging.error(f"Error fetching research drive {drive_name} from ProjectDB: {e}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error occurred while fetching research drive {drive_name}: {e}")
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
        except Exception as e:
            logging.error(f"Unexpected error occurred while fetching drive groups for drive ID {drive_id}: {e}")
            raise

    def get_research_drive_projects(self, drive_id: int) -> list[ResearchDriveProject]:
        """Return the project associated with a given research drive."""
        try:
            query_params = {"expand": "project"}
            response = self._client.get(f"/researchdrive/{drive_id}/project", params=query_params)
            response.raise_for_status()
            project_list = response.json()
            return [ResearchDriveProject.model_validate(project_info["project"]) for project_info in project_list]
        except httpx.HTTPError as e:
            logging.error(f"Error fetching project for research drive ID {drive_id} from ProjectDB: {e}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error occurred while fetching project for research drive ID {drive_id}: {e}")
            raise

    def update_project_notes(self, project_id: int, new_notes: str) -> None:
        """Update the notes for a given project."""
        try:
            payload = {"notes": new_notes}
            response = self._client.patch(f"/project/{project_id}", json=payload)
            response.raise_for_status()
            logging.info(f"Successfully updated notes for project ID {project_id}.")
        except httpx.HTTPError as e:
            logging.error(f"Error updating project notes for project ID {project_id} in ProjectDB: {e}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error occurred while updating project notes for project ID {project_id}: {e}")
            raise

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> ProjectDBAPIClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
