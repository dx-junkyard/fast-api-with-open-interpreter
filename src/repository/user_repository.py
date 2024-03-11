from typing import Dict, List, Any

from src.domain.model.user import User

user_database: Dict[str, User] = {}


def upsert_user(user_id: str, messages: List[Any], content: bytes | None) -> None:
    if user_id in user_database:
        user_database[user_id].messages = messages
        user_database[user_id].file = content
    else:
        user_database[user_id] = User(name=user_id, messages=messages, file=content)


def get_user(user_id: str) -> User:
    return user_database[user_id]


def exist_history(user_id: str) -> bool:
    return user_id in user_database \
        and user_database[user_id].messages is not None \
        and len(user_database[user_id].messages) > 0
