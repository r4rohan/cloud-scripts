#Import Terraform's State Using Automation

Terraform is a powerful tool for managing cloud-based infrastructure and resources, but managing infrastructure with code has its challenges. Terraform's infrastructure as code configuration approach offers a relatively simple method for updating your infrastructure when it changes, rather than having to rebuild it regularly. However, because Terraform manages your infrastructure for you, it can be difficult to keep track of the changes in your infrastructure which generates a lot of questions, few of them would be:
 - Can you easily find out what version of a resource exists in your environment? 
 - Do you know who is using a particular resource?
 - Can you easily roll back to an earlier version? 

In many cases, you won't have the answers to these questions without scanning through documentation and inspecting existing resources and infrastructure.

Thus, we make use of terraforms most useful feature which is to import new resources into your system as they are created on your provider’s platform, without having to manually type them into your configuration file. To do this automatically we have various methods like:
 - using terraform Import commands but, we would have to do it for each resource individually, 
 - using terraformer but, it do not have all the resources that it can import, 
 - we can write scripts to import terraform resources. 

 This article takes you through the third approach where we generate terraform code using python3 and jinja2 templates. 

**Code Explanation**


**Usage:**

Please follow the below steps to run this code:

 - Run the scripts/generate-terraform.py script against the newly created resources.

    ```
    python3 scripts/generate-terraform.py --project_list ${PROJECT}
    ```

 - Once you have run the generated-terraform.py script please make sure the variables file exist in the project directory before moving to futher steps:
   
   ```
   Check for the file with name: variables.tf
   ```

 - Now that we have code generated in the specific folder, change directory to that folder and initialize Terraform:

    ```
    terraform init
    ```

 - Format and Validate the terraform code as well
   
   ```
   terraform validate && terraform fmt
   ```

 - Create the plan:

    ```
    terraform plan -out plan.tfplan
    ```

 - Create the JSON file form the plan:

    ```
    terraform show -json plan.tfplan > plan.json
    ```

 - Run the import script to import the resources in plan.json to the Terraform state. Running without the --apply options will simply print out the commands that will occur.

    ```
    python3 ../scripts/import-terraform.py
    ```

 - Apply the import:

    ```
    python3 ../scripts/import-terraform.py --apply
    ```

 - Verify the results:

    ```
    terraform plan -out plan.tfplan
    ```

 - Let's apply the above to get the services into the state file. No real changes will occur as the service are already enabled

    ```
    terraform apply plan.tfplan
    ```

 - Let's verify the state.

    ```
    terraform state list
    ```
