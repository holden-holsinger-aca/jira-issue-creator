import requests
from excel import extract_excel_info
from add_issue import add_issue
import json
from config import BASE_URL


create_issue_url = f"{BASE_URL}/issue"

# Extract all tickets from Excel
tickets = extract_excel_info()

if not tickets:
    print("No tickets found in Excel file")
    exit()


epic_tickets = tickets[1:5]
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
for ticket in tickets[4:]:
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
