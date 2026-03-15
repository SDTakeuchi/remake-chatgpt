# remake-chatgpt

LLM と対話するシンプルなチャットアプリ（学習用）。  
依存関係のインストール・実行は **Docker 内**で行い、ローカルにパッケージを置かずに動かせます。  
バックエンドは **Python（FastAPI + LangChain）** で、[agent-book](https://github.com/GenerativeAgents/agent-book)（『LangChain と LangGraph による RAG・AI エージェント［実践］入門』）と同じ技術・パッケージを優先して使用しています。

- **Python 3.10**（agent-book README の動作確認環境）
- **langchain-core / langchain-openai**（第4・5章と同じバージョン）
- **pydantic / httpx**（既知のエラー回避のため README 記載のピン）
- **FastAPI / Uvicorn**（第4章で使用）
- **OpenAI 互換 API** により、OpenAI 本家のほか **Gemini（Google AI）** なども利用可能（`config/env.yaml` の `base_url` と `model` で指定）。

## 前提

- Docker / Docker Compose が利用できること
- `config/env.yaml` に LLM API の設定があること（後述）

## 起動方法

1. **設定ファイルの準備**

   ```bash
   cp config/env.example.yaml config/env.yaml
   ```

   `config/env.yaml` を開き、`llm.api_key` など必要項目を記入する。  
   （`config/env.yaml` は .gitignore 済みでリポジトリに含めません）

2. **コンテナのビルドと起動**

   ```bash
   docker compose up --build
   ```

   - **フロントエンド**: http://localhost:3000 （ブラウザで開く）
   - **バックエンド API**: http://localhost:3001

## 開発

- バックエンドの依存（pip install）・実行はコンテナ内で行います。
- ソースを変更した場合は `docker compose up --build` で再ビルドしてください。
- ローカルに Python や npm を入れずに開発したい場合は、上記の手順だけで問題ありません。

## 構成

- `frontend/` … Next.js + React。チャット UI（メッセージ一覧・入力・ストリーミング表示）。
- `backend/` … Python + FastAPI + LangChain。POST `/chat` でストリーミング応答（SSE）。
- `config/env.yaml` … LLM API 設定（YAML）。Git にコミットしない。
- `config/env.example.yaml` … 設定のサンプル。リポジトリにコミットする。
