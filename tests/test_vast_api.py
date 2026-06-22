import pytest
from unittest.mock import MagicMock, patch

from services.vast_api import VastAPIClient, ViewAccessProtocol

class TestVastAPIClient:

    @patch("services.vast_api.VASTClient")
    def test_create_view_requires_smb_share_name_when_smb_enabled(
        self, mock_vast_client: MagicMock
    ) -> None:
        mock_vast_client.return_value = MagicMock()
        client = VastAPIClient("vast.example", "token", "research-drives")

        with pytest.raises(ValueError, match="smb_share_name is required"):
            client.create_view(
                path="/research-drives/drive-a",
                policy_id=1,
                protocols=[ViewAccessProtocol.SMB],
            )

    @patch("services.vast_api.VASTClient")
    def test_create_view_rejects_invalid_smb_share_name(
        self, mock_vast_client: MagicMock
    ) -> None:
        mock_vast_client.return_value = MagicMock()
        client = VastAPIClient("vast.example", "token", "research-drives")

        with pytest.raises(ValueError, match="contains invalid characters"):
            client.create_view(
                path="/research-drives/drive-a",
                policy_id=1,
                protocols=[ViewAccessProtocol.SMB],
                smb_share_name="bad/name",
            )

    @patch("services.vast_api.VASTClient")
    def test_create_view_requires_s3_fields_when_s3_enabled(
        self, mock_vast_client: MagicMock
    ) -> None:
        mock_vast_client.return_value = MagicMock()
        client = VastAPIClient("vast.example", "token", "research-drives")

        with pytest.raises(
            ValueError, match="s3_bucket_name and s3_bucket_owner are required"
        ):
            client.create_view(
                path="/research-drives/drive-a",
                policy_id=1,
                protocols=[ViewAccessProtocol.S3],
            )
