from pydantic import BaseModel


class Quota(BaseModel):
    """Represents a Vast Data quota."""

    id: int
    name: str
    soft_limit: int  # bytes
    hard_limit: int  # bytes
    used_capacity: int  # bytes
    used_effective_capacity: int  # bytes
    percent_capacity: int
    path: str  # The path this quota is applied to (e.g. "/myview")
