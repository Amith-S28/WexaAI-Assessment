"""
Statistical Engine for Graph Database Cloud Benchmarking.
Computes high-resolution percentiles (p50, p90, p95, p99), mean, stddev, variance, and throughput.
"""

from typing import List, Dict, Any, Optional
import numpy as np

class LatencyStats:
    """Computes and formats latency distributions and throughput metrics."""
    
    def __init__(self, latencies_ms: List[float], total_duration_sec: Optional[float] = None, cold_latency_ms: Optional[float] = None):
        self.raw = np.array(latencies_ms, dtype=np.float64) if latencies_ms else np.array([], dtype=np.float64)
        self.count = len(self.raw)
        self.cold_latency_ms = cold_latency_ms if cold_latency_ms is not None else (self.raw[0] if self.count > 0 else 0.0)
        self.total_duration_sec = total_duration_sec
        
        if self.count > 0:
            self.mean = float(np.mean(self.raw))
            self.stddev = float(np.std(self.raw))
            self.min = float(np.min(self.raw))
            self.max = float(np.max(self.raw))
            self.p50 = float(np.percentile(self.raw, 50))
            self.p90 = float(np.percentile(self.raw, 90))
            self.p95 = float(np.percentile(self.raw, 95))
            self.p99 = float(np.percentile(self.raw, 99))
        else:
            self.mean = self.stddev = self.min = self.max = 0.0
            self.p50 = self.p90 = self.p95 = self.p99 = 0.0

        if self.total_duration_sec and self.total_duration_sec > 0:
            self.qps = round(self.count / self.total_duration_sec, 2)
        else:
            self.qps = round(1000.0 / self.mean, 2) if self.mean > 0 else 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "count": self.count,
            "mean_ms": round(self.mean, 2),
            "stddev_ms": round(self.stddev, 2),
            "min_ms": round(self.min, 2),
            "max_ms": round(self.max, 2),
            "p50_ms": round(self.p50, 2),
            "p90_ms": round(self.p90, 2),
            "p95_ms": round(self.p95, 2),
            "p99_ms": round(self.p99, 2),
            "cold_ms": round(self.cold_latency_ms, 2),
            "qps": self.qps
        }

    def summary_str(self) -> str:
        return f"p50: {self.p50:.2f}ms | p95: {self.p95:.2f}ms | p99: {self.p99:.2f}ms | QPS: {self.qps}"
