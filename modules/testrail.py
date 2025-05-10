"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.

TestRail API binding for Python 3.x.

Compatible with TestRail 6.8 and later.

Learn more:

http://docs.gurock.com/testrail-api2/start
http://docs.gurock.com/testrail-api2/accessing

TestRail is Copyright Gurock Software GmbH. See license.md for details.

=====

This module comprises classes to encapsulate (a) a TestRail interactive session
and (b) the API calls necessary for this repo to communicate results in the
required way. Further information is found in class and method docstrings.
"""

import base64
import logging
from time import sleep

import requests


class APIClient:
    """
    TestRail API session.

    Attributes:
    ===========

    base_url: str
      The "home" of the TestRail instance in question.

    local: bool
      Assign True if communicating with an instance of Testrail on localhost.
    """

    def __init__(self, base_url, local=False):
        self.user = ""
        self.password = ""
        if not base_url.endswith("/"):
            base_url += "/"
        if local:
            self.__url = base_url
        else:
            self.__url = base_url + "index.php?/api/v2/"

    def send_get(self, uri, filepath=None):
        """Issue a GET request (read) against the API.

        Args:
            uri: The API method to call including parameters, e.g. get_case/1.
            filepath: The path and file name for attachment download; used only
                for 'get_attachment/:attachment_id'.

        Returns:
            A dict containing the result of the request.
        """
        return self.__send_request("GET", uri, filepath)

    def send_post(self, uri, data):
        """Issue a POST request (write) against the API.

        Args:
            uri: The API method to call, including parameters, e.g. add_case/1.
            data: The data to submit as part of the request as a dict; strings
                must be UTF-8 encoded. If adding an attachment, must be the
                path to the file.

        Returns:
            A dict containing the result of the request.
        """
        return self.__send_request("POST", uri, data)

    def __send_request(self, method, uri, data):
        url = self.__url + uri

        auth = str(
            base64.b64encode(bytes("%s:%s" % (self.user, self.password), "utf-8")),
            "ascii",
        ).strip()
        headers = {"Authorization": "Basic " + auth}

        if method == "POST":
            if uri[:14] == "add_attachment":  # add_attachment API method
                files = {"attachment": (open(data, "rb"))}
                response = requests.post(url, headers=headers, files=files)
                files["attachment"].close()
            else:
                headers["Content-Type"] = "application/json"
                response = requests.post(url, headers=headers, json=data)
        else:
            headers["Content-Type"] = "application/json"
            response = requests.get(url, headers=headers)

        if response.status_code > 201:
            try:
                error = response.json()
            except (
                requests.exceptions.HTTPError
            ):  # response.content not formatted as JSON
                error = str(response.content)
            raise APIError(
                "TestRail API returned HTTP %s (%s)" % (response.status_code, error)
            )
        else:
            if uri[:15] == "get_attachment/":  # Expecting file, not JSON
                try:
                    open(data, "wb").write(response.content)
                    return data
                except FileNotFoundError:
                    return "Error saving attachment."
            else:
                try:
                    return response.json()
                except requests.exceptions.HTTPError:
                    return {}


class APIError(Exception):
    pass


class TestRail:
    """
    Object describing all necessary API endpoints (and related data handling
    methods) for test result reporting.

    Attributes:
    ===========

    host: str
      The "home" of the TestRail instance in question

    username: str
      The username of the TestRail user

    password: str
      The API key of the user in question

    local: bool
      Assign True if the instance of TestRail is hosted on localhost
    """

    def __init__(self, host, username, password, local=False):
        self.client = APIClient(host, local)
        self.client.user = username
        self.client.password = password

    # Public Methods

    def get_test_case(self, case_id):
        """Get a given Test Case"""
        return self.client.send_get(f"get_case/{case_id}")

    def get_suites(self, project_id):
        """Get all suites for project"""
        return self.client.send_get(f"get_suites/{project_id}")

    def update_cases_in_suite(self, suite_id, case_ids, **kwargs):
        """Given a suite and a list of test cases, update all listed
        test cases according to keyword args"""
        if not kwargs:
            return None
        return self.client.send_post(
            f"update_cases/{suite_id}", {"case_ids": case_ids, **kwargs}
        )

    def update_test_case(self, case_id, **kwargs):
        """Given a test case id, update according to keyword args"""
        if not kwargs:
            return None
        return self.client.send_post(f"update_case/{case_id}", kwargs)

    def create_test_run_on_plan_entry(
        self, plan_id, entry_id, config_ids, description=None, case_ids=None
    ):
        """
        Add a test run on an entry (subplan) associated with a plan.

        plan_id: (str | int)
          The id of the plan containing the entry

        entry_id: (str | int)
          The id of the entry on which to create the run

        config_ids: list[str | int]
          A list of confif ids to associate with the run

        description: str
          (Optional) The description of the run

        case_ids: list[str | int]
          (Optional) Case ids to associate with the run. If not
          passed, all cases associated with the entry will be added.
        """
        logging.info(f"run on plan entry configs {config_ids}")
        payload = {
            "config_ids": config_ids,
            "description": description,
            "include_all": not bool(case_ids),
        }
        if case_ids:
            payload["case_ids"] = case_ids
        logging.info(f"create run on entry payload:\n{payload}")
        return self.client.send_post(
            f"add_run_to_plan_entry/{plan_id}/{entry_id}", payload
        )

    def update_run_in_entry(self, run_id, **kwargs):
        """
        Given a run id and args, update a run in an entry (subplan).

        Valid args are listed here:
        https://support.testrail.com/hc/en-us/articles/7077711537684-Plans#updateruninplanentry
        """
        logging.info(f"update run in entry payload {kwargs}")
        return self.client.send_post(f"update_run_in_plan_entry/{run_id}", kwargs)

    def matching_milestone(self, testrail_project_id, milestone_name):
        """Given a project id and a milestone name, return the milestone object that matches"""
        milestones_response = self._get_milestones(
            testrail_project_id
        )  # returns reverse chronological order
        milestones = milestones_response["milestones"]
        logging.info(f"Found {len(milestones)} milestones")
        logging.info(milestones)
        for milestone in milestones:
            if milestone_name == milestone["name"]:
                logging.info(milestone)
                return milestone
        return None

    def matching_submilestone(self, milestone, submile_name):
        """Given a milestone object and a submilestone name, return the submile object that matches"""
        for submile in milestone["milestones"]:
            if submile_name == submile["name"]:
                return submile
        return None

    def matching_plan_in_milestone(self, testrail_project_id, milestone_id, plan_name):
        """Given a project id, a milestone id, and a plan name,
        return the plan object that matches"""
        plans = self._get_plans_in_milestone(testrail_project_id, milestone_id)
        for plan in plans:
            if plan_name in plan["name"]:
                return self._get_full_plan(plan.get("id"))
        return None

    def matching_custom_field(self, name):
        """Given a name, return the case_field object that matches (name or label)"""
        custom_fields = self._get_case_fields()
        for field in custom_fields:
            if name in field.get("name") or name in field.get("label"):
                return field
        return None

    def create_new_plan(
        self,
        testrail_project_id,
        name,
        description=None,
        milestone_id=None,
        entries=None,
    ):
        """
        Create a new test plan (on a milestone).

        Arguments:
        ==========

        testrail_project_id: (str | int)
          Id of the TestRail project

        name: str
          Name to give the new plan

        description: str
          (Optional) Description string for the plan

        milestone_id: (str | int)
          (Optional) Id of the milestone. If present the plan will attach to the milestone.

        entries: list[dict]
          (Optional) The runs or entries of the plan to add.
        """
        payload = {
            "name": name,
            "description": description,
            "milestone_id": milestone_id,
        }
        if entries:
            payload["entries"] = entries
        return self.client.send_post(f"/add_plan/{testrail_project_id}", payload)

    def create_new_plan_entry(
        self,
        plan_id,
        suite_id,
        name=None,
        description=None,
        case_ids=None,
        config_ids=None,
        runs=None,
    ):
        """
        Create a new entry (subplan) on a plan.

        Arguments:
        ==========

        plan_id: (str | int)
          Id of the plan

        suite_id: (str | int)
          Id of the suite to test in the entry

        description: str
          (Optional) Description string for the entry

        case_ids: list[str | int]
          (Optional) List of case ids to add to the entry.
          If blank, all cases in suite will be added.

        config_ids: list[str | int]
          (Optional) List of relevant config ids.

        runs: list[dict]
          (Optional) The runs or entries of the plan to add.
        """
        payload = {
            "suite_id": suite_id,
            "name": name,
            "description": description,
            "include_all": bool(case_ids),
        }
        if payload.get("include_all"):
            payload["case_ids"] = case_ids
        if payload.get("config_ids"):
            payload["config_ids"] = config_ids
        if runs:
            payload["runs"] = runs
        return self.client.send_post(f"/add_plan_entry/{plan_id}", payload)

    def matching_configs(self, testrail_project_id, config_group_id, config_name):
        """Given a project id, a config group id, and a config name, return the matching config object"""
        configs = self.client.send_get(f"/get_configs/{testrail_project_id}")
        matching_group = next(c for c in configs if c.get("id") == config_group_id)
        logging.info(f"matching group|| {matching_group}")
        cfgs = [
            c
            for c in matching_group.get("configs")
            if config_name == c.get("name").strip()
        ]
        return cfgs

    def add_config(self, config_group_id, name):
        """Add a config to a config group"""
        return self.client.send_post(f"/add_config/{config_group_id}", {"name": name})

    def get_run(self, run_id):
        """Return a run object by id"""
        return self.client.send_get(f"/get_run/{run_id}")

    def get_test_results(self, run_id):
        """Given a run id, return all test objects in that run"""
        results_rs_json = self.client.send_get(f"/get_tests/{run_id}")
        return results_rs_json.get("tests")

    def get_custom_fields(self):
        """Gets all fields of cases"""
        return self.client.send_get("get_case_fields/")

    def update_case_field(self, case_id, field_id, content):
        """Set the provided field with the new content"""
        data = {field_id: content}
        return self.client.send_post(f"update_case/{case_id}", data)

    def update_test_cases(
        self,
        testrail_project_id,
        testrail_run_id,
        testrail_suite_id,
        test_case_ids=[],
        status="passed",
    ):
        """Given a project id, a run id, and a suite id, for each case given a status,
        update the test objects with the correct status code"""
        status_key = {"passed": 1, "skipped": 3, "xfailed": 4, "failed": 5}
        if not test_case_ids:
            test_case_ids = [
                test_case.get("id")
                for test_case in self._get_test_cases(
                    testrail_project_id, testrail_suite_id
                )
            ]
        data = {
            "results": [
                {"case_id": test_case_id, "status_id": status_key.get(status)}
                for test_case_id in test_case_ids
            ]
        }
        return self._update_test_run_results(testrail_run_id, data)

    # Private Methods

    def _get_test_cases(self, testrail_project_id, testrail_test_suite_id):
        return self.client.send_get(
            f"get_cases/{testrail_project_id}&suite_id={testrail_test_suite_id}"
        )

    def _update_test_run_results(self, testrail_run_id, data):
        return self.client.send_post(f"add_results_for_cases/{testrail_run_id}", data)

    def _get_milestones(self, project_id, **filters):
        """
        Retrieves milestones for a given project with optional filters.

        Args:
            project_id (int): The ID of the project.
            **filters: Arbitrary keyword arguments representing API filters.

        Available Filters:
            is_completed (bool or int):
                - Set to True or 1 to return completed milestones only.
                - Set to False or 0 to return open (active/upcoming) milestones only.

            is_started (bool or int):
                - Set to True or 1 to return started milestones only.
                - Set to False or 0 to return upcoming milestones only.

            limit (int):
                - The number of milestones the response should return.
                - The default response size is 250 milestones.

            offset (int):
                - Where to start counting the milestones from (the offset).
                - Used for pagination.

        Returns:
            dict: The API response containing milestones.
        """

        if not project_id:
            raise ValueError("Project ID must be provided.")

        # Base endpoint
        endpoint = f"get_milestones/{project_id}"

        # Process filters
        if filters:
            # Convert boolean values to integers (API expects 1 or 0)
            for key in ["is_completed", "is_started"]:
                if key in filters and isinstance(filters[key], bool):
                    filters[key] = int(filters[key])

            # Build query parameters
            query_params = "&".join(f"{key}={value}" for key, value in filters.items())
            endpoint = f"{endpoint}&{query_params}"

        # Make API call
        return self.client.send_get(endpoint)

    def _get_plans_in_milestone(self, testrail_project_id, milestone_id):
        plan_obj = self.client.send_get(
            f"get_plans/{testrail_project_id}&milestone_id={milestone_id}"
        )
        return plan_obj.get("plans")

    def _get_full_plan(self, plan_id):
        return self.client.send_get(f"get_plan/{plan_id}")

    def _get_case_fields(self):
        return self.client.send_get("get_case_fields")

    def _retry_api_call(self, api_call, *args, max_retries=3, delay=5):
        """
        Retries the given API call up to max_retries times with a delay between attempts.

        :param api_call: The API call method to retry.
        :param args: Arguments to pass to the API call.
        :param max_retries: Maximum number of retries.
        :param delay: Delay between retries in seconds.
        """
        for attempt in range(max_retries):
            try:
                return api_call(*args)
            except Exception:
                if attempt == max_retries - 1:
                    raise  # Reraise the last exception
                sleep(delay)
