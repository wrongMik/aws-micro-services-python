import os
import json
import logging
from uuid import uuid4
from typing import Any, Dict, Callable

import boto3

from micro_core.utils import AwsEncoder
from micro_aws.s3_bucket import S3Bucket
from micro_aws.base_handler import BaseLambdaHandler
from micro_aws.dynamodb_table import DynamoDBTable
from micro_core.logging_config import configure_logging

configure_logging(
    service="sqs-users-processor",
    instance=str(uuid4()),
    level=os.getenv("LOG_LEVEL", "DEBUG"),
)

LOGGER = logging.getLogger()


class SQSUsersProcessor(BaseLambdaHandler):
    def __init__(
        self,
        users_table: DynamoDBTable,
        micro_s3_bucket: S3Bucket,
    ):
        self._users_table = users_table
        self._micro_s3_bucket = micro_s3_bucket

    @property
    def action_mapping(self) -> Dict[str, Callable[[str], None]]:
        return {
            "create-user": self._create_user_task,
            "delete-user": self._delete_user_task,
        }

    def handle_request(
        self,
        event: Dict[str, Any],
        context: Any,
        **kwargs: Any,
    ):
        """
        Entry point for the invocation of the lambda function.

        Reference:
            https://docs.aws.amazon.com/lambda/latest/dg/with-sqs.html
            https://docs.aws.amazon.com/lambda/latest/dg/python-context.html

        Args:
            event (Dict[str, Any]): Map of the entire sqs event
            context (object): Object that provides methods, properties and information about the invocation,
                function, and execution environment.
        """
        LOGGER.debug("Start function=%s, received event=%s", context.invoked_function_arn, event)
        for record in event.get("Records", []):
            message_body = json.loads(record.get("body"))
            user_id: str = message_body.get("user_id")
            try:
                action = message_body["action"]
                callable_action = self.action_mapping[action]
                callable_action(user_id)
            except Exception as exc:
                LOGGER.exception(exc)

    def _create_user_task(self, user_id: str):
        user_item = self._users_table.get_item(hash_key_value=user_id)
        object = self._micro_s3_bucket.upload_content(
            key=f"users/{user_id}.json",
            body=json.dumps(obj=user_item, cls=AwsEncoder),
            content_type="application/json",
        )
        LOGGER.info(f"Upload object: {object}")

    def _delete_user_task(self, user_id: str):
        response = self._micro_s3_bucket.delete_file(key=f"users/{user_id}.json")
        LOGGER.info(f"Delete object: {response}")


def create_lambda_handler(bucket_name: str, table_name: str) -> SQSUsersProcessor:
    boto3_s3_resource = boto3.resource("s3")
    boto3_dynamodb_resource = boto3.resource("dynamodb")
    return SQSUsersProcessor(
        users_table=DynamoDBTable.from_boto3_dynamodb_resource(
            boto3_dynamodb_resource=boto3_dynamodb_resource,
            table_name=table_name,
        ),
        micro_s3_bucket=S3Bucket.from_boto3_s3_resource(
            boto3_s3_resource=boto3_s3_resource,
            bucket_name=bucket_name,
        ),
    )


if os.getenv("AWS_EXECUTION_ENV"):
    handler = create_lambda_handler(
        bucket_name=os.getenv("BUCKET_NAME", "invalid"),
        table_name=os.getenv("TABLE_NAME", "invalid"),
    )
