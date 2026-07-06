from pydantic import BaseModel


class ResearchDriveAclGroups(BaseModel):
    """Represents a ProjectDB research drive ACL group."""

    model_config = {"extra": "ignore"}

    drive_name: str
    group_name: str
    inheritance: str
    permission: str
    posix_permissions: str
