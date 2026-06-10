from pydantic import BaseModel


class ResearchDriveProject(BaseModel):
    """Represents the project information for a ProjectDB research drive."""

    model_config = {"extra": "ignore"}

    id: int
    notes: str
