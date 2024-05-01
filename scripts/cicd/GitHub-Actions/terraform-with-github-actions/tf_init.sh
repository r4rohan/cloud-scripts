# exit script upon any non-zero exit code
set -o errexit

# initialization of terraform
terraform init
terraform get
