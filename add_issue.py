import requests
import json
import config


# required fields (refer to the user story submit form to confirm the ones I add below):
# Space, Work type, Summary,

# Fields we want to seriously consider adding:

# jira API docs
# https://developer.atlassian.com/cloud/jira/platform/rest/v2/api-group-issues/#api-rest-api-2-issue-post
# the payload as below needs to be updated to the required fields


def add_issue(payload: dict, full_url: str) -> dict:
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
