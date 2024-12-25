# Twitter Streaming Pipeline with GCP

This project streams tweets from the **Twitter API** into **Google BigQuery** or **Google Cloud Storage** (GCS) for dead-letter handling. The pipeline processes real-time data using **Apache Beam** and enables transformation and analysis in BigQuery. Provisioning of GCP resources is automated using **Terraform**.

---

## **Features**

1. **Real-Time Streaming**: Streams tweets into **Google Pub/Sub** for ingestion.
2. **Dual Pipelines**:
   - **ETL Pipeline**: Aggregates tweet counts per minute and writes to BigQuery.
   - **ELT Pipeline**: Streams raw tweets into BigQuery for further transformation.
3. **Dead-Letter Handling**: Stores unprocessable tweets in **Google Cloud Storage**.
4. **Scalability**: Uses **Google Dataflow** for distributed data processing.
5. **Automated GCP Provisioning**: Deploys GCP resources like Pub/Sub, BigQuery, and GCS using **Terraform**.
6. **Customizable**: Easily adaptable to different Twitter stream rules and GCP setups.

---

## **Tech Stack**

- **Programming Language**: Python
- **Frameworks/Libraries**:
  - **Apache Beam**: Data processing
  - **Tweepy**: Twitter API integration
  - **Google Cloud Pub/Sub**: Message ingestion
  - **BigQuery Schema Generator**: Dynamic schema generation
- **Infrastructure as Code**: Terraform
- **Cloud Platform**: Google Cloud Platform (GCP)

---

## **Setup and Prerequisites**

### **1. Twitter Developer Setup**

- Sign up for a [Twitter Developer account](https://developer.twitter.com/en/docs/developer-portal/overview).
- Create an app and generate a **Bearer Token**.

### **2. Google Cloud Setup**

- Create a **GCP account** and a project.
- Ensure billing is enabled for the project.

### **3. Dependencies**

- Install the following tools:
  - **Terraform**: Provision GCP resources.
  - **Python 3.8+**: Run the pipeline.
  - **Google Cloud SDK**: Authenticate and manage GCP resources.

---

## **Steps to Run the Pipeline**

### **1. Provision GCP Resources**

- Navigate to the `terraform` directory and apply the Terraform scripts:

    ```bash
    cd terraform
    terraform init
    terraform apply
    ```

### **2. Install Dependencies**

- Set up a Python virtual environment and install required libraries:

    ```bash
    make setup
    make install
    ```

### **3. Start Streaming Tweets**

- Open two terminal windows:
  - Terminal 1: Stream tweets into Pub/Sub:

    ```bash
    make stream_tweets
    ```

  - Terminal 2: Process tweets into BigQuery:

    ```bash
    make process_tweets
    ```

### **4. Monitor Logs and Data**

- Logs are stored in tweet.log for debugging.
- Data is written to BigQuery tables or GCS (dead-letter).

### **5. Clean Up Resources**

- Destroy GCP resources to save costs:

    ```bash
    terraform destroy
    ```

---

## Pipeline Architecture

1. **Input**: Streams tweets from the Twitter API into Google Pub/Sub.
2. **Processing:

    - **ETL Pipeline**: Aggregates tweets per minute.
    - **ELT Pipeline**: Writes raw tweets to BigQuery.

3. **Output**:

    - Processed data is written to BigQuery.
    - Failed records are stored in GCS for inspection.

---

## **Environment Variables**

Ensure the following environment variables are set in the `Makefile`:

- `TWITTER_BEARER_TOKEN`: Your Twitter API Bearer Token.
- `GCP_PROJECT_ID`: GCP Project ID.
- `PUBSUB_TOPIC`: Pub/Sub topic for streaming tweets.
- `GCP_REGION`: GCP region.
- `GCP_STAGING_BUCKET`: Staging bucket for Apache Beam.
- `GCP_TEMP_BUCKET`: Temporary bucket for Apache Beam.
- `BIGQUERY_AGGREGATE_TABLE`: BigQuery table for aggregated data.
- `BIGQUERY_RAW_TABLE`: BigQuery table for raw data.
- `DEAD_LETTER_BUCKET`: GCS bucket for dead-letter data.

---

## **Files and Directories**

- `/main.py`: Streams tweets from Twitter API to Pub/Sub.
- `/process_tweets.py`: Processes tweets into BigQuery.
- `/terraform/`: Terraform scripts for provisioning GCP resources.
- `/Makefile`: Commands for pipeline automation.
- `/requirements.txt`: Python dependencies.

---

## **Future Enhancements**

- Add support for more complex transformations in Apache Beam.
- Implement additional data quality checks and error handling.
- Enable multi-region deployment for improved reliability.

---

## **Troubleshooting**

- **Error: Insufficient Permissions**:
  - Ensure the GCP Service Account has the required roles (e.g., `roles/pubsub.admin`, `roles/bigquery.admin`).
- **Terraform State Issues**:
  - Delete the local `terraform/state` directory and reinitialize Terraform.
- **Pipeline Errors**:
  - Check logs in `tweet.log` and debug issues in data formatting or schema mismatches.

---

## **License**

This project is open-source and licensed under the [MIT License](LICENSE).

---
