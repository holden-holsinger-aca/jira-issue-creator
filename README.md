# Jira Issue Creator

A Python script to bulk create Jira issues from Excel spreadsheets, including support for creating parent epics and linking child issues.

## Features

- Extract issue data from Excel files
- Create parent epic automatically
- Link child issues to parent epic
- Support for custom fields (Initiative field)

## Setup

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate it: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux)
4. Set environment variable for Jira token: `set jira_token=YOUR_API_TOKEN` (Windows)
5. Update `config.py` with your Jira instance details

## Usage

1. Prepare an Excel file `tickets_to_create.xlsx` with columns:
   - Column A: issuetype (5 for Epic, 6 for Story)
   - Column B: project (e.g., GRW)
   - Column C: summary (issue title)
   - Ticket rows must be on a worksheet named `Sheet1` (row 1 headers, data starting row 2)

2. **Workbook configuration (required):**
   - In the spreadsheet's `config` sheet, set cell `A2` to the **Business Unit (BU) name**.
   - Ensure Excel **AutoSave is OFF** for this workbook. Before running the script, **save and close Excel completely** so `script.py` reads the latest on-disk file.

3. **Important Excel Structure Requirements:**
   - Each Excel file should contain **exactly ONE epic** (issuetype 5) - this will be the parent
   - All other rows should be stories (issuetype 6) that will be linked to the epic
   - The Excel functionality currently supports **one business unit's onboarding at a time**
   - Ensure the epic is in the first row (Row 2, after headers) for proper linking
   - If `Sheet1` is missing/renamed, the script will error and list available sheet names

4. Run the script:
   ```bash
   python script.py
   ```

## SonarQube Ticket Creation

The tool supports automatic creation of Jira tickets from SonarQube issues. This feature allows you to track code quality issues identified by SonarQube as Jira tickets.

### How It Works

1. **Issue Retrieval**: The `get_sonar_issue.py` script fetches SonarQube issue details via the SonarQube API, extracting:
   - Rule name
   - Severity level
   - File location and line number
   - Issue message/description

2. **Ticket Creation**: The `create_issue_from_sonar()` function in `script.py`:
   - Checks if a Jira ticket already exists for the SonarQube issue using `sonar_tracking.py`
   - If not found, creates a new Jira ticket (issuetype 3 - Task) in the GRW project
   - Includes the SonarQube issue details and a link back to the SonarQube entry
   - Assigns the ticket to the current sprint

3. **Tracking**: The `sonar_tracking.py` module maintains a CSV file (`sonar_tickets_created.csv`) that tracks:
   - SonarQube issue key
   - Associated Jira ticket key
   - Creation date

### Usage

```python
from script import create_issue_from_sonar

# Create a Jira ticket for a SonarQube issue
If the URL for the SonarQube ticket is "https://sonar.acaglobal.dev/project/issues?issueStatuses=OPEN%2CCONFIRMED&open=683986a2-08ce-4814-9db6-2e8b290e422f&id=drl-api",

You would grab the id from the url and put it as below
create_issue_from_sonar("683986a2-08ce-4814-9db6-2e8b290e422f")
```

The system prevents duplicate ticket creation by checking the tracking CSV file before creating new tickets.

## Files

- `script.py` - Main entry point (contains `create_issue_from_sonar()` function)
- `add_issue.py` - Jira API request handler
- `excel.py` - Excel file parser
- `config.py` - Configuration and credentials
- `get_sonar_issue.py` - SonarQube API interface for fetching issue details
- `sonar_tracking.py` - Tracks created tickets to prevent duplicates
- `get_vector_service_user_stories.py` - Retrieves Jira tickets with Vector Service label
- `tickets_to_create.xlsx` - Input data file
- `sonar_tickets_created.csv` - Tracking file for SonarQube ticket creation

## Requirements

- Python 3.7+
- openpyxl
- requests

## Dev Story Batch Creation

Use `create_dev_stories.py` to create a set of similar dev stories that all link to the same epic.

The script has built-in controller lists for both `te-findings-api` and `te-api`. It picks the correct default list from `--api-name` unless you override it with `--files-from`.

The script includes the current legacy controller list by default and creates story summaries in this format:

```text
Update LegacyAuthorizationController in te-findings-api to v3
```

It also adds this default user-story style description:

```text
As a developer, I should update LegacyAuthorizationController in te-findings-api to v3 so that the legacy endpoint aligns with the current API contract and platform standards.
```

Run a preview first:

```bash
python create_dev_stories.py --epic-key GRW-123 --api-name te-findings-api --dry-run
```

Create the stories in Jira:

```bash
python create_dev_stories.py --epic-key GRW-123 --api-name te-findings-api
```

Create stories for the built-in `te-api` controller list:

```bash
python create_dev_stories.py --epic-key GRW-123 --api-name te-api
```

Optional overrides:

- `--files-from controllers.txt` to supply a different file list
- `--api-name te-api` to switch the generated ticket text to a different API or solution name
- `--summary-template "Update {name} controller to v3"` to customize the summary
- `--description-template "As a developer, I should update {controller} to v3 so that ..."` to customize the repeated description
- `--issue-type-id 6` to change the Jira issue type id if needed
