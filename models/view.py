from pydantic import BaseModel

from models.quota import Quota


class View(BaseModel):
    """Represents a Vast Data view."""

    name: str
    path: str
    #TODO:
