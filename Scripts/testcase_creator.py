import requests
import os
import json
from typing import List, Any, Dict, Tuple
from xml.sax.saxutils import escape as xml_escape

# ================================
# ENV & CONSTANTS
# ================================
ORG = os.getenv("AZURE_ORG")
PROJECT = os.getenv("AZURE_PROJECT")
PAT = os.getenv("AZURE_PAT")
ASSIGNED_TO = os.getenv("AZURE_EMAIL")

AUTH = ("", PAT or "")

BASE_WIT_URL = f"https://dev.azure.com/{ORG}/{PROJECT}/_apis/wit"
BASE_TESTPLAN_URL = f"https://dev.azure.com/{ORG}/{PROJECT}/_apis/testplan"


# ================================
# PUBLIC ENTRY
# ================================
def create_test_cases(story: Dict[str, Any], tests_json: Any, plan_id: int, suite_id: int):
    """
    Main entry point:
    - Creates test case work items
    - Links them to suite
    - Links them to user story
    """

    # Normalize AI output - allow flat list or dict with type keys
    if isinstance(tests_json, list):
        all_cases = tests_json
    elif isinstance(tests_json, dict):
        all_cases = []
        for key in ("positive", "negative", "edge"):
            if key in tests_json and isinstance(tests_json[key], list):
                all_cases.extend(tests_json[key])
    else:
        raise Exception("Unexpected AI JSON format: " + str(type(tests_json)))

    if not all_cases:
        print("No test cases to create (empty AI output).")
        return

    for idx, tc in enumerate(all_cases, start=1):
        try:
            if not isinstance(tc, dict):
                raise ValueError(f"Test case #{idx} is not an object: {type(tc)}")

            test_case_id = create_test_case_work_item(tc)
            if test_case_id:
                link_test_to_suite(test_case_id, plan_id, suite_id)
                link_test_case_to_story(test_case_id, story["id"])
                print(f"Created test case #{idx}: ID {test_case_id}")
        except Exception as e:
            print(f"Failed creating test case #{idx}: {e}\nPayload:\n{json.dumps(tc, indent=2, ensure_ascii=False)}")




# ================================
# CREATE TEST CASE WORK ITEM
# ================================
def create_test_case_work_item(test_case: Dict[str, Any]) -> int:
    """
    Creates Azure DevOps Test Case Work Item.
    """
    title = _to_str(test_case.get("title", "AI Generated Test Case"))
    test_type = test_case.get("type", "positive")
    pairs = normalize_to_pairs(test_case)
    steps_xml = build_test_steps_xml_from_pairs(pairs)

    patch_document = [
        {"op": "add", "path": "/fields/System.Title", "value": title},
        {"op": "add", "path": "/fields/System.AssignedTo", "value": ASSIGNED_TO or ""},
        {"op": "add", "path": "/fields/Microsoft.VSTS.TCM.Steps", "value": steps_xml},
        {"op": "add", "path": "/fields/System.Tags", "value": f"AI_Generated;{test_type}"},
    ]

    url = f"{BASE_WIT_URL}/workitems/$Test%20Case?api-version=7.0"
    response = requests.post(
        url,
        headers={"Content-Type": "application/json-patch+json", "Accept": "application/json"},
        auth=AUTH,
        data=json.dumps(patch_document),
        timeout=30,
    )

    if response.status_code not in (200, 201):
        raise Exception(f"Work item creation failed: {response.status_code} {response.text}")

    return int(response.json()["id"])


# ================================
# BUILD AZURE TEST STEP XML
# ================================
def build_test_steps_xml_from_pairs(pairs: List[Tuple[str, str]]) -> str:
    """
    Builds the XML expected by Microsoft.VSTS.TCM.Steps.
    """
    if not pairs:
        pairs = [("No steps provided", "")]

    xml_parts = []
    last_id = len(pairs)
    xml_parts.append(f'<steps id="0" last="{last_id}">')

    for i, (action, expected) in enumerate(pairs, start=1):
        action = xml_escape(action or "")
        expected = xml_escape(expected or "")

        xml_parts.append(
            f'<step id="{i}" type="ValidateStep">'
            f'<parameterizedString isformatted="true">{action}</parameterizedString>'
            f'<parameterizedString isformatted="true">{expected}</parameterizedString>'
            f'<description/>'
            f'</step>'
        )

    xml_parts.append("</steps>")
    return "".join(xml_parts)


# ================================
# LINK TEST CASE TO TEST SUITE
# ================================
def link_test_to_suite(test_case_id: int, plan_id: int, suite_id: int):
    """
    Adds a test case to a suite using the testplan REST API.
    """
    url = f"{BASE_TESTPLAN_URL}/Plans/{plan_id}/Suites/{suite_id}/TestCase?api-version=7.1"
    payload = {"workItemIds": [test_case_id]}

    response = requests.post(
        url,
        auth=AUTH,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        data=json.dumps(payload),
        timeout=30,
    )

    if response.status_code not in (200, 201):
        raise Exception(f"Suite link failed: {response.status_code} {response.text}")


# ================================
# LINK TEST CASE TO USER STORY
# ================================
def link_test_case_to_story(test_case_id: int, story_id: int):
    """
    Adds Tested By relation (reverse link to the story).
    """
    patch_document = [
        {
            "op": "add",
            "path": "/relations/-",
            "value": {
                "rel": "Microsoft.VSTS.Common.TestedBy-Reverse",
                "url": f"{BASE_WIT_URL}/workItems/{story_id}",
            },
        }
    ]

    url = f"{BASE_WIT_URL}/workitems/{test_case_id}?api-version=7.0"
    response = requests.patch(
        url,
        headers={"Content-Type": "application/json-patch+json", "Accept": "application/json"},
        auth=AUTH,
        data=json.dumps(patch_document),
        timeout=30,
    )

    if response.status_code not in (200, 201):
        raise Exception(f"Story link failed: {response.status_code} {response.text}")


# ================================
# NORMALIZATION HELPERS
# ================================
def _to_str(x: Any) -> str:
    """
    Convert any value into a single-line string representation.
    """
    if x is None:
        return ""
    if isinstance(x, str):
        return x
    if isinstance(x, list):
        return " ".join(_to_str(i) for i in x if i is not None)
    if isinstance(x, dict):
        for k in ("text", "title", "action", "step", "description", "value"):
            if k in x:
                return _to_str(x[k])
        return json.dumps(x, ensure_ascii=False)
    return str(x)


def normalize_to_pairs(test_case: Dict[str, Any]) -> List[Tuple[str, str]]:
    """
    Produce [(action, expected), ...] from a single test_case dict.
    """
    default_expected = _to_str(test_case.get("expected", ""))
    steps = test_case.get("steps", [])

    if not isinstance(steps, list):
        steps = [steps]

    pairs: List[Tuple[str, str]] = []
    for s in steps:
        if isinstance(s, dict):
            action = _to_str(s.get("action") or s.get("step") or s.get("description") or s)
            exp = _to_str(s.get("expected") or s.get("result") or default_expected)
        else:
            action = _to_str(s)
            exp = default_expected
        pairs.append((action.strip(), exp.strip()))
    return pairs
