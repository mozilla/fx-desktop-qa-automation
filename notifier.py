from google.cloud import storage


# def write_read():
#     """Write and read a blob from GCS using file-like IO"""
#     # The ID of your GCS bucket
#     bucket_name = "notifier-artifact-bucket"

#     # The ID of your new GCS object
#     blob_name = "new_file"

#     storage_client = storage.Client()
#     bucket = storage_client.bucket(bucket_name)
#     blob = bucket.blob(blob_name)

#     # Mode can be specified as wb/rb for bytes mode.
#     # See: https://docs.python.org/3/library/io.html
#     with blob.open("w") as f:
#         f.write("Hello world")

#     with blob.open("r") as f:
#         print(f.read())

# write_read()

# import os

# from slack_sdk import WebClient
# from slack_sdk.errors import SlackApiError

# # Your OAuth access token
# token = os.getenv("SLACK_KEY")

# # Initialize a Web API client
# client = WebClient(token=token)

# try:
#     response = client.chat_postMessage(
#         channel="#desktop-qa-monitoring-notifier",  # Channel ID or name (e.g., #general)
#         text="from actions... 1",
#     )
#     print("i have sent the message.")
# except SlackApiError as e:
#     print(f"Error sending message: {e.response['error']}")


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
