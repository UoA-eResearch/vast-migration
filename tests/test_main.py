from argparse import Namespace
from pathlib import Path
from types import SimpleNamespace

import pytest

import main
from models.research_drive import ResearchDrive
from models.view import View


def test_get_secret_value_returns_string_payload() -> None:
    barbican = SimpleNamespace(secrets=SimpleNamespace(get=lambda _ref: SimpleNamespace(payload=" secret-value ")))

    value = main._get_secret_value(barbican, "secret-ref", "ProjectDB API key")

    assert value == "secret-value"


def test_get_secret_value_decodes_bytes_payload() -> None:
    barbican = SimpleNamespace(secrets=SimpleNamespace(get=lambda _ref: SimpleNamespace(payload=b" token-bytes \n")))

    value = main._get_secret_value(barbican, "secret-ref", "VAST token")

    assert value == "token-bytes"


def test_get_secret_value_raises_for_missing_payload() -> None:
    barbican = SimpleNamespace(secrets=SimpleNamespace(get=lambda _ref: SimpleNamespace(payload=None)))

    with pytest.raises(RuntimeError, match="has no payload"):
        main._get_secret_value(barbican, "secret-ref", "VAST token")


def test_get_secret_value_wraps_barbican_error() -> None:
    def _raise(_ref: str):
        raise ValueError("not found")

    barbican = SimpleNamespace(secrets=SimpleNamespace(get=_raise))

    with pytest.raises(RuntimeError, match="Error retrieving ProjectDB API key from Barbican"):
        main._get_secret_value(barbican, "secret-ref", "ProjectDB API key")


def test_main_dry_run_smoke(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    drives_file = tmp_path / "drives.csv"
    drives_file.write_text("drive-a\n", encoding="utf-8")

    archived_file = tmp_path / "archived.csv"
    archived_file.write_text(
        "research_project,premigrated_used_kb,migrated_used_kb\n"
        "drive-a,1024,2048\n",
        encoding="utf-8",
    )

    cfg = SimpleNamespace(
        log_level="INFO",
        project_db_api_key="projectdb-key-ref",
        project_db_api_host="projectdb.example",
        vast_token="vast-token-ref",
        vast_address="vast.example",
        research_drives_root="research-drives",
        view_policy_name="policy-a",
        write_output_files=False,
    )

    monkeypatch.setattr(main, "load_config", lambda: cfg)
    monkeypatch.setattr(main, "create_barbican_client", lambda _cfg: SimpleNamespace())
    monkeypatch.setattr(
        main,
        "_get_secret_value",
        lambda barbican, secret_ref, secret_label: {
            "projectdb-key-ref": "projectdb-api-key",
            "vast-token-ref": "vast-token",
        }[secret_ref],
    )

    class FakeProjectDBAPIClient:
        def __init__(self, base_url: str, api_key: str) -> None:
            self.base_url = base_url
            self.api_key = api_key

        def __enter__(self):
            return self

        def __exit__(self, *_args: object) -> None:
            return None

        def get_research_drive_by_name(self, drive_name: str) -> ResearchDrive:
            return ResearchDrive(id=10, name=drive_name, allocated_gb=5.0, used_gb=2.0)

        def get_drive_groups(self, drive_id: int) -> SimpleNamespace:
            return SimpleNamespace(adm_group="adm", ro_group="ro", rw_group="rw", t_group="t")

        def get_research_drive_projects(self, drive_id: int) -> list[SimpleNamespace]:
            return [SimpleNamespace(id=123, notes="")]

        def update_project_notes(self, project_id: int, new_notes: str) -> None:
            return None

    monkeypatch.setattr(main, "ProjectDBAPIClient", FakeProjectDBAPIClient)

    calls: dict[str, int] = {"get_views": 0, "get_view_policies": 0, "create_research_drive": 0}

    class FakeVastAPIClient:
        def __init__(self, address: str, token: str, research_drives_root: str) -> None:
            assert address == "vast.example"
            assert token == "vast-token"
            assert research_drives_root == "research-drives"

        def get_views(self) -> list[View]:
            calls["get_views"] += 1
            return []

        def get_view_policies(self, name: str):
            calls["get_view_policies"] += 1
            assert name == "policy-a"
            return [{"id": 99}]

        def create_research_drive(self, **_kwargs: object) -> None:
            calls["create_research_drive"] += 1

    monkeypatch.setattr(main, "VastAPIClient", FakeVastAPIClient)

    monkeypatch.setattr(
        main.argparse.ArgumentParser,
        "parse_args",
        lambda _self: Namespace(
            drives_file=str(drives_file),
            archived_data_file=str(archived_file),
            dry_run=True,
        ),
    )

    main.main()

    assert calls["get_views"] == 1
    assert calls["get_view_policies"] == 1
    assert calls["create_research_drive"] == 0
