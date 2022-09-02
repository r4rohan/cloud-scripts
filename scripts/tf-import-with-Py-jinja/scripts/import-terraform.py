import json
import subprocess
import argparse
import re

def project(projectId):

    address = projectId["address"]
    project = projectId["change"]["after"]["project_id"]
    cmd = f"terraform import {address} \"{project}\""
    print(cmd)
    if args.apply:
        subprocess.run(f"{cmd}", shell=True)

def service_accounts(account):

    address = account["address"]
    account_id = account["change"]["after"]["account_id"]
    project = account["change"]["after"]["project"]
    email = "{}@{}.iam.gserviceaccount.com".format(account_id,project)
    cmd = f"terraform import {address} projects/{project}/serviceAccounts/{email}"
    print(cmd)
    if args.apply:
        subprocess.run(f"{cmd}", shell=True)

def iam_binding(binding):

    global name
    name = 0
    address = binding["address"]
    project = binding["change"]["after"]["project"]
    role = binding["change"]["after"]["role"]
    members = binding["change"]["after"]["members"]
    res_name = project + '-' + str(name)
    # cmd = f"terraform import google_project_iam_binding.{res_name} '{project} {role}'"
    cmd = f"terraform import {address} '{project} {role}'"
    name = name + 1
    print(cmd)
    if args.apply:
        subprocess.run(f"{cmd}", shell=True)

def vpc(item):

    address = item["address"]
    project = item["change"]["after"]["project"]
    auto_create_subnetworks  = item["change"]["after"]["auto_create_subnetworks"]
    name = item["change"]["after"]["name"]
    mtu = item["change"]["after"]["mtu"]
    cmd = f"terraform import {address} projects/{project}/global/networks/{name}"
    print(cmd)
    if args.apply:
        subprocess.run(f"{cmd}", shell=True)

def gcs(item):

    address = item["address"]
    # project = item["change"]["after"]["project"]
    location  = item["change"]["after"]["location"]
    name = item["change"]["after"]["name"]
    force_destroy = item["change"]["after"]["force_destroy"]
    versioning = item["change"]["after"]["versioning"]
    storage_class = item["change"]["after"]["storage_class"]
    uniform_bucket_level_access = item["change"]["after"]["uniform_bucket_level_access"]
    cmd = f"terraform import {address} {name}"
    print(cmd)
    if args.apply:
        subprocess.run(f"{cmd}", shell=True)

def gcs_iam_binding(binding):

    global name
    name = 0
    address = binding["address"]
    # project = item["change"]["after"]["project"]
    bucket = binding["change"]["after"]["bucket"]
    role = binding["change"]["after"]["role"]
    members = binding["change"]["after"]["member"]
    res_name = bucket + '-' + str(name)
    
    # print(members[])
    def Convert(string):
        li = list(string.split(","))
        return li

    member_list = Convert(members)
    # print(member_list)
    member_len = len(member_list)
    # print(member_len)
    x = 0
    while x < member_len:
        members_new = member_list[x]    
        result = re.search("'(.*)'", members_new)
        new_members = result.group(1)
        x +=1
        cmd = f"terraform import {address} '{bucket} {role} {new_members}'"
        name = name + 1
        print(cmd)
        if args.apply:
            subprocess.run(f"{cmd}", shell=True)

def import_resources(plan):
    for i in plan["resource_changes"]:
        if i["change"]["actions"][0] == "create":
            if i["type"] == "google_project":
                project(i)

    for i in plan["resource_changes"]:
        if i["change"]["actions"][0] == "create":
            if i["type"] == "google_service_account":
                service_accounts(i)

    for i in plan["resource_changes"]:
        if i["change"]["actions"][0] == "create":
            if i["type"] == "google_project_iam_binding":
                iam_binding(i)

    for i in plan["resource_changes"]:
        if i["change"]["actions"][0] == "create":
            if i["type"] == "google_compute_network":
                vpc(i)

    for i in plan["resource_changes"]:
        if i["change"]["actions"][0] == "create":
            if i["type"] == "google_storage_bucket":
                gcs(i)    

    for i in plan["resource_changes"]:
        if i["change"]["actions"][0] == "create":
            if i["type"] == "google_storage_bucket_iam_member":
                gcs_iam_binding(i)
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='GCP Report')
    parser.add_argument('--apply', default=False, action="store_true")
    args = parser.parse_args()

    with open("plan.json") as f:
        plan = json.loads(f.read())

    import_resources(plan)
    