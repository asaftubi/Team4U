import base64
import boto3
import json
import random
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv

# טען את משתני הסביבה מקובץ .env
load_dotenv(dotenv_path='.env')


def generate_image(prompt, model_id="amazon.titan-image-generator-v2:0", output_dir="output"):

    # Create a Bedrock Runtime client
    client = boto3.client("bedrock-runtime", region_name="us-east-1")

    # Define the image generation request payload
    native_request = {
        "textToImageParams": {"text": prompt},
        "taskType": "TEXT_IMAGE",
        "imageGenerationConfig": {
            "cfgScale": 10,
            "seed": random.randint(0, 1000),  # Random seed for variability
            "width": 1024,
            "height": 1024,
            "numberOfImages": 1
        }
    }

    # Convert the request payload to JSON
    request = json.dumps(native_request)

    try:
        # Invoke the model and get the response
        response = client.invoke_model(modelId=model_id, body=request)

        # Decode the response body
        model_response = json.loads(response["body"].read())
        base64_image_data = model_response["images"][0]

        # Prepare output directory
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Find a unique filename
        i = 1
        while os.path.exists(os.path.join(output_dir, f"image_{i}.png")):
            i += 1

        # Save the generated image
        image_data = base64.b64decode(base64_image_data)
        image_path = os.path.join(output_dir, f"image_{i}.png")
        print(output_dir)
        with open(image_path, "wb") as file:
            file.write(image_data)

        print(f"The generated image has been saved to {image_path}.")

    except ClientError as e:
        print(f"ClientError: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


def main():
    # Define the prompt for the image generation
    prompt = " A penguin dressed as a businessman, balancing on a unicycle, could be both humorous and whimsical."

    # Call the image generation function
    generate_image(prompt)


if __name__ == "__main__":
    main()
