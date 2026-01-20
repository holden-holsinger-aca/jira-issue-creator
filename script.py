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

# Create the epic (first row with issuetype 5)
epic_ticket = tickets[0]
epic_payload = json.dumps(
    {
        "fields": {
            "issuetype": {"id": str(epic_ticket["issuetype"])},
            "project": {"key": epic_ticket["project"]},
            "summary": epic_ticket["summary"],
            "customfield_15377": {"value": "Review Workspace"},
        }
    }
)

print("Creating Epic...")
epic_result = add_issue(payload=epic_payload, full_url=create_issue_url)
epic_key = epic_result.get("key")
print(f"Epic created with key: {epic_key}\n")

# Create child issues (remaining rows) with parent link
for ticket in tickets[1:]:
    child_payload = json.dumps(
        {
            "fields": {
                "issuetype": {"id": str(ticket["issuetype"])},
                "project": {"key": ticket["project"]},
                "summary": ticket["summary"],
                "customfield_15377": {"value": "Review Workspace"},
                "parent": {"key": epic_key},
                "description": ticket["description"],
                "customfield_11930": ticket["acceptance_criteria"],
            }
        }
    )

    print(f"Creating child issue: {ticket['summary']}")
    add_issue(payload=child_payload, full_url=create_issue_url)
