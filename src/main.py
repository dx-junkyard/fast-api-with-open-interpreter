from typing import Annotated
from fastapi import BackgroundTasks, FastAPI, Form, HTTPException, File
from fastapi.responses import StreamingResponse
import interpreter
import os
from fastapi.middleware.cors import CORSMiddleware
import json
import requests
import tomllib

interpreter.model = f"azure/{os.environ['AZURE_API_DEPLOYMENT_ID']}"
interpreter.auto_run = True  # ユーザーの確認なしで生成されたコードを自動的に実行できるようになる
interpreter.api_base = os.environ["AZURE_API_BASE"]
interpreter.api_key = os.environ["AZURE_API_KEY"]
interpreter.api_version = os.environ["AZURE_API_VERSION"]
interpreter.debug_mode = False
interpreter.temperature = 0.7
interpreter.conversation_history = True
interpreter.context_window = int(os.environ["AZURE_CONTEXT_WINDOW"])


origins = ["http://localhost:3000"]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# pyproject.tomlファイルのパス
file_path = 'pyproject.toml'

# tomlファイルを読み込む
with open(file_path, 'rb') as toml_file:
    data = tomllib.load(toml_file)

# バージョン情報を取得
version = data['tool']['poetry']['version']


@app.get("/")
def read_root():
    return {"version": version}


def build_prompt_with_input(input_file, output_filename, message):
    return f"""
あなたは、pdf/エクセル/csvといった様々なファイルから表を抽出し、csvファイルに変換するスペシャリストです。
以下の規則に従い、ユーザの質問に回答してください。従わない場合はペナルティが発生します。

* 回答の最初は以下のように答えてください。
- Ver.{version}のAIが質問を承りました。

* 変換した結果を出力ファイルに結果を書き込んでください。
入力ファイル: {input_file if input_file else "なし"}
出力ファイル: {output_filename if output_filename else "なし"}

* 利用するpythonライブラリはすでにインストールされています。
- CSVファイルに関連するライブラリ : pandas
- エクセルファイルに関連するライブラリ : openpyxl
- PDFファイルに関連するライブラリ : pypdf
- PDFファイルから表を読み取るライブラリ : tabula-py

* 以下のライブラリは使ってはいけません。違反したら1億円のペナルティが発生します。
- PyPDF2

* 入力ファイルがテキストファイルの場合はnkfコマンドを使って文字コードを調べてください。
なお出力する文字コードはUTF-8にしなければなりません。

* pandasを使うときは以下の規則を守らなければなりません。
- read_csv関数を実行するときは、1行目をヘッダに指定してください
- to_csv関数を実行するときは、引数にquoting=csv.QUOTE_NONNUMERICをつけてください

* 必ず日本語で回答しなければなりません。

* ユーザに対して確認をとる必要はありません。計画を立てたらすぐ実行してください。

最後にユーザのメッセージを示します。
===
{message}
"""


def build_prompt(output_filename, message):
    return f"""
あなたは、pdf/エクセル/csvといった様々なファイルから表を抽出し、csvファイルに変換するスペシャリストです。
以下の規則に従い、ユーザの質問に回答してください。従わない場合はペナルティが発生します。

* 回答の最初は以下のように答えてください。
- Ver.{version}のAIが質問を承りました。

 * ファイル操作に関する質問の場合は、
「{output_filename}」のファイルを操作して、同じファイルに結果を書き込んでください。

* 利用するpythonライブラリはすでにインストールされています。
- CSVファイルに関連するライブラリ : pandas
- エクセルファイルに関連するライブラリ : openpyxl
- PDFファイルに関連するライブラリ : pypdf
- PDFファイルから表を読み取るライブラリ : tabula-py

* 以下のライブラリは使ってはいけません。違反したら1億円のペナルティが発生します。
- PyPDF2

* 以下のツールはすでにインストールされています
- java
- nkf

* pandasを使うときは以下の規則を守らなければなりません。
- read_csv関数を実行するときは、1行目をヘッダに指定してください
- to_csv関数を実行するときは、引数にquoting=csv.QUOTE_NONNUMERICをつけてください

* 入力ファイルがテキストファイルの場合は文字コードは文字コードをnkfコマンドを使って調べてください。
なお出力する文字コードはUTF-8にしなければなりません。

* 必ず日本語で回答しなければなりません。

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
