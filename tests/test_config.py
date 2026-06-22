from unittest.mock import patch

import pytest
from pydantic import ValidationError

from config import create_barbican_client, load_config


def _set_required_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OS_AUTH_URL", "https://keystone.example/v3")
    monkeypatch.setenv("OS_APPLICATION_CREDENTIAL_ID", "app-cred-id")
    monkeypatch.setenv("OS_APPLICATION_CREDENTIAL_SECRET", "app-cred-secret")
    monkeypatch.setenv("VAST_ADDRESS", "vast.example")
    monkeypatch.setenv("VAST_TOKEN", "vast-token-secret-ref")
    monkeypatch.setenv("PROJECT_DB_API_HOST", "projectdb.example")
    monkeypatch.setenv("PROJECT_DB_API_KEY", "projectdb-key-secret-ref")
    monkeypatch.setenv("RESEARCH_DRIVES_ROOT", "research-drives")
    monkeypatch.setenv("VIEW_POLICY_NAME", "default-policy")


def test_load_config_reads_required_env(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_required_env(monkeypatch)

    cfg = load_config()

    assert cfg.auth_url == "https://keystone.example/v3"
    assert cfg.vast_address == "vast.example"
    assert cfg.project_db_api_host == "projectdb.example"
    assert cfg.research_drives_root == "research-drives"


def test_load_config_raises_when_required_env_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OS_AUTH_URL", raising=False)
    monkeypatch.delenv("OS_APPLICATION_CREDENTIAL_ID", raising=False)
    monkeypatch.delenv("OS_APPLICATION_CREDENTIAL_SECRET", raising=False)
    monkeypatch.delenv("VAST_ADDRESS", raising=False)
    monkeypatch.delenv("VAST_TOKEN", raising=False)
    monkeypatch.delenv("PROJECT_DB_API_HOST", raising=False)
    monkeypatch.delenv("PROJECT_DB_API_KEY", raising=False)
    monkeypatch.delenv("RESEARCH_DRIVES_ROOT", raising=False)
    monkeypatch.delenv("VIEW_POLICY_NAME", raising=False)

    with pytest.raises(ValidationError):
        load_config()


def test_create_barbican_client_passes_expected_kwargs(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_required_env(monkeypatch)
    monkeypatch.setenv("OS_REGION_NAME", "Melbourne")
    monkeypatch.setenv("OS_INTERFACE", "public")
    cfg = load_config()

    with patch("config.barbican_client.Client") as client_ctor:
        sentinel_client = object()
        client_ctor.return_value = sentinel_client

        result = create_barbican_client(cfg)

    assert result is sentinel_client
    client_ctor.assert_called_once()
    kwargs = client_ctor.call_args.kwargs
    assert kwargs["version"] == "v1"
    assert kwargs["region_name"] == "Melbourne"
    assert kwargs["service_type"] == "key-manager"
    assert kwargs["interface"] == "public"
    assert "session" in kwargs
