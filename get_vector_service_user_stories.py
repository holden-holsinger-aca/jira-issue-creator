import requests
from config import BASE_URL, AUTH, HEADERS


def search_vector_service_detailed():
    url = f"{BASE_URL}/search/jql"
    params = {
        "jql": 'labels = "VectorService" AND customfield_11930 is not EMPTY',
        "startAt": 0,
        "maxResults": 50,
        "fields": "key,summary,description,customfield_11930,customfield_15510",
    }

    response = requests.get(
        url, params=params, headers=HEADERS, auth=AUTH, verify=False
    )

    return response.json()


def retrieve_formatted_ticket_info():
    results = search_vector_service_detailed()
    training_data = []
    for issue in results["issues"]:
        flattened_result = {}
        flattened_result["key"] = issue["key"] if issue["key"] else ""

        flattened_result["summary"] = (
            issue["fields"]["summary"] if issue["fields"]["summary"] else ""
        )

        flattened_result["description"] = (
            issue["fields"]["description"] if issue["fields"]["description"] else ""
        )

        flattened_result["acceptance_criteria"] = (
            issue["fields"]["customfield_11930"]
            if issue["fields"]["customfield_11930"]
            else ""
        )

        flattened_result["release_notes"] = (
            issue["fields"]["customfield_15510"]
            if issue["fields"]["customfield_15510"]
            else ""
        )

        training_data.append(flattened_result)

    return training_data


retrieve_formatted_ticket_info()
