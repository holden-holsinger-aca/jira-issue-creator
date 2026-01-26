import json
import requests
import urllib3

from config import SONAR_AUTH, SONAR_BASE_URL, SONAR_HEADERS


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_sonar_issue(issue_key: str) -> dict:
	"""Fetch a SonarQube issue via /api/issues/search.

	The API expects the `issues` query param (comma-separated issue keys).
	Example: /api/issues/search?issues=AYubfL6kkWggubew-Kpv
	"""

	url = f"{SONAR_BASE_URL}/api/issues/search"
	params = {"issues": issue_key}

	response = requests.get(
		url,
		params=params,
		headers=SONAR_HEADERS,
		auth=SONAR_AUTH,
		verify=False,
	)
	
	trimmed_response = response.json()["issues"][0]
	relevant_fields = {}
	relevant_fields["rule"] = trimmed_response.get("rule")
	relevant_fields["severity"] = trimmed_response.get("severity")
	file = trimmed_response.get("component")
	line = trimmed_response.get("line")
	relevant_fields["location"] = f"{file} line:{line}"
	relevant_fields["issue"] = trimmed_response.get("message")
	

	return relevant_fields
	


if __name__ == "__main__":
	result = get_sonar_issue("AYubfL6kkWggubew-Kpv")
	print(json.dumps(result, sort_keys=True, indent=2))
