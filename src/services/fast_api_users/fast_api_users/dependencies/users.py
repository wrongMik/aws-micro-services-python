import os
from functools import lru_cache

from fastapi import Depends
from boto3.resources.base import ServiceResource
from fast_api_users.dependencies.aws_services import boto3_sqs_resource, boto3_dynamodb_resource

from micro_aws.sqs_queue import SqsQueue
from micro_aws.dynamodb_table import DynamoDBTable


@lru_cache
def users_table_name() -> str:
    return os.getenv("TABLE_NAME", "invalid")


@lru_cache
def micro_sqs_queue_url() -> str:
    return os.getenv("QUEUE_URL", "invalid")


@lru_cache
def users_table(
    boto3_dynamodb_resource: ServiceResource = Depends(boto3_dynamodb_resource),
    table_name: str = Depends(users_table_name),
) -> DynamoDBTable:
    return DynamoDBTable.from_boto3_dynamodb_resource(
        boto3_dynamodb_resource=boto3_dynamodb_resource,
        table_name=table_name,
    )


@lru_cache
def micro_sqs_queue(
    boto3_sqs_resource: ServiceResource = Depends(boto3_sqs_resource),
    micro_sqs_queue_url: str = Depends(micro_sqs_queue_url),
) -> SqsQueue:
    return SqsQueue.from_boto3_sqs_resource(
        boto3_sqs_resource=boto3_sqs_resource,
        queue_url=micro_sqs_queue_url,
    )
