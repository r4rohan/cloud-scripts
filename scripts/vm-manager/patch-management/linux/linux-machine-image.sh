#!/usr/bin/sh

set -e

getInstanceMetadata()
{
    KEY=$1
    echo $(curl -s -H "Metadata-Flavor: Google" "http://metadata/computeMetadata/v1/instance/$KEY")
}

getVmName()
{
    echo $(getInstanceMetadata name)
}

getZone()
{
    zone=$(getInstanceMetadata zone)
    echo $zone | sed 's/.*\(zones\/\)\(europe-west4-a\).*/\2/'
}
newMachineimage()
{
    VM=$1
    ZONE=$2
    TDATE=$(date "+%d%m%Y%H%M%S")
   
    gcloud compute machine-images create $VM-$TDATE  \
        --source-instance $VM  \
        --source-instance-zone $ZONE

    echo 0
}

vmName=$(getVmName);
zone=$(getZone);

echo -n "Creating Machine-Image: ";
result=$(newMachineimage $vmName $zone)

if [ $result -eq 0 ]; then
    echo "done"
else
    echo "failed"
    exit 1
fi