class InMemoryTracer:
    """Simple in-memory tracer for observability without external dependencies"""

    def __init__(self, max_traces: int = 10000):
        self.traces = []
        self.max_traces = max_traces
        self.lock = threading.Lock()

    def add_trace(self, operation: str, input_data: dict, output_data: dict,
                  duration_ms: float, status: str = "success", error: str = None):
        """Add a trace to memory"""
        with self.lock:
            trace = {
                "timestamp": datetime.utcnow().isoformat(),
                "operation": operation,
                "input": input_data,
                "output": output_data,
                "duration_ms": duration_ms,
                "status": status,
                "error": error
            }
            self.traces.append(trace)

            # Keep memory bounded
            if len(self.traces) > self.max_traces:
                self.traces = self.traces[-self.max_traces:]

    def get_traces(self, operation: str = None, limit: int = 100):
        """Retrieve traces"""
        with self.lock:
            result = self.traces
            if operation:
                result = [t for t in result if t["operation"] == operation]
            return result[-limit:]

    def get_stats(self):
        """Get statistics about traces"""
        with self.lock:
            if not self.traces:
                return {}

            stats = defaultdict(lambda: {"count": 0, "total_duration": 0, "errors": 0})

            for trace in self.traces:
                op = trace["operation"]
                stats[op]["count"] += 1
                stats[op]["total_duration"] += trace["duration_ms"]
                if trace["status"] == "error":
                    stats[op]["errors"] += 1

            # Calculate averages
            for op in stats:
                if stats[op]["count"] > 0:
                    stats[op]["avg_duration"] = stats[op]["total_duration"] / stats[op]["count"]

            return dict(stats)

    def export_json(self, filepath: str):
        """Export traces to JSON file"""
        with self.lock:
            with open(filepath, 'w') as f:
                json.dump(self.traces, f, indent=2)

    def clear(self):
        """Clear all traces"""
        with self.lock:
            self.traces = []
