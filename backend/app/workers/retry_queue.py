from __future__ import annotations

import heapq
import threading
import time
from typing import Any, Callable, Tuple

from loguru import logger
from sqlalchemy.orm import object_session


class RetryQueue:
    _instance: "RetryQueue" | None = None

    def __init__(self):
        self.queue: list[Tuple[float, int, Any, Callable]] = []
        self.lock = threading.Lock()
        self.thread: threading.Thread | None = None
        self.running = False
        self.backoff = [5, 20, 60]

    @classmethod
    def get_instance(cls) -> "RetryQueue":
        if cls._instance is None:
            cls._instance = cls()
            cls._instance.start()
        return cls._instance

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def schedule_retry(
        self,
        appointment: Any,
        callback: Callable,
        attempt: int = 0,
        delay_seconds: float = 0.0,
    ):
        run_at = time.time() + max(delay_seconds, 0.0)
        with self.lock:
            heapq.heappush(self.queue, (run_at, attempt, appointment, callback))

    def _mark_failed(self, appointment: Any):
        try:
            session = object_session(appointment)
            if session:
                appointment.reminder_status = "failed"
                session.add(appointment)
                session.commit()
        except Exception:
            pass

    def _run(self):
        while self.running:
            task = None
            sleep_for = 0.5
            now = time.time()
            with self.lock:
                if self.queue and self.queue[0][0] <= now:
                    task = heapq.heappop(self.queue)
                elif self.queue:
                    sleep_for = max(self.queue[0][0] - now, 0.1)
            if task:
                _, attempt, appointment, callback = task
                tenant_id = str(getattr(appointment, "tenant_id", None))
                appt_id = str(getattr(appointment, "id", None))
                try:
                    callback(appointment, attempt)
                    logger.info(
                        {
                            "tenant_id": tenant_id,
                            "lead_id": str(getattr(appointment, "lead_id", None)),
                            "appointment_id": appt_id,
                            "action": "reminder_retry",
                            "slot_start": getattr(appointment, "slot_start", None),
                            "timezone": getattr(
                                getattr(appointment, "slot_start", None), "tzinfo", None
                            ),
                            "source": "retry_queue",
                            "success": True,
                            "latency_ms": 0.0,
                            "attempt": attempt,
                        }
                    )
                except Exception as exc:
                    logger.warning(
                        {
                            "tenant_id": tenant_id,
                            "lead_id": str(getattr(appointment, "lead_id", None)),
                            "appointment_id": appt_id,
                            "action": "reminder_retry",
                            "slot_start": getattr(appointment, "slot_start", None),
                            "timezone": getattr(
                                getattr(appointment, "slot_start", None), "tzinfo", None
                            ),
                            "source": "retry_queue",
                            "success": False,
                            "latency_ms": 0.0,
                            "attempt": attempt,
                            "error": str(exc),
                        }
                    )
                    if attempt >= 2:
                        self._mark_failed(appointment)
                    else:
                        delay = self.backoff[min(attempt, len(self.backoff) - 1)]
                        self.schedule_retry(
                            appointment, callback, attempt + 1, delay_seconds=delay
                        )
                continue
            time.sleep(sleep_for)
