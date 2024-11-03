import os
import logging
from flask import Flask, request, jsonify
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from model_according_to_KB import query_knowledge_base as qkb
from dotenv import load_dotenv
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


# Create a Slack app instance
slack_app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

# Create a Flask app
app = Flask(__name__)

# Initialize the SlackRequestHandler
handler = SlackRequestHandler(slack_app)

# Store processed events to prevent duplicate processing
processed_events = set()


@slack_app.event("message")
def handle_message(event, say):
    logger.info(f"Handling message: {event}")
    try:
        # Check if the message subtype is 'bot_message'
        if event.get('subtype') == 'bot_message':
            print(event)
            message_text = event['text']

            user_id = event.get('user', 'Unknown')  # Fallback if user ID isn't in bot messages
            clean_message = message_text.strip()

            logger.info(f"Received bot message from user {user_id}: {clean_message}")

            # Process the message
            response = process_message(clean_message)

            slack_app.client.chat_postMessage(channel=event['channel'], text=response, thread_ts=event['ts'])

            # Send the response back to Slack
            # say(response)
        else:
            # If it's not a bot message, check if the text is "GURU HELP"
            message_text = event['text'].strip()
            Target_channel = os.environ.get("TARGET_CHANNEL_ID")
            if message_text.upper() == "GURU HELP":
                # Retrieve the original message
                original_message = get_original_message(event)
                target_channel = Target_channel  # Replace with the ID of the target channel

                if original_message:
                    # Convert timestamp to a readable date and time
                    timestamp = float(event['ts'])
                    dt_object = datetime.fromtimestamp(timestamp)
                    date_str = dt_object.strftime("%Y-%m-%d %H:%M:%S")  # Format as needed

                    # Send the original message with date and time to the target channel
                    slack_app.client.chat_postMessage(
                        channel=target_channel,
                        text=f"Original message (sent on {date_str}): {original_message}"
                    )
                else:
                    # Send error message to the target channel
                    slack_app.client.chat_postMessage(
                        channel=target_channel,
                        text="Unable to retrieve the original message. Please try again."
                    )
            else:
                logger.info("Message is neither 'bot_message' nor 'GURU HELP', ignoring.")

    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        say("An error occurred while processing your request. Please try again or contact support.")


def get_original_message(event):
    # Implement logic to retrieve the original message here
    try:
        # Use Slack's conversations.history API to fetch messages in the thread
        channel_id = event['channel']
        thread_ts = event.get('thread_ts', event['ts'])  # Use event ts if no thread_ts

        # Fetch thread history to locate the original message
        result = slack_app.client.conversations_replies(channel=channel_id, ts=thread_ts)
        messages = result['messages']

        # Assume the first message in the thread is the original question
        if messages:
            return messages[0]['text']
    except Exception as e:
        logger.error(f"Error retrieving original message: {str(e)}")

    return None
# @slack_app.event("message")
# def handle_message(event, say):
#     logger.info(f"Handling message: {event}")
#     try:
#         print(event)
#         message_text = event['text']
#
#         user_id = event['user']
#         clean_message = message_text.strip()
#
#         logger.info(f"Received message from user {user_id}: {clean_message}")
#
#         # Process the message
#         response = process_message(clean_message)
#
#         # Send the response back to Slack
#         say(response)
#
#     except Exception as e:
#         logger.error(f"Error processing message: {str(e)}")
#         say("An error occurred while processing your request. Please try again or contact support.")


@slack_app.event("app_mention")
def handle_mention(event, say):
    logger.info(f"Handling app mention: {event}")
    try:
        # Use a unique identifier for deduplication
        event_id = event.get("event_ts")  # or "client_msg_id" if available
        if not event_id or event_id in processed_events:
            logger.info(f"Duplicate app mention detected: {event_id}. Ignoring.")
            return  # Ignore duplicate mentions

        # Mark the mention as processed
        processed_events.add(event_id)

        message_text = event['text']
        user_id = event['user']
        clean_message = message_text.split('>', 1)[-1].strip()

        logger.info(f"Received mention from user {user_id}: {clean_message}")

        # Process the message
        response = process_message(clean_message)
        slack_app.client.chat_postMessage(channel=event['channel'], text=response, thread_ts=event['ts'])

        # Send the response back to Slack

        # say(response)

    except Exception as e:
        logger.error(f"Error processing mention: {str(e)}")
        say("An error occurred while processing your request. Please try again or contact support.")


def process_message(message):
    try:
        # Add the introductory message
        intro_message = "Hello I am Guru bot, and the answer I am providing is based on previous responses.\n\n\n"
        # Query knowledge base and return response
        response = qkb(message)
        # Add the summary message
        response += ("\n\n\nIf the answer is not sufficient and you would like to escalate this to a developer, please"
                     " reply to your original question with 'GURU HELP'.")
        # Combine intro, response, and summary message
        full_response = intro_message + response
        return full_response
    except Exception as e:
        logger.error(f"Error in processing message: {str(e)}")
        return "An error occurred while processing your request. Please try again or contact support."


@app.route("/slack/events", methods=["POST"])
def slack_events():
    # Handle events sent from Slack
    data = request.json
    logger.info(f"Received event: {data}")

    # Verify the request is from Slack
    if "type" in data:
        if data["type"] == "url_verification":
            return jsonify({"challenge": data["challenge"]})

        # Handle event_callback
        if data["type"] == "event_callback":
            event_id = data.get("event_id")

            # Deduplicate based on event_id
            if event_id in processed_events:
                logger.info(f"Duplicate event detected: {event_id}. Ignoring.")
                return jsonify({"status": "ignored"}), 200

            # Mark event as processed
            processed_events.add(event_id)

    # Let Slack Bolt handle the event
    return handler.handle(request)


@app.route("/", methods=["GET"])
def health_check():
    return "Bot is running!", 200


@app.errorhandler(Exception)
def handle_error(e):
    logger.error(f"An error occurred: {str(e)}")
    return {"status": "error", "message": str(e)}, 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000)  # Run on port 3000
