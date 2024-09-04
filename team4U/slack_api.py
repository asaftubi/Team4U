# pip install slack_sdk

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# החלף ב-token שלך
SLACK_BOT_TOKEN = 'xoxe.xoxp-1-Mi0yLTc2NjkxMDUxMTAxNDYtNzY5MTkzNDk2Njg5Ni03Njc1NTg1NzMyMDY2LTc2Njg5NTE4MzI4ODYtMWY3NmMyM2Y1ZDYzNmE1OGVhZWExMWE5MDczYjE4OGI5MjUyYzI4Y2M2NDRiNTMzMGQ2NWFlOTUwOTkzOWZhYQ'

# החלף ב-ID של הערוץ שלך
CHANNEL_ID = 'C07K8KFCVFH'

# יצירת אובייקט WebClient עם ה-token שלך
client = WebClient(token=SLACK_BOT_TOKEN)


def fetch_channel_history(channel_id):
    try:
        # בקשת היסטוריית ההודעות מהערוץ
        response = client.conversations_history(channel=channel_id)
        messages = response['messages']

        # הדפסת ההודעות
        for message in messages:
            print(message.get('text', ''))

    except SlackApiError as e:
        print(f"Error fetching conversations: {e.response['error']}")


# קריאה לפונקציה עם ID של הערוץ
fetch_channel_history(CHANNEL_ID)

