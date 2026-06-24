import requests
import json
import config

# required fields (refer to the user story submit form to confirm the ones I add below):
# Space, Work type, Summary,

# Fields we want to seriously consider adding:

# jira API docs
# https://developer.atlassian.com/cloud/jira/platform/rest/v2/api-group-issues/#api-rest-api-2-issue-post
# the payload as below needs to be updated to the required fields


def add_optional_fields(
    fields: dict,
    assignee_account_id: str | None = None,
    labels: list[str] | None = None,
) -> None:
    effective_assignee = (
        assignee_account_id
        if assignee_account_id is not None
        else config.DEFAULT_ASSIGNEE_ACCOUNT_ID
    )
    if effective_assignee:
        fields["assignee"] = {"accountId": effective_assignee}

    effective_labels = labels if labels is not None else config.DEFAULT_JIRA_LABELS
    if effective_labels is None:
        return

    existing_labels = fields.get("labels")
    if isinstance(existing_labels, list):
        fields["labels"] = list(dict.fromkeys(existing_labels + effective_labels))
    else:
        fields["labels"] = list(dict.fromkeys(effective_labels))


def add_issue(payload: str, full_url: str) -> dict:
    response = requests.request(
        "POST",
        full_url,
        data=payload,
        headers=config.HEADERS,
        auth=config.AUTH,
        verify=False,
    )

    result = json.loads(response.text)
    print(json.dumps(result, sort_keys=True, indent=4, separators=(",", ": ")))
    return result
