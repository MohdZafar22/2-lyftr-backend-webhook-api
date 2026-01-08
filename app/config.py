
import os

DATABASE_URL = os.getenv("DATABASE_URL")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

if DATABASE_URL is None:
    raise RuntimeError("DATABASE_URL env var not set")
