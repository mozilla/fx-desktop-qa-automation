import json
import os
import mimetypes
import datetime

from google.cloud import storage
from google.oauth2 import service_account
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

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

def get_content_type(filename):
    """
    Return the MIME type based on the filename extension.
    """
    content_type, _ = mimetypes.guess_type(filename)
    return content_type or 'text/plain'

def get_current_timestamp():
    """
    Returns the current date and time formatted as 'YYYY-mm-dd_HHmm_SS'.

    :return: str, formatted timestamp
    """
    now = datetime.datetime.now()
    formatted_timestamp = now.strftime("%Y-%m-%d_%H%M_%S")
    return formatted_timestamp


def list_and_write(source_directory: str, cur_call: int):
    if cur_call > 5:
        print("This function has recursed too many times. Stopping execution")
        return

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

        # the current directory
        source_path = os.path.join(source_directory, filename)

        # if the item is a file, directly upload
        if os.path.isfile(source_path):
            new_filename = filename
            target_path = os.path.join(source_directory, new_filename)

            content_type = get_content_type(source_path)
            blob = bucket.blob(target_path)
            blob.content_type = content_type

            with (
                open(source_path, "r") as infile,
                blob.open("w", content_type=content_type) as f,
            ):
                contents = infile.read()
                f.write(contents)

            # TODO: return the URL that it has

        # if the item is a file, increment recursion count and recurse on the directory
        elif os.path.isdir(source_path):
            list_and_write(os.path.join(source_directory, filename), cur_call+1)

try:
    time_now = get_current_timestamp()
    list_and_write(f"{time_now}/artifacts-mac", 0)
    list_and_write(f"{time_now}/artifacts-win", 0)
except Exception as e:
    print("The artifact upload process ran into some issues: ", e)
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
