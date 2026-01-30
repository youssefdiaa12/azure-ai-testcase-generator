
#Adding them from scripts file
from Scripts.azure_client import get_recent_user_stories, get_work_item_raw
from Scripts.hierarchy_manager import get_feature_and_epic
from Scripts.gemini_client import generate_test_cases
from Scripts.test_management import (
    get_or_create_test_plan,
    get_or_create_suite
)
from Scripts.testcase_creator import create_test_cases


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
    create_test_cases(story, ai_tests, plan_id, suite_id)
