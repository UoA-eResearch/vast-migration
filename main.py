import argparse
import logging

import vastpy

from config import PROJECT_DB_API_HOST, PROJECT_DB_API_KEY, VAST_HOST, VAST_TOKEN, LOG_LEVEL, WRITE_OUTPUT_FILES
from services.project_db_api import ProjectDBAPIClient
from services.vast_api import VastAPIClient

logging.basicConfig(level=getattr(logging, LOG_LEVEL), format="%(asctime)s %(levelname)s %(message)s")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create Vast views for research drives migrated from Unifiles."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Fetch drives and check for existing views, but do not create any views in Vast.",
    )
    args = parser.parse_args()

    if args.dry_run:
        logging.info("Dry run mode enabled — no views will be created.")

    # Retrieve research drives from ProjectDB
    with ProjectDBAPIClient(
        "https://" + PROJECT_DB_API_HOST, PROJECT_DB_API_KEY
    ) as project_db:
        drives = project_db.get_research_drives()
        logging.info(f"Retrieved {len(drives)} research drives from ProjectDB.")

    # TODO: Fetch information about archived data on tape, and adjust quotas accordingly.

    # Initialize Vast API client
    vast = VastAPIClient(VAST_HOST, VAST_TOKEN)
    logging.info("Initialized Vast API client: %s", str(vast))
    # track how many views we create vs skip due to already existing
    created_views = []
    skipped_views = []
    error_views = []

    # For each research drive, create a matching view in Vast and apply the quota
    for drive in drives:
        try:
            if args.dry_run:
                logging.info(
                    f"[DRY RUN] Would create view for research drive {drive.name} with quota {drive.allocated_gb} GB."
                )
                created_views.append(drive)
            else:
                vast.create_research_drive(
                    name=drive.name,
                    quota_gb=int(drive.allocated_gb),
                    group_prefix="unifiles",
                    policy_id=None,  # TODO: Will require a policy ID in Production, but can be left as None for now (use default policy)
                    create_dir=False,  # Don't create the directory since it should already exist once the Unifiles migration is complete
                )
                created_views.append(drive)
        except vastpy.RESTFailure as e:
            if e.status == 409:
                logging.info(
                    f"Conflict for research drive {drive.name}. Skipping. Details: {e}"
                )
                skipped_views.append({"drive": drive, "error": e})
            else:
                raise
        except Exception as e:
            logging.error(f"Error creating view for research drive {drive.name}: {e}")
            error_views.append({"drive": drive, "error": e})

    # Final summary of results
    logging.info("Finished processing research drives.")
    if args.dry_run:
        logging.info(
            f"[DRY RUN] Would have created views for {len(created_views)} drives."
        )
    else:
        logging.info(f"Created views for {len(created_views)} drives.")
    logging.info(f"Skipped views for {len(skipped_views)} drives (already exist).")
    logging.info(f"Error occurred with {len(error_views)} drives.")

    if WRITE_OUTPUT_FILES:
        logging.info("Writing results to output files...")
        import os
        os.makedirs("output", exist_ok=True)
        with open("output/created_views.txt", "w") as f:
            for drive in created_views:
                f.write(f"{drive.name}\n")

        with open("output/skipped_views.txt", "w") as f:
            for item in skipped_views:
                f.write(f"{item['drive'].name}: {item['error']}\n")

        with open("output/error_views.txt", "w") as f:
            for item in error_views:
                f.write(f"{item['drive'].name}: {item['error']}\n")

if __name__ == "__main__":
    main()
