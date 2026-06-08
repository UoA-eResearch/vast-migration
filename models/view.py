from pydantic import BaseModel


class ShareACL(BaseModel):
    fqdn: str
    name: str
    perm: str
    grantee: str


class ShareACLConfig(BaseModel):
    acl: list[ShareACL]
    enabled: bool


class View(BaseModel):
    """Represents a Vast Data view."""

    model_config = {"extra": "ignore"}

    id: int | None = None
    name: str | None = None
    path: str
    policy: str | None = None
    policy_id: int | None = None
    protocols: list[str] = []
    share: str | None = None
    share_acl: ShareACLConfig | None = None
