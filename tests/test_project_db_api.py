import pytest
import respx
from httpx import Response

from services.project_db_api import ProjectDBAPIClient

class TestProjectDBAPIClient:

    @respx.mock
    def test_get_research_drive_by_name_returns_first_result(self) -> None:
        route = respx.get("https://projectdb.example/researchdrive/drive-a").mock(
            return_value=Response(
                200,
                json=[
                    {
                        "id": 1,
                        "name": "drive-a",
                        "allocated_gb": 100.0,
                        "used_gb": 50.0,
                    },
                    {
                        "id": 2,
                        "name": "drive-a-duplicate",
                        "allocated_gb": 200.0,
                        "used_gb": 80.0,
                    },
                ],
            )
        )

        with ProjectDBAPIClient("https://projectdb.example", "api-key") as client:
            drive = client.get_research_drive_by_name("drive-a")

        assert route.called
        assert drive.id == 1
        assert drive.name == "drive-a"
        assert drive.allocated_gb == 100.0

    @respx.mock
    def test_get_research_drive_by_name_raises_on_empty_response(self) -> None:
        respx.get("https://projectdb.example/researchdrive/missing-drive").mock(
            return_value=Response(200, json=[])
        )

        with ProjectDBAPIClient("https://projectdb.example", "api-key") as client:
            with pytest.raises(
                ValueError, match="No research drive found with name missing-drive"
            ):
                client.get_research_drive_by_name("missing-drive")
