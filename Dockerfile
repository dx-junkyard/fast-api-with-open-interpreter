FROM --platform=linux/x86_64 python:3.13.0

# 必要なツールをインストール
RUN apt-get update &&  \
    apt-get install -y nkf &&  \
    apt-get install -y default-jdk

# poetryをインストール
RUN pip install poetry
RUN poetry config virtualenvs.create false

# 必要なファイルをコピー
COPY pyproject.toml poetry.lock ./
COPY src/ ./src
COPY history/ ./history

# 依存関係をインストールする
RUN poetry install

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80"]