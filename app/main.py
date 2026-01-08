
from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field, validator
import hmac, hashlib, time, uuid, re

from app.config import WEBHOOK_SECRET
from app.models import init_db, get_connection
from app.storage import insert_message, list_messages, stats
from app.logging_utils import log_event
from app.metrics import *

app = FastAPI()

@app.on_event("startup")
def startup():
    init_db()

class WebhookMessage(BaseModel):
    message_id: str = Field(..., min_length=1)
    from_: str = Field(..., alias="from")
    to: str
    ts: str
    text: str | None = Field(None, max_length=4096)

    @validator("from_", "to")
    def e164(cls, v):
        if not re.match(r"^\+\d+$", v):
            raise ValueError("invalid E.164")
        return v

    @validator("ts")
    def iso_ts(cls, v):
        if not v.endswith("Z"):
            raise ValueError("must be UTC Z")
        return v

@app.post("/webhook")
async def webhook(req: Request):
    start = time.time()
    request_id = str(uuid.uuid4())
    body = await req.body()
    sig = req.headers.get("X-Signature")

    expected = hmac.new(
        WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256,
    ).hexdigest()

    if not sig or not hmac.compare_digest(sig, expected):
        record_http("/webhook", 401)
        record_webhook("invalid_signature")
        log_event(
            level="ERROR",
            request_id=request_id,
            method="POST",
            path="/webhook",
            status=401,
            latency_ms=0,
            result="invalid_signature",
        )
        raise HTTPException(401, detail="invalid signature")

    msg = WebhookMessage.model_validate_json(body)
    result = insert_message(msg.model_dump(by_alias=True))

    latency = int((time.time() - start) * 1000)
    observe_latency(latency)
    record_http("/webhook", 200)
    record_webhook(result)

    log_event(
        level="INFO",
        request_id=request_id,
        method="POST",
        path="/webhook",
        status=200,
        latency_ms=latency,
        message_id=msg.message_id,
        dup=result == "duplicate",
        result=result,
    )

    return {"status": "ok"}

@app.get("/messages")
def messages(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    from_: str | None = Query(None, alias="from"),
    since: str | None = None,
    q: str | None = None,
):
    total, rows = list_messages(
        {"from_msisdn": from_, "since": since, "q": q},
        limit,
        offset,
    )

    return {
        "data": [
            {
                "message_id": r[0],
                "from": r[1],
                "to": r[2],
                "ts": r[3],
                "text": r[4],
            }
            for r in rows
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
    }

@app.get("/stats")
def get_stats():
    total, senders, first, last = stats()
    return {
        "total_messages": total,
        "senders_count": len(senders),
        "messages_per_sender": [
            {"from": s[0], "count": s[1]} for s in senders
        ],
        "first_message_ts": first,
        "last_message_ts": last,
    }

@app.get("/health/live")
def live():
    return {"status": "ok"}

@app.get("/health/ready")
def ready():
    try:
        conn = get_connection()
        conn.execute("SELECT 1")
        conn.close()
        if not WEBHOOK_SECRET:
            raise Exception()
        return {"status": "ready"}
    except Exception:
        raise HTTPException(503)

@app.get("/metrics", response_class=PlainTextResponse)
def metrics():
    return render_metrics()
