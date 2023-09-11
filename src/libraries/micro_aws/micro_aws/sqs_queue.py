from __future__ import annotations

import json
from typing import Any, Dict

from boto3.resources.base import ServiceResource

from micro_core.utils import AwsEncoder


class SqsQueue:
    """
    Implementation of the AWS SQS service
    (wrapper around boto3.session.Session.resource('sqs'))
    """

    def __init__(self, boto3_sqs_queue: Any):
        self._queue = boto3_sqs_queue

    @classmethod
    def from_boto3_sqs_resource(cls, boto3_sqs_resource: ServiceResource, queue_url: str) -> SqsQueue:
        """
        Args:
            boto3_sqs_resource (ServiceResource): the instance of a boto3.session.Session.resource('sqs')
            queue_url (str): the arn of the topic where publish the messages
        """
        return cls(boto3_sqs_resource.Queue(queue_url))

    def send_message(self, body: Dict[str, Any]) -> Dict[str, str]:
        """
        Reference:
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sqs.html#SQS.Queue.send_message
        """
        return self._queue.send_message(MessageBody=json.dumps(body, cls=AwsEncoder))
