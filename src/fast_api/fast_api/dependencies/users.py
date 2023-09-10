import os
from functools import lru_cache

from fastapi import Depends
from boto3.resources.base import ServiceResource

from micro_core.services.dynamodb_table import DynamoDBTable

from fast_api.dependencies.aws_services import boto3_dynamodb_resource


@lru_cache
def users_table_name() -> str:
    return os.getenv('TABLE_NAME', 'users-table')


@lru_cache
def users_table(
    boto3_dynamodb_resource: ServiceResource = Depends(boto3_dynamodb_resource),
    table_name: str = Depends(users_table_name),
) -> DynamoDBTable:
    return DynamoDBTable.from_boto3_dynamodb_resource(
        boto3_dynamodb_resource=boto3_dynamodb_resource,
        table_name=table_name,
    )
