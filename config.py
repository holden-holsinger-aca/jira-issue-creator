import os
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth


load_dotenv()

# API Configuration
BASE_URL = "https://acaalpha.atlassian.net/rest/api/2"
EMAIL = "holden.holsinger@acaglobal.com"

# must get the API Key from Jira and use correct key to access it below
API_KEY = os.getenv("JIRA_TOKEN")
AUTH = HTTPBasicAuth("holden.holsinger@acaglobal.com", API_KEY)

# Headers
HEADERS = {"Accept": "application/json", "Content-Type": "application/json"}

# Common endpoints
ENDPOINTS = {
    "search_jql": f"{BASE_URL}/search/jql",
    "issues": f"{BASE_URL}/issues",
    "myself": f"{BASE_URL}/myself",
}
