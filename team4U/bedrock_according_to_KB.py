import boto3
import csv
import json
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv

# טוען משתני סביבה מקובץ .env
load_dotenv(dotenv_path='.env')


def fetch_all_files_from_bucket():
    s3_client = boto3.client('s3',
                             aws_access_key_id=os.getenv('aws_access_key_id'),
                             aws_secret_access_key=os.getenv('aws_secret_access_key'),
                             region_name="eu-west-1"  # שנה בהתאם
                             )

    bucket_name = "health-channle"  # שם הדלי שלך

    try:
        # רשימת כל האובייקטים (קבצים) בדלי
        response = s3_client.list_objects_v2(Bucket=bucket_name)

        if 'Contents' not in response:
            print("No files found in the bucket.")
            return []

        all_kb_data = []

        for obj in response['Contents']:
            file_key = obj['Key']
            file_object = s3_client.get_object(Bucket=bucket_name, Key=file_key)

            # ניסיון לקרוא עם קידודים שונים
            for encoding in ['utf-8', 'ISO-8859-1', 'Windows-1252']:
                try:
                    file_data = file_object['Body'].read().decode(encoding)
                    print(f"Reading file: {file_key} with encoding {encoding}")
                    break
                except UnicodeDecodeError:
                    continue
            else:
                print(f"File {file_key} cannot be decoded with available encodings. Skipping.")
                continue

            # ניסיון לקרוא כ-CSV
            try:
                csv_reader = csv.DictReader(file_data.splitlines())
                for row in csv_reader:
                    # הנחת עמודות בשם 'question' ו-'answer'
                    question = row.get('question', 'N/A')
                    answer = row.get('answer', 'N/A')
                    all_kb_data.append({'question': question, 'answer': answer})
            except Exception as e:
                print(f"Error reading file {file_key}: {e}")

        return all_kb_data

    except ClientError as e:
        print(f"Error fetching files from S3: {e}")
        return []


def main():
    client = boto3.client("bedrock-runtime",
                          aws_access_key_id=os.getenv('aws_access_key_id'),
                          aws_secret_access_key=os.getenv('aws_secret_access_key'),
                          region_name="eu-west-1",  # שנה בהתאם
                          )

    model_id = "eu.anthropic.claude-3-5-sonnet-20240620-v1:0"  # ID של המודל שלך
    system_prompt = "You are a helpful assistant."

    # הבאת נתונים מכל הקבצים בדלי S3
    kb_data = fetch_all_files_from_bucket()

    if kb_data:
        user_question = "How can a balanced diet affect energy levels and daily performance?"

        # שילוב כל התוכן מהקבצים לכדי בסיס ידע אחיד
        kb_content = "\n".join(
            [f"Question: {entry.get('question', 'N/A')}\nAnswer: {entry.get('answer', 'N/A')}" for entry in kb_data])
        full_prompt = f"{system_prompt}\nKnowledge Base:\n{kb_content}\n\nQuestion: {user_question}"

        try:
            prompt_payload = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 150,
                "messages": [
                    {"role": "user", "content": full_prompt}
                ],
                "temperature": 0.1
            })

            response = client.invoke_model(
                modelId=model_id,
                contentType="application/json",
                body=prompt_payload
            )

            response_body = json.loads(response["body"].read())
            print(f"Model Response: {response_body}")

        except ClientError as e:
            print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
