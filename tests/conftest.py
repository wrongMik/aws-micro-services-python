import os
from typing import Any, TypeVar, Generator

import boto3
import pytest
from moto import mock_dynamodb
from fast_api_users.app import app
from boto3.resources.base import ServiceResource
from starlette.testclient import TestClient
from fast_api_users.dependencies import users, aws_services

from micro_aws.dynamodb_table import DynamoDBTable

T = TypeVar("T")

YieldFixture = Generator[T, None, None]


@pytest.fixture(scope="session")
def region_name() -> str:
    return "eu-west-1"


# https://github.com/spulec/moto/issues/889
# https://github.com/spulec/moto/issues/2634
@pytest.fixture(scope="session")
def aws_credentials() -> None:
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"


@pytest.fixture(scope="session")
def boto3_dynamodb_resource(aws_credentials: None, region_name: str) -> YieldFixture[ServiceResource]:
    with mock_dynamodb():
        yield boto3.resource("dynamodb", region_name)


@pytest.fixture(scope="session")
def users_table_name() -> str:
    return "users-table"


@pytest.fixture(scope="session")
def users_boto3_table(boto3_dynamodb_resource: ServiceResource, users_table_name: str) -> Any:
    return boto3_dynamodb_resource.create_table(
        TableName=users_table_name,
        KeySchema=[{"AttributeName": "user_id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "user_id", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )


@pytest.fixture(scope="session")
def users_table(users_boto3_table: Any) -> DynamoDBTable:
    return DynamoDBTable(users_boto3_table)


@pytest.fixture(scope="module")
def test_app() -> YieldFixture[TestClient]:
    client = TestClient(app)
    yield client


@pytest.fixture(scope="module")
def override_dependencies(
    users_table_name: str,
    users_table: DynamoDBTable,
    boto3_dynamodb_resource: ServiceResource,
) -> None:
    app.dependency_overrides = {
        users.users_table_name: lambda: users_table_name,
        users.users_table: lambda: users_table,
        aws_services.boto3_dynamodb_resource: lambda: boto3_dynamodb_resource,
    }


class LambdaContext:
    def __init__(self):
        self.function_name = "test-func"
        self.memory_limit_in_mb = 128
        self.invoked_function_arn = "arn:aws:lambda:eu-west-1:809313241234:function:test-func"
        self.aws_request_id = "52fdfc07-2182-154f-163f-5f0f9a621d72"

    def get_remaining_time_in_millis(self) -> int:
        return 1000
