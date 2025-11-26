from __future__ import annotations

import threading
from collections import defaultdict, deque
from typing import Any, Deque, Dict, Tuple


class _Registry:
    def __init__(self):
        self.counters: Dict[str, Dict[Tuple[Tuple[str, str], ...], float]] = defaultdict(
            dict
        )
        self.gauges: Dict[str, Dict[Tuple[Tuple[str, str], ...], float]] = defaultdict(
            dict
        )
        self.histograms: Dict[
            str, Dict[Tuple[Tuple[str, str], ...], Deque[float]]
        ] = defaultdict(dict)
        self.lock = threading.Lock()
        self.hist_max_samples = 500

    def inc_counter(self, name: str, labels: Dict[str, Any], value: float = 1.0):
        key = tuple(sorted((k, str(v)) for k, v in labels.items()))
        with self.lock:
            self.counters[name][key] = self.counters[name].get(key, 0.0) + value

    def set_gauge(self, name: str, labels: Dict[str, Any], value: float):
        key = tuple(sorted((k, str(v)) for k, v in labels.items()))
        with self.lock:
            self.gauges[name][key] = float(value)

    def observe_histogram(self, name: str, labels: Dict[str, Any], value: float):
        key = tuple(sorted((k, str(v)) for k, v in labels.items()))
        with self.lock:
            dq = self.histograms[name].get(key)
            if dq is None:
                dq = deque(maxlen=self.hist_max_samples)
                self.histograms[name][key] = dq
            dq.append(float(value))

    def export_prometheus(self) -> str:
        lines: list[str] = []
        with self.lock:
            for name, series in self.counters.items():
                for label_key, val in series.items():
                    label_txt = ",".join(f'{k}="{v}"' for k, v in label_key)
                    lines.append(f'{name}{{{label_txt}}} {val}')
            for name, series in self.gauges.items():
                for label_key, val in series.items():
                    label_txt = ",".join(f'{k}="{v}"' for k, v in label_key)
                    lines.append(f'{name}{{{label_txt}}} {val}')
            for name, series in self.histograms.items():
                for label_key, vals in series.items():
                    if not vals:
                        continue
                    label_txt = ",".join(f'{k}="{v}"' for k, v in label_key)
                    # Exponer recuento y suma simple (no buckets)
                    lines.append(f'{name}_count{{{label_txt}}} {len(vals)}')
                    lines.append(f'{name}_sum{{{label_txt}}} {sum(vals)}')
        return "\n".join(lines)

    # Helpers for tests/alerts/SLO
    def get_counter(self, name: str, labels: Dict[str, Any]) -> float:
        key = tuple(sorted((k, str(v)) for k, v in labels.items()))
        return self.counters.get(name, {}).get(key, 0.0)

    def get_histogram(self, name: str, labels: Dict[str, Any]) -> list[float]:
        key = tuple(sorted((k, str(v)) for k, v in labels.items()))
        dq = self.histograms.get(name, {}).get(key, deque())
        return list(dq)


_REGISTRY = _Registry()


def inc_counter(name: str, labels: Dict[str, Any] | None = None, value: float = 1.0):
    _REGISTRY.inc_counter(name, labels or {}, value)


def observe_histogram(
    name: str, value: float, labels: Dict[str, Any] | None = None
):
    _REGISTRY.observe_histogram(name, labels or {}, value)


def set_gauge(name: str, value: float, labels: Dict[str, Any] | None = None):
    _REGISTRY.set_gauge(name, labels or {}, value)


def export_metrics() -> str:
    return _REGISTRY.export_prometheus()


def get_registry():
    return _REGISTRY
