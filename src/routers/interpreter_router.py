import json
import os
from typing import Annotated

from fastapi import APIRouter, HTTPException, File, Form
from fastapi.responses import StreamingResponse

from src.config.logger import logger
from src.domain.model.filename import FileName
from src.repository.interpreter_client import create_interpreter
from src.repository.user_repository import get_user, upsert_user, exist_history

router = APIRouter(prefix="/api")


def build_prompt(filename: FileName | None, message: str, user_id) -> str:
    file_prompt = f"""
ユーザの回答文を考えるに当たり、過去のファイルの情報を参照する場合は、以下の情報を参考にしてください。
入力ファイル: {filename.input}
また、ユーザの回答文にファイルを添付する場合は、以下の情報を参考にしてください。
出力ファイル: {filename.output}
    """ if filename is not None else ""

    return f"""
ユーザの質問に回答してください。
{file_prompt}
ユーザ名: {user_id}
===
{message}
"""


@router.post("/chat")
def chat_endpoint(
        user_id: Annotated[str, Form()],
        message: Annotated[str, Form()],
        is_first: Annotated[bool, Form()],
):
    filename = None

    if exist_history(user_id) and get_user(user_id).file is not None:
        logger.info("file exists")
        filename = FileName()

        # fileを一時的に保存する
        with open(filename.input, "wb") as f:
            user = get_user(user_id)
            f.write(user.file)

        # outputファイルを一時的に作成する
        with open(filename.output, "w") as f:
            f.write("")

    message = build_prompt(filename, message, user_id)

    try:
        return StreamingResponse(
            event_stream(message, filename, user_id, is_first),
            media_type="text/event-stream")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500)


@router.post("/chat/file")
def chat_endpoint_with_file(
        file: Annotated[bytes, File()],
        user_id: Annotated[str, Form()],
        message: Annotated[str, Form()],
        is_first: Annotated[bool, Form()],
):
    filename = FileName()

    message = build_prompt(filename, message, user_id)

    # fileを一時的に保存する
    with open(filename.input, "wb") as f:
        f.write(file)

    # outputファイルを一時的に作成する
    with open(filename.output, "w") as f:
        f.write("")

    try:
        return StreamingResponse(
            event_stream(message, filename, user_id, is_first),
            media_type="text/event-stream")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500)


def event_stream(message: str,
                 filename: FileName | None,
                 user_id: str,
                 is_first: bool = False):
    session = create_interpreter()

    if exist_history(user_id) and not is_first:
        logger.info("thread exists")
        session.messages = get_user(user_id).messages

    for result in session.chat(message, stream=True, display=False):
        result_json = json.dumps(result, ensure_ascii=False)
        yield f"data: {result_json}\n\n"

    if filename is not None:
        with open(filename.output, "rb") as f:
            content = f.read()

        # contentの中身が空の場合は、inputファイルを保存する
        if len(content) == 0:
            with open(filename.input, "rb") as f:
                content = f.read()
        else:
            result_json = json.dumps({'file_id': filename.base}, ensure_ascii=False)
            yield f"data: {result_json}\n\n"

        upsert_user(user_id, session.messages, content)

        if os.path.exists(filename.input):
            os.remove(filename.input)

        if os.path.exists(filename.output):
            os.remove(filename.output)
