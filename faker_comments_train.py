import time
import uuid
from datetime import datetime, timezone, timedelta
from faker import Faker
from google.cloud import bigquery

PROJECT_ID = "ambient-elf-487017-d6"
DATASET_ID = "youtube_comments"
TABLE_ID = "comments_train"

# Target load
HOURS = 5
RECORDS_PER_HOUR = 1000

# Insert every 20 seconds
BATCH_INTERVAL_SECONDS = 300   # 5 min

BATCHES_PER_HOUR = 3600 // BATCH_INTERVAL_SECONDS  # 180 batches/hour
RECORDS_PER_BATCH = RECORDS_PER_HOUR // BATCHES_PER_HOUR  # ~5.55 → 5 or 6

fake = Faker()
client = bigquery.Client(project=PROJECT_ID)
table_fqn = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

sentiments = ["positive", "neutral", "negative"]

def make_row(now_utc: datetime):
    published_at = now_utc - timedelta(minutes=fake.random_int(min=0, max=180))
    return {
        "comment_id": str(uuid.uuid4()),
        "comment_text": fake.sentence(nb_words=fake.random_int(min=6, max=18)),
        "published_at": published_at.isoformat(),
        "sentiment_label": fake.random_element(elements=sentiments),
        "ingested_at": now_utc.isoformat(),
    }

total_batches = HOURS * BATCHES_PER_HOUR
total_target = total_batches * RECORDS_PER_BATCH

print(f"Target: ~{RECORDS_PER_HOUR}/hour for {HOURS} hours")
print(f"Batch every {BATCH_INTERVAL_SECONDS}s -> {RECORDS_PER_BATCH} rows/batch")
print(f"Total planned inserts: {total_target} rows\n")

for b in range(total_batches):
    start = datetime.now(timezone.utc)
    rows = [make_row(start) for _ in range(RECORDS_PER_BATCH)]

    errors = client.insert_rows_json(table_fqn, rows)
    if errors:
        print(f"[Batch {b+1}/{total_batches}] ❌ Insert errors:", errors)
    else:
        print(f"[Batch {b+1}/{total_batches}] ✅ Inserted {len(rows)} rows at {start.isoformat()}")

    # Sleep until next interval
    elapsed = (datetime.now(timezone.utc) - start).total_seconds()
    sleep_for = max(0, BATCH_INTERVAL_SECONDS - elapsed)
    time.sleep(sleep_for)

print("\nDone.")
