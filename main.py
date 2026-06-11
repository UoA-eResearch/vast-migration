import argparse
import csv
import logging
import os

import vastpy

from config import (
    LOG_LEVEL,
    PROJECT_DB_API_HOST,
    PROJECT_DB_API_KEY,
    RESEARCH_DRIVES_ROOT,
    VAST_ADDRESS,
    VAST_TOKEN,
    WRITE_OUTPUT_FILES,
)
from models.research_drive import ResearchDrive
from services.project_db_api import ProjectDBAPIClient
from services.vast_api import VastAPIClient

logging.basicConfig(level=getattr(logging, LOG_LEVEL), format="%(asctime)s %(levelname)s %(message)s")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create Vast views for research drives migrated from Unifiles."
    )
    # add csv file argument for list of drives to process
    parser.add_argument(
        "--drives-file",
        type=str,
        required=True,
        help="Path to CSV file containing list of drive names to process (one drive name per line). E.g., 'C:\\path\\to\\drives_to_process.csv'.",
    )
    parser.add_argument(
        "--archived-data-file",
        type=str,
        required=True,
        help="Path to CSV file containing information about size of archived data on tape. E.g., 'C:\\path\\to\\drives-archived-data.csv'.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Fetch drive details and check for existing views, but do not create any views in Vast.",
    )
    args = parser.parse_args()

    if args.dry_run:
        logging.info("[DRY RUN] Dry run mode enabled — no views will be created.")

    # Track success, skipped and error cases for reporting at the end
    created_views = []
    skipped_views = []
    error_views = []

    # Read list of drives to process from csv file
    with open(args.drives_file, encoding="utf-8") as f:
        drive_names_to_process = {line.strip() for line in f if line.strip()}
    logging.info(f"Loaded {len(drive_names_to_process)} drive names to process from {args.drives_file}.")

    # Read information about archived data on tape, and adjust quotas accordingly.
    # Use the ProjectDB quota + premigrated_used + migrated_used to determine the total required quota for each
    # drive, and update the drive allocated_gb value accordingly before creating the view in Vast.
    with open(args.archived_data_file, encoding="utf-8") as f:
        csv_reader = csv.DictReader(f)
        archived_data = {}
        for line in csv_reader:
            drive_name = line["research_project"]
            premigrated_used_kb = float(line["premigrated_used_kb"].replace(",", ""))
            migrated_used_kb = float(line["migrated_used_kb"].replace(",", ""))
            archived_data[drive_name] = {
                "total_archived_used_gb": (premigrated_used_kb + migrated_used_kb)
                / (1024 ** 2)  # Convert KB to GB
            }
    logging.info(f"Loaded archived data info from {args.archived_data_file}.")

    # Retrieve research drives from ProjectDB
    with ProjectDBAPIClient(
        "https://" + PROJECT_DB_API_HOST, PROJECT_DB_API_KEY
    ) as project_db:
        # Fetch drive information for each drive name
        drives: list[ResearchDrive] = []
        for drive_name in drive_names_to_process:
            try:
                drive = project_db.get_research_drive_by_name(drive_name)
                drives.append(drive)
            except Exception as e:
                error_views.append({"drive": drive_name, "error": e})
        logging.info(f"Retrieved {len(drives)} research drives from ProjectDB.")

        for drive in drives:
            if drive.name in archived_data:
                total_archived_used_gb = archived_data[drive.name]["total_archived_used_gb"]
                original_allocated_gb = drive.allocated_gb
                if total_archived_used_gb > 0:
                    drive.allocated_gb += total_archived_used_gb
                    logging.info(
                        f"Adjusted allocated GB for drive {drive.name} from {original_allocated_gb} GB to {drive.allocated_gb} GB based on archived data usage of {total_archived_used_gb} GB."
                    )
            else:
                logging.warning(f"No archived data information found for drive {drive.name}. Using original allocated GB of {drive.allocated_gb} GB.")

        # Initialize Vast API client
        vast = VastAPIClient(VAST_ADDRESS, VAST_TOKEN)

        # Get all existing views in Vast to check for duplicates before creating new ones
        existing_views = vast.get_views()
        logging.info(f"Retrieved {len(existing_views)} existing views from Vast.")

        # For each research drive, create a matching view in Vast and apply the quota
        for drive in drives:
            try:
                # Get the drive group information from ProjectDB
                drive_groups = project_db.get_drive_groups(drive_id=drive.id)

            except Exception as e:
                logging.error(f"Error fetching drive groups for research drive {drive.name}: {e}")
                error_views.append({"drive": drive.name, "error": e})
                continue

            try:
                if any(view.path == f"/{RESEARCH_DRIVES_ROOT}/{drive.name}" for view in existing_views):
                    logging.info(
                        f"View for research drive {drive.name} already exists. Skipping."
                    )
                    skipped_views.append({"drive": drive.name, "details": "Found an existing view in Vast."})
                    continue

                if args.dry_run:
                    logging.info(
                        f"[DRY RUN] Would create view for drive {drive.name} with quota {drive.allocated_gb} GB."
                    )
                    created_views.append({"drive": drive.name, "drive_id": drive.id, "quota_gb": drive.allocated_gb})
                else:
                    vast.create_research_drive(
                        name=drive.name,
                        quota_gb=round(drive.allocated_gb),
                        groups=drive_groups,
                        # TODO: Will require a policy ID in Production, but leave as None for now (use default policy)
                        policy_id=None,
                        # Don't create the directory since it should exist once the Unifiles migration is complete
                        create_dir=False,
                    )
                    created_views.append({"drive": drive.name, "drive_id": drive.id, "quota_gb": drive.allocated_gb})
            except vastpy.RESTFailure as e:
                if e.status == 409:
                    logging.info(
                        f"Conflict for research drive {drive.name}. Skipping. Details: {e}"
                    )
                    skipped_views.append({"drive": drive.name, "details": e})
                else:
                    logging.error(f"HTTP error for research drive {drive.name}: {e}")
                    error_views.append({"drive": drive.name, "error": e})
            except Exception as e:
                logging.error(f"Error creating view for research drive {drive.name}: {e}")
                error_views.append({"drive": drive.name, "error": e})

        # Update the project notes in ProjectDB for drives that had views successfully created
        if args.dry_run:
            logging.info(
                f"[DRY RUN] Would have updated project notes for {len(created_views)} drives."
            )
        else:
            for drive_info in created_views:
                drive_name = drive_info["drive"]
                try:
                    projects = project_db.get_research_drive_projects(drive_id=drive_info["drive_id"])
                    for project in projects:
                        new_notes = f"{project.notes}\n\n[Automated Update] A view has been created in Vast for research drive {drive_name} associated with this project."
                        project_db.update_project_notes(project_id=project.id, new_notes=new_notes)
                except Exception as e:
                    logging.error(f"Error updating project notes for research drive {drive_name}: {e}")
                    error_views.append({"drive": drive_name, "error": f"View created but failed to update project notes: {e}"})

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
            os.makedirs("output", exist_ok=True)
            with open("output/created_views.txt", "w") as f:
                for drive in created_views:
                    f.write(f"{drive['drive']} (ID: {drive['drive_id']}): {drive['quota_gb']} GB\n")

            with open("output/skipped_views.txt", "w") as f:
                for item in skipped_views:
                    f.write(f"{item['drive']}: {item['details']}\n")

            with open("output/error_views.txt", "w") as f:
                for item in error_views:
                    f.write(f"{item['drive']}: {item['error']}\n")

if __name__ == "__main__":
    main()
