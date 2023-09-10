import uuid
import logging
from http import HTTPStatus
from typing import Union, Optional

from fastapi import Query, Depends, APIRouter, status
from fastapi.responses import JSONResponse

from micro_core.utils import pick_keys
from micro_core.services.dynamodb_table import DynamoDBTable

from fast_api.dependencies.users import users_table
from fast_api.models.users_model import User, CreateUser, UserIterator, UserIDsIterator
from fast_api.models.message_model import Message

LOGGER = logging.getLogger()

router = APIRouter(prefix='/users', tags=['users', 'user'])


@router.get('/', response_model=Union[UserIterator, UserIDsIterator])
async def get_users(
    next_token: Optional[str] = Query(default=None),
    only_ids: Optional[bool] = Query(default=None),
    users_table: DynamoDBTable = Depends(users_table),
):
    iterator = users_table.get_items(next_token=next_token)
    if only_ids:
        return UserIDsIterator(user_ids=[item['user_id'] for item in iterator.items], next_token=iterator.next_token)
    # workaround to do not use the prokection expression in dynamo
    return UserIterator(
        users=pick_keys(
            dicts=iterator.items,
            keys=User.__fields__.keys(),
        ),
        next_token=iterator.next_token,
    )


@router.get('/{user_id}', response_model=User)
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
    '/',
    status_code=HTTPStatus.CREATED,
    response_model=User,
)
async def create_user(
    user: CreateUser,
    users_table: DynamoDBTable = Depends(users_table),
):
    user_id = str(uuid.uuid4())
    item = dict(user).update({'user_id': user_id})
    users_table.add_item(item=item)
    return User(**item)


@router.delete('/{user_id}', response_model=Message)
async def delete_user(
    user_id: str,
    users_table: DynamoDBTable = Depends(users_table),
):
    users_table.delete_item(hash_key_value=user_id)
    return Message(message=f"Delete user: {user_id} deleted")
