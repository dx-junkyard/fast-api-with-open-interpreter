from typing import Annotated
from fastapi import BackgroundTasks, FastAPI, Form, HTTPException, File
from fastapi.responses import StreamingResponse
import interpreter
import os
from fastapi.middleware.cors import CORSMiddleware
import json
import requests

interpreter.model = f"azure/{os.environ['AZURE_API_DEPLOYMENT_ID']}"
interpreter.auto_run = True  # ユーザーの確認なしで生成されたコードを自動的に実行できるようになる
interpreter.api_base = os.environ["AZURE_API_BASE"]
interpreter.api_key = os.environ["AZURE_API_KEY"]
interpreter.api_version = os.environ["AZURE_API_VERSION"]
interpreter.debug_mode = True
interpreter.temperature = 0.7
interpreter.conversation_history = True


origins = ["http://localhost:3000"]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"status": "200"}


def build_prompt_with_input(input_file, output_filename, message):
    return f"""
以下の規則に従い、ユーザの質問に回答してください。従わない場合はペナルティが発生します。

(1)
変換した結果を出力ファイルに結果を書き込んでください。
入力ファイル: {input_file if input_file else "なし"}
出力ファイル: {output_filename if output_filename else "なし"}

(2) 
利用するライブラリは以下を推奨します。
- CSVファイルに関連する処理 : pandas
- エクセルファイルに関連する処理 : openpyxl
- PDFファイルに関連する処理 : pymupdf

(3)
必ず日本語で回答しなければなりません。

最後にユーザのメッセージを示します。
===
{message}
"""


def build_prompt(output_filename, message):
    return f"""
以下の規則に従い、ユーザの質問に回答してください。従わない場合はペナルティが発生します。

(1)
ファイル操作に関する質問の場合は、
「{output_filename}」のファイルを操作して、同じファイルに結果を書き込んでください。

(2) 
利用するライブラリは以下を推奨します。
- CSVファイルに関連する処理 : pandas
- エクセルファイルに関連する処理 : openpyxl
- PDFファイルに関連する処理 : pymupdf

(3)
必ず日本語で回答しなければなりません。

最後にユーザのメッセージを示します。
===
{message}
"""


@app.post("/chat")
def chat_endpoint(
    message: Annotated[str, Form()],
    uuid: Annotated[str, Form()],
    background_tasks: BackgroundTasks,
):
    output_filename = f"{uuid}_output.csv"

    message = build_prompt(output_filename, message)

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


@app.post("/chat/file")
def chat_endpoint_with_file(
    file: Annotated[bytes, File()],
    extension: Annotated[str, Form()],
    uuid: Annotated[str, Form()],
    message: Annotated[str, Form()],
    background_tasks: BackgroundTasks,
):
    input_filename = f"{uuid}_input.{extension}"
    output_filename = f"{uuid}_output.csv"

    message = build_prompt_with_input(input_filename, output_filename, message)

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
