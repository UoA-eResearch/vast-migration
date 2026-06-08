from pydantic import BaseModel


class ResearchDrive(BaseModel):
    """Represents a ProjectDB research drive."""

    model_config = {"extra": "ignore"}

    id: int
    name: str
    allocated_gb: float
    used_gb: float
