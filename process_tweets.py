import argparse
import json
from time import time_ns
from typing import NamedTuple
import logging
import apache_beam as beam
from apache_beam.coders.row_coder import RowCoder
from apache_beam.io import fileio
from apache_beam.io.gcp.bigquery import BigQueryDisposition, WriteToBigQuery
from apache_beam.io.gcp.pubsub import ReadFromPubSub
from apache_beam.options.pipeline_options import GoogleCloudOptions, PipelineOptions, StandardOptions
from apache_beam.transforms import CombineGlobally
from apache_beam.transforms.combiners import CountCombineFn
from apache_beam.transforms.trigger import AccumulationMode, AfterCount, AfterProcessingTime, AfterWatermark
from apache_beam.transforms.window import FixedWindows
from apache_beam.runners import DirectRunner
from bigquery_schema_generator.generate_schema import SchemaGenerator, read_existing_schema_from_file
from google.cloud import bigquery


class GetTimestamp(beam.DoFn):
    def process(self, element, window=beam.DoFn.WindowParam):
        window_start = window.start.to_utc_datetime().strftime("%Y-%m-%dT%H:%M:%S")
        output = {'timestamp': window_start, 'num_tweets': element}
        yield output

class AggregateSchema(NamedTuple):
    timestamp: str
    num_tweets: str

beam.coders.registry.register_coder(AggregateSchema, RowCoder)

class ParseJsonStream(beam.DoFn):
    def process(self, element):
        try:
            row = json.loads(element.decode("utf-8"))
            yield beam.pvalue.TaggedOutput('parsed_row', row)
        except:
            # Dead letter handling for unexpected values
            yield beam.pvalue.TaggedOutput('unparsed_row', element.decode("utf-8"))

class WriteToBQ(beam.DoFn):
    def __init__(self, bq_table):
        self.bq_table = bq_table
    def start_bundle(self):
        self.client = bigquery.Client()
    def process(self, element):
        # table where we're going to store the data
        table_id = self.bq_table
        # function to help with the json -> bq schema transformations
        generator = SchemaGenerator(input_format='dict', 
                        quoted_values_are_strings=True, 
                        keep_nulls=True
                        )
        # Get original schema to assist the deduce_schema function.
        # If the table doesn't exist
        # proceed with empty original_schema_map
        try:
            table_file_name = f"original_schema_{table_id}.json"
            table = self.client.get_table(table_id)
            self.client.schema_to_json(table.schema, table_file_name)
            print("All good")
            with open(table_file_name) as f:
                original_schema = json.load(f)
                original_schema_map = read_existing_schema_from_file(original_schema)
        except Exception as error:
            print(error)
            print(f"{table_id} table does not exists. Proceed without getting schema")
            original_schema_map = None

        with open("element.json", "w") as f:
            json_text = json.dump(element, f)
        #json_text = yaml.safe_load(json_text)
        # generate the new schema, we need to write it to a file
        # because schema_from_json only accepts json file as input

        schema_map, error_logs = generator.deduce_schema(
                                            input_data=[element], 
                                            schema_map=original_schema_map)
        
        schema = generator.flatten_schema(schema_map)

        schema_file_name = "schema_map.json"
        with open(schema_file_name, "w") as output_file:
            json.dump(schema, output_file)

        # convert the generated schema to a version that BQ understands
        bq_schema = self.client.schema_from_json(schema_file_name)


        job_config = bigquery.LoadJobConfig(
            source_format= bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
            schema_update_options=[
                        bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION,
                        bigquery.SchemaUpdateOption.ALLOW_FIELD_RELAXATION
                        ],
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
            schema=bq_schema
        )
        try:
            load_job = self.client.load_table_from_json(
                        [element],
                        table_id,
                        job_config=job_config
                    )  # Make an API request.
            load_job.result()  # Waits for the job to complete.
            if load_job.errors:
                logging.info(f"result={load_job.error_result}\n")
                logging.info(f"errors={load_job.errors}")
            else:
                logging.info(f'Loaded {len(element)} rows.')
        except Exception as error:
            logging.info(f'Error: {error} with loading rows')

def run():
    # Command line arguments
    parser = argparse.ArgumentParser(description='Load json from Pub/Sub into BigQuery')

     # Google Cloud options
    parser.add_argument('--project',required=True, help='Specify Google Cloud project')
    parser.add_argument('--region', required=True, help='Specify Google Cloud region')
    parser.add_argument('--staging_location', required=True, help='Specify Cloud Storage bucket for staging')
    parser.add_argument('--temp_location', required=True, help='Specify Cloud Storage bucket for temp')
    parser.add_argument('--runner', required=True, help='Specify Apache Beam Runner')

    # Pipeline-specific options
    parser.add_argument('--aggregate_table', required=True, help='Output BQ table')
    parser.add_argument('--raw_table', required=True, help='Output BQ table for filtered data')
    parser.add_argument('--input_topic', required=True, help='Input Pub/Sub topic')
    parser.add_argument('--dead_letter_bucket', required=True, help='GCS Bucket for unparsable Pub/Sub messages')

    opts, pipeline_opts = parser.parse_known_args()
    options = PipelineOptions(pipeline_opts, save_main_session=True, streaming=True)
    options.view_as(GoogleCloudOptions).project = opts.project
    options.view_as(GoogleCloudOptions).region = opts.region
    options.view_as(GoogleCloudOptions).staging_location = opts.staging_location
    options.view_as(GoogleCloudOptions).temp_location = opts.temp_location
    options.view_as(GoogleCloudOptions).job_name = '{0}{1}'.format('streaming-minute-tweet-pipeline-', time_ns())
    options.view_as(StandardOptions).runner = opts.runner

    input_topic = opts.input_topic
    aggregate_table = opts.aggregate_table
    dead_letter_bucket = opts.dead_letter_bucket
    raw_table = opts.raw_table

    output_path = dead_letter_bucket + '/tweet_deadletter/'

    aggregate_schema = {
        "fields": [
            {
                "name": "timestamp",
                "type": "STRING"
            },
            {
                "name": "num_tweets",
                "type": "STRING"
            }
        ]
    }

    p = beam.Pipeline(options=options)

    rows = (p 
        | 'Read From PubSub' >> ReadFromPubSub(topic=input_topic)
        | 'Parse Json' >> beam.ParDo(ParseJsonStream())
                            .with_outputs('parsed_row', 'unparsed_row') 
    )

    (rows.unparsed_row 
        | 'BatchOver10Minutes' >> beam.WindowInto(FixedWindows(60),
                                    trigger=AfterProcessingTime(60),
                                    accumulation_mode=AccumulationMode.DISCARDING)
        | 'WriteUnparsedtoGCS' >> fileio.WriteToFiles(
            path=output_path, #to dead letter bucket
            shards=1,
            max_writers_per_bundle=0
        )
    )

    parsed_per_minute = (rows.parsed_row
        | 'WindowByMinute' >> beam.WindowInto(FixedWindows(60),
                                trigger=AfterWatermark(late=AfterCount(1)),
                                allowed_lateness=60*10,
                                accumulation_mode=AccumulationMode.ACCUMULATING
        )
    )

    
    (parsed_per_minute
        | 'CountTweetsPerMinute' >> CombineGlobally(CountCombineFn()).without_defaults()
        | 'AddWindowTimestamp' >> beam.ParDo(GetTimestamp()).with_output_types(AggregateSchema)
        | 'WriteAggToBigQuery' >> WriteToBigQuery(
            table=aggregate_table,
            schema=aggregate_schema,
            create_disposition=BigQueryDisposition.CREATE_IF_NEEDED,
            write_disposition=BigQueryDisposition.WRITE_APPEND
        )
    )
    
    (parsed_per_minute
        | 'WriteRawDataToBQ' >> beam.ParDo(WriteToBQ(raw_table))
    )
    
    logging.basicConfig(level=logging.INFO, 
        #format='%(asctime)s-%(levelname)s: %(message)s',
        #datefmt='%d-%b-%y %H:%M:%S'
        )
    logging.info("Building pipeline ...")

    p.run().wait_until_finish()

if __name__ == '__main__':
  run()