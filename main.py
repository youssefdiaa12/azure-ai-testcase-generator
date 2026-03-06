#Adding them from scripts file
from Scripts.azure_client import get_recent_user_stories, get_work_item_raw
from Scripts.hierarchy_manager import get_feature_and_epic,get_related_test_cases
from Scripts.gemini_client import generate_test_cases
from Scripts.test_management import (
    get_or_create_test_plan,
    get_or_create_feature_suite,
    get_or_create_userstory_suite,
    create_regression_suite,
    Add_TC_to_suite)
from Scripts.testcase_creator import create_test_cases

relevant_test_cases = []
regression_suite_id = None
stories = get_recent_user_stories()

t = 0
for story in stories:

    raw_story = get_work_item_raw(story["id"])

    feature, epic = get_feature_and_epic(raw_story)

    if not feature:
        print("Story missing feature hierarchy")
        continue

    if not epic:
        print("Story missing epic hierarchy")
        continue

    tc_ids=(get_related_test_cases(raw_story, relation_type="Related"))
    if tc_ids:
        relevant_test_cases.extend(tc_ids)
    print("the related tc size is "+ str(len(relevant_test_cases)))

    plan_id,plan_root_suite = get_or_create_test_plan(epic)
    feature_suite_id = get_or_create_feature_suite(plan_id, feature,plan_root_suite)
    userstory_suite_id=get_or_create_userstory_suite(plan_id,raw_story,feature_suite_id)
    if userstory_suite_id == -1:
        print("the user story test plan already exists and it has test cases generated")
        continue

    regression_suite_id = create_regression_suite(plan_id,plan_root_suite)



#story['id']
    ai_tests = generate_test_cases(story)
    create_test_cases(story, ai_tests, plan_id, userstory_suite_id)






if regression_suite_id:
    for related_test_case in relevant_test_cases:
        print("the id is "+str(related_test_case))
        Add_TC_to_suite(plan_id,regression_suite_id,related_test_case)
        




























































