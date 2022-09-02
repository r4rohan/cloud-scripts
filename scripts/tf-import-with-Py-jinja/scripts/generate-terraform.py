#Import libararies that will help in executing gcloud commands, format output in json,etc.
from jinja2 import Template, Environment, FileSystemLoader
import argparse
import requests
import json
import os
import string
import random
import subprocess
import json
import shlex
import shutil
import re

from datetime import datetime
from pprint import pprint

def get_gcp_token():
    """Get access token to run against GCP"""
    return os.popen('gcloud auth application-default print-access-token').read().strip("\n")

def list_resources(resource,token = get_gcp_token()):
    """Generic function to list all resources of a given type on all pages from GCP"""

    if resource["method"] == "POST":
        request = requests.post(resource["url"], headers=headers)
    elif resource["method"] == "GET":
        request = requests.get(resource["url"], headers=headers)

    # Add the values to a list that is return, requesting the next page if the list is large
    if resource["topLevel"] in request.json().keys():
        resource_sublist = request.json()[resource["topLevel"]]
        while "nextPageToken" in request.json() and request.json()["nextPageToken"] != "":
            url = "{}?pageToken={}".format(resource["url"], request.json()['nextPageToken'])
            request = requests.get(url, headers=headers)
            resource_sublist += request.json()[resource["topLevel"]]
        return resource_sublist
    return []

def gen_project(project,module_location):
    """Generate the project module"""
    # get the list of enabled service from GCP
    projectId = project["projectId"]
    project_services = {
        "url": f"https://serviceusage.googleapis.com/v1/projects/{projectId}/services",
        "method": "GET",
        "topLevel": "services"
    }
    # return a list of disctionaries of services
    services = list_resources(project_services)

    service_list = []
    # iterate over the list and only include the enabled ones
    for service in services:
        if service["state"] != "DISABLED":
            service_list.append(service["config"]["name"])
    
    # load the template to populate the variables
    instance_template = TEMPLATE_ENVIRONMENT.get_template("project-module-template.jinja2")

    # render the template variables and write to disk
    with open(f"{module_location}/{projectId}.tf", "w") as f:
        f.write(instance_template.render(
            project_name = project["name"],
            project_id = project["projectId"],
            api_services = json.dumps(service_list)
        ))

def gen_service_accounts(project,module_location):
    """Generate services account TF code, one for every account"""

    projectId = project["projectId"]
    service_accounts = {
        "url": f"https://iam.googleapis.com/v1/projects/{projectId}/serviceAccounts",
        "method": "GET",
        "topLevel": "accounts"
    }
    # returns a list of dictionaries of serivce accounts
    accounts = list_resources(service_accounts)

    # Load the template
    sa_template = TEMPLATE_ENVIRONMENT.get_template("service-account.jinja2")

    # ignore service accounts that contain the project number, these are usually created by GCP   
    ignore_list = [project["projectNumber"]]

    # iterate through the accounts
    for account in accounts:
        include_sa = True
        # check agains the ignore list
        for i in ignore_list:
            if i in account["email"]:
                include_sa = False
        # write populated template to the file
        if include_sa:
            with open(f"{module_location}/service-accounts.tf", "a") as f:
                f.write(sa_template.render(
                    project_id = projectId,
                    service_account_id = account["email"].split("@")[0],
                    service_account_display_name = account["displayName"],
                    service_account_description = account.get("description", "").rstrip()
            ) + os.linesep)

def gen_iam_binding(project,module_location):
    """Generate IAM BINDING TF code, one for every account"""
    
    global name
    name = 0
    projectId = project["projectId"]
    iam_bindings = {
        "url": f"https://cloudresourcemanager.googleapis.com/v1/projects/{projectId}:getIamPolicy",
        "method": "POST",
        "topLevel": "bindings"
    }
    
    # returns a list of dictionaries of serivce accounts
    bindings = list_resources(iam_bindings)

    # Load the template
    iambinding_template = TEMPLATE_ENVIRONMENT.get_template("iam-bindings.jinja2")

    # ignore service accounts that contain the project number, these are usually created by GCP
    ignore_list = [project["projectNumber"]]

    # iterate through the Bindings
    for binding in bindings:
        include_binding = True

        # check agains the ignore list
        for i in ignore_list:
            if i in binding["members"]:
                include_binding = False
        
        # write populated template to the file
        if include_binding:
            with open(f"{module_location}/iam-binding.tf", "a") as f:
                f.write(iambinding_template.render(
                    res_name = projectId + '-' + str(name),
                    project_id = projectId,
                    iambinding_roles = binding["role"],
                    iambinding_member = binding["members"]
            ) + os.linesep)
            name = name + 1
        

def gen_vpc(project,module_location):
    """Generate VPC TF code, one for every account"""

    projectId = project["projectId"]
    vpc_list = {
        "url": f"https://compute.googleapis.com/compute/v1/projects/{projectId}/global/networks",
        "method": "GET",
        "topLevel": "items"
    }

    # returns a list of dictionaries of serivce accounts
    items = list_resources(vpc_list)

    # Load the template
    vpc_template = TEMPLATE_ENVIRONMENT.get_template("vpc.jinja2")

    # ignore service accounts that contain the project number, these are usually created by GCP   
    ignore_list = [project["projectNumber"]]

    # iterate through the accounts
    for item in items:
        include_vpc = True
        # check agains the ignore list
        for i in ignore_list:
            if i in item["name"]:
                include_vpc = False
        # write populated template to the file
        if include_vpc:
            with open(f"{module_location}/vpc.tf", "a") as f:
                f.write(vpc_template.render(
                    project_id = projectId,
                    auto_create_subnetworks = item["autoCreateSubnetworks"],
                    vpc_name = item["name"],
                    mtu = item["mtu"]
            ) + os.linesep)

def gen_gcs(project,module_location):
    """Generate GCS TF code, one for every account"""

    projectId = project["projectId"]
    gcs_list = {
        "url": f"https://storage.googleapis.com/storage/v1/b?project={projectId}",
        "method": "GET",
        "topLevel": "items"
    }

    # returns a list of dictionaries of serivce accounts
    items = list_resources(gcs_list)
    
    # Load the template
    gcs_template = TEMPLATE_ENVIRONMENT.get_template("gcs.jinja2")

    # ignore service accounts that contain the project number, these are usually created by GCP   
    ignore_list = [project["projectNumber"]]

    # iterate through the accounts
    for item in items:
        include_gcs = True
        # check agains the ignore list
        for i in ignore_list:
            if i in item["name"]:
                include_gcs = False

        bucket_name = item["name"]
        # write populated template to the file
        if include_gcs:
            result = bucket_name.replace(".", "-"),
            result1 = re.search("'(.*)'", str(result))
            result2 = result1.group(1)
            with open(f"{module_location}/gcs.tf", "a") as f:
                f.write(gcs_template.render(
                    project_id = projectId,
                    gcs_name = item["name"],
                    res_name = str(result2),
                    gcs_location = item["location"],
                    gcs_force_destroy = "true",
                    gcs_uniform_bla = "true",
                    gcs_versioning = "true",
                    gcs_storage_class = item["storageClass"]
            ) + os.linesep)

def gen_gcs_iam_binding(project,module_location):
    """Generate GCS Iam Binding TF code, one for every account"""

    projectId = project["projectId"]

    #List name of the GCS buckets
    gcs_name_list = {
        "url": f"https://storage.googleapis.com/storage/v1/b?project={projectId}",
        "method": "GET",
        "topLevel": "items"
    }

    #Global variable to be added to the name of iam binding resource
    global name
    name = 0

    items = list_resources(gcs_name_list)
    # print(gcs_name)

    # iterate through the accounts
    for item in items:
        
        #list Bucket name for futher use
        bucket_name = item["name"]
        # print(bucket_name)

        #List the iam binding for individual buckets
        gcs_list = {
            "url": f"https://storage.googleapis.com/storage/v1/b/{bucket_name}/iam",
            "method": "GET",
            "topLevel": "bindings"
        }

        bindings = list_resources(gcs_list)
        # print(bindings)
        
        # Load the template
        gcs_template = TEMPLATE_ENVIRONMENT.get_template("gcs-iam-bindings.jinja2")

        # ignore service accounts that contain the project number, these are usually created by GCP   
        ignore_list = [project["projectNumber"]]

        results = "zero"
        for binding in bindings:
            include_gcs = True
            # check agains the ignore list
            for i in ignore_list:
                if i in binding["role"]:
                    include_gcs = False

            # write populated template to the file
            if include_gcs:
                result = bucket_name.replace(".", "-"),
                result1 = re.search("'(.*)'", str(result))
                result2 = result1.group(1)
                with open(f"{module_location}/gcs_iam_bindings.tf", "a") as f:
                    f.write(gcs_template.render(
                        project_id = projectId,
                        iambinding_bucket_name = bucket_name,
                        res_name = str(result2) + '-' + str(name),
                        iambinding_roles = binding["role"],
                        iambinding_member = binding["members"]
                ) + os.linesep)
                name = name + 1
        

if __name__ == "__main__":
    
    # get the command arguments
    parser = argparse.ArgumentParser(description='GCP Report')
    parser.add_argument('--project_list', nargs='+')
    parser.add_argument('--outputfolder', default=".")
    args = parser.parse_args()

    # initialize the Jinja environemnt
    TEMPLATE_ENVIRONMENT = Environment(loader=FileSystemLoader("../scripts/templates"))

    # set headers for the API request
    headers = {"Authorization": "Bearer {}".format(get_gcp_token()), "content-type": "application/json"}

    # loop through the list of projects from the command arguments
    for projectId in args.project_list:
        
        # Get the current working directory and put it in a variable called "path"
        cwd = os.getcwd()
        path = cwd

        # Join various path components and check if the folder exist or not
        folder = os.path.join(path, projectId)
        folder_exist = os.path.isdir(folder) 

        #If folder exist, change into that directory and generate code else create the directory and change into that directory to generate code
        if folder_exist:
            shutil.copy('variables.tf', folder)
            os.chdir(folder)
            currentdir = os.getcwd()
            print("Directory with project name exist: {}".format(currentdir))
            print("Project: {}".format(projectId)) 

            # get project metadata
            url = f"https://cloudresourcemanager.googleapis.com/v1/projects/{projectId}"
            project = requests.get(url, headers=headers).json()

            # generate the resources
            gen_project(project, args.outputfolder)
            gen_service_accounts(project, args.outputfolder)
            gen_iam_binding(project, args.outputfolder)
            gen_vpc(project, args.outputfolder)
            gen_gcs(project, args.outputfolder)
            gen_gcs_iam_binding(project, args.outputfolder)
            
        else:
            print("Directory with Project name doesnt not exist. Creating the directory....")
            os.mkdir(folder)
            shutil.copy('variables.tf', folder)
            os.chdir(folder)
            directorycurrent = os.getcwd()
            print("Directory created and switched to the created directory: {}".format(directorycurrent))
            print("Project: {}".format(projectId)) 

            # get project metadata
            url = f"https://cloudresourcemanager.googleapis.com/v1/projects/{projectId}"
            project = requests.get(url, headers=headers).json()

            # generate the resources
            gen_project(project, args.outputfolder)
            gen_service_accounts(project, args.outputfolder)
            gen_iam_binding(project, args.outputfolder)
            gen_vpc(project, args.outputfolder)
            gen_gcs(project, args.outputfolder)
            gen_gcs_iam_binding(project, args.outputfolder)
