from Scripts.azure_client import get_work_item_raw

def get_parent(work_item,work_item_type=None):

    relations = work_item.get("relations", [])

    for rel in relations:
        if "Hierarchy-Reverse" in rel["rel"]:
            #check the parent is feature when work_item_type is User Story
            if work_item_type=="User Story":
                parent_url = rel["url"]
                parent_id = parent_url.split("/")[-1]
                parent_item = get_work_item_raw(parent_id)
                if parent_item["fields"]["System.WorkItemType"]=="Feature":
                    return parent_item
            #check the parent is epic when work_item_type is Feature
            if work_item_type=="Feature":
                parent_url = rel["url"]
                parent_id = parent_url.split("/")[-1]
                parent_item = get_work_item_raw(parent_id)
                if parent_item["fields"]["System.WorkItemType"]=="Epic":
                    return parent_item

    return None

def get_related_test_cases(work_item,relation_type=None):

    relations = work_item.get("relations", [])
    print("the relations are "+str(relations))
    related_test_cases = []
    for rel in relations:
        if "Hierarchy-Reverse" in rel["rel"]:
            #check if the new user story has related old user stories that might be 
            # affected and need regression tests
            if relation_type=="Related":
                parent_url = rel["url"]
                related_id = parent_url.split("/")[-1]
                print("the related id is "+str(related_id))
                related_item_id = get_work_item_raw(related_id)
                if related_item_id["fields"]["System.WorkItemType"]== "Test Case":
                    print("the tc id related is found and it's id is "+str(related_item_id))
                    related_test_cases.append(related_item_id)
        

    return related_test_cases


def get_feature_and_epic(story):

    feature = get_parent(story, work_item_type="User Story")
    epic = None

    if feature:
        epic = get_parent(feature, work_item_type="Feature")

    return feature, epic
