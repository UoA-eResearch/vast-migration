#####
# {
#             "actions": {
#                 "href": "/project/4242/action"
#             },
#             "codes": {
#                 "href": "/project/4242/code"
#             },
#             "creation_date": "2026-06-02T02:49:08Z",
#             "description": "In this project we aim to develop new methods for the detection of a certain eye movement called optokinetic nystagmus, from video and eye tracking data. Therefore we require storage to house data containing video of the face (webcam), video of the eyes (infra-red cameras) and eye tracking data (text format files) with the intent of determining optimal parameters for detection of specific eye movement features. We require storage to house data that we have already collected and data that we would like to collect. ",
#             "division": "BIOENGINST",
#             "end_date": "2029-06-01",
#             "external_references": {
#                 "href": "/project/4242/externalreference"
#             },
#             "href": "/project/4242",
#             "id": 4242,
#             "last_modified": "2026-06-02T02:49:08Z",
#             "members": {
#                 "href": "/project/4242/member"
#             },
#             "next_review_date": "",
#             "notes": "I would like to move existing data to this drive",
#             "original_end_date": "",
#             "properties": {
#                 "href": "/project/4242/property"
#             },
#             "requirements": "Part of a funded project research, Requires human ethics research, Research involving children",
#             "research_outputs": {
#                 "href": "/project/4242/researchoutput"
#             },
#             "services": {
#                 "href": "/project/4242/service"
#             },
#             "start_date": "2026-06-02",
#             "status": {
#                 "href": "/projectstatus/1"
#             },
#             "title": "Eye movement analysis",
#             "todo": ""
#         }
#####

from pydantic import BaseModel

class ResearchDriveProject(BaseModel):
    """Represents the project information for a ProjectDB research drive."""

    model_config = {"extra": "ignore"}

    id: int
    notes: str