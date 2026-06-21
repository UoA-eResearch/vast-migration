from barbicanclient.v1 import client as barbican_client
from keystoneauth1 import identity, session
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Configuration settings for the Vast Data migration script."""

    auth_type: str = Field(validation_alias="OS_AUTH_TYPE", default="v3applicationcredential")
    auth_url: str = Field(validation_alias="OS_AUTH_URL")
    region_name: str = Field(validation_alias="OS_REGION_NAME", default="Melbourne")
    interface: str = Field(validation_alias="OS_INTERFACE", default="public")
    application_credential_id: str = Field(validation_alias="OS_APPLICATION_CREDENTIAL_ID")
    application_credential_secret: str = Field(validation_alias="OS_APPLICATION_CREDENTIAL_SECRET")
    vast_address: str = Field(validation_alias="VAST_ADDRESS")
    vast_token: str = Field(validation_alias="VAST_TOKEN")
    project_db_api_host: str = Field(validation_alias="PROJECT_DB_API_HOST")
    research_drives_root: str = Field(validation_alias="RESEARCH_DRIVES_ROOT")
    view_policy_name: str = Field(validation_alias="VIEW_POLICY_NAME")
    log_level: str = Field(validation_alias="LOG_LEVEL", default="INFO")
    write_output_files: bool = Field(validation_alias="WRITE_OUTPUT_FILES", default=True)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


class BarbicanClient:
    """Client for interacting with OpenStack Barbican to retrieve secrets."""

    def __init__(self, config: Config):
        self.config = config
        self.session = self._create_session()

    def _create_session(self) -> session.Session:
        """Create an authenticated session with OpenStack Keystone."""
        auth = identity.V3ApplicationCredential(
            auth_url=self.config.auth_url,
            application_credential_id=self.config.application_credential_id,
            application_credential_secret=self.config.application_credential_secret,
        )
        return session.Session(auth=auth)

    def create_client(self) -> barbican_client.Client:
        """Create a Barbican client using the authenticated session."""
        return barbican_client.Client(version="v1", session=self.session, region_name=self.config.region_name)


config = Config()
bclient = BarbicanClient(config)
barbican = bclient.create_client()
