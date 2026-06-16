import json
import requests
import urllib3
import subprocess
from urllib.parse import urlparse, parse_qs
import re
import sys

from config import SONAR_AUTH, SONAR_BASE_URL, SONAR_HEADERS

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Project ID to local repository path mapping
PROJECT_REPO_MAP = {
    "te-api": r"C:\source\repos\te-findings-api",
    "drl-api": r"C:\source\repos\drl-api",
    "rw-api": r"C:\source\repos\te-findings-api",
    "mcl-api": r"C:\source\repos\master-content-library",
}


def parse_sonar_url(url: str) -> tuple[str, str]:
    """Parse SonarQube issue URL to extract sonar ticket key and project ID.

    Args:
            url: SonarQube issues URL containing 'open' and 'id' parameters

    Returns:
            Tuple of (issue_key, project_id)

    Example:
            https://sonar.acaglobal.dev/project/issues?open=AYubetXqkWggubew9-Nq&id=te-api
            -> ("AYubetXqkWggubew9-Nq", "te-api")
    """
    parsed = urlparse(url)
    params = parse_qs(parsed.query)

    issue_key = params.get("open", [None])[0]
    project_id = params.get("id", [None])[0]

    if not issue_key or not project_id:
        raise ValueError(f"URL missing 'open' or 'id' parameter: {url}")

    return issue_key, project_id


def extract_jira_id(issue_message: str) -> str:
    """Extract JIRA ID from issue message.

    Args:
            issue_message: The issue message/description from SonarQube

    Returns:
            JIRA ID (e.g., "GRW-1234")
    """
    # Pattern matches JIRA-style IDs (e.g., GRW-1234, TE-567)
    match = re.search(r"([A-Z]+\-\d+)", issue_message)
    if match:
        return match.group(1)
    return None


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


def create_and_switch_branch(repo_path: str, branch_name: str) -> bool:
    """Create a new git branch and switch to it, bringing active changes along.

    Args:
            repo_path: Path to the git repository
            branch_name: Name of the new branch (e.g., "task/GRW-1234")

    Returns:
            True if successful, False otherwise
    """
    try:
        # Stash current changes
        stash_result = subprocess.run(
            ["git", "stash"], cwd=repo_path, capture_output=True, text=True, check=False
        )
        print(f"Stashed changes: {stash_result.stdout.strip()}")

        # Create and switch to new branch
        branch_result = subprocess.run(
            ["git", "checkout", "-b", branch_name],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True,
        )
        print(f"Created and switched to branch: {branch_result.stdout.strip()}")

        # Apply stashed changes
        apply_result = subprocess.run(
            ["git", "stash", "pop"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=False,
        )
        print(f"Applied stashed changes: {apply_result.stdout.strip()}")

        return True
    except subprocess.CalledProcessError as e:
        print(f"Error creating branch: {e.stderr}")
        return False
    except FileNotFoundError:
        print("Git is not installed or not in PATH")
        return False


def process_sonar_url(sonar_url: str) -> dict:
    """Process a SonarQube URL to create a git branch and fetch issue details.

    Args:
            sonar_url: Full SonarQube issues URL with 'open' and 'id' parameters

    Returns:
            Dictionary with issue details and git branch info
    """
    try:
        # Parse URL to get issue key and project ID
        issue_key, project_id = parse_sonar_url(sonar_url)
        print(f"Extracted issue key: {issue_key}, project ID: {project_id}")

        # Get issue details from SonarQube
        issue_details = get_sonar_issue(issue_key)
        print(f"Fetched issue details: {json.dumps(issue_details, indent=2)}")

        # Extract JIRA ID from issue message
        jira_id = extract_jira_id(issue_details.get("issue", ""))
        if not jira_id:
            raise ValueError(
                f"Could not extract JIRA ID from issue: {issue_details.get('issue')}"
            )
        print(f"Extracted JIRA ID: {jira_id}")

        # Get repository path from project ID
        repo_path = PROJECT_REPO_MAP.get(project_id)
        if not repo_path:
            raise ValueError(
                f"Unknown project ID: {project_id}. Known projects: {list(PROJECT_REPO_MAP.keys())}"
            )
        print(f"Repository path: {repo_path}")

        # Create branch
        branch_name = f"task/{jira_id}"
        success = create_and_switch_branch(repo_path, branch_name)

        return {
            "success": success,
            "issue_key": issue_key,
            "project_id": project_id,
            "jira_id": jira_id,
            "branch_name": branch_name,
            "repo_path": repo_path,
            "issue_details": issue_details,
        }
    except Exception as e:
        print(f"Error processing URL: {str(e)}")
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # URL provided as argument
        sonar_url = sys.argv[1]
        result = process_sonar_url(sonar_url)
        print(json.dumps(result, indent=2))
        sys.exit(0 if result.get("success") else 1)
    else:
        # Example with a test issue key
        result = get_sonar_issue("AYubfL6kkWggubew-Kpv")
        print(json.dumps(result, sort_keys=True, indent=2))
