from typing import Dict

from interpreter import Interpreter

from src.domain.model.user import User

user_database: Dict[str, User] = {}


def upsert_thread(user_id: str, thread: Interpreter) -> None:
    if user_id in user_database:
        user_database[user_id].thread = thread
    else:
        user_database[user_id] = User(name=user_id, thread=thread)


def upsert_file(user_id: str, content: bytes) -> None:
    if user_id in user_database:
        user_database[user_id].file = content
    else:
        user_database[user_id] = User(name=user_id, file=content)


def get_user(user_id: str) -> User:
    return user_database[user_id]


def exist_thread(user_id: str) -> bool:
    return user_id in user_database and user_database[user_id].thread is not None
