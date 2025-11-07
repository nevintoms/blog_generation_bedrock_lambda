# Use the native inference API to send a text message to Meta Llama 3.

import boto3
import json
from datetime import datetime
from botocore.exceptions import ClientError

def blog_generate_using_bedrock(blogtopic: str) -> str:

    # Create a Bedrock Runtime client in the AWS Region of your choice.
    client = boto3.client("bedrock-runtime", region_name="us-west-2")

    # Set the model ID, e.g., Llama 3 70b Instruct.
    model_id = "meta.llama3-70b-instruct-v1:0"

    # Define the prompt for the model.
    # prompt = "Describe the purpose of a 'hello world' program in one line."

    # Embed the prompt in Llama 3's instruction format.
    formatted_prompt = f"""
    <|begin_of_text|><|start_header_id|>user<|end_header_id|>
    {blogtopic}
    <|eot_id|>
    <|start_header_id|>assistant<|end_header_id|>
    """

    # Format the request payload using the model's native structure.
    native_request = {
        "prompt": formatted_prompt,
        "max_gen_len": 512,
        "temperature": 0.5,
    }

    # Convert the native request to JSON.
    request = json.dumps(native_request)

    try:
        # Invoke the model with the request.
        response = client.invoke_model(modelId=model_id, body=request)

    except (ClientError, Exception) as e:
        print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
        exit(1)

    # Decode the response body.
    model_response = json.loads(response["body"].read())

    # Extract and print the response text.
    response_text = model_response["generation"]
    return response_text

def save_blog_details_s3(s3_key, s3_bucket, generate_blog):
    s3 = boto3.client('s3')
    try:
        s3.put_object(Bucket=s3_bucket, Key=s3_key, Body=generate_blog)
        print("Code saved to s3")

    except Exception as e:
        print("Error when saving the code to s3")

def lambda_handler(event, context):
    # TODO implement
    event = json.loads(event['body'])
    blogtopic = event['blog_topic']

    generate_blog = blog_generate_using_bedrock(blogtopic)

    if generate_blog:
        current_time = datetime.now().strftime('%H%M%S')
        s3_key = f"blog-output/{current_time}.txt"
        s3_bucket = 'blog-generate-using-bedrock-lambda'
        save_blog_details_s3(s3_key, s3_bucket, generate_blog)
    else:
        print("No blog was generated")
    return {
        'statusCode': 200,
        'body': json.dumps('Blog Generation is completed')
    }




