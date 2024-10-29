import functools
import logging
import os

import requests
from requests.packages.urllib3.util.retry import Retry


@functools.lru_cache()
def get_tc_secret():
    """Returns the Taskcluster secret.

    Returns False when not running on tc
    """
    tc_proxy = os.environ.get("TASKCLUSTER_PROXY_URL")
    if not tc_proxy:
        return False
    logging.warning("tc_prox is not in env")
    session = requests.Session()
    retry = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
    http_adapter = requests.adapters.HTTPAdapter(max_retries=retry)
    session.mount("https://", http_adapter)
    session.mount("http://", http_adapter)
    secrets_url = f"{tc_proxy}/secrets/v1/secret/project%2Fmozilla%2Ffx-desktop-qa-automation%2Flevel-3%2Ftestrail"

    res = session.get(secrets_url, timeout=30)
    res.raise_for_status()
    logging.warning("secret is got")

    return res.json()["secret"]
