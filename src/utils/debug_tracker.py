"""
Debug Tracker
Uses contextvars to track request-scoped debug information (tool usage, routing)
across the async application without passing objects around.
"""
from contextvars import ContextVar
from typing import List, Dict, Any, Optional
import time

# Thread-safe context variable
_debug_context: ContextVar[Optional["DebugTracker"]] = ContextVar("debug_context", default=None)

class DebugTracker:
    def __init__(self):
        self.start_time = time.time()
        self.logs: List[Dict[str, Any]] = []
        self.routing_info: str = "Unknown"
        self.language_detected: str = "Unknown"
        self.guardrail_status: str = "Passed"
        self.agents_triggered: List[str] = []

    def log_event(self, event_type: str, details: Dict[str, Any]):
        """Generic log event"""
        self.logs.append({
            "type": event_type,
            "timestamp_ms": int((time.time() - self.start_time) * 1000),
            **details
        })

    def get_info(self) -> Dict[str, Any]:
        """Return collected debug info"""
        return {
            "routing": self.routing_info,
            "language": self.language_detected,
            "guardrail": self.guardrail_status,
            "logs": self.logs,
            "total_time_ms": int((time.time() - self.start_time) * 1000)
        }

# ============================================================================
# Public API
# ============================================================================

def init_tracker():
    """Initialize a new tracker for the current context (request)"""
    _debug_context.set(DebugTracker())

def log_tool_usage(tool_name: str, input_str: str, output_str: str, metadata: Dict = None):
    """Log when a tool is used"""
    tracker = _debug_context.get()
    if tracker:
        # Truncate long outputs for display
        display_output = output_str[:500] + "..." if len(output_str) > 500 else output_str
        
        tracker.log_event("tool_usage", {
            "tool": tool_name,
            "input": input_str,
            "output": display_output,
            "metadata": metadata or {}
        })

def set_routing_info(route: str, lang: str):
    """Set the routing decision"""
    tracker = _debug_context.get()
    if tracker:
        tracker.routing_info = route
        tracker.language_detected = lang

def set_guardrail_status(status: str):
    """Set guardrail status"""
    tracker = _debug_context.get()
    if tracker:
        tracker.guardrail_status = status

def get_current_debug_info() -> Dict[str, Any]:
    """Get the final debug object"""
    tracker = _debug_context.get()
    return tracker.get_info() if tracker else {}

def get_tracker_instance():
    """Get the raw tracker instance for manual propagation (threading)"""
    return _debug_context.get()

def set_tracker_instance(tracker):
    """Set the raw tracker instance manually (used in threads)"""
    _debug_context.set(tracker)
