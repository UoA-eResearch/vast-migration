# class VastAPIClient:
#     """Client for managing views and quotas in Vast Data."""


#     def close(self) -> None:
#         self._client.close()

#     def __enter__(self) -> VastAPIClient:
#         return self

#     def __exit__(self, *args: object) -> None:
#         self.close()


"""Minimal wrapper for the VAST Data python SDK (vastpy).

This module provides `VastAPI`, a small wrapper around
`vastpy.VASTClient`. It validates configuration, initializes the SDK
client, and offers a few helper methods for common operations.

"""

import logging
from enum import Enum
from typing import Any

import vastpy
from vastpy import VASTClient

from config import RESEARCH_DRIVES_ROOT
from models.research_drive_groups import ResearchDriveGroups
from models.view import View

log = logging.getLogger("vast_request")


# This is not a comprehensive list of supported protocols. We can add more as needed.
class ViewAccessProtocol(Enum):
    SMB = "SMB"
    S3 = "S3"
    NFS = "NFS"


class VastAPIClient:
    """Wrapper for `vastpy.VASTClient` that provides helper methods for managing views and quotas in Vast Data."""
    def __init__(
        self,
        address: str,
        token: str,
    ):
        if not address:
            raise ValueError("address is required")

        if not token:
            raise ValueError("token is required")

        self.address = address
        self._token = token

        # Initialize the underlying client.
        self.client = VASTClient(address=address, token=token)
        log.info("Initialized VAST client for %s", address)


    ### View Management ###
    def get_view(self, view_id: int) -> Any:
        """Return the view with the specified `view_id`.

        Raises RuntimeError when the client is not available or when the
        underlying call fails.
        """
        if not self.client:
            raise RuntimeError("VAST client not initialized")

        return self.client.views[view_id].get()

    def get_views(self, path: str = "") -> list[View]:
        """Return the list of views from the cluster. Optionally filter by `path`.

        Raises RuntimeError when the client is not available or when the
        underlying call fails.
        """
        if not self.client:
            raise RuntimeError("VAST client not initialized")

        return [View.model_validate(v) for v in self.client.views.get(path=path)]


    def create_view(
        self,
        path: str,
        policy_id: int | None = None,
        create_dir: bool = True,
        protocols: list[ViewAccessProtocol] | None = None,
        smb_share_name: str | None = None,
        s3_bucket_name: str | None = None,
        s3_bucket_owner: str | None = None,
    ) -> Any:
        """Create a view at `path` using `policy_id` or the default policy.

        `protocols` defaults to ['SMB', 'S3'] if not provided.
        Raises on failure.
        """
        if not self.client:
            raise RuntimeError("VAST client not initialized")
        # Default protocols and normalization to string values
        protocols = protocols or [
            ViewAccessProtocol.SMB,
            ViewAccessProtocol.S3,
        ]
        prot_list: list[str] = []
        for p in protocols:
            if isinstance(p, ViewAccessProtocol):
                prot_list.append(p.value)
            else:
                prot_list.append(str(p).upper())

        # SMB validations
        if "SMB" in prot_list:
            if not smb_share_name:
                raise ValueError(
                    "smb_share_name is required when SMB protocol is enabled"
                )
            forbidden = set('/\\:|<>*?"')
            if any(c in forbidden for c in smb_share_name):
                raise ValueError(
                    'smb_share_name contains invalid characters; it cannot include any of: /\\:|<>*?"'
                )

        # S3 validations
        if "S3" in prot_list:
            if not s3_bucket_name or not s3_bucket_owner:
                raise ValueError(
                    "s3_bucket_name and s3_bucket_owner are required when S3 protocol is enabled"
                )

        if not policy_id:
            policies = self.client.viewpolicies.get(name="default")
            if not policies:
                raise RuntimeError("no default view policy found")
            default = policies[0]
            policy_id = default.get("id") if isinstance(default, dict) else None
            if not policy_id:
                raise RuntimeError("could not determine default policy id")
        view_data = {
            "path": path,
            "policy_id": policy_id,
            "create_dir": create_dir,
            "protocols": prot_list,
            "share": smb_share_name,
            "bucket": s3_bucket_name,
            "bucket-owner": s3_bucket_owner,
            "s3-versioning": True if "S3" in prot_list else None,
        }
        # Remove None values so the API doesn't receive JSON nulls for optional fields
        view_data = {k: v for k, v in view_data.items() if v is not None}
        log.info("creating view with data: %s", view_data)
        return self.client.views.post(**view_data)

    def update_view(
        self,
        view_id: int,
        params: dict,
    ) -> Any:
        """Update the view with the specified `view_id` with the given `params`.
        This allows passing of all options for now.

        Raises on failure.

        Example: To enable share acl on a view this is the data you need to pass:
        {
          "share_acl": {
           "enabled": True,
           "acl": [
             {
               "fqdn": "UoA.auckland.ac.nz",    # The fully qualified domain name of the Active Directory domain
               "name": "<GROUP_OR_USER_NAME>",  # The name of the Active Directory group or user
               "perm": "<PERMISSION_TYPE>",     # FULL | CHANGE | READ
               "grantee": "<GRANTEE_TYPE>",     # groups | users
             }
           ]
          }
        }
        Ref: https://support.vastdata.com/s/api-docs Views > Modify a View
        """
        if not self.client:
            raise RuntimeError("VAST client not initialized")
        log.info("updating view %s with params: %s", view_id, params)
        return self.client.views[view_id].patch(**params)


    ### View Policy Management ###
    def get_view_policies(self) -> Any:
        """Return the list of view policies from the cluster.

        Raises RuntimeError when the client is not available or when the
        underlying call fails.
        """
        if not self.client:
            raise RuntimeError("VAST client not initialized")

        return self.client.viewpolicies.get()


    def create_view_policy(self, policy: Any) -> Any:
        """Create a view policy with the specified policy schema (refer to API documentation).

        Raises on failure.
        """
        if not self.client:
            raise RuntimeError("VAST client not initialized")

        log.info("creating view policy: %s", policy)
        return self.client.viewpolicies.post(**policy)


    ### Quota Management ###
    def get_quotas(self, path: str = "") -> Any:
        """Return the list of quotas from the cluster. Optionally filter by `path`.

        Raises RuntimeError when the client is not available or when the
        underlying call fails.
        """
        if not self.client:
            raise RuntimeError("VAST client not initialized")

        return self.client.quotas.get(path=path)


    def get_quota(self, quota_id: int) -> Any:
        """Return the quota with the specified `quota_id`.

        Raises RuntimeError when the client is not available or when the
        underlying call fails.
        """
        if not self.client:
            raise RuntimeError("VAST client not initialized")

        return self.client.quotas[quota_id].get()


    def create_quota(self, name: str, path: str, quota_gb: int) -> Any:
        """Create a quota with the specified `name`, `path`, and `quota_gb` size.

        Raises on failure.
        Args:
            name: Name of the quota to create
            path: The path to the directory to which quota limits apply.
            quota_gb: The quota size in gigabytes.
        """
        if not self.client:
            raise RuntimeError("VAST client not initialized")

        # Set quota
        quota_bytes = quota_gb * 1024 * 1024 * 1024
        quota_data = {
            "name": f"{name}-quota",
            "path": path,
            "hard_limit": quota_bytes,
            "soft_limit": int(quota_bytes * 0.8),
        }
        log.info("creating quota with data: %s", quota_data)
        return self.client.quotas.post(**quota_data)


    def modify_quota(self, quota_id: int, quota_gb: int) -> Any:
        """Modify the quota with the specified `quota_id` to have the new `quota_gb` size.

        Raises on failure.
        Args:
            quota_id: ID of the quota to modify
            quota_gb: The new quota size in gigabytes.
        """
        if not self.client:
            raise RuntimeError("VAST client not initialized")

        # Update quota
        quota_bytes = quota_gb * 1024 * 1024 * 1024
        quota_data = {
            "hard_limit": quota_bytes,
            "soft_limit": int(quota_bytes * 0.8),
        }
        log.info("modifying quota %s with data: %s", quota_id, quota_data)
        return self.client.quotas[quota_id].patch(**quota_data)


    def delete_quota(self, quota_id: int) -> None:
        """Delete the quota with the specified `quota_id`.

        Raises on failure.
        """
        if not self.client:
            raise RuntimeError("VAST client not initialized")

        log.info("deleting quota %s", quota_id)
        self.client.quotas[quota_id].delete()


    ### Research Drive Handlers ###
    def create_research_drive(
            self,
            name: str,
            quota_gb: int,
            groups: ResearchDriveGroups,
            policy_id: int | None,
            create_dir: bool = True
        ):
        """Create an SMB view for a research drive using the default SMB policy.

        Once the view is created, this handler also adds the appropriate ACLs,
        and sets the specified quota on the view's path.

        Use this handler to create research drives with consistent configuration and permissions,
        instead of having to call the individual methods separately.

        Raises on failure.
        """
        if not self.client:
            raise RuntimeError("VAST client not initialized")

        # Create the view with the default SMB policy
        log.info("creating research drive view for %s", name)
        view = self.create_view(
            path=f"/{RESEARCH_DRIVES_ROOT}/{name}",
            policy_id=policy_id,
            create_dir=create_dir,
            protocols=[ViewAccessProtocol.SMB],
            smb_share_name=name,
        )
        view_id = view.get("id")
        if not view_id:
            raise RuntimeError("could not determine created view id")

        # Define the ACL based on the groups
        acl = []
        if groups.ro_group:
            acl.append({
                "fqdn": "UoA.auckland.ac.nz",
                "name": f"{groups.ro_group}",
                "perm": "READ",
                "grantee": "groups",
            })
        if groups.rw_group:
            acl.append({
                "fqdn": "UoA.auckland.ac.nz",
                "name": f"{groups.rw_group}",
                "perm": "CHANGE",
                "grantee": "groups",
            })
        if groups.adm_group:
            acl.append({
                "fqdn": "UoA.auckland.ac.nz",
                "name": f"{groups.adm_group}",
                "perm": "FULL",
                "grantee": "groups",
            })
        
        if acl:
            acl_params = {
                "share_acl": {
                    "enabled": True,
                    "acl": acl
                }
            }
            log.info("setting ACL on view %s with params: %s", view_id, acl_params)
            self.update_view(view_id=view_id, params=acl_params)

        # Set quota on the view's path
        log.info(
            "setting quota on research drive %s with size %s GB", name, quota_gb
        )
        try:
            self.create_quota(name=f"{name}", path=f"/{RESEARCH_DRIVES_ROOT}/{name}", quota_gb=quota_gb)
        except vastpy.RESTFailure as e:
            if e.status == 409:
                log.info(
                    "Quota for research drive %s already exists. Attempting to modify existing quota. Details: %s",
                    name,
                    e,
                )
                quotas = self.get_quotas(path=f"/{RESEARCH_DRIVES_ROOT}/{name}")
                if not quotas:
                    raise RuntimeError(f"no quotas found for path /{RESEARCH_DRIVES_ROOT}/{name}")
                quota = quotas[0]  # Assuming one quota per research drive path
                quota_id = quota.get("id") if isinstance(quota, dict) else None
                if not quota_id:
                    raise RuntimeError(f"could not determine quota id for path /{RESEARCH_DRIVES_ROOT}/{name}")
                self.modify_quota(quota_id=quota_id, quota_gb=quota_gb)
            else:
                raise
        except Exception as e:
            log.error("failed to create quota for research drive %s: %s", name, e)
            raise

        return {"status": "success", "result": f"created _drive_for_{name}"}


    def resize_research_drive(self, name: str, quota_gb: int):
        """Resize the research drive with the specified `name` to have the new `quota_gb` size.

        Raises on failure.
        Args:
            name: Name of the research drive to resize
            quota_gb: The new quota size in gigabytes.
        """
        if not self.client:
            raise RuntimeError("VAST client not initialized")

        # Get the quota for the view's path
        quotas = self.get_quotas(path=f"/{RESEARCH_DRIVES_ROOT}/{name}")
        if not quotas:
            raise RuntimeError(f"no quotas found for path /{RESEARCH_DRIVES_ROOT}/{name}")

        quota = quotas[0]  # Assuming one quota per research drive path
        quota_id = quota.get("id") if isinstance(quota, dict) else None
        if not quota_id:
            raise RuntimeError(f"could not determine quota id for path /{RESEARCH_DRIVES_ROOT}/{name}")

        # Update the quota with the new size
        log.info(
            "resizing research drive %s by modifying quota %s to size %s GB",
            name,
            quota_id,
            quota_gb,
        )
        quota = self.modify_quota(quota_id=quota_id, quota_gb=quota_gb)
        return {
            "status": "success",
            "folder": name,
            "used_gb": quota.get("used_capacity") / (1024 * 1024 * 1024),
            "quota_gb": quota.get("hard_limit") / (1024 * 1024 * 1024),
        }


    def check_research_drive(self, name: str) -> Any:
        """Return statistics on research drive allocation and current use

        Raises on error.
        """
        if not self.client:
            raise RuntimeError("VAST client not initialized")

        quotas = self.get_quotas(path=f"/{RESEARCH_DRIVES_ROOT}/{name}")
        if not quotas:
            raise RuntimeError(f"no quotas found for path /{RESEARCH_DRIVES_ROOT}/{name}")
        quota = quotas[0]  # Assuming one quota per research drive path
        return {
            "status": "success",
            "folder": name,
            "used_gb": quota.get("used_capacity") / (1024 * 1024 * 1024),
            "quota_gb": quota.get("hard_limit") / (1024 * 1024 * 1024),
        }
