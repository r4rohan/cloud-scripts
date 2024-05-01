# exit if any of the commands fails
set -o errexit

# checking and deleting any old tf_plan file
if [ -f "tf_plan" ]; 
  then
    rm "tf_plan"
fi
