from google.cloud import language_v1
from google.cloud import bigquery

def main():
    client = language_v1.LanguageServiceClient()
    bq_client = bigquery.Client()

    # Fetch latest comments
    query = """
    SELECT comment_id, comment_text
    FROM `ambient-elf-487017-d6.youtube_comments.comments`
    LIMIT 100
    """
    comments = bq_client.query(query).result()

    # Analyze sentiment
    rows_to_insert = []
    for row in comments:
        doc = language_v1.Document(
            content=row.comment_text,
            type_=language_v1.Document.Type.PLAIN_TEXT
        )
        sentiment = client.analyze_sentiment(request={"document": doc}).document_sentiment
        rows_to_insert.append({
            "comment_id": row.comment_id,
            "comment_text": row.comment_text,
            "sentiment_score": sentiment.score,
            "sentiment_magnitude": sentiment.magnitude
        })

    # Write results back to BigQuery
    table_id = "ambient-elf-487017-d6.youtube_comments.sentiment"
    bq_client.insert_rows_json(table_id, rows_to_insert)
    print(f"Inserted {len(rows_to_insert)} rows with sentiment scores")


if __name__ == "__main__":
    main()