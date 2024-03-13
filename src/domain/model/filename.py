import uuid


class FileName:
    base: str
    input: str
    output: str

    def __init__(self):
        self.base = str(uuid.uuid4())
        self.input = f"{self.base}_input.tmp"
        self.output = f"{self.base}_output.tmp"
