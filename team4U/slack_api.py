import csv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os
from dotenv import load_dotenv

# טען את משתני הסביבה מקובץ .env
load_dotenv(dotenv_path='.env')  # וודא שהקובץ נטען

# השתמש במשתנים
SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')

# הדפס הערכים לצורך בדיקה
print(f"SLACK_BOT_TOKEN: {SLACK_BOT_TOKEN}")
print(f"CHANNEL_ID: {CHANNEL_ID}")
print("hello team4U")

# Create a WebClient object with your token
client = WebClient(token=SLACK_BOT_TOKEN)


def fetch_channel_history(channel_id):
    print(f"SLACK_BOT_TOKEN: {SLACK_BOT_TOKEN}")
    print(f"CHANNEL_ID: {CHANNEL_ID}")
    print("bcfbgvf")

    try:
        # Open a CSV file for writing
        with open('slack_messages.csv', mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Write header row
            writer.writerow(['timestamp', 'user', 'text', 'reply_to', 'reply_text'])

            # Initialize the cursor for pagination
            cursor = None

            while True:
                # Request channel history with cursor for pagination
                response = client.conversations_history(
                    channel=channel_id,
                    cursor=cursor,
                    limit=200  # You can adjust this number to fetch up to 200 messages per request
                )
                messages = response['messages']

                # Create a dictionary to store messages by timestamp
                message_dict = {}
                for message in messages:
                    timestamp = message.get('ts', '')
                    user = message.get('user', '')
                    text = message.get('text', '')
                    reply_to = ''
                    reply_texts = []

                    # Store the message in the dictionary
                    message_dict[timestamp] = {
                        'user': user,
                        'text': text,
                        'reply_texts': reply_texts
                    }

                    # Check if the message has replies
                    if 'thread_ts' in message:
                        thread_ts = message['thread_ts']
                        # Fetch replies for this thread
                        reply_response = client.conversations_replies(channel=channel_id, ts=thread_ts)
                        replies = reply_response['messages']

                        # Add replies to the corresponding original message
                        for reply in replies:
                            if reply.get('ts') != thread_ts:  # Skip the original message itself
                                reply_texts.append(reply.get('text', ''))
                                reply_timestamp = reply.get('ts', '')
                                writer.writerow([reply_timestamp, reply.get('user', ''), '', thread_ts, reply.get('text', '')])
                                print(f'Reply Timestamp: {reply_timestamp}, Reply User: {reply.get("user", "")}, Reply Text: {reply.get("text", "")}, Reply To: {thread_ts}')

                    # Write the original message
                    writer.writerow([timestamp, user, text, '', ''])
                    print(f'Timestamp: {timestamp}, User: {user}, Text: {text}, Reply To: {reply_to}')

                # Check if there's more messages to fetch
                cursor = response.get('response_metadata', {}).get('next_cursor')
                if not cursor:
                    break

        print("Messages and replies saved to slack_messages.csv successfully.")

    except SlackApiError as e:
        print(f"Error fetching conversations: {e.response['error']}")


# Call the function with the channel ID
fetch_channel_history(CHANNEL_ID)