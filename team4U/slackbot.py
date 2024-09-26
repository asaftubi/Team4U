

import os
import logging
from flask import Flask, request, jsonify
from slack_bolt import App
from model_according_to_KB import query_knowledge_base as qkb
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Create a Flask app
app = Flask(__name__)

# Create a Slack app instance
slack_app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# Store processed events to prevent duplicate processing
processed_events = set()


@app.route("/slack/events", methods=["POST"])
def slack_events():
    # Handle events sent from Slack
    data = request.json
    logger.info(f"Received event: {data}")

    # Verify the request is from Slack
    if "type" in data:
        if data["type"] == "url_verification":
            return jsonify({"challenge": data["challenge"]})

        # Handle app_mention events
        if data["type"] == "event_callback":
            event = data["event"]

            # Deduplicate based on event_id
            event_id = data.get("event_id")
            if event_id in processed_events:
                logger.info(f"Duplicate event detected: {event_id}. Ignoring.")
                return jsonify({"status": "ignored"}), 200

            # Mark event as processed
            processed_events.add(event_id)

            if event.get("type") == "app_mention":
                return handle_mention(event)

    return jsonify({"status": "ignored"}), 200


def handle_mention(event):
    logger.info(f"Handling app mention: {event}")
    try:
        # Immediately respond to Slack to prevent retries
        message_text = event['text']
        user_id = event['user']
        clean_message = message_text.split('>', 1)[-1].strip()

        logger.info(f"Received message from user {user_id}: {clean_message}")

        # Process the message asynchronously
        response = process_message(clean_message)

        # Send the response back to Slack
        slack_app.client.chat_postMessage(channel=event['channel'], text=response)
        return jsonify({"status": "success"}), 200

    except Exception as e:
        logger.error(f"Error processing mention: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500


def process_message(message):
    try:
        # Query knowledge base and return response
        return qkb(message)
    except Exception as e:
        logger.error(f"Error in processing message: {str(e)}")
        return "An error occurred while processing your request. Please try again or contact support."


@app.errorhandler(Exception)
def handle_error(e):
    logger.error(f"An error occurred: {str(e)}")
    return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(port=3000)  # or any other port you prefer
