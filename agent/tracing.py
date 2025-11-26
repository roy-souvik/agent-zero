from tracer_instance import tracer

def trace_operation(operation_name: str):
    """Decorator to automatically trace function calls"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            import time
            start = time.time()

            input_data = {"args": str(args)[:200], "kwargs": str(kwargs)[:200]}

            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start) * 1000
                tracer.add_trace(operation_name, input_data, {"result": str(result)[:500]}, duration_ms, "success")
                return result
            except Exception as e:
                duration_ms = (time.time() - start) * 1000
                tracer.add_trace(operation_name, input_data, {}, duration_ms, "error", str(e))
                raise
        return wrapper
    return decorator

# ==================== Observability Endpoints ====================

def get_traces_api(operation: str = None, limit: int = 100):
    """Get traces for API endpoint"""
    return tracer.get_traces(operation=operation, limit=limit)


def get_stats_api():
    """Get statistics for API endpoint"""
    return tracer.get_stats()


def export_traces_api(filepath: str = "traces.json"):
    """Export traces to JSON file"""
    tracer.export_json(filepath)
    return {"status": "Traces exported to " + filepath}