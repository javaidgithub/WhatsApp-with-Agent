# WhatsApp with Agent (FastAPI + Redis + WhatsApp Web + Streamlit)

This repo contains:

- **`server.py`**: a FastAPI service that receives WhatsApp messages and pushes them into a **Redis queue** (`whatsapp:messages`). It also exposes an **SSE stream** (`/stream`) to consume queued messages in real time.
- **`GroupMessages.js`**: uses `whatsapp-web.js` to listen to **group** messages and POST them to FastAPI (`/ingest/group`).
- **`ChannelMessages.js`**: uses `puppeteer` to scrape **channel** messages in WhatsApp Web and POST them to FastAPI (`/ingest/channel`).
- **`assignment_agent.py`**: a Streamlit app that turns raw Urdu text into a polished Urdu news article using **Groq** or **OpenAI** (via LangChain) with a simple human review loop.

## Prerequisites

- **Python 3.11+** (works with 3.13)
- **Node.js 18+**
- **Docker Desktop** (for Redis)
- A WhatsApp account that can log into WhatsApp Web

## 1) Start Redis (Docker)

```bash
docker run -d --name redis-wa -p 6379:6379 redis
```

Useful commands:

```bash
# Start Redis (after reboot)
docker start redis-wa

# Stop Redis
docker stop redis-wa

# View live queue length
docker exec -it redis-wa redis-cli llen whatsapp:messages

# Flush the queue
docker exec -it redis-wa redis-cli del whatsapp:messages
```

## 2) Python setup (FastAPI + Streamlit agent)

Create a venv and install deps:

```bash
py -3.13 -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

Environment variables (create a local `.env` file — it is ignored by git):

- **`MODEL_PROVIDER`**: `groq` (default) or `openai`
- **`GROQ_API_KEY`**: required if `MODEL_PROVIDER=groq`
- **`OPENAI_API_KEY`**: required if `MODEL_PROVIDER=openai`

## 3) Node setup (WhatsApp ingesters)

Install Node dependencies:

```bash
npm install
```

## 4) Run the system

Start the FastAPI service (message ingest + queue + SSE):

```bash
uvicorn server:app --reload --port 8000
```

Run the group listener:

```bash
node .\GroupMessages.js
```

Run the channel scraper (opens a browser; you log in and open the channel manually):

```bash
node .\ChannelMessages.js
```

Run the Streamlit “Urdu News Research Agent” UI:

```bash
streamlit run assignment_agent.py
```

## API quick reference

- **POST** `/ingest/group`: queue a group message
- **POST** `/ingest/channel`: queue a channel message
- **GET** `/stream`: Server-Sent Events stream of messages from Redis
- **GET** `/queue/length`: current Redis queue length
- **DELETE** `/queue/flush`: flush the queue