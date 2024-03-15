#!/bin/bash

instances=$(gcloud sql instances list --format="value(name)")
consul=$(consul catalog services)

instances_list=($instances)
consul_services_list=($consul)

registered_instances=()
non_registered_instances=()

# Loop through instances_list
for i in "${instances_list[@]}"; do
    found=false
    # Loop through consul_services_list
    for j in "${consul_services_list[@]}"; do
        if [[ "$i" == "$j" ]]; then
            registered_instances+=("$i")
            found=true
            break
        fi
    done

    if [[ "$found" == false ]]; then
        non_registered_instances+=("$i")
    fi
done

# Print matching instances
echo "------ Registered SQL Instances ------"
for registered_instances in "${registered_instances[@]}"; do
    echo "$registered_instances"
done

# Print non-matching instances from instances_list
echo "------ Non-registered SQL Instances ------"
for non_registered_instance in "${non_registered_instances[@]}"; do
    echo "$non_registered_instance"
done

echo "------ Registering Non-registered SQL Instances ------"
if [ ${#non_registered_instances} -gt 0 ]; then
    for non_registered_instance in "${non_registered_instances[@]}"; do
        instance_name=$(gcloud sql instances describe $non_registered_instance --format="table(name)" | tr -d 'NAME ')
        instance_private_ip=$(gcloud sql instances describe $non_registered_instance --format="table(ipAddresses.ipAddress)" | tr -d 'IP_ADDRESS ' | tr -d '[]' | tr -d "''")
        length_instance_private_ip=${#instance_private_ip[@]}

        for i in "${instance_private_ip[@]}"; do
            if [ ${#i} -gt 0 ]; then
                echo "-------------------------------------------"
                consul services register -name $instance_name -address $instance_private_ip -port 3306
            fi
        done
        if [ ${length_instance_private_ip} -eq 0 ]; then
            exit 1
        fi
    done
else
    echo "Nothing to add"
    exit 1
fi
