import boto3
import logging
import sys
import os
from dotenv import load_dotenv
load_dotenv(dotenv_path='.env')


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def query_knowledge_base(message):
    bedrock_agent_runtime = boto3.client('bedrock-agent-runtime',
        aws_access_key_id=os.getenv('aws_access_key_id'),
        aws_secret_access_key=os.getenv('aws_secret_access_key'),
        region_name="us-east-1" ) # שנה בהתאם)

    request_body = {
        "input": {
            "text": message
        },
        "retrieveAndGenerateConfiguration": {
            "type": "KNOWLEDGE_BASE",
            "knowledgeBaseConfiguration": {
                "knowledgeBaseId": "IFGNAI9DOT",
                "modelArn": "anthropic.claude-3-5-sonnet-20240620-v1:0"
            }
        }
    }

    response = bedrock_agent_runtime.retrieve_and_generate(**request_body)

    generated_text = response['output']['text']
    return generated_text


def main():
    print("Welcome to the AWS Bedrock Knowledge Base Query Tool")
    print("Type 'quit' to exit the program")

    while True:
        user_input = input("\nEnter your question: ").strip()

        if user_input.lower() == 'quit':
            print("Thank you for using the AWS Bedrock Knowledge Base Query Tool. Goodbye!")
            break

        if not user_input:
            print("Please enter a valid question.")
            continue

        try:
            logger.info(f"Querying knowledge base with: {user_input}")
            answer = query_knowledge_base(user_input)

            print("\nAnswer:")
            print(answer)
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            print("Sorry, I couldn't generate an answer. Please try again or rephrase your question.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram interrupted by user. Exiting...")
        sys.exit(0)