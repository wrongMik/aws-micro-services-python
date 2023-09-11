from typing import Any, Dict, List

import pytest

from tests.conftest import LambdaContext
from sqs_batch_processing.app import processor, lambda_handler


@pytest.fixture
def sqs_batch_processing_lambda_context() -> LambdaContext:
    return LambdaContext()


@pytest.fixture
def sqs_event() -> Dict[str, List[Dict[str, Any]]]:
    """
    Fake SQS event
    """
    return {
        "Records": [
            {
                "messageId": "059f36b4-87a3-44ab-83d2-661975830a7d",
                "receiptHandle": "AQEBwJnKyrHigUMZj6rYigCgxlaS3SLy0a",
                "body": '{"Message": "success"}',
                "attributes": {
                    "ApproximateReceiveCount": "1",
                    "SentTimestamp": "1545082649183",
                    "SenderId": "AIDAIENQZJOLO23YVJ4VO",
                    "ApproximateFirstReceiveTimestamp": "1545082649185",
                },
                "messageAttributes": {},
                "md5OfBody": "e4e68fb7bd0e697a0ae8f1bb342846b3",
                "eventSource": "aws:sqs",
                "eventSourceARN": "arn:aws:sqs:us-east-2:123456789012:my-queue",
                "awsRegion": "us-east-1",
            },
            {
                "messageId": "244fc6b4-87a3-44ab-83d2-361172410c3a",
                "receiptHandle": "AQEBwJnKyrHigUMZj6rYigCgxlaS3SLy0a",
                "body": "SGVsbG8sIHRoaXMgaXMgYSB0ZXN0Lg==",
                "attributes": {
                    "ApproximateReceiveCount": "1",
                    "SentTimestamp": "1545082649183",
                    "SenderId": "AIDAIENQZJOLO23YVJ4VO",
                    "ApproximateFirstReceiveTimestamp": "1545082649185",
                },
                "messageAttributes": {},
                "md5OfBody": "e4e68fb7bd0e697a0ae8f1bb342846b3",
                "eventSource": "aws:sqs",
                "eventSourceARN": "arn:aws:sqs:us-east-2:123456789012:my-queue",
                "awsRegion": "us-east-1",
            },
        ]
    }


def test_app_batch_partial_response(
    sqs_event: Dict[str, List[Dict[str, Any]]], sqs_batch_processing_lambda_context: LambdaContext
):
    # GIVEN
    processor_result = processor  # access processor for additional assertions
    successful_record = sqs_event["Records"][0]
    failed_record = sqs_event["Records"][1]
    expected_response = {"batchItemFailures": [{"itemIdentifier": failed_record["messageId"]}]}

    # WHEN
    ret = lambda_handler(sqs_event, sqs_batch_processing_lambda_context)

    # THEN
    assert ret == expected_response
    assert len(processor_result.fail_messages) == 1
    assert processor_result.success_messages[0] == successful_record
