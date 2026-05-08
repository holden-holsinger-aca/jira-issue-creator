import argparse
import json
from pathlib import Path

from add_issue import add_issue
from config import BASE_URL

DEFAULT_PROJECT_KEY = "GRW"
DEFAULT_ISSUE_TYPE_ID = 6
DEFAULT_WORKSPACE_VALUE = "Review Workspace"
DEFAULT_API_NAME = "te-findings-api"
DEFAULT_SUMMARY_TEMPLATE = "Update {controller} in {api} to v3"
DEFAULT_DESCRIPTION_TEMPLATE = (
    "As a developer, I should update {controller} in {api} to v3 so that the "
    "legacy endpoint aligns with the current API contract and platform "
    "standards."
)

DEFAULT_CONTROLLER_FILES_BY_API = {
    "te-findings-api": [
        "LegacyAssociatedSectionsController.cs",
        "LegacyAuthorizationController.cs",
        "LegacyCommentsController.cs",
        "LegacyControllerBase.cs",
        "LegacyDashboardActionItemsController.cs",
        "LegacyDashboardRequestListsController.cs",
        "LegacyDashboardReviewsController.cs",
        "LegacyDashboardTasksController.cs",
        "LegacyDefaultFindingsController.cs",
        "LegacyDefaultReviewsController.cs",
        "LegacyDirectoryController.cs",
        "LegacyFindingsController.cs",
        "LegacyFindingWorkflowController.cs",
        "LegacyMasterRequestListsController.cs",
        "LegacyMasterRequestListWorkflowController.cs",
        "LegacyMasterReviewTestsController.cs",
        "LegacyMasterTestWorkflowController.cs",
        "LegacyOccurrencesController.cs",
        "LegacyOccurrenceWorkflowActionController.cs",
        "LegacyOccurrenceWorkflowController.cs",
        "LegacyQueueProcessorController.cs",
        "LegacyRecommendationsController.cs",
        "LegacyRecommendationWorkflowController.cs",
        "LegacyReferenceDataController.cs",
        "LegacyRelayQueueProcessorController.cs",
        "LegacyRequestListItemCommentsController.cs",
        "LegacyRequestListsController.cs",
        "LegacyRequestListWorkflowController.cs",
        "LegacyRequestsController.cs",
        "LegacyReviewController.cs",
        "LegacyReviewsWorkflowController.cs",
        "LegacyReviewTypesController.cs",
        "LegacyRwSettingsController.cs",
        "LegacySchedulesController.cs",
        "LegacyUserController.cs",
    ],
    "te-api": [
        "LegacyAssetController.cs",
        "LegacyBetaFeaturesController.cs",
        "LegacyClientProfileController.cs",
        "LegacyControllerBase.cs",
        "LegacyDirectoryController.cs",
        "LegacyEngagementAssetController.cs",
        "LegacyEngagementController.cs",
        "LegacyFileExchangeController.cs",
        "LegacyReferenceDataController.cs",
        "LegacyReportController.cs",
        "LegacySettingController.cs",
        "LegacyTeamsAuthController.cs",
        "LegacyUsersController.cs",
    ],
}

CREATE_ISSUE_URL = f"{BASE_URL}/issue"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create Jira dev stories for controller migration work."
    )
    parser.add_argument(
        "--epic-key",
        required=True,
        help="Epic key that all stories should link to.",
    )
    parser.add_argument(
        "--project-key",
        default=DEFAULT_PROJECT_KEY,
        help="Jira project key.",
    )
    parser.add_argument(
        "--issue-type-id",
        type=int,
        default=DEFAULT_ISSUE_TYPE_ID,
        help="Jira issue type id for the created stories.",
    )
    parser.add_argument(
        "--summary-template",
        default=DEFAULT_SUMMARY_TEMPLATE,
        help="Summary template. Tokens: {file}, {controller}, {name}, {api}.",
    )
    parser.add_argument(
        "--description-template",
        default=DEFAULT_DESCRIPTION_TEMPLATE,
        help="Optional description template. Tokens: {file}, {controller}, {name}, {api}.",
    )
    parser.add_argument(
        "--api-name",
        default=DEFAULT_API_NAME,
        help="API or solution name to include in generated tickets.",
    )
    parser.add_argument(
        "--files-from",
        help="Optional text file with one controller filename per line.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the generated stories without creating Jira issues.",
    )
    return parser.parse_args()


def resolve_controller_files(api_name: str, files_from: str | None) -> list[str]:
    if not files_from:
        return list(
            DEFAULT_CONTROLLER_FILES_BY_API.get(
                api_name, DEFAULT_CONTROLLER_FILES_BY_API[DEFAULT_API_NAME]
            )
        )

    return [
        line.strip()
        for line in Path(files_from).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def format_template(template: str, file_name: str, api_name: str) -> str:
    controller_name = Path(file_name).stem
    controller_short_name = controller_name.removesuffix("Controller")
    return template.format(
        file=file_name,
        controller=controller_name,
        name=controller_short_name,
        api=api_name,
    )


def build_payload(
    epic_key: str,
    project_key: str,
    issue_type_id: int,
    summary: str,
    description: str | None,
) -> str:
    fields = {
        "issuetype": {"id": str(issue_type_id)},
        "project": {"key": project_key},
        "summary": summary,
        "customfield_15377": {"value": DEFAULT_WORKSPACE_VALUE},
        "parent": {"key": epic_key},
    }

    if description:
        fields["description"] = description

    return json.dumps({"fields": fields})


def main() -> None:
    args = parse_args()
    controller_files = resolve_controller_files(args.api_name, args.files_from)

    for file_name in controller_files:
        summary = format_template(args.summary_template, file_name, args.api_name)
        description = format_template(
            args.description_template, file_name, args.api_name
        )
        payload = build_payload(
            epic_key=args.epic_key,
            project_key=args.project_key,
            issue_type_id=args.issue_type_id,
            summary=summary,
            description=description,
        )

        if args.dry_run:
            print(summary)
            print(description)
            print()
            continue

        print(f"Creating child issue: {summary}")
        add_issue(payload=payload, full_url=CREATE_ISSUE_URL)


if __name__ == "__main__":
    main()
