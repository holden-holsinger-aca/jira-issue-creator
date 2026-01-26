import csv
import os
from datetime import datetime

TRACKING_FILE = "sonar_tickets_created.csv"


def initialize_tracking_file():
    """Create the CSV file if it doesn't exist."""
    if not os.path.exists(TRACKING_FILE):
        with open(TRACKING_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["sonar_issue_key", "jira_ticket_key", "created_date"])


def is_ticket_created(sonar_issue_key: str) -> bool:
    """Check if a Jira ticket already exists for this SonarQube issue."""
    initialize_tracking_file()
    
    with open(TRACKING_FILE, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["sonar_issue_key"] == sonar_issue_key:
                return True
    return False


def get_existing_ticket(sonar_issue_key: str) -> str | None:
    """Get the Jira ticket key if one exists for this SonarQube issue."""
    initialize_tracking_file()
    
    with open(TRACKING_FILE, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["sonar_issue_key"] == sonar_issue_key:
                return row["jira_ticket_key"]
    return None


def record_created_ticket(sonar_issue_key: str, jira_ticket_key: str):
    """Record a newly created Jira ticket for a SonarQube issue."""
    initialize_tracking_file()
    
    with open(TRACKING_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([sonar_issue_key, jira_ticket_key, datetime.now().isoformat()])
