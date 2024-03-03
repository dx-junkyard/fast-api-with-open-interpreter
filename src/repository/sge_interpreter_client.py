import os

import interpreter


def create_interpreter():
    interpreter_client = interpreter.Interpreter()
    interpreter_client.model = f"azure/{os.environ['AZURE_API_DEPLOYMENT_ID']}"
    interpreter_client.auto_run = True  # ユーザーの確認なしで生成されたコードを自動的に実行できるようになる
    interpreter_client.api_base = os.environ["AZURE_API_BASE"]
    interpreter_client.api_key = os.environ["AZURE_API_KEY"]
    interpreter_client.api_version = os.environ["AZURE_API_VERSION"]
    interpreter_client.debug_mode = False
    interpreter_client.temperature = 0.7
    interpreter_client.conversation_history = True
    interpreter_client.context_window = int(os.environ["AZURE_CONTEXT_WINDOW"])

    interpreter_client.system_message = (interpreter_client.system_message
                                         .replace("First, write a plan.", "") + custom_instruction)

    return interpreter_client


# search generative experience prompt
custom_instruction = f"""
あなたは、検索クエリを解釈し、ユーザが知りたい情報を提供するスペシャリストです。
ユーザは「東京 観光」のような検索クエリを入力します。
あなたは、その検索クエリに対して持っている知識をもとに、回答内容を作成してください。
例えば、「東京 観光」のような検索クエリに対しては、東京の観光地の情報を提供してください。
"""