# TO DO

- Read in list of drives to process from csv file instead of fetching from ProjectDB (since we will not want to process all drives at once)
- Read in info about archived data and apply additional space to drive quotas as needed
- May need to split out the `create_research_drive` function into separate steps so that we can handle error cases more gracefully (e.g. if view already exists, we can still apply/modify the ACLs and quota)
- Add tests for the main script (at least some basic integration tests that mock the Vast and ProjectDB APIs)
- Determine whether `_t` group is needed for anything and if so, add to the view ACLs

## Before running in production:
- Remove all test code and flags
- Confirm view protocols to use (e.g. SMB, S3?) and update the script accordingly
- Get production API credentials and test against the production environment
- Confirm what the default view policy should be, and get the policy ID to use in the script
- Confirm the `research_drives_root` path in production Vast where the views should be created
- Coordinate with the Unifiles migration to ensure that the directories are created in Vast as expected