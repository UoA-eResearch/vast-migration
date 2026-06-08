from pydantic import BaseModel


class ResearchDriveGroups(BaseModel):
    """Represents the group information for a ProjectDB research drive."""

    model_config = {"extra": "ignore"}

    adm_group: str
    ro_group: str
    rw_group: str
    t_group: str
