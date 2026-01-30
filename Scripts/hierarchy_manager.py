from azure_client import get_work_item_raw

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


def get_feature_and_epic(story):

    feature = get_parent(story, work_item_type="User Story")
    epic = None

    if feature:
        epic = get_parent(feature, work_item_type="Feature")

    return feature, epic
