from azure_client import get_recent_user_stories, get_work_item_raw
from hierarchy_manager import get_feature_and_epic
from gemini_client import generate_test_cases
from test_management import (
    get_or_create_test_plan,
    get_or_create_suite
)
from testcase_creator import create_test_cases


stories = get_recent_user_stories()

t = 0
for story in stories:

    raw_story = get_work_item_raw(story["id"])

    feature, epic = get_feature_and_epic(raw_story)

    if not epic:
        print("Story missing epic hierarchy")
        continue

    plan_id,plan_root_suite = get_or_create_test_plan(epic)
    suite_id = get_or_create_suite(plan_id, feature,plan_root_suite,story['id'])

    ai_tests = generate_test_cases(story)
    t=t+1
    print("the ai test for the user story " +str(t) + " is "+ str(ai_tests))
    create_test_cases(story, ai_tests, plan_id, suite_id)
