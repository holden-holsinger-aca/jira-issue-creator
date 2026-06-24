import os
from requests.auth import HTTPBasicAuth

# API Configuration
BASE_URL = "https://acaalpha.atlassian.net/rest/api/2"
EMAIL = "holden.holsinger@acaglobal.com"

# must get the API Key from Jira and use correct key to access it below
API_KEY = os.getenv("JIRA_TOKEN")
AUTH = HTTPBasicAuth("holden.holsinger@acaglobal.com", API_KEY)

# Headers
HEADERS = {"Accept": "application/json", "Content-Type": "application/json"}

# Default Jira values for created tickets.
# Set accountId from Jira user profile. Leave blank to skip assignment.
DEFAULT_ASSIGNEE_ACCOUNT_ID = "712020:dca60159-0102-45e2-b41e-9417176ddd49"
DEFAULT_JIRA_LABELS = ["ProdSupport"]

# Common endpoints
ENDPOINTS = {
    "search_jql": f"{BASE_URL}/search/jql",
    "issues": f"{BASE_URL}/issues",
    "myself": f"{BASE_URL}/myself",
}


# SonarQube API Configuration
SONAR_BASE_URL = "https://sonar.acaglobal.dev"
SONAR_TOKEN = (
    os.getenv("sonarqube_token")
    or os.getenv("SONAR_TOKEN")
    or os.getenv("SONARQUBE_TOKEN")
)

# SonarQube supports token-based auth via HTTP Basic (token as username, blank password)
SONAR_AUTH = HTTPBasicAuth(SONAR_TOKEN, "") if SONAR_TOKEN else None
SONAR_HEADERS = {"Accept": "application/json"}
