# agent-book 準拠: Python 3.10（README 動作確認環境）+ LangChain
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY config.py chat.py main.py schemas.py ./

EXPOSE 3001
ENV PORT=3001

# 設定は docker-compose で /app/config にマウントし CONFIG_PATH を渡す
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3001"]
