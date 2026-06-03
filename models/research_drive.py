from pydantic import BaseModel


class ResearchDrive(BaseModel):
    """Represents a ProjectDB research drive."""

    name: str
    #TODO:
