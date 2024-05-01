#!/bin/sh

export CI_BUILD_SHA="x${CI_BUILD_REF:0:8}"

deploy_vm() {
	if [ $1 == 'dev' ]
	then
		echo 'DEV DEPLOYMENT'
		echo $DEV_GCP_TOKEN > /tmp/key.json
		gcloud auth activate-service-account --key-file /tmp/key.json
		gcloud beta compute ssh --tunnel-through-iap --zone "us-central1-a" "spring-boot-vm" --project "cloudorbit-dev" --command="sudo systemctl stop hello-world"
		sleep 5
		gcloud compute scp target/hello-world.jar spring-boot-vm:/hello-world --zone=us-central1-a --project "cloudorbit-dev" --tunnel-through-iap
		gcloud beta compute ssh --tunnel-through-iap --zone "us-central1-a" "spring-boot-vm" --project "cloudorbit-dev" --command="sudo systemctl start hello-world"

	elif [ $1 == 'stg' ]
	then
		echo 'STAGE DEPLOYMENT'
		echo $STG_GCP_TOKEN > /tmp/key.json
		gcloud auth activate-service-account --key-file /tmp/key.json
		gcloud beta compute ssh --tunnel-through-iap --zone "us-central1-a" "spring-boot-vm" --project "cloudorbit-stg" --command="sudo systemctl stop hello-world"
		sleep 5
		gcloud compute scp target/hello-world.jar spring-boot-vm:/hello-world --zone=us-central1-a --project "cloudorbit-stg" --tunnel-through-iap
		gcloud beta compute ssh --tunnel-through-iap --zone "us-central1-a" "spring-boot-vm" --project "cloudorbit-stg" --command="sudo systemctl start hello-world"

	elif [ $1 == 'prod' ]
	then
		echo 'PROD DEPLOYMENT'
		echo $PROD_GCP_TOKEN > /tmp/key.json
		gcloud auth activate-service-account --key-file /tmp/key.json
		gcloud beta compute ssh --tunnel-through-iap --zone "us-central1-a" "spring-boot-vm" --project "cloudorbit-prod" --command="sudo systemctl stop hello-world"
		sleep 5
		gcloud compute scp target/hello-world.jar spring-boot-vm:/hello-world --zone=us-central1-a --project "cloudorbit-prod" --tunnel-through-iap
		gcloud beta compute ssh --tunnel-through-iap --zone "us-central1-a" "spring-boot-vm" --project "cloudorbit-prod" --command="sudo systemctl start hello-world"

	else
		echo 'Unknown environment "$1".'
	fi
}
