from __future__ import annotations

import random
import string
import logging
from typing import Any, Dict, List, Tuple, Union, Optional
from dataclasses import dataclass

from boto3.resources.base import ServiceResource
from boto3.dynamodb.conditions import (
    Attr,
    Equals,
    Between,
    LessThan,
    BeginsWith,
    GreaterThan,
    ConditionBase,
    LessThanEquals,
    GreaterThanEquals,
)

from micro_core.utils import decode, encode

LOGGER = logging.getLogger()


@dataclass(frozen=True)
class DynamoDBTableKeySchema:
    hash_key: str
    range_key: Optional[str]


@dataclass(frozen=True)
class DynamoDBTableIndex:
    name: str
    key_schema: DynamoDBTableKeySchema


@dataclass
class DynamoDBTableIterator:
    items: List[Dict[str, Any]]
    next_token: Optional[str] = None


@dataclass
class DynamoDBTableQueryParameters:
    index_name: str
    hash_key_condition: Equals
    range_key_condition: Optional[
        Union[
            Equals,
            BeginsWith,
            Between,
            LessThan,
            LessThanEquals,
            GreaterThan,
            GreaterThanEquals,
        ]
    ] = None


class DynamoDBTable:
    """
    Generic class to data access in AWS DynamoDB
    (wrapper around boto3.session.resource('dynamodb').Table(<table>))

    Reference:
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#table
    """

    def __init__(self, boto3_dynamodb_table: Any):
        self._table = boto3_dynamodb_table
        self._table_name = self._table.table_name
        self._table_arn = self._table.table_arn

        for key in self._table.key_schema:
            range_key = None
            if key["KeyType"] == "HASH":
                hash_key = key["AttributeName"]
            elif key["KeyType"] == "RANGE":
                range_key = key["AttributeName"]

        self._key_schema = DynamoDBTableKeySchema(hash_key, range_key)
        self._indexes: List[DynamoDBTableIndex] = []
        if self._table.global_secondary_indexes:
            for index in self._table.global_secondary_indexes:
                index_name = index["IndexName"]
                range_key = None
                for key in index["KeySchema"]:
                    if key["KeyType"] == "HASH":
                        hash_key = key["AttributeName"]
                    elif key["KeyType"] == "RANGE":
                        range_key = key["AttributeName"]
                self._indexes.append(
                    DynamoDBTableIndex(
                        name=index_name,
                        key_schema=DynamoDBTableKeySchema(
                            hash_key,
                            range_key,
                        ),
                    )
                )

    @classmethod
    def from_boto3_dynamodb_resource(cls, boto3_dynamodb_resource: ServiceResource, table_name: str) -> DynamoDBTable:
        """
        Args:
            boto3_dynamodb_resource (ServiceResource):
            table_name (str):
        """
        return cls(boto3_dynamodb_resource.Table(table_name))

    @property
    def table_name(self) -> str:
        """
        Represent the full table name of the DynamoDB table

        Reference:
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Table.table_name
        """
        return self._table_name

    @property
    def key_schema(self) -> DynamoDBTableKeySchema:
        """
        Represent the field used as hash key for the DynamoDB table

        Reference:
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Table.key_schema
        """
        return self._key_schema

    @property
    def indexes(self) -> List[DynamoDBTableIndex]:
        """
        Represent the global indexes of DynamoDB table, empty list in case no index are defined

        Reference:
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Table.global_secondary_indexes
        """
        return self._indexes

    def _create_key_arg(
        self,
        hash_key_value: str,
        range_key_value: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Create the key arg for operation on a single item

        Args:
            hash_key_value (str): the value of the hash key for the item we want to retrieve
            range_key_value (str): the value of the range key for the item we want to retrieve,
                needed only if range key defined

        Returns:
            key (Dict[str, str]): the dictionary to pass to as key argument

        Raises:
            Exception: the expected key has to be composite, only hash_key used
        """
        key = {self._key_schema.hash_key: hash_key_value}
        if self._key_schema.range_key:
            if not range_key_value:
                raise Exception(
                    f"Table={self.table_name} has a composite key. "
                    f"Value for range_key={self._key_schema.range_key} not specified"
                )
            key[self._key_schema.range_key] = range_key_value
        return key

    def get_item(
        self,
        hash_key_value: str,
        range_key_value: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get the item specified by the key

        Reference:
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Table.get_item

        Args:
            hash_key_value (str): the value of the hash key for the item we want to retrieve
            range_key_value (str): the value of the range key for the item we want to retrieve,
                needed only if range key defined

        Returns:
            (Dict[str, Any]): the dictionary that map the item we want to retrieve
        """
        LOGGER.debug("Get item from DynamoDB table %s for key=%s,%s", self.table_name, hash_key_value, range_key_value)
        key = self._create_key_arg(hash_key_value, range_key_value)
        response = self._table.get_item(Key=key)
        return response.get("Item", {})

    def get_items(
        self,
        next_token: Optional[str] = None,
        limit: Optional[int] = 100,
        query_parameters: Optional[DynamoDBTableQueryParameters] = None,
    ) -> DynamoDBTableIterator:
        """
        Get the list of items from the table, using
        boto3.session.resource('dynamodb').Table(<table>).scan() method or
        boto3.session.resource('dynamodb').Table(<table>).query() method depending on the optional parameter
        index_name

        Reference:
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Table.scan
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Table.query

        Args:
            next_token (Optional[str]):
            limit (Optional[int]):
            index_name (Optional[str]):

        Returns:
            (Dict[str, Any]): the dictionary that map the item we want to retrieve
        """
        LOGGER.debug(
            "Get items from DynamoDB table %s with token=%s,limit=%s,index_name=%s",
            self.table_name,
            next_token,
            limit,
            query_parameters,
        )
        get_items_args: Dict[str, Any] = {"Limit": limit}
        if next_token:
            get_items_args["ExclusiveStartKey"] = decode(next_token)

        if query_parameters:
            get_items_args["IndexName"] = query_parameters.index_name
            get_items_args["KeyConditionExpression"] = query_parameters.hash_key_condition
            if query_parameters.range_key_condition:
                get_items_args["KeyConditionExpression"] = (
                    get_items_args["KeyConditionExpression"] & query_parameters.hash_key_condition
                )
            response = self._table.query(**get_items_args)
        else:
            response = self._table.scan(**get_items_args)

        if "LastEvaluatedKey" in response:
            return DynamoDBTableIterator(
                items=response.get("Items"),
                next_token=encode(response["LastEvaluatedKey"]),
            )
        return DynamoDBTableIterator(items=response.get("Items"))

    def _condition_expression_on_key(self, exists: bool = False) -> ConditionBase:
        return Attr(self._key_schema.hash_key).exists() if exists else Attr(self._key_schema.hash_key).not_exists()

    def add_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add item to the table

        Reference:
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Table.put_item

        Args:
            item (Dict[str, Any]): the item to add into the table

        Returns:
            item (Dict[str, Any]): the dictionary represent the item just inserted

        Raises:
            Exception: if the item already exist
        """
        args = {"Item": item, "ConditionExpression": self._condition_expression_on_key()}
        try:
            response = self._table.put_item(**args)
            LOGGER.debug("Created new DynamoDB item response=%s", response)
        except self._table.meta.client.exceptions.ConditionalCheckFailedException as c_error:
            raise Exception(f"Table={self.table_name} already contains {item}") from c_error
        return item

    def _create_update_expressions(self, item: Dict[str, Any]) -> Tuple[str, Dict[str, Any], Dict[str, Any]]:
        """
        Creates the dynamodb update expression and expression attribute values
        used in the update_item_by_key

        Remarks:
            If the item args contains dotted (.) fields, those will be interpreted as nested map.
            If you try to update a map that do not exist the boto3.resource will raise a
                ValidationException.

        Args:
            item (Dict[str, Any]): dictionary with the new field to set

        Returns:
            (Tuple):
                update_expression (str): dynamodb update expression
                expression_attribute_names (Dict[str, Any]): dynamodb expression_attribute_names
                expression_attribute_values (Dict[str, Any]): dynamodb expression_attribute_values
        """

        def create_random_expression_attribute_name_key(field: str) -> str:
            letters = string.ascii_letters
            key = "".join(random.choice(letters) for _ in range(len(field)))
            return f"#{key}"

        update_expression = "SET "
        expression_attribute_names = {}
        expression_attribute_values = {}

        for field, value in item.items():
            update_expression_field = None
            # in this way we can define nested properties with the dot (.) and
            # update only the part specified as last word after the dot (.)
            if "." in field:
                field_splits = field.split(".")
                for field_split in field_splits:
                    key = create_random_expression_attribute_name_key(field_split)
                    expression_attribute_names[key] = field_split
                    update_expression_field = f"{update_expression_field}.{key}" if update_expression_field else key

                expression_attribute_values[":" + field_splits[-1]] = value
                update_expression += f"{update_expression_field}=:{field_splits[-1]},"

            else:
                key = create_random_expression_attribute_name_key(field)
                expression_attribute_names[key] = field
                update_expression_field = key
                expression_attribute_values[":" + field] = value
                update_expression += f"{update_expression_field}=:{field},"

        # remove the last comma
        update_expression = update_expression.rsplit(",", 1)[0]
        return (update_expression, expression_attribute_names, expression_attribute_values)

    def update_item_by_key(
        self,
        hash_key_value: str,
        updates: Dict[str, Any],
        range_key_value: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Update the item specified by the keys

        Reference:
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Table.update_item

        Args:
            hash_key_value (str): the value of the hash key for the item we want to retrieve
            updates (Dict[str, Any]): a dictionary with the fields we want to update
            range_key_value (str): the value of the range key for the item we want to retrieve,
                needed only if range key defined

        Returns:
            (Dict[str, Any]): the dictionary with the updated fields
        """
        LOGGER.debug(
            "Update item from DynamoDB table %s for key=%s,%s with updates=%s",
            self.table_name,
            hash_key_value,
            range_key_value,
            updates,
        )

        key = self._create_key_arg(hash_key_value, range_key_value)
        update_expression, expression_attribute_names, expression_attribute_values = self._create_update_expressions(
            item=updates
        )

        LOGGER.debug(
            "Update item from DynamoDB table %s for key=%s,%s with "
            "update_expression=%s, expression_attribute_names=%s, "
            "expression_attribute_values=%s",
            self.table_name,
            hash_key_value,
            range_key_value,
            update_expression,
            expression_attribute_names,
            expression_attribute_values,
        )

        args = {
            "Key": key,
            "UpdateExpression": update_expression,
            "ExpressionAttributeNames": expression_attribute_names,
            "ExpressionAttributeValues": expression_attribute_values,
            "ConditionExpression": self._condition_expression_on_key(exists=True),
        }

        self._table.update_item(**args)

        return updates

    def delete_item(
        self,
        hash_key_value: str,
        range_key_value: Optional[str] = None,
    ):
        """
        Delete the item specified by the keys

        Reference:
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Table.delete_item

        Args:
            hash_key_value (str): the value of the hash key for the item we want to retrieve
            range_key_value (str): the value of the range key for the item we want to retrieve,
                needed only if range key defined
        """
        LOGGER.debug(
            "Delete item from DynamoDB table %s for key=%s,%s", self.table_name, hash_key_value, range_key_value
        )
        try:
            key = self._create_key_arg(hash_key_value=hash_key_value, range_key_value=range_key_value)
            self._table.delete_item(
                Key=key,
                ConditionExpression=self._condition_expression_on_key(exists=True),
            )
        except self._table.meta.client.exceptions.ConditionalCheckFailedException as c_error:
            raise Exception(f"Table={self.table_name} does not contain {key}") from c_error
