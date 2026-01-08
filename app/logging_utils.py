
import json
from datetime import datetime

def log_event(**kwargs):
    record = {
        "ts": datetime.utcnow().isoformat() + "Z",
        **kwargs,
    }
    print(json.dumps(record))
