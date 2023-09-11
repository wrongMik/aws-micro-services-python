import uuid
import logging
from http import HTTPStatus
from typing import Union, Optional

from fastapi import Query, Depends, APIRouter, status
from fastapi.responses import JSONResponse
from fast_api_users.dependencies.users import users_table, micro_sqs_queue
from fast_api_users.models.users_model import User, CreateUser, UserIterator, UserIDsIterator
from fast_api_users.models.message_model import Message

from micro_core.utils import pick_keys
from micro_aws.sqs_queue import SqsQueue
from micro_aws.dynamodb_table import DynamoDBTable

LOGGER = logging.getLogger()

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=Union[UserIterator, UserIDsIterator])
async def get_users(
    next_token: Optional[str] = Query(default=None),
    only_ids: Optional[bool] = Query(default=None),
    users_table: DynamoDBTable = Depends(users_table),
):
    iterator = users_table.get_items(next_token=next_token)
    if only_ids:
        return UserIDsIterator(user_ids=[item["user_id"] for item in iterator.items], next_token=iterator.next_token)
    # workaround to do not use the projection expression in dynamodb
    return UserIterator(
        users=pick_keys(
            dicts=iterator.items,
            keys=User.__fields__.keys(),
        ),
        next_token=iterator.next_token,
    )


@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: str,
    users_table: DynamoDBTable = Depends(users_table),
):
    user_item = users_table.get_item(hash_key_value=user_id)
    if user_item:
        return pick_keys(
            dicts=user_item,
            keys=User.__fields__.keys(),
        )
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"message": f"user with user_id: {user_id} not found"},
    )


@router.post(
    "/",
    status_code=HTTPStatus.CREATED,
    response_model=User,
)
async def create_user(
    user: CreateUser,
    users_table: DynamoDBTable = Depends(users_table),
    micro_sqs_queue: SqsQueue = Depends(micro_sqs_queue),
):
    user_id = str(uuid.uuid4())
    item = dict(user)
    item.update({"user_id": user_id})
    response = users_table.add_item(item=item)
    LOGGER.info("users_table.add_item(item=%s) -> response:%s", item, response)
    response = micro_sqs_queue.send_message(body={"action": "create-user", "user_id": user_id})
    LOGGER.info(
        'micro_sqs_queue.send_message(body={"action": "create-user", "user_id": %s}) -> response:%s',
        user_id,
        response,
    )
    return User(**item)


@router.delete("/{user_id}", response_model=Message)
async def delete_user(
    user_id: str,
    users_table: DynamoDBTable = Depends(users_table),
    micro_sqs_queue: SqsQueue = Depends(micro_sqs_queue),
):
    users_table.delete_item(hash_key_value=user_id)
    micro_sqs_queue.send_message(body={"action": "delete-user", "user_id": user_id})
    return Message(message=f"Delete user: {user_id} deleted")
