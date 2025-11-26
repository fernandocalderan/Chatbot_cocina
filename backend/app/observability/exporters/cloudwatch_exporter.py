from __future__ import annotations

import json
import queue
import threading
import time
from typing import Callable, Optional

try:
    import boto3
except Exception:
    boto3 = None


def cloudwatch_sink(log_group: str, log_stream: Optional[str] = None) -> Callable:
    """
    Returns a sink function for Loguru that ships logs to CloudWatch asynchronously.
    """
    if boto3 is None:
        def noop_sink(message):
            return
        return noop_sink

    client = boto3.client("logs")
    stream_name = log_stream or "app"
    q: queue.Queue = queue.Queue()

    def ensure_stream():
        try:
            client.create_log_stream(logGroupName=log_group, logStreamName=stream_name)
        except client.exceptions.ResourceAlreadyExistsException:
            pass

    ensure_stream()

    def worker():
        sequence_token = None
        while True:
            line = q.get()
            try:
                kwargs = {
                    "logGroupName": log_group,
                    "logStreamName": stream_name,
                    "logEvents": [
                        {"timestamp": int(time.time() * 1000), "message": str(line).strip()}
                    ],
                }
                if sequence_token:
                    kwargs["sequenceToken"] = sequence_token
                resp = client.put_log_events(**kwargs)
                sequence_token = resp.get("nextSequenceToken", sequence_token)
            except Exception:
                pass
            q.task_done()

    threading.Thread(target=worker, daemon=True).start()

    def sink(message):
        q.put(message)

    return sink
