import time
from contextlib import contextmanager
from prometheus_client import Counter, Histogram, start_http_server

TOOL_USAGE_COUNTER = Counter(
    "agent_tool_usage_total",
    "Number of times each tool was called",
    ["tool"],
)

NODE_LATENCY = Histogram(
    "agent_node_latency_seconds",
    "Latency of each agent node in seconds",
    ["node"],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0],
)

QUERY_COUNTER = Counter(
    "agent_queries_total",
    "Total number of queries processed",
    ["status"],
)

QUERY_LATENCY = Histogram(
    "agent_query_latency_seconds",
    "End-to-end query latency",
    buckets=[1.0, 2.0, 5.0, 10.0, 30.0, 60.0],
)


@contextmanager
def track_time(histogram: Histogram, labels: dict):
    """Context manager to track execution time in a Prometheus histogram."""
    start = time.time()
    try:
        yield
    finally:
        elapsed = time.time() - start
        histogram.labels(**labels).observe(elapsed)


def start_metrics_server(port: int = 8000):
    """Start Prometheus metrics HTTP server."""
    start_http_server(port)
    print(f"Prometheus metrics available at http://localhost:{port}/metrics")
