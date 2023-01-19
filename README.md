# Twitter Streaming pipeline with GCP
This project connects to the Twitter API and streams tweets into bigquery or Google Cloud Storage (deadletter handling). Data flows from Twitter into Google Cloud PubSub, passes through apache beam using DirectRunner or DataflowRunner and into Bigquery or Google Cloud Storage (deadletter handling -> in case tweet data cannot be processed by the pipeline into Bigquery for any reason). The processing code creates two apache beam pipelines which out data into two bigquery datasets:
* An ETL pipeline that performs a simple tweet count per minute
* An ELT pipeline that streams raw tweets into Bigquery for further transformation and analysis as needed

### Terraform To Do:
* Create a service account + roles and enable relevant gloud services
* Create pubsub topic
* Create Bigquery dataset
* Create GCS bucket

## Prerequisites:
* Sign up for a Twitter Developer account and create an App
* Generate a **Bearer Token** from your App in the [Twitter developer portal](https://developer.twitter.com/en/docs/developer-portal/overview)
* Create an account on [GCP](https://cloud.google.com/) and create a project

## Steps to Run Pipeline:
1. Use terraform to provision dependent resources on Google Cloud Platform
```sh
cd terraform
terraform init
terraform apply
```

2. Install dependencies:
```sh
make install
```

3. Run the following commands on 2 seperate terminals: starts streaming tweets into pubsub and processing into bigquery
* First, substitute the command line interface (CLI) input values in the `Makefile`
```sh
make stream_tweets
make process tweets
```
* The pipeline runs until cancelled using `CTRL+C`

4. When finished, destroy the GCP resources to save cost:
```sh
terraform destroy
```
