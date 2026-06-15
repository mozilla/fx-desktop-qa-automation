import os
import re
from subprocess import check_call, check_output

import requests
import thclient
from bs4 import BeautifulSoup as soup

# Assume beta link is in env as FX_DOWNLOAD_LINK
BUILDHUB = "buildhub.json"
TREEHERDER_LINK = "https://treeherder.mozilla.org/jobs?repo=mozilla-beta&searchStr=Windows%2Cshippable%2Fopt&revision={}"
ARTIFACT_LINK = "https://firefox-ci-tc.services.mozilla.com/api/queue/v1/task/{}/runs/0/artifacts/public%2Fbuild%2Ftarget.cppunittest.tests.tar.zst"


def main():
    # get buildhub json
    download_dir, _ = os.getenv("FX_DOWNLOAD_URL").rsplit("/", 1)
    response = requests.get(f"{download_dir}/{BUILDHUB}")
    response.raise_for_status()

    # use buildhub info to derive TH link
    buildinfo = response.json()
    rev = buildinfo.get("source").get("revision")
    response = requests.get(TREEHERDER_LINK.replace("{}", rev))
    response.raise_for_status()
    th_source = soup(response.content)
    task_link = th_source.find(
        "button", {"data-testid": "job-btn", "title": re.compile("^")}
    )
    job_id = task_link["data-job-id"]
    treeherder = thclient.TreeherderClient()
    jobs_list = treeherder.get_jobs(project="mozilla-beta", id=job_id)
    if not jobs_list:
        return None  # replace with raise

    # use taskcluster api to get artifact
    task_id = jobs_list[-1].get("task_id")
    artifact_json_url = ARTIFACT_LINK.replace("{}", task_id)
    response = requests.get(artifact_json_url)
    response.raise_for_status()
    artifact_url = response.json().get("url")
    response = requests.get(artifact_url)
    response.raise_for_status()

    # write and extract artifact with tests
    with open("cpptests.tar.zst", "wb") as fh:
        for chunk in response.iter_content(chunk_size=2048):
            if chunk:
                fh.write(chunk)
    check_call(["7za", "e", "cpptests.tar.zst"])

    # run tests
    itcptr_testout = check_output(["cppunittest\\TestDllInterceptor.exe"]).decode()
    icptxp_testout = check_output(
        ["cppunittest\\TestDllInterceptorCrossProcess.exe"]
    ).decode()
    assert "all tests passed" in itcptr_testout.strip().split("\n")[-1]
    assert "TEST-PASS" in icptxp_testout.strip().split("\n")[-1]
    assert "TEST-UNEXPECTED-FAIL" in icptxp_testout


if __name__ == "__main__":
    main()
