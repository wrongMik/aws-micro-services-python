from __future__ import annotations

from typing import Any, Union, Optional

from botocore.response import StreamingBody
from boto3.resources.base import ServiceResource


class S3Bucket:
    '''
    Implementation of the AWS S3 service
    (wrapper around boto3.session.Session.resource('s3'))
    '''

    def __init__(self, boto3_s3_bucket: Any):
        self._bucket = boto3_s3_bucket

    @classmethod
    def from_boto3_s3_resource(cls, boto3_s3_resource: ServiceResource, bucket_name: str) -> S3Bucket:
        return cls(boto3_s3_resource.Bucket(bucket_name))

    def upload_content(self, key: str, body: Union[bytes, str], content_type: Optional[str] = None) -> Any:
        '''
        Returns:
            (S3.Object):

        Reference:
            https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Object
        '''
        args = {'Key': key, 'Body': body}
        if content_type:
            args['ContentType'] = content_type
        return self._bucket.put_object(**args)

    def get_content(self, key: str) -> StreamingBody:
        return self._bucket.Object(key).get()['Body']
