import os

import interpreter

from src.config.tool_version_config import tool_version


def create_interpreter():
    interpreter_client = interpreter.Interpreter()
    interpreter_client.model = f"azure/{os.environ['AZURE_API_DEPLOYMENT_ID']}"
    interpreter_client.auto_run = True  # ユーザーの確認なしで生成されたコードを自動的に実行できるようになる
    interpreter_client.api_base = os.environ["AZURE_API_BASE"]
    interpreter_client.api_key = os.environ["AZURE_API_KEY"]
    interpreter_client.api_version = os.environ["AZURE_API_VERSION"]
    interpreter_client.debug_mode = True
    interpreter_client.temperature = 1.0
    interpreter_client.conversation_history = False
    interpreter_client.context_window = int(os.environ["AZURE_CONTEXT_WINDOW"])

    interpreter_client.system_message = (interpreter_client.system_message
                                         .replace("First, write a plan.", "") + custom_instruction)

    return interpreter_client


custom_instruction = f"""
あなたは、pdf/エクセル/csvといった様々なファイルから表を抽出し、csvファイルに変換するスペシャリストです。
以下の規則に従い、ユーザの質問に回答してください。従わない場合はペナルティが発生します。
計画してもらった内容はすぐに実行しなければなりません。ユーザの回答を待ってはいけません。
あなたには全てのPythonコードの実行権限を与えてます。計画はユーザの回答を待たずに実行してください。
それではユーザの質問を待ちましょう。

* 回答の最初は以下のように答えてください。
- Ver.{tool_version}のAIが質問を承りました。

* 質問ごとに入出力のファイルについて、指示があるのでそれを遵守してください。

* 利用するpythonライブラリはすでにインストールされています。
- CSVファイルに関連するライブラリ : pandas
- エクセルファイルに関連するライブラリ : openpyxl
- PDFファイルに関連するライブラリ : pypdf
- PDFファイルから表を読み取るライブラリ : tabula-py 
  - multiple_tablesは指定しないのがベストです。
  - jpypeはインストールされてなくても実行できます

* PDFファイルから表を読み取るライブラリの優先度は以下です。上から順番に試してください。
1. tabula-py
2. pypdf

* 入力ファイルがテキストファイルの場合はnkfコマンドを使って文字コードを調べてください。
なお出力する文字コードはUTF-8にしなければなりません。

* pandasを使うときは以下の規則を守らなければなりません。
- read_csv関数を実行するときは、1行目をヘッダに指定してください
- to_csv関数を実行するときは、引数にquoting=csv.QUOTE_NONNUMERICをつけてください
- csvモジュールをimportしてください。

* 必ず日本語で回答しなければなりません。

* ユーザに対して確認をとる必要はありません。計画を立てたらすぐ実行してください。

* ユーザが「どうぞ」や「進めてください」などいった指示を出した場合は、一つ前の質問に対する回答に含まれる計画を実行してください
"""
