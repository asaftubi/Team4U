import time
import requests
import csv
from datetime import datetime
from dotenv import load_dotenv
import os

# טוען את המשתנים מקובץ .env
load_dotenv()

# הגדרות מתוך קובץ ה-ENV
SLACK_TOKEN = os.getenv('SLACK_BOT_TOKEN')
CHANNEL_ID = os.getenv('SLACK_CHANNEL_ID')
API_URL = 'https://slack.com/api/conversations.history'

# הגדרת headers בצורה גלובלית
headers = {
    'Authorization': f'Bearer {SLACK_TOKEN}'
}

# פונקציה לבדוק אם הטוקן תקין
def check_token_validity():
    response = requests.get('https://slack.com/api/auth.test', headers=headers)

    if response.status_code == 200:
        data = response.json()
        if data.get('ok'):
            return True  # הטוקן תקין
        else:
            print(f"Invalid token: {data.get('error')}")
            return False  # הטוקן לא תקין
    else:
        print(f"Error checking token validity: {response.status_code}, {response.text}")
        return False  # אירעה שגיאה בבדיקת הטוקן

# פונקציה לבצע קריאה עם נסיונות חוזרים במקרים של שגיאות זמניות
def make_request_with_retry(url, params, headers, retries=3):
    for attempt in range(retries):
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            return response
        elif response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 1))
            print(f"Rate limit hit. Sleeping for {retry_after} seconds.")
            time.sleep(retry_after)
        else:
            print(f"Attempt {attempt + 1} failed with status: {response.status_code}, {response.text}")
            time.sleep(2 ** attempt)  # נסיון חוזר עם המתנה גיאומטרית
    return None

# פונקציה לקבלת שם הערוץ
def get_channel_name(channel_id):
    response = make_request_with_retry(
        'https://slack.com/api/conversations.info',
        params={'channel': channel_id},
        headers=headers
    )
    if response and response.status_code == 200:
        data = response.json()
        if data.get('ok'):
            return data.get('channel', {}).get('name', 'channel')
        else:
            print(f"Error fetching channel info: {data.get('error')}")
    else:
        print("Failed to fetch channel info after retries.")
    return 'channel'

# פונקציה להורדת כל ההודעות מהערוץ
def fetch_all_messages(channel_id, oldest_time):
    all_messages = []
    next_cursor = None

    # הדפסת הזמן שממנו מושכים את ההודעות
    print(f"Fetching messages from: {datetime.fromtimestamp(oldest_time)}")

    while True:
        params = {
            'channel': channel_id,
            'oldest': f"{oldest_time:.6f}",  # המרה למחרוזת עם 6 ספרות עשרוניות
            'limit': 100
        }

        if next_cursor:
            params['cursor'] = next_cursor

        # ביצוע הקריאה עם נסיונות חוזרים
        response = make_request_with_retry(API_URL, params, headers)

        if response is None:
            print("Failed to fetch messages after retries.")
            break

        print(f"API Response: {response.status_code}, {response.text}")

        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                messages = data.get('messages', [])
                print(f"Fetched {len(messages)} messages.")
                all_messages.extend(messages)
                next_cursor = data.get('response_metadata', {}).get('next_cursor')
                if not next_cursor:
                    break
            else:
                print(f"Error fetching messages: {data.get('error')}")
                break
        else:
            print(f"Error fetching messages: {response.status_code}, {response.text}")
            break

    return all_messages

# פונקציה להורדת הודעות משרשורים
def fetch_thread_messages(channel_id, thread_ts, oldest_time):
    thread_messages = []
    params = {
        'channel': channel_id,
        'ts': thread_ts,
        'oldest': f"{oldest_time:.6f}",
        'limit': 100
    }

    print(f"Fetching thread messages from: {datetime.fromtimestamp(oldest_time)} for thread_ts: {thread_ts}")

    # ביצוע הקריאה עם נסיונות חוזרים
    response = make_request_with_retry('https://slack.com/api/conversations.replies', params, headers)

    if response is None:
        print("Failed to fetch thread messages after retries.")
        return thread_messages

    print(f"Thread API Response: {response.status_code}, {response.text}")

    if response.status_code == 200:
        data = response.json()
        if data.get('ok'):
            messages = data.get('messages', [])
            print(f"Fetched {len(messages)} thread messages.")
            thread_messages.extend(messages)
        else:
            print(f"Error fetching thread messages: {data.get('error')}")
    else:
        print(f"Error fetching thread messages: {response.status_code}, {response.text}")

    return thread_messages

# בדיקת תקינות הטוקן
if not check_token_validity():
    print("Exiting the program due to invalid token.")
    exit()  # יציאה מהתוכנית אם הטוקן אינו תקין

# חותם זמן ליוניקס עבור 24 השעות האחרונות
current_time = time.time()
yesterday_time = current_time - 24 * 60 * 60

print(f"Current time: {current_time}, Yesterday time: {yesterday_time}")

# הורדת כל ההודעות מהערוץ
messages = fetch_all_messages(CHANNEL_ID, yesterday_time)
data = []

# עיבוד ההודעות והתגובות בשרשורים
for message in messages:
    if 'text' in message:
        data.append({
            'timestamp': message.get('ts'),
            'user': message.get('user', 'unknown'),
            'text': message.get('text', ''),
            'is_thread': 'No',
            'thread_ts': ''
        })

        if 'thread_ts' in message:
            thread_ts = message['thread_ts']
            thread_messages = fetch_thread_messages(CHANNEL_ID, thread_ts, yesterday_time)
            for idx, thread_message in enumerate(thread_messages):
                data.append({
                    'timestamp': thread_message.get('ts'),
                    'user': thread_message.get('user', 'unknown'),
                    'text': thread_message.get('text', ''),
                    'is_thread': 'Yes' if idx != 0 else 'Original',
                    'thread_ts': thread_ts
                })

# קבלת שם הערוץ
channel_name = get_channel_name(CHANNEL_ID)

# קבלת תאריך ליצירת שם קובץ
today_date = datetime.now().strftime('%Y-%m-%d')
filename = f"{channel_name}_{today_date}.csv"

# יצירת הקובץ באותה התיקייה שבה הקוד נמצא
if data:
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['timestamp', 'user', 'text', 'is_thread', 'thread_ts'])
        writer.writeheader()
        writer.writerows(data)

    print(f"File '{filename}' has been created successfully!")
else:
    print("No messages found in the specified time period.")
