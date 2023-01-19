install:
  pip install --upgrade pip && \
  pip install -r requirements.txt

stream_tweets:
  python main.py \
    --bearer_token=${TWITTER_BEARER_TOKEN} \
    --stream_rule="Elon Musk" \
    --project_id=${GCP_PROJECT_ID} \
    --topic=${PUBSUB_TOPIC}

process_tweets:
  python process_tweets.py \
    --project=${GCP_PROJECT_ID} \
    --region=${GCP_REGION} \
    --staging_location=${GCP_STAGING_BUCKET} \
    --temp_location=${GCP_TEMP_BUCKET} \
    --runner=${BEAM_RUNNER} \
    --aggregate_table=${BIGQUERY_AGGREGATE_TABLE} \
    --raw_table=${BIGQUERY_RAW_TABLE} \
    --input_topic=${PUBSUB_TOPIC} \
    --dead_letter_bucket=${DEAD_LETTER_BUCKET}
