import requests
from excel import extract_excel_info
from add_issue import add_issue
import json
from config import BASE_URL
from get_sonar_issue import get_sonar_issue
from sonar_tracking import is_ticket_created, get_existing_ticket, record_created_ticket


CREATE_FROM_EXCEL = False

create_issue_url = f"{BASE_URL}/issue"


def create_issues_from_excel():
    # Extract all tickets from Excel
    tickets_from_excel = extract_excel_info()

    if not tickets_from_excel:
        print("No tickets found in Excel file")
        exit()

    # in the future, could clean this up further to
    # find the first ticket with value 6 and that'll be the first index

    epic_tickets = tickets_from_excel[:4]  # set to the last value that is an epic
    created_epics = {}
    for epic in epic_tickets:
        epic_payload = json.dumps(
            {
                "fields": {
                    "issuetype": {"id": str(epic["issuetype"])},
                    "project": {"key": epic["project"]},
                    "summary": epic["summary"],
                    "customfield_15377": {"value": "Review Workspace"},
                }
            }
        )

        print("Creating Epic...")
        epic_result = add_issue(payload=epic_payload, full_url=create_issue_url)
        epic_key = epic_result.get("key")
        created_epics[epic["epic_id"]] = epic_key
        print(f"Epic created with key: {epic_key}\n")

    # Create child issues (remaining rows) with parent link
    for ticket in tickets_from_excel[4:]:
        # find the epic that matches the epic to link to
        epic_parent = created_epics[ticket["epic_id"]]
        child_payload = json.dumps(
            {
                "fields": {
                    "issuetype": {"id": str(ticket["issuetype"])},
                    "project": {"key": ticket["project"]},
                    "summary": ticket["summary"],
                    "customfield_15377": {"value": "Review Workspace"},
                    "parent": {"key": epic_parent},
                    "description": ticket["description"],
                }
            }
        )

        print(f"Creating child issue: {ticket['summary']}")
        add_issue(payload=child_payload, full_url=create_issue_url)


def create_issue_from_sonar(issue_id: str):
    # Check if ticket already exists
    if is_ticket_created(issue_id):
        existing_ticket = get_existing_ticket(issue_id)
        print(f"Ticket already exists for SonarQube issue {issue_id}: {existing_ticket}")
        return existing_ticket
    
    sonar_issue = get_sonar_issue(issue_id)
    issue_url = f"https://sonar.acaglobal.dev/project/issues?id=rw-api&open={issue_id}"

    sonar_jira_ticket_payload = json.dumps(
        {
            "fields": {
                "issuetype": {"id": 3},
                "project": {"key": "GRW"},
                "summary": f"SonarQube {sonar_issue['issue']}",
                "customfield_15377": {"value": "Review Workspace"},
                "description": (
                    f"An issue needs to be addressed on {sonar_issue['location']}. "
                    f"Per SonarQube rule {sonar_issue['rule']}, SonarQube indicates {sonar_issue['issue']}. The url to the SonarQube entry is {issue_url}"
                ),
                # id of current sprint
                "customfield_10430": 12944,
            }
        }
    )

    result = add_issue(payload=sonar_jira_ticket_payload, full_url=create_issue_url)
    jira_key = result.get("key")
    
    if jira_key:
        record_created_ticket(issue_id, jira_key)
        print(f"Created Jira ticket {jira_key} for SonarQube issue {issue_id}")
    
    return jira_key


if CREATE_FROM_EXCEL:
    create_issues_from_excel()

else:
    sonar_issue_key = "AYubfL6kkWggubew-Kpv"
    create_issue_from_sonar(sonar_issue_key)
