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
# Kept for completeness (not used for suite-link anymore)
BASE_TEST_URL = f"https://dev.azure.com/{ORG}/{PROJECT}/_apis/test"
# Newer test plan endpoint for adding to suite
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

    # Normalize AI output "collection" shape — allow:
    #   - flat list of test cases
    #   - dict with positive/negative(/edge) keys
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
            # Basic shape check for better diagnostics
            if not isinstance(tc, dict):
                raise ValueError(f"Test case #{idx} is not an object: {type(tc)} -> {tc!r}")

            test_case_id = create_test_case_work_item(tc)
            if test_case_id:
                link_test_to_suite(test_case_id, plan_id, suite_id)
                link_test_case_to_story(test_case_id, story["id"])
                print(f"Created and linked test case #{idx}: ID {test_case_id}")
        except Exception as e:
            print(f"Failed creating test case #{idx}: {e}\nPayload:\n{json.dumps(tc, indent=2, ensure_ascii=False)}")


# ================================
# CREATE TEST CASE WORK ITEM
# ================================
def create_test_case_work_item(test_case: Dict[str, Any]) -> int:
    """
    Creates Azure DevOps Test Case Work Item.
    - Normalizes steps/expected to safe string pairs
    - Writes Microsoft.VSTS.TCM.Steps XML
    """

    title = _to_str(test_case.get("title", "AI Generated Test Case"))
    pairs = normalize_to_pairs(test_case)  # [(action, expected), ...]
    steps_xml = build_test_steps_xml_from_pairs(pairs)

    patch_document = [
        {"op": "add", "path": "/fields/System.Title", "value": title},
        {"op": "add", "path": "/fields/System.AssignedTo", "value": ASSIGNED_TO or ""},
        {"op": "add", "path": "/fields/Microsoft.VSTS.TCM.Steps", "value": steps_xml},
        {"op": "add", "path": "/fields/System.Tags", "value": "AI_Generated"},
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
    Use *raw XML tags* (<steps>, <step>, <parameterizedString>), and escape only inner text.
    """

    if not pairs:
        pairs = [("No steps provided", "")]

    xml_parts = []
    last_id = len(pairs)  # 1..N works in practice for step ids
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
# LINK TEST CASE TO TEST SUITE (modern endpoint)
# ================================
def link_test_to_suite(test_case_id: int, plan_id: int, suite_id: int):
    """
    Adds a test case to a suite using the 'testplan' REST API.
    This is the newer, supported route.
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
    Avoids non-string surprises when escaping for XML.
    """
    if x is None:
        return ""
    if isinstance(x, str):
        return x
    if isinstance(x, list):
        return " ".join(_to_str(i) for i in x if i is not None)
    if isinstance(x, dict):
        # Common keys the AI might use
        for k in ("text", "title", "action", "step", "description", "value"):
            if k in x:
                return _to_str(x[k])
        return json.dumps(x, ensure_ascii=False)
    return str(x)


def normalize_to_pairs(test_case: Dict[str, Any]) -> List[Tuple[str, str]]:
    """
    Produce [(action, expected), ...] robustly from a single test_case dict.
    Accept these shapes:
      - steps: [ "Click X", "Click Y" ], expected: "Z appears"
      - steps: [ {"action": "...", "expected": "..."}, {"action": "..."} ], expected: "default"
      - steps: "Single line" (coerced to [ "Single line" ])
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