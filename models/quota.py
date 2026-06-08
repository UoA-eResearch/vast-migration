from pydantic import BaseModel


class Quota(BaseModel):
    """Represents a Vast Data quota."""

    id: int
    name: str
    soft_limit: int
    hard_limit: int
    used_capacity: int
    used_effective_capacity: int
    percent_capacity: int
    path: str # The path this quota is applied to (e.g. "/myview")
