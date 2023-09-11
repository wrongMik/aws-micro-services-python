import json
from typing import Any, Dict

import pytest

from tests.conftest import LambdaContext
from powertools_hello_world.app import lambda_handler


@pytest.fixture
def hello_world_lambda_context() -> LambdaContext:
    return LambdaContext()


@pytest.fixture
def http_api_gw_event():
    """Generates HTTP API GW Event"""

    return {
        "version": "2.0",
        "routeKey": "GET /power/hello",
        "rawPath": "/power/hello",
        "rawQueryString": "",
        "cookies": [
            "awsccc=eyJlIjoxLCJwIjoxLCJmIjoxLCJhIjoxLCJpIjoiNDg5M2RiYTAtNDA0ZC00ZWJjLTg4MzktMWY0YmY4NDYxN2U0IiwidiI6IjEifQ=="
        ],
        "headers": {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en",
            "content-length": "0",
            "host": "piuxg04uu7.execute-api.eu-central-1.amazonaws.com",
            "sec-ch-ua": '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
            "x-amzn-trace-id": "Root=1-6503557d-72916f0c5ca2ac7d6a10133c",
            "x-forwarded-for": "77.2.45.94",
            "x-forwarded-port": "443",
            "x-forwarded-proto": "https",
        },
        "requestContext": {
            "accountId": "668174223132",
            "apiId": "piuxg04uu7",
            "domainName": "piuxg04uu7.execute-api.eu-central-1.amazonaws.com",
            "domainPrefix": "piuxg04uu7",
            "http": {
                "method": "GET",
                "path": "/power/hello",
                "protocol": "HTTP/1.1",
                "sourceIp": "77.2.45.94",
                "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
            },
            "requestId": "LQpLngCUFiAEMDQ=",
            "routeKey": "GET /power/hello",
            "stage": "$default",
            "time": "14/Sep/2023:18:48:29 +0000",
            "timeEpoch": 1694717309283,
        },
        "isBase64Encoded": False,
    }


# https://docs.pytest.org/en/7.1.x/how-to/capture-stdout-stderr.html#accessing-captured-output-from-a-test-function
# capsys is a built-in pytest fixture
def capture_metrics_output_multiple_emf_objects(capsys):
    return [json.loads(line.strip()) for line in capsys.readouterr().out.split("\n") if line]


def test_lambda_handler(http_api_gw_event: Dict[str, Any], hello_world_lambda_context: LambdaContext, capsys):
    result = lambda_handler(http_api_gw_event, hello_world_lambda_context)

    cold_start_blob, custom_metrics_blob = capture_metrics_output_multiple_emf_objects(capsys)
    assert cold_start_blob["ColdStart"] == [1.0]
    assert cold_start_blob["function_name"] == "test-func"
    assert "SuccessfulGreetings" in custom_metrics_blob

    data = json.loads(result["body"])
    assert result["statusCode"] == 200
    assert "message" in result["body"]
    assert data["message"] == "hello unknown!"
