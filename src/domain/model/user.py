from interpreter import Interpreter


class User:
    name: str
    thread: Interpreter
    file: bytes | None

    def __init__(self, name: str, thread: Interpreter = None, file: bytes = None):
        self.name = name
        self.thread = thread
        self.file = file
