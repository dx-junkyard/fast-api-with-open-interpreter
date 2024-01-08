from typing import Annotated
from fastapi import FastAPI, Form, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
import interpreter
import os
from fastapi.middleware.cors import CORSMiddleware
import json
import uuid

interpreter.model = f"azure/{os.environ['AZURE_API_DEPLOYMENT_ID']}"
interpreter.auto_run = True  # ユーザーの確認なしで生成されたコードを自動的に実行できるようになる
interpreter.api_base = os.environ["AZURE_API_BASE"]
interpreter.api_key = os.environ["AZURE_API_KEY"]
interpreter.api_version = os.environ["AZURE_API_VERSION"]
interpreter.debug_mode = False
interpreter.temperature = 1.0
interpreter.conversation_history = False


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


def build_prompt(input_file, output_filename, message):
    return f"""
ユーザの質問に回答してください。なお入力ファイルが指定されている場合は、入力ファイルを読み込み、
変換した結果を出力ファイルに結果を書き込んでください。
入力ファイル: {input_file if input_file else "なし"}
出力ファイル: {output_filename if output_filename else "なし"}
メッセージは下記です。
===
{message}
"""


@app.post("/chat")
def chat_endpoint(
    file: Annotated[bytes, File()],
    extension: Annotated[str, Form()],
    message: Annotated[str, Form()],
):
    uid = uuid.uuid4()
    input_filename = f"{uid}_input.{extension}"
    output_filename = f"{uid}_output.csv"

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

            if "end_of_message" in result and result["end_of_message"]:
                with open(output_filename, "r") as f:
                    lines = f.readlines()
                    print(len(lines))

            yield f"data: {resultJson}\n\n"

    try:
        return StreamingResponse(event_stream(), media_type="text/event-stream")
    except Exception as e:
        print(e)
        # tenpファイルを削除する
        os.remove(input_filename)
        os.remove(output_filename)
        raise HTTPException(status_code=500)
