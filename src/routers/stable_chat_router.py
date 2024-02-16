import json
import os
from typing import Annotated

import interpreter
import requests
from fastapi import BackgroundTasks, Form, HTTPException, File, APIRouter
from fastapi.responses import StreamingResponse


interpreter.model = f"azure/{os.environ['AZURE_API_DEPLOYMENT_ID']}"
interpreter.auto_run = True  # ユーザーの確認なしで生成されたコードを自動的に実行できるようになる
interpreter.api_base = os.environ["AZURE_API_BASE"]
interpreter.api_key = os.environ["AZURE_API_KEY"]
interpreter.api_version = os.environ["AZURE_API_VERSION"]
interpreter.debug_mode = False
interpreter.temperature = 0.7
interpreter.conversation_history = True
interpreter.context_window = int(os.environ["AZURE_CONTEXT_WINDOW"])


def build_prompt(input_file, output_filename, message):
    return f"""
ユーザの質問に回答してください。
{"入力ファイル: " + input_file if input_file else ""}
{"出力ファイル: " + output_filename if output_filename else ""}
===
{message}
"""


router = APIRouter()


@router.post("/chat")
def chat_endpoint(
        message: Annotated[str, Form()],
        uuid: Annotated[str, Form()],
        background_tasks: BackgroundTasks,
):
    output_filename = f"{uuid}_output.csv"

    message = build_prompt(None, output_filename, message)

    def event_stream():
        for result in interpreter.chat(message, stream=True):
            resultJson = json.dumps(result, ensure_ascii=False)
            yield f"data: {resultJson}\n\n"

    background_tasks.add_task(after_task, output_filename)

    try:
        return StreamingResponse(event_stream(), media_type="text/event-stream")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500)


@router.post("/chat/file")
def chat_endpoint_with_file(
        file: Annotated[bytes, File()],
        extension: Annotated[str, Form()],
        uuid: Annotated[str, Form()],
        message: Annotated[str, Form()],
        background_tasks: BackgroundTasks,
):
    input_filename = f"{uuid}_input.{extension}"
    output_filename = f"{uuid}_output.csv"

    message = build_prompt(input_filename, output_filename, message)

    # fileを一時的に保存する
    with open(input_filename, "wb") as f:
        f.write(file)

    # outputファイルを一時的に作成する
    with open(output_filename, "w") as f:
        f.write("")

    def event_stream():
        for result in interpreter.chat(message, stream=True):
            resultJson = json.dumps(result, ensure_ascii=False)
            yield f"data: {resultJson}\n\n"

    background_tasks.add_task(after_task, output_filename)

    try:
        return StreamingResponse(event_stream(), media_type="text/event-stream")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500)


post_url = os.environ["OUTPUT_UPLOAD_URL"]
headers = {
    "Authorization": f"Bearer {os.environ['OUTPUT_UPLOAD_TOKEN']}",
}


def after_task(output_filename):
    files = {"files": open(output_filename, "rb")}
    res = requests.post(post_url, files=files, headers=headers)
    print(res.text)
