import json
import os

from google.cloud import storage
from google.oauth2 import service_account
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# def write_read():
#     """Write and read a blob from GCS using file-like IO"""
#     # The ID of your GCS bucket
#     bucket_name = "notifier-artifact-bucket"
#     # The ID of your new GCS object
#     blob_name = "new_folder/new_file.txt"
#     # Path to your service account key file
#     # key_path = "credentials.json"

#     # Using stored JSON
#     credential_string = os.getenv("GCP_CREDENTIAL")
#     credentials_dict = json.loads(credential_string)

#     # Load credentials from the service account key file
#     credentials = service_account.Credentials.from_service_account_info(
#         credentials_dict
#     )
#     # Initialize the client with explicit credentials
#     storage_client = storage.Client(credentials=credentials)
#     bucket = storage_client.bucket(bucket_name)
#     blob = bucket.blob(blob_name)
#     # Set the Content-Type before writing
#     blob.content_type = "text/plain"
#     # Write data to the blob
#     with blob.open("w", content_type="text/plain") as f:
#         f.write("Hello world")


def send_slack_message():
    token = os.getenv("SLACK_KEY")

    # Initialize a Web API client
    client = WebClient(token=token)

    try:
        response = client.chat_postMessage(
            channel="#desktop-qa-monitoring-notifier",  # Channel ID or name (e.g., #general)
            text="from ACTIONS... 1",
        )
        print("i have sent the message.")
    except SlackApiError as e:
        print(f"Error sending message: {e.response['error']}")


def list_artifacts():
    try:
        # List all files and directories in the specified path
        contents_windows = os.listdir("artifacts-win")
        contents_mac = os.listdir("artifacts-mac")
        print("Directory contents (windows):", contents_windows)
        print("Directory contents (mac):", contents_mac)
    except FileNotFoundError:
        print("Directory not found:")


def list_and_write(source_directory):
    bucket_name = "notifier-artifact-bucket"

    credential_string = os.getenv("GCP_CREDENTIAL")
    credentials_dict = json.loads(credential_string)

    credentials = service_account.Credentials.from_service_account_info(
        credentials_dict
    )

    storage_client = storage.Client(credentials=credentials)
    bucket = storage_client.bucket(bucket_name)
    # Loop through each file in the specified source directory
    for filename in os.listdir(source_directory):
        source_path = os.path.join(source_directory, filename)
        if os.path.isfile(source_path):
            new_filename = filename
            target_path = os.path.join(source_directory, new_filename)

            blob = bucket.blob(target_path)
            # Set the Content-Type before writing
            blob.content_type = "text/plain"
            # Write data to the blob
            with (
                open(source_path, "r") as infile,
                blob.open("w", content_type="text/plain") as f,
            ):
                contents = infile.read()
                f.write(contents)

        elif os.path.isdir(source_path):
            list_and_write(os.path.join(source_directory, filename))


list_and_write("artifacts-mac")
list_and_write("artifacts-win")
send_slack_message()

# Your OAuth access token


# {
#     "display_information": {
#         "name": "Demo App"
#     },
#     "settings": {
#         "org_deploy_enabled": false,
#         "socket_mode_enabled": false,
#         "is_hosted": false,
#         "token_rotation_enabled": false
#     }
# }
