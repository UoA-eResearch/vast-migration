import httpx

from models.research_drive import ResearchDrive
from models.view import View


class VastAPIClient:
    """Client for managing views and quotas in Vast Data."""

    def __init__(self, base_url: str = "", api_key: str = "") -> None:
        self.base_url = base_url
        self._client = httpx.Client(
            base_url=base_url,
            headers={"Authorization": f"Bearer {api_key}"} if api_key else {},
        )

    def create_view(self, research_drive: ResearchDrive) -> View:
        """Create a Vast view corresponding to a ProjectDB research drive."""
        raise NotImplementedError

    def set_quota(self, research_drive: ResearchDrive) -> None:
        """Apply the quota from a ProjectDB research drive to the matching Vast view."""
        raise NotImplementedError

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> VastAPIClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
