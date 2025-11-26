from __future__ import annotations

import base64
import json
import queue
import threading
import time
from typing import Callable, Optional

import requests


def loki_sink(endpoint: str, basic_auth: Optional[str] = None) -> Callable:
    """
    Returns a sink function for Loguru that ships logs to Loki in the background.
    """
    q: queue.Queue = queue.Queue()

    auth_header = None
    if basic_auth:
        auth_header = base64.b64encode(basic_auth.encode()).decode()

    def worker():
        while True:
            line = q.get()
            try:
                payload = {
                    "streams": [
                        {
                            "stream": {"app": "chatbot"},
                            "values": [
                                [
                                    str(int(time.time() * 1e9)),
                                    line,
                                ]
                            ],
                        }
                    ]
                }
                headers = {"Content-Type": "application/json"}
                if auth_header:
                    headers["Authorization"] = f"Basic {auth_header}"
                requests.post(endpoint, headers=headers, data=json.dumps(payload), timeout=2)
            except Exception:
                pass
            q.task_done()

    threading.Thread(target=worker, daemon=True).start()

    def sink(message):
        q.put(str(message).strip())

    return sink
