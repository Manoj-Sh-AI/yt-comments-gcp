import yaml
import os
import json
from google.cloud import pubsub_v1
from google.cloud import language_v1
from googleapiclient.discovery import build
from flask import Request, jsonify, render_template_string

# Load config.yaml
with open("config.yaml") as f:
    config = yaml.safe_load(f)

# --- Existing Clients ---
# Initialize clients
youtube = build("youtube", "v3", developerKey=config["youtube_api_key"])
publisher = pubsub_v1.PublisherClient()

# Try to get project ID from env; fall back to explicit default for safety
PROJECT_ID = os.environ.get("GCP_PROJECT", "ambient-elf-487017-d6")
TOPIC_NAME = config["pubsub_topic"]
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_NAME)

print(f"[INIT] Using Project ID: {PROJECT_ID}")
print(f"[INIT] Using Topic: {TOPIC_NAME}")
print(f"[INIT] Full topic path: {topic_path}")

# --- New Client for Sentiment Analysis ---
language_client = language_v1.LanguageServiceClient()

# --- New HTML Template for Sentiment Prediction UI ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sentiment Analysis</title>
    <style>
        body { font-family: sans-serif; display: flex; justify-content: center; margin-top: 50px; background-color: #f4f4f9; }
        .container { width: 500px; padding: 20px; background-color: #fff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h2 { color: #333; }
        textarea { width: 100%; height: 100px; margin-bottom: 10px; border: 1px solid #ccc; border-radius: 4px; padding: 8px; font-size: 1rem; }
        button { padding: 10px 15px; background-color: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background-color: #0056b3; }
        #result { margin-top: 20px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; background-color: #e9ecef; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Comment Sentiment Predictor</h2>
        <p>Enter a comment to predict its sentiment.</p>
        <textarea id="comment" placeholder="e.g., 'This is a wonderful product!'"></textarea>
        <button onclick="predictSentiment()">Predict</button>
        <div id="result" style="display:none;"></div>
    </div>

    <script>
        async function predictSentiment() {
            const comment = document.getElementById('comment').value;
            const resultDiv = document.getElementById('result');
            resultDiv.style.display = 'block';

            if (!comment) {
                resultDiv.innerText = 'Please enter a comment.';
                return;
            }

            const response = await fetch('/predict_sentiment', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ comment: comment })
            });
            const data = await response.json();

            let sentiment = data.score > 0.2 ? "Positive" : (data.score < -0.2 ? "Negative" : "Neutral");
            resultDiv.innerHTML = `<p><strong>Sentiment:</strong> ${sentiment}</p><p><strong>Probability Score:</strong> ${data.score.toFixed(3)}</p>`;
        }
    </script>
</body>
</html>
"""

def main(request: Request):
    # --- Router to handle different endpoints ---
    if request.path == '/predict_ui':
        return render_template_string(HTML_TEMPLATE)
    elif request.path == '/predict_sentiment':
        return predict_sentiment(request)
    elif request.path == '/ingest_comments':
        return ingest_comments(request)
    else:
        # Default to existing behavior or a welcome page
        return ingest_comments(request)

def ingest_comments(request: Request):
    """
    Original function to fetch YouTube comments and publish them to Pub/Sub.
    """
    print("[INFO] YouTube comment ingestion started...")
    try:
        # Fetch latest comments for the configured channel
        request_youtube = youtube.commentThreads().list(
            part="snippet",
            allThreadsRelatedToChannelId=config["channel_id"],
            maxResults=config["max_results"]
        )
        response = request_youtube.execute()
        print(f"[INFO] Retrieved {len(response.get('items', []))} comments from YouTube API.")
    except Exception as e:
        print(f"[ERROR] Failed to fetch YouTube comments: {e}")
        return f"Error fetching comments: {e}", 500

    published_count = 0
    for item in response.get("items", []):
        try:
            comment_text = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            comment_id = item["snippet"]["topLevelComment"]["id"]
            message_json = json.dumps({
                "id": comment_id,
                "comment": comment_text
            })

            print(f"[PUBLISH] Sending comment ID {comment_id[:10]}...")  # show short prefix for readability
            future = publisher.publish(topic_path, message_json.encode("utf-8"))
            future.result()  # Wait for confirmation
            published_count += 1

        except Exception as e:
            print(f"[ERROR] Failed to publish comment: {e}")

    print(f"[SUCCESS] Published {published_count} comments to Pub/Sub topic: {topic_path}")
    return f"Comments pushed to Pub/Sub ({published_count} messages).", 200

def predict_sentiment(request: Request):
    """
    New function to handle sentiment prediction for a given comment.
    """
    if request.method != 'POST':
        return 'Only POST requests are accepted', 405

    request_json = request.get_json(silent=True)
    if not request_json or 'comment' not in request_json:
        return jsonify({'error': 'Missing "comment" in request body'}), 400

    comment_text = request_json['comment']

    try:
        document = language_v1.Document(
            content=comment_text, type_=language_v1.Document.Type.PLAIN_TEXT
        )
        sentiment = language_client.analyze_sentiment(
            request={"document": document}
        ).document_sentiment

        return jsonify({'score': sentiment.score, 'magnitude': sentiment.magnitude})
    except Exception as e:
        print(f"[ERROR] Could not analyze sentiment: {e}")
        return jsonify({'error': 'Failed to analyze sentiment'}), 500