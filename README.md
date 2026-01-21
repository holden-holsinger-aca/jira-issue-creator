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

## Files

- `script.py` - Main entry point
- `add_issue.py` - Jira API request handler
- `excel.py` - Excel file parser
- `config.py` - Configuration and credentials
- `tickets_to_create.xlsx` - Input data file

## Requirements

- Python 3.7+
- openpyxl
- requests
