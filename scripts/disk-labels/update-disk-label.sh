# Array variable declaration
zones=()
instances=()
labels=()
l=()

#get the list of zones
zones=$(gcloud compute zones list | grep NAME | awk '{print $2}')
#echo "$zones"
# echo "==========="

for z in $zones
do
    #Current zone
    echo "$z"
    
    # set project name from 1st parameter
    gcloud config set project "$1"

    # # set zone from 2nd parameter
    gcloud config set compute/zone $z

    config=$(gcloud config list)
    echo "$config"
    
    while IFS= read -r line; do
        instances+=( "$line" )
    done < <(gcloud compute instances list --zones=$z --format="value(name)")

    echo "${instances[@]}"

    for i in  "${instances[@]}"
    do
      labels="$(gcloud compute instances describe "$i" --zone="$z" --format="csv(labels)")"
      if [ "${labels}" != "" ]
      then
          # converting lables to list of lables
          for j in "${labels[@]}"
          do
          # removing .,space and replacing : for each label in the list
            l=$(echo "$j" |sed 1d| tr ';' ',')
            gcloud compute disks add-labels "$i" --labels="${l}"
          done
      fi
    done
done
