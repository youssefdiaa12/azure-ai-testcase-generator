import requests
import os
import json
import html
from typing import List

ORG = os.getenv("AZURE_ORG")
PROJECT = os.getenv("AZURE_PROJECT")
PAT =   os.getenv("AZURE_PAT")                               
ASSIGNED_TO =  os.getenv("AZURE_EMAIL")

AUTH = ("", PAT)

BASE_WIT_URL = f"https://dev.azure.com/{ORG}/{PROJECT}/_apis/wit"
BASE_TEST_URL = f"https://dev.azure.com/{ORG}/{PROJECT}/_apis/test"


# =========================================================
# PUBLIC FUNCTION
# =========================================================

def create_test_cases(story, tests_json, plan_id, suite_id):
    """
    Main entry point:
    - Creates test case work items
    - Links them to suite
    - Links them to user story
    """
    # Normalize AI output

    if isinstance(tests_json, list):
        # Case: AI returned a flat list of test cases
        all_cases = tests_json

    elif isinstance(tests_json, dict):
        # Case: AI returned categorized test cases
        all_cases = tests_json.get("positive", []) + tests_json.get("negative", [])

    else:
        raise Exception("Unexpected AI JSON format: " + str(type(tests_json)))

    for tc in all_cases:
        try:
            test_case_id = create_test_case_work_item(tc)
            if test_case_id:
                link_test_to_suite(test_case_id, plan_id, suite_id)
                link_test_case_to_story(test_case_id, story["id"])
        except Exception as e:
            print(f" Failed creating test case: {str(e)}")


# =========================================================
# CREATE TEST CASE WORK ITEM
# =========================================================

def create_test_case_work_item(test_case):
    """
    Creates Azure DevOps Test Case Work Item
    """

    title = test_case.get("title", "AI Generated Test Case")
    steps = test_case.get("steps", [])
    expected = test_case.get("expected", "")

    steps_xml = build_test_steps_xml(steps, expected)

    patch_document = [
        {
            "op": "add",
            "path": "/fields/System.Title",
            "value": title
        },
        {
            "op": "add",
            "path": "/fields/System.AssignedTo",
            "value": ASSIGNED_TO
        },
        {
            "op": "add",
            "path": "/fields/Microsoft.VSTS.TCM.Steps",
            "value": steps_xml
        },
        {
            "op": "add",
            "path": "/fields/System.Tags",
            "value": "AI_Generated"
        }
    ]

    url = f"{BASE_WIT_URL}/workitems/$Test%20Case?api-version=7.0"

    response = requests.post(
        url,
        headers={"Content-Type": "application/json-patch+json"},
        auth=AUTH,
        data=json.dumps(patch_document)
    )

  


    if response.status_code not in [200, 201]:
        raise Exception(response.text)

    return response.json()["id"]


# =========================================================
# BUILD AZURE TEST STEP XML
# =========================================================

def build_test_steps_xml(steps: List[str], expected: str) -> str:
    """
    Azure DevOps requires test steps stored as XML.
    """

    xml = '<steps id="0" last="{}">'.format(len(steps))

    step_id = 1

    for step in steps:

        xml += f"""
        <step id="{step_id}" type="ActionStep">
            <parameterizedString isformatted="true">
                {html.escape(step)}
            </parameterizedString>
            <parameterizedString isformatted="true">
                {html.escape(expected)}
            </parameterizedString>
        </step>
        """

        step_id += 1

    xml += "</steps>"


    return xml


# =========================================================
# LINK TEST CASE TO TEST SUITE
# =========================================================

def link_test_to_suite(test_case_id, plan_id, suite_id):
    print("I'm on the link of test cases to the test suites")
    url = f"{BASE_TEST_URL}/Plans/{plan_id}/Suites/{suite_id}/testcases/{test_case_id}?api-version=7.0"

    response = requests.post(url, auth=AUTH)

    if response.status_code not in [200, 201]:
        raise Exception(f"Suite link failed: {response.text}")



# =========================================================
# LINK TEST CASE TO USER STORY
# =========================================================

def link_test_case_to_story(test_case_id, story_id):
    """
    Adds Tested By relation
    """

    patch_document = [
        {
            "op": "add",
            "path": "/relations/-",
            "value": {
                "rel": "Microsoft.VSTS.Common.TestedBy-Reverse",
                "url": f"{BASE_WIT_URL}/workItems/{story_id}"
            }
        }
    ]

    url = f"{BASE_WIT_URL}/workitems/{test_case_id}?api-version=7.0"

    response = requests.patch(
        url,
        headers={"Content-Type": "application/json-patch+json"},
        auth=AUTH,
        data=json.dumps(patch_document)
    )

    if response.status_code not in [200, 201]:
        raise Exception(f"Story link failed: {response.text}")

