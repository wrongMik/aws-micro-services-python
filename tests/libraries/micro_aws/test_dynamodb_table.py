import uuid
import random
import string
from typing import Any
from datetime import datetime

import pytest

from micro_aws.dynamodb_table import DynamoDBTable, DynamoDBTableIndex, DynamoDBTableKeySchema


def random_friendly_name(length: int = 10) -> str:
    letters = string.ascii_letters
    return "".join(random.choice(letters) for i in range(length))


def create_faker_user_item():
    user_id = str(uuid.uuid4())
    return {
        "user_id": user_id,
        "name": random_friendly_name(),
        "surname": random_friendly_name(),
        "created_at": datetime.now().isoformat(),
    }


class TestDynamoDBTable:
    @pytest.fixture(autouse=True)
    def _setup(
        self,
        users_boto3_table: Any,
        users_table: DynamoDBTable,
    ):
        self._boto3_dynamodb_table = users_boto3_table
        self._dynamodb_table = users_table

    def test_table_properties(self, users_table_name: str):
        assert self._dynamodb_table.table_name == users_table_name
        assert isinstance(self._dynamodb_table.key_schema, DynamoDBTableKeySchema)
        assert isinstance(self._dynamodb_table.indexes, list)
        for index in self._dynamodb_table.indexes:
            assert isinstance(index, DynamoDBTableIndex)

    def test_get_item(self):
        # Given an item
        fake_item = create_faker_user_item()
        # When the item is inserted in the table
        self._boto3_dynamodb_table.put_item(Item=fake_item)
        # Then I'm able to retrieve it with the wrapper class
        item = self._dynamodb_table.get_item(hash_key_value=fake_item["user_id"])
        assert isinstance(item, dict)
        assert fake_item == item
