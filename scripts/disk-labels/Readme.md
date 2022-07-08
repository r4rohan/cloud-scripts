This script will be used to update the disk labels for each Virtual Machine that has disk assosicated to it with the same label as of the VM.

Implememtation:
Try running this script via google cloud shell for better performance.

Steps:
1) First step would be be open up the cloud shell and run the below command:
    gcloud config set project <$project_id>
    
2) Second steps is to just run the script using the below command:
    bash update-disk-label.sh <$project_id>
