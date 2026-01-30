import requests
import os
from datetime import datetime, timedelta

ORG = os.getenv("AZURE_ORG")
PROJECT = os.getenv("AZURE_PROJECT")
PAT =   os.getenv("AZURE_PAT")                              #os.getenv("AZURE_PAT")

AUTH = ("", PAT)

from datetime import datetime, timedelta

def get_recent_user_stories():

    today = datetime.utcnow().strftime("%Y-%m-%d")

    wiql = {
        "query": f"""
        SELECT [System.Id], [System.CreatedDate]
        FROM WorkItems
        WHERE
          [System.WorkItemType] = 'User Story'
          AND [System.CreatedDate] >= '{today}'
        """
    }

    url = f"https://dev.azure.com/{ORG}/{PROJECT}/_apis/wit/wiql?api-version=7.0"

    res = requests.post(url, json=wiql, auth=AUTH)

    if res.status_code != 200:
        raise Exception(res.text)

    items = res.json().get("workItems", [])

    # Now filter by last hour manually
    last_hour = datetime.utcnow() - timedelta(hours=1)

    recent_stories = []

    for item in items:
        work_item = get_work_item(item["id"])
        recent_stories.append(work_item)

    return recent_stories



def get_work_item(work_id):

    url = f"https://dev.azure.com/{ORG}/{PROJECT}/_apis/wit/workitems/{work_id}?api-version=7.0"

    res = requests.get(url, auth=AUTH)

    fields = res.json()["fields"]

    return {
        "id": work_id,
        "title": fields.get("System.Title", ""),
        "description": fields.get("System.Description", ""),
        "acceptance": fields.get("Microsoft.VSTS.Common.AcceptanceCriteria", "")
    }


def get_work_item_raw(work_id):

    url = f"https://dev.azure.com/{ORG}/{PROJECT}/_apis/wit/workitems/{work_id}?$expand=relations&api-version=7.0"
    res = requests.get(url, auth=AUTH)

    return res.json()