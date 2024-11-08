import functools
import logging
import os

import requests
from requests.packages.urllib3.util.retry import Retry


@functools.lru_cache()
def get_tc_secret(secret_name="testrail", level=3):
    """Returns the Taskcluster secret.

    Returns False when not running on tc
    """
    if not os.environ.get("TASKCLUSTER_ROOT_URL"):
        return False
    tc_home = os.environ.get("TASKCLUSTER_PROXY_URL", "http://taskcluster")
    session = requests.Session()
    retry = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
    http_adapter = requests.adapters.HTTPAdapter(max_retries=retry)
    session.mount("https://", http_adapter)
    session.mount("http://", http_adapter)
    secrets_url = f"{tc_home}/secrets/v1/secret/project/mozilla/fx-desktop-qa-automation/level-{level}/{secret_name}"

    res = session.get(secrets_url, timeout=30)
    res.raise_for_status()
    logging.warning("secret is got")

    return res.json()["secret"]
