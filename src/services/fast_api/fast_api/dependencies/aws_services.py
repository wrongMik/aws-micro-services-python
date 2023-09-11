import logging
from functools import lru_cache

import boto3
from boto3.resources.base import ServiceResource

LOGGER = logging.getLogger()


@lru_cache
def boto3_dynamodb_resource() -> ServiceResource:
    return boto3.resource("dynamodb")
