
#Adding them from scripts file
from Scripts.azure_client import get_recent_user_stories, get_work_item_raw
from Scripts.hierarchy_manager import get_feature_and_epic
from Scripts.gemini_client import generate_test_cases
from Scripts.test_management import (
    get_or_create_test_plan,
    get_or_create_feature_suite,
    get_or_create_userstory_suite
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
    feature_suite_id = get_or_create_feature_suite(plan_id, feature,plan_root_suite)
    userstory_suite_id=get_or_create_userstory_suite(plan_id,raw_story,feature_suite_id) 


#story['id']
    ai_tests = generate_test_cases(story)
    print("ai test response is "+str(ai_tests))
    create_test_cases(story, ai_tests, plan_id, userstory_suite_id)
