# def write_read():
#     """Write and read a blob from GCS using file-like IO"""
#     # The ID of your GCS bucket
#     bucket_name = "notifier-artifact-bucket"
#     # The ID of your new GCS object
#     blob_name = "new_folder/new_file.txt"
#     # Path to your service account key file
#     key_path = "credentials.json"
#     # Load credentials from the service account key file
#     credentials = service_account.Credentials.from_service_account_file(key_path)
#     # Initialize the client with explicit credentials
#     storage_client = storage.Client(credentials=credentials)
#     bucket = storage_client.bucket(bucket_name)
#     blob = bucket.blob(blob_name)
#     # Set the Content-Type before writing
#     blob.content_type = 'text/plain'
#     # Write data to the blob
#     with blob.open("w", content_type='text/plain') as f:
#         f.write("Hello world")
# write_read()
import os

from google.cloud import storage
from google.oauth2 import service_account
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Your OAuth access token
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
