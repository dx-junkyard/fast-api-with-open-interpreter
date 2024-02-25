from typing import List, Any


class User:
    name: str
    messages: List[Any]
    file: bytes | None

    def __init__(self, name: str, messages=None, file: bytes = None):
        if messages is None:
            messages = []
        self.name = name
        self.messages = messages
        self.file = file
