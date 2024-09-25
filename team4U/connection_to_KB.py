import boto3
import os
from dotenv import load_dotenv


load_dotenv()

# קריאה למשתנים מהסביבה
access_key = os.getenv('AWS_ACCESS_KEY_ID')
secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
region = os.getenv('AWS_REGION')

# יצירת לקוח Bedrock
bedrock_client = boto3.client('bedrock-agent-runtime',
                              aws_access_key_id=access_key,
                              aws_secret_access_key=secret_key,
                              region_name=region)


# שליחת הבקשה עם הפרמטרים כ-keyword arguments
request_body = {
    "input": {
        "text": "How can a diet high in low-glycemic index foods help in managing diabetes?"
    },
    "retrieveAndGenerateConfiguration": {
        "type": "KNOWLEDGE_BASE",
        "knowledgeBaseConfiguration": {
            "knowledgeBaseId": "IFGNAI9DOT",
            "modelArn": "anthropic.claude-3-5-sonnet-20240620-v1:0"
        }
    }
}

response = bedrock_client.retrieve_and_generate(**request_body)

# קבלת התוצאה מהמודל
configuration = response['output']['text']

print(487578920346572364578)
print(configuration)