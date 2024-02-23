# fast-api-with-open-interpreter
OpenInterpreterの機能をFastAPIで提供するためのプロジェクトです。

## How to build and run

1. Build image

```bash
docker build -t fast-api-with-open-interpreter .
```

2. Run container

```bash
docker run -it --env-file=.env --rm --name fast-api-with-open-interpreter -p 8081:80 fast-api-with-open-interpreter
```

## How to deploy

## export requirements

```bash
$ poetry export -f requirements.txt --output requirements.txt --without-hashes
```

## push to docker hub

```bash
docker container commit <container-id> <hub-user>/<repo-name>[:<tag>]

docker tag <image-id> <repo-name>

docker push <hub-user>/<repo-name>[:<tag>]
```

## 開発に参加するためには？

fast-api-with-open-interpreter の開発に興味を持っていただき、ありがとうございます。
より良いアプリケーションの実現のため、機能改善やバグ修正の参加を募集しています。

皆さんが開発に参加するために、一連の開発の流れの例を記載します。

### 事前知識

本プロジェクトは、git-flow に基づいて開発を行います。
[A successful Git branching model » nvie.com](https://nvie.com/posts/a-successful-git-branching-model/)

原則、develop ブランチに向けて Pull Request を作成してください。
develop ブランチにマージされたコードは、リリースのタイミングで main ブランチにマージされます。

main ブランチにマージされたコードは、CODEOWNERS によってリリースパッケージが作成された後に、本番環境にデプロイされます。

### 開発の流れ

#### 1. issue の作成

機能改善の要望やバグの報告があれば、まずは報告をお願いします。

#### 2. リポジトリのフォーク

GitHub のリポジトリページで本プロジェクトをフォークしてください。

#### 3. プロダクトコードの修正

作成した issue に関して、プロダクトコードに変更を加えましょう。

#### 4. 変更したコードの push

変更したコードを push しましょう。
ブランチ名は「feature/issue-{IssueID}」のような命名規則としてください。

#### 5. PR の作成

develop ブランチに向けて PR を作成しましょう。CODEOWNERS のメンバーがレビューします。

#### 6. プルリクエストのレビュー

プルリクエストがレビューされ、問題がなければ本プロジェクトにマージされます。
CODEOWNERS から修正の指摘があった場合は、それに応じて変更を加えてください。