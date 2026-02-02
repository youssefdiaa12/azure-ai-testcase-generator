import requests
import os
from urllib.parse import quote

ORG = os.getenv("AZURE_ORG")
PROJECT = os.getenv("AZURE_PROJECT")
PAT =   os.getenv("AZURE_PAT")

AUTH = ("", PAT)


def get_or_create_test_plan(epic):

    plan_name = f"EPIC-{epic['id']} - {epic['fields']['System.Title']}"

    plans = get_all_test_plans()


    for plan in plans:
        if plan["name"] == plan_name:
            return plan["id"],plan["rootSuite"]

    return create_test_plan(plan_name)


def get_all_test_plans():
    url = f"https://dev.azure.com/{ORG}/{PROJECT}/_apis/testplan/plans?api-version=7.0"

    res = requests.get(url, auth=AUTH)

    return res.json()["value"]


def create_test_plan(name):

    url = f"https://dev.azure.com/{ORG}/{PROJECT}/_apis/testplan/plans?api-version=7.0"
#https://dev.azure.com/{ORG}/{PROJECT}/_apis/testplan/plans?api-version=7.0
    body = {"name": name}
    res = requests.post(url, json=body, auth=AUTH)


    return res.json()["id"],res.json()["rootSuite"]


# Additional functions for test suite and test case management can be added here.
def get_or_create_feature_suite(plan_id, feature,plan_root_suite):

    suite_name = f"FEATURE-{feature['id']} - {feature['fields']['System.Title']}"

    suites = get_suites(plan_id)

    for suite in suites:
        if suite["name"] == suite_name:
            return suite["id"]

    return create_feature_suite(plan_id, suite_name,feature['id'],plan_root_suite)


def create_feature_suite(plan_id, name,feature_id,plan_root_suite):

# GET https://dev.azure.com/{organization}/{project}/_apis/testplan/Plans/{planId}/suites?api-version=7.1
# POST https://dev.azure.com{organization}/{project}/_apis/testplan/Plans/{planId}/Suites?api-version=7.1
#GET https://dev.azure.com/{organization}/{project}/_apis/testplan/Plans/{planId}/suites?api-version=7.1

    url = f"https://dev.azure.com/{ORG}/{PROJECT}/_apis/testplan/Plans/{plan_id}/suites?api-version=7.0"

    body= {
    "name": name,
    "suiteType": "1",
    "parentSuite": {
        "id":plan_root_suite["id"]
        }
    }


    res = requests.post(url, json=body, auth=AUTH)


    return res.json()["id"]




def get_or_create_userstory_suite(plan_id, userstory,plan_root_suite):

    suite_name = f"{userstory['fields']['System.Title']}"
    suites = get_suites(plan_id)

    for suite in suites:
        if suite["name"] == suite_name:
            return suite["id"]

    return create_userstory_suite(plan_id, suite_name,userstory['id'],plan_root_suite)





def create_userstory_suite(plan_id, name,user_story_id,plan_root_suite):

# GET https://dev.azure.com/{organization}/{project}/_apis/testplan/Plans/{planId}/suites?api-version=7.1
# POST https://dev.azure.com{organization}/{project}/_apis/testplan/Plans/{planId}/Suites?api-version=7.1
#GET https://dev.azure.com/{organization}/{project}/_apis/testplan/Plans/{planId}/suites?api-version=7.1

    url = f"https://dev.azure.com/{ORG}/{PROJECT}/_apis/testplan/Plans/{plan_id}/suites?api-version=7.0"

    body= {
    "name": name,
    "suiteType": "3",  # Requirement based suite
    "requirementId": user_story_id,
    "parentSuite": {
        "id":plan_root_suite
        }
    }


    res = requests.post(url, json=body, auth=AUTH)


    return res.json()["id"]



def get_suites(plan_id):

    
    url = f"https://dev.azure.com/{ORG}/{PROJECT}/_apis/testplan/plans/{plan_id}/suites?api-version=7.0"

    res = requests.get(url, auth=AUTH)

    return res.json()["value"]