import requests
import csv


def get_channel_history(slack_token, channel_id, limit=1000, cursor=None):
    url = 'https://slack.com/api/conversations.history'

    headers = {
        'Authorization': f'Bearer {slack_token}'
    }

    params = {
        'channel': channel_id,
        'limit': limit
    }

    if cursor:
        params['cursor'] = cursor

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        if data.get('ok'):
            return data['messages'], data.get('response_metadata', {}).get('next_cursor')
        else:
            print(f"Slack API error: {data.get('error')}")
            return [], None
    else:
        print(f"Request failed with status code: {response.status_code}")
        return [], None


def get_replies(slack_token, channel_id, thread_ts):
    url = 'https://slack.com/api/conversations.replies'

    headers = {
        'Authorization': f'Bearer {slack_token}'
    }

    params = {
        'channel': channel_id,
        'ts': thread_ts
    }
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        if data.get('ok'):
            return data['messages']
        else:
            print(f"Slack API error: {data.get('error')}")
            return []
    else:
        print(f"Request failed with status code: {response.status_code}")
        return []


def save_messages_to_csv(messages, file_name='slack_messages.csv'):
    # Define the CSV file headers
    headers = ['User', 'Text', 'Is Reply', 'Thread TS']

    # Open a file to write to it
    with open(file_name, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        # Write headers to the CSV
        writer.writerow(headers)

        # Write each message to the CSV
        for message in messages:
            writer.writerow([message['user'], message['text'], 'No', message['ts']])

            # Check if there are replies to this message
            if 'replies' in message:
                for reply in message['replies']:
                    writer.writerow([reply['user'], reply['text'], 'Yes', reply['ts']])


def main():
    # Replace with your Slack OAuth token
    slack_token = 'privet'

    # Replace with your Slack channel ID
    channel_id = 'C07K8KFCVFH'

    # Initialize the cursor for pagination
    cursor = None
    all_messages = []

    while True:
        # Fetch the channel history
        messages, cursor = get_channel_history(slack_token, channel_id, cursor=cursor)

        if messages:
            print(f"Retrieved {len(messages)} messages from the channel:")
            for message in messages:
                all_messages.append(message)
                print(f"User: {message.get('user')} - Text: {message.get('text')}")

                # Check if the message has replies
                if 'reply_count' in message and message['reply_count'] > 0:
                    thread_ts = message['ts']
                    replies = get_replies(slack_token, channel_id, thread_ts)
                    message['replies'] = replies  # Store replies in the message object
                    print(f"  {message['reply_count']} replies found:")
                    for reply in replies:
                        print(f"    User: {reply.get('user')} - Text: {reply.get('text')}")

            # Save all messages (and replies) to a CSV file
            save_messages_to_csv(all_messages, 'slack_messages.csv')
            print("Messages and replies saved to slack_messages.csv")
        else:
            print("No messages retrieved or an error occurred.")

        # If no cursor is returned, break the loop (end of conversation history)
        if not cursor:
            break


if __name__ == "__main__":
    main()
