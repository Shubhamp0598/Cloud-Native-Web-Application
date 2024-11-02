# Import necessary packages
import json
import zipfile
import requests
from io import BytesIO
import base64
from google.cloud import storage
import os
import re
import boto3
import uuid

# Get gcp private key from environment variables and decrypt it
decoded_bytes = base64.b64decode(os.getenv("GOOGLE_CRED"))
decoded_json_string = decoded_bytes.decode("utf-8")
decoded_json = json.loads(decoded_json_string)

# Regex to validate if the url is in a valid format
url_validation_regex_pattern = r'^https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&\/=]*)$'

# Get gcp bucket name, aws region, and dynamodb table name from environment variables
gcs_bucket = os.getenv("GCP_BUCKET_NAME")
aws_region = os.getenv("AWS_REGION_DETAILS")
dynamodb_table = os.getenv("DYNAMODB_TABLE_NAME")

# Initialize Google Cloud Storage client with credentials
storage_client = storage.Client.from_service_account_info(decoded_json)

# Create an instance of dynamodb client using boto3
dynamodb_client = boto3.client('dynamodb', region_name=aws_region)

# Function to update dynamodb table
def update_dynamodb(email, submission_url, submission_attempt, submission_id, file_name):
    dynamodb_table_name = dynamodb_table  # Replace with your actual DynamoDB table name

    params = {
        'TableName': dynamodb_table_name,
        'Item': {
            'id': {'S': str(uuid.uuid4())},
            'email': {'S': email},
            'submissionAttempt': {'S': submission_attempt},
            'submissionUrl': {'S': submission_url},
            'submissionId': {'S': submission_id},
            'fileName': {'S': file_name}
        }
    }
    return dynamodb_client.put_item(TableName=params['TableName'], Item=params['Item'])

# Function to send an email to the student email using mailgun api key
def send_simple_message(to_email,assignment_name,message):
    print("====Attempting to send email=======")
    domain = os.getenv("MAILGUN_DOMAIN") # get mailgun domain from environment variables
    api = os.getenv("MAILGUN_API_KEY") # get mailgun api key from environment variables
    my_email = "shivanishahwork2@gmail.com"
    return requests.post(
		f"https://api.mailgun.net/v3/{domain}/messages",
		auth=("api", f"{api}"),
		data={"from": f"Shivani Shah<{my_email}>",
			"to": [f"{to_email}"],
			"subject": f"Submission notification for {assignment_name}",
			"html": f"{message}"})

# Function to format email body in html
def format_email_body(submission_url, file_name, attempt, message, user_email):
    return f"""<!DOCTYPE html>
                            <html lang="en">
                            <head>
                            <meta charset="UTF-8">
                            <meta name="viewport" content="width=device-width, initial-scale=1.0">
                            <style>
                                /* Add your styles here */
                            </style>
                            </head>
                            <body>
                            <p><strong>Dear Student,</strong></p>

                            <p><strong>Here are your submission details:</strong></p>
                            <ul>
                                <li><strong>Submission URL:</strong> {submission_url}</li>
                                <li><strong>Submission File Name:</strong> {file_name}</li>
                                <li><strong>Submission Attempt:</strong> {attempt}</li>
                                <li><strong>Status of the download:</strong> {message}</li>
                            </ul>

                            <p style="text-align: center;">This mail is intended to be received for {user_email}.</p>
                            </body>
                            </html>
                            """
# Function to compare submission_url link format with a valid url link regex pattern
def validate_regex(regex_pattern, input_string):
    pattern = re.compile(regex_pattern)
    match = pattern.fullmatch(input_string)
    return match is not None

# Function to validate if the url in the argument ( in our case, submission_url) is a valid zip file or not
def validate_zip_file_url(file_url):
    try:
        # Download the file
        response = requests.get(file_url)
        response.raise_for_status()

        # Check if the response appears to be a valid ZIP file
        is_valid_zip = is_zip_file(response.content)

        if is_valid_zip:
            print(f"{file_url} is a valid URL pointing to a .zip file.")
            return True
        else:
            print(f"{file_url} does not point to a valid .zip file.")
            return False

    except requests.exceptions.RequestException as error:
        print(f"Error validating URL: {error}")

        return False

# Helper function to check if the url passed in the argument of `validate_zip_file_url` function is a valid zip file or not
def is_zip_file(content):
    try:
        # Attempt to create a ZipFile instance with the content
        with zipfile.ZipFile(BytesIO(content)) as zip_file:
            return True
    except zipfile.BadZipFile:
        # If an error occurs, it's not a valid ZIP file
        return False

# Function to download zip file in the url passed in the argument
def download_zip_file(url):
    try:
        # Make an HTTP GET request to the URL
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        response.raise_for_status()

        # Return the binary content
        return response.content
    except requests.exceptions.RequestException as error:
        # Raise an exception if there is an error during the request
        raise RuntimeError(f"Error downloading ZIP file: {error}")

# Function to perform actions on triggering lambda - Uses all the functions defined above
# This function essentially loads the message sent from AWS SNS service, validates if the url submitted by the users accessed from the SNS message is 
# valid zip file url or not. If it is a valid zip file url, then it downloads the zip file and upload it to the
# google cloud storage bucket using google private key passed through the environment variables, sends an email to the
# user uploading the file by accessing the user's email id from the SNS message, and updates DynamoDB table with each sent email.
# It also email students if there is an issue with the submission url with the reason why the submission was not uploaded on google cloud
# storage bucket. For AWS, the credentials are provided by pulumi since we will be running this file as a part of pulumi

def lambda_handler(event, context):
    try:
        # Extract SNS message from the event
        sns_message = json.loads(event['Records'][0]['Sns']['Message']) 
        # Access individual fields from the SNS message
        submission_id = sns_message['submission_id']
        assignment_name = sns_message['assignment_name']
        user_email = sns_message['user_email']
        submission_url = sns_message['submission_url']
        attempt = sns_message['attempt']

        # if the regex pattern matches with the submission_url then enter this case
        if validate_regex(url_validation_regex_pattern, submission_url):
            # Check if the submission_url points to a valid zip file
            validateResponse = validate_zip_file_url(submission_url)
            if validateResponse:
                # Log or process the extracted information
                print(f"Received SNS message: {sns_message}")
                try:
                    print("=======Trying to download zip file=====")
                    # Save content of the zip file present in submission_url to zipFileContent
                    zipFileContent = download_zip_file(submission_url)
                    print(f"=======Downloaded zipFileContent=======")

                    file_name = f"{submission_id}{assignment_name}.zip"
                    print(f"====Attempting to upload zip file {file_name} to the bucket====")
                    bucket = storage_client.bucket(gcs_bucket) # get bucket name and access bucket from gcp
                    blob = bucket.blob(file_name) # create a file in the bucket with file_name
                    # Upload the content to the file
                    blob.upload_from_string(zipFileContent)
                    # Define variables to call send_simple_message, format_email_body, and update_dynamodb functions
                    # Send a file upload success email in this case
                    to_email = user_email
                    assignment = assignment_name
                    message = f"File uploaded successfully for {assignment}. This was your {attempt} attempt. The path to your submission's cloud storage bucket is: Buckets/{gcs_bucket}/{file_name}"
                    html_body = format_email_body(submission_url, file_name, attempt, message, user_email)
                    send_simple_message(to_email,assignment,html_body)
                    update_dynamodb(user_email, submission_url, attempt, submission_id, file_name)
                    return print("===========Successfully uploaded the file to gcs!===========")
                except Exception as e:
                    # Define variables to call send_simple_message, format_email_body, and update_dynamodb functions
                    # Send a file upload fail message in this case
                    to_email = user_email
                    assignment = assignment_name
                    file_name = "No file name"
                    message = f"File upload failed for {assignment}. This was your {attempt} attempt. There was an error either while downloading your file or uploading it to the cloud storage bucket."
                    html_body = format_email_body(submission_url, file_name, attempt, message, user_email)
                    send_simple_message(to_email,assignment,html_body)
                    update_dynamodb(user_email, submission_url, attempt, submission_id, file_name)
                    return print(f"An error occured while trying to upload file to the bucket: {e}")
            else:
                # Define variables to call send_simple_message, format_email_body, and update_dynamodb functions
                # Send a file submission failed message in this case
                to_email = user_email
                assignment = assignment_name
                file_name = "No file name"
                message = f"Submission failed for {assignment}. This was your {attempt} attempt. There was an error due to an invalid zip file upload."
                html_body = format_email_body(submission_url, file_name, attempt, message, user_email)
                send_simple_message(to_email,assignment,html_body)
                update_dynamodb(user_email, submission_url, attempt, submission_id, file_name)
                # Return an error response for invalid zip file
                return {
                    'statusCode': 400,
                    'body': json.dumps(f'Invalid zip file in submission_url - {submission_url}')
                }
        else:
            # Define variables to call send_simple_message, format_email_body, and update_dynamodb functions
            # Send a submission failed for invalid url format message for this case
            to_email = user_email
            assignment = assignment_name
            file_name = "No file name"
            message = f"Submission failed for {assignment}. This was your {attempt} attempt. There was an error due to an invalid URL format."
            html_body = format_email_body(submission_url, file_name, attempt, message, user_email)
            send_simple_message(to_email,assignment,html_body)
            update_dynamodb(user_email, submission_url, attempt, submission_id, file_name)
            # Return an error response for invalid zip file
            return {
                'statusCode': 400,
                'body': json.dumps(f'Invalid URL in submission_url - {submission_url}')
            }

    except Exception as e:
        # Log the error and return an error response if SNS message cannot be processed
        print(f"Error processing SNS message: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps('Error processing SNS message')
        }