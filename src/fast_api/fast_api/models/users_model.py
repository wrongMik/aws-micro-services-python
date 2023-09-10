from typing import List, Optional

from pydantic import BaseModel


class BaseIterator(BaseModel):
    next_token: Optional[str] = None


class BaseUser(BaseModel):
    user_id: str


class User(BaseUser):
    name: str
    surname: str
    address: Optional[str] = None


class UserIDsIterator(BaseIterator):
    user_ids: List[str]


class UserIterator(BaseIterator):
    users: List[User]


class CreateUser(BaseModel):
    name: str
    surname: str
