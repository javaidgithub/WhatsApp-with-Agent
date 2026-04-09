import asyncio
import json
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import redis.asyncio as aioredis

app = FastAPI(title="WhatsApp Message Queue")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

REDIS_URL = "redis://localhost:6379"
QUEUE_KEY = "whatsapp:messages"

redis_client: aioredis.Redis = None


@app.on_event("startup")
async def startup():
    global redis_client
    redis_client = await aioredis.from_url(REDIS_URL, decode_responses=True)


@app.on_event("shutdown")
async def shutdown():
    await redis_client.close()


# ── Pydantic Models ────────────────────────────────────────────────────────────

class GroupMessage(BaseModel):
    source: str = "group"
    group_name: str
    sender: str
    message: str
    timestamp: Optional[float] = None


class ChannelMessage(BaseModel):
    source: str = "channel"
    channel_name: Optional[str] = "WhatsApp Channel"
    message: str
    timestamp: Optional[float] = None


# ── Ingest Endpoints ───────────────────────────────────────────────────────────

@app.post("/ingest/group")
async def ingest_group(msg: GroupMessage):
    """Called by GroupMessages.js on every group message received."""
    payload = msg.dict()
    payload["timestamp"] = payload.get("timestamp") or time.time()
    await redis_client.rpush(QUEUE_KEY, json.dumps(payload))
    return {"status": "queued", "source": "group"}


@app.post("/ingest/channel")
async def ingest_channel(msg: ChannelMessage):
    """Called by ChannelMessages.js on every channel message scraped."""
    payload = msg.dict()
    payload["timestamp"] = payload.get("timestamp") or time.time()
    await redis_client.rpush(QUEUE_KEY, json.dumps(payload))
    return {"status": "queued", "source": "channel"}


# ── SSE Stream ─────────────────────────────────────────────────────────────────

@app.get("/stream")
async def stream(request: Request):
    """
    Server-Sent Events endpoint.
    Frontend connects once and receives messages in real time as they
    are pushed into the Redis queue.
    """
    async def event_generator():
        yield "data: {\"type\":\"connected\"}\n\n"
        while True:
            if await request.is_disconnected():
                break
            # BLPOP blocks up to 2 s, returns (key, value) or None
            item = await redis_client.blpop(QUEUE_KEY, timeout=2)
            if item:
                _, raw = item
                yield f"data: {raw}\n\n"
            else:
                # heartbeat to keep connection alive
                yield ": ping\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


# ── Queue Stats ────────────────────────────────────────────────────────────────

@app.get("/queue/length")
async def queue_length():
    length = await redis_client.llen(QUEUE_KEY)
    return {"queue_length": length}


@app.delete("/queue/flush")
async def flush_queue():
    await redis_client.delete(QUEUE_KEY)
    return {"status": "flushed"}
