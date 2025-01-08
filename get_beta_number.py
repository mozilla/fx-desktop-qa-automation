import requests
from os import environ
from bs4 import BeautifulSoup

beta_url = "https://ftp.mozilla.org/pub/firefox/releases/"

# Fetch the page
response = requests.get(beta_url)
response.raise_for_status()

# Parse the HTML content
soup = BeautifulSoup(response.text, 'html.parser')

latest_beta_num = -1
latest_beta_ver = ""

# Extract the text of each line
for line in soup.find_all('a'):
    line_text = line.getText().split(".")
    if len(line_text) < 2 or not line_text[0]:
        continue
    beta_num = int(line_text[0])
    # Find the latest beta version
    if beta_num >= latest_beta_num:
        latest_beta_num = beta_num
        latest_beta_ver = line.getText()[:-1]

environ["LATEST"] = latest_beta_ver
