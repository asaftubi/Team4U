import boto3
import json
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv

# טען את משתני הסביבה מקובץ .env
load_dotenv(dotenv_path='.env')

def main():
    client = boto3.client("bedrock-runtime",
                          aws_access_key_id=os.getenv('aws_access_key_id'),
                          aws_secret_access_key=os.getenv('aws_secret_access_key'),
                          region_name="eu-west-1",
                          )
    model_id = "eu.anthropic.claude-3-5-sonnet-20240620-v1:0"
    system_prompt = "You are a helpful assistant."
    user_message = "who is lebron james?"

    try:
        prompt_payload = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 70,
            "messages": [
                {"role": "user", "content": user_message}
            ],
<<<<<<< HEAD
            "temperature": 0.5

=======
            "temperature": 0.1
>>>>>>> e91340ce2070c6b6f09e915aa54d275f12140ef8
        })

        response = client.invoke_model(
            modelId=model_id,
            contentType="application/json",
            body=prompt_payload
        )

        response_body = json.loads(response["body"].read())
        print(f"Model Response: {response_body}")
        # print(f"Model Response: {response_body['content'][0]['text']}")


    except ClientError as e:
        if e.response['Error']['Code'] == 'ValidationException':
            print(f"Validation Error: {e}")
        elif e.response['Error']['Code'] == 'AccessDeniedException':
            print("Access Denied. Check your IAM permissions and Bedrock model access.")
        else:
            print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()