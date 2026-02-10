import requests
from config import AUTH, HEADERS


def get_current_sprint():
    """
    Get the current active sprint ID for a board using the Agile API.

    Args:
        board_id (int): The Jira board ID

    Returns:
        int: The current sprint ID, or None if no active sprint found
    """

    board_id = 574  # the board for GRW Roadmap

    url = f"https://acaalpha.atlassian.net/rest/agile/1.0/board/{board_id}/sprint"
    params = {"state": "active"}

    try:
        response = requests.get(url, auth=AUTH, headers=HEADERS, params=params)
        response.raise_for_status()

        sprints = response.json().get("values")
        active_grw_sprint = sprints[0]

        if sprints:
            sprint_id = sprints[0]["id"]
            sprint_name = sprints[0]["name"]
            print(f"Current active sprint: {sprint_name} (ID: {sprint_id})")
            return sprint_id
        else:
            print(f"No active sprint found for board {board_id}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error fetching current sprint: {e}")
        return None


if __name__ == "__main__":
    # Test the function - replace with your actual board ID
    # You can find the board ID in the URL when viewing your board:
    # https://acaalpha.atlassian.net/jira/software/projects/GRW/boards/{board_id}
    sprint_id = get_current_sprint()
    if sprint_id:
        print(f"Sprint ID: {sprint_id}")
    else:
        print("Could not retrieve sprint ID")
