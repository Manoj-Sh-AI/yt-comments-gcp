import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions
import json, re
from datetime import datetime
import yaml

# Load config
with open("config.yaml") as f:
    config = yaml.safe_load(f)

PROJECT_ID = config["project_id"]
BUCKET = config["bucket"]
PUBSUB_TOPIC = config["pubsub_topic"]
BQ_DATASET = config["bq_dataset"]
BQ_TABLE = config["bq_table"]

class CleanComment(beam.DoFn):
    def process(self, element):
        record = json.loads(element.decode("utf-8"))
        text = record.get("comment", "")
        text = text.lower()
        text = re.sub(r"http\S+", "", text)
        text = re.sub(r"[^a-z\s]", "", text)
        yield {
            "comment_id": record.get("id"),
            "comment_text": text,
            "published_at": datetime.utcnow().isoformat()
        }



def run(argv=None):
    options = PipelineOptions(
        project=PROJECT_ID,
        region="us-central1", 
        runner="DataflowRunner",
        temp_location=f"gs://{BUCKET}/temp",
        staging_location=f"gs://{BUCKET}/staging"
    )
    options.view_as(StandardOptions).streaming = True

with beam.Pipeline(options=options) as p:
    (
        p
        | "ReadFromPubSub" >> beam.io.ReadFromPubSub(
            topic=f"projects/{PROJECT_ID}/topics/{PUBSUB_TOPIC}"
        )
        | "CleanText" >> beam.ParDo(CleanComment())
        | "WriteToBigQuery" >> beam.io.WriteToBigQuery(
            table=f"{PROJECT_ID}:{BQ_DATASET}.{BQ_TABLE}",
            schema="comment_id:STRING, comment_text:STRING, published_at:TIMESTAMP",
            write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND
        )
    )

if __name__ == "__main__":
    run()