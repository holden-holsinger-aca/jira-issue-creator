import requests
from excel import extract_excel_info
from add_issue import add_issue
import json
from config import BASE_URL, HEADERS, AUTH
from ticket_generator import generate_ticket_details

# Configuration flag: Set to False to skip AI-enhanced ticket generation
generate_details = True

create_issue_url = f"{BASE_URL}/issue"

# Extract all tickets from Excel
tickets = extract_excel_info()

if not tickets:
    print("No tickets found in Excel file")
    exit()

# Extract summaries for tickets that need LLM enhancement (child tickets)
child_tickets = tickets[1:]  # All tickets except the epic
if child_tickets and generate_details:
    summaries = [ticket["summary"] for ticket in child_tickets]
    
    print(f"\nGenerating enhanced descriptions and acceptance criteria...")
    try:
        # Generate ticket details using local LLM
        enhanced_details = generate_ticket_details(summaries)
        
        # Update tickets with generated content
        for ticket, details in zip(child_tickets, enhanced_details):
            ticket["description"] = details["description"]
            ticket["acceptance_criteria"] = details["acceptance_criteria"]
            print(f"✅ Enhanced: {ticket['summary'][:50]}...")
    except Exception as e:
        print(f"⚠️  Warning: LLM generation failed ({e}). Using Excel data as-is.")
elif child_tickets and not generate_details:
    print(f"\n⚠️  Skipping AI enhancement (generate_details=False). Using Excel data as-is.")

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

print("\n" + "="*60)
print("Creating Epic in Jira...")
print("="*60)
epic_result = add_issue(payload=epic_payload, full_url=create_issue_url)
epic_key = epic_result.get("key")
print(f"✅ Epic created with key: {epic_key}\n")

# Create child issues (remaining rows) with parent link
print("="*60)
print("Creating child issues in Jira...")
print("="*60)
for idx, ticket in enumerate(child_tickets, start=1):
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

    print(f"[{idx}/{len(child_tickets)}] Creating: {ticket['summary']}")
    result = add_issue(payload=child_payload, full_url=create_issue_url)
    if result.get("key"):
        print(f"✅ Created: {result.get('key')}\n")

print("="*60)
print(f"✅ All done! Created 1 epic and {len(child_tickets)} child issues.")
print("="*60)
