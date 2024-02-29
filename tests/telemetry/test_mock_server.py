import pytest
import requests
from pytest_httpserver import HTTPServer


def test_json_client(httpserver: HTTPServer):
    httpserver.expect_request("/foobar").respond_with_json({"foo": "bar"})
    assert requests.get(httpserver.url_for("/foobar")).json() == {"foo": "bar"}
