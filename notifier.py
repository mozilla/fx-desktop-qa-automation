import datetime
import json
import mimetypes
import os
from typing import List

from google.cloud import storage
from google.oauth2 import service_account
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from blocks import return_slack_blocks


def send_slack_message(report_file: str):
    print("Trying to send Slack Message...")
    token = os.getenv("SLACK_KEY")

    # Initialize a Web API client
    client = WebClient(token=token)

    try:
        client.chat_postMessage(
            channel="#desktop-qa-monitoring-notifier",
            text="Important update from ACTIONS...",  # This is required but can be anything if blocks are used
            blocks=return_slack_blocks(report_file),
        )
    except SlackApiError as e:
        print(f"Error sending message: {e.response['error']}")


def get_content_type(filename):
    """
    Return the MIME type based on the filename extension.
    """
    content_type, _ = mimetypes.guess_type(filename)
    return content_type or "text/plain"


def get_current_timestamp():
    """
    Returns the current date and time formatted as 'YYYY-mm-dd_HHmm_SS'.

    :return: str, formatted timestamp
    """
    print("Getting the current date...")
    now = datetime.datetime.now()
    formatted_timestamp = now.strftime("%Y-%m-%d-%H%M_%S")
    return formatted_timestamp


def list_and_write(source_directory: str, links: List[str]):
    print(f"Trying to traverse {source_directory} and write files...")

    for root, dirs, files in os.walk(source_directory):
        for file in files:
            fullpath = os.path.join(root, file)

            target_path = os.path.join(f"{time_now}", (fullpath))

            content_type = get_content_type(file)
            blob = bucket.blob(target_path)
            blob.content_type = content_type
            read_mode = "rb" if content_type == "image/png" else "r"
            write_mode = "wb" if content_type == "image/png" else "w"

            links.append(f"{root_url}{target_path}")

            with (
                open(fullpath, read_mode) as infile,
                blob.open(write_mode, content_type=content_type) as f,
            ):
                contents = infile.read()
                f.write(contents)


def compile_link_file(links_win: List[str], links_mac: List[str]):
    print("Compiling the current artifact link file...")
    links_mac.sort()
    links_win.sort()

    output_file_path = os.path.join(time_now, "full_report.txt")
    content_type = get_content_type(output_file_path)
    bucket = storage_client.bucket(bucket_name)

    blob = bucket.blob(output_file_path)
    with blob.open("w", content_type=content_type) as f:
        f.write("Windows Artifacts:\n\n")

        for url in links_win:
            f.write(url + "\n")

        f.write("\nMac Artifacts:\n\n")

        for url in links_mac:
            f.write(url + "\n")
    return f"{root_url}{time_now}/full_report.txt"


time_now = get_current_timestamp()
links_win = []
links_mac = []
root_url = "https://storage.googleapis.com/notifier-artifact-bucket/"
report_file = ""

try:
    credential_string = os.getenv("GCP_CREDENTIAL")
    credentials_dict = json.loads(credential_string)
    credentials = service_account.Credentials.from_service_account_info(
        credentials_dict
    )
    storage_client = storage.Client(credentials=credentials)
    bucket_name = "notifier-artifact-bucket"
    bucket = storage_client.bucket(bucket_name)
    list_and_write("artifacts-mac", links_mac)
    list_and_write("artifacts-win", links_win)
except Exception as e:
    print("The artifact upload process ran into some issues: ", e)


try:
    report_file = compile_link_file(links_win, links_mac)
except Exception as e:
    print(f"The link compilation had some issues: {e}")

send_slack_message(report_file)

print("Message sent! Script finished successfully.")
