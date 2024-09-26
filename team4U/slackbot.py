import os
import logging
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from ping_pong_bedrock import query_knowledge_base as qkb
from dotenv import load_dotenv

# הגדרת לוגר
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# טעינת משתני סביבה
load_dotenv()

# יצירת אפליקציית Slack
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

@app.event("app_mention")
def handle_mention(event, say):
    print(45435534)
    try:


        # קבלת הטקסט של ההודעה
        message_text = event['text']
        user_id = event['user']

        # הסרת אזכור הבוט מההודעה
        clean_message = message_text.split('>', 1)[-1].strip()

        logger.info(f"Received message from user {user_id}: {clean_message}")

        # עיבוד ההודעה
        response = process_message(clean_message)

        # שליחת התגובה בחזרה ל-Slack
        say(f"{response}")

    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        say("מצטער, אירעה שגיאה בעיבוד הבקשה שלך. אנא נסה שוב מאוחר יותר.")

def process_message(message):
    try:
        return qkb(message)
    except Exception as e:
        logger.error(f"Error in start function: {str(e)}")
        return "אירעה שגיאה בעיבוד הבקשה. אנא נסה שוב או פנה לתמיכה."

@app.event("message")
def handle_message(message, say):
    # טיפול בהודעות רגילות (לא אזכורים)
    if "text" in message and message.get("subtype") is None:
        logger.info(f"Received message: {message['text']}")
        # כאן תוכל להוסיף לוגיקה נוספת לטיפול בהודעות רגילות

@app.error
def global_error_handler(error, body, logger):
    logger.error(f"Error: {error}")
    logger.error(f"Request body: {body}")

def start_server():
    handler = SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN"))
    logger.info("Starting the bot...")
    handler.start()


if __name__ == "__main__":
    start_server()
