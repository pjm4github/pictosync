"""
debug_trace.py

Debug instrumentation for tracking down crashes.
Enable by setting DEBUG_TRACE = True below.
"""

import sys
import traceback
from datetime import datetime
from functools import wraps

# Set to True to enable debug tracing
DEBUG_TRACE = True

# Set to True to trace paint events (very verbose)
TRACE_PAINT = False

# Log file (None for stderr only)
LOG_FILE = "pictosync_debug.log"

_log_file = None


def _get_log_file():
    global _log_file
    if LOG_FILE and _log_file is None:
        try:
            _log_file = open(LOG_FILE, "w", encoding="utf-8")
        except Exception:
            pass
    return _log_file


def trace(msg: str, category: str = "INFO"):
    """Print a trace message with timestamp."""
    if not DEBUG_TRACE:
        return
    if category == "PAINT" and not TRACE_PAINT:
        return

    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    line = f"[{timestamp}] [{category}] {msg}"

    print(line, file=sys.stderr, flush=True)

    log_file = _get_log_file()
    if log_file:
        try:
            log_file.write(line + "\n")
            log_file.flush()
        except Exception:
            pass


def trace_exception(msg: str = "Exception"):
    """Print exception info."""
    if not DEBUG_TRACE:
        return
    trace(f"{msg}: {traceback.format_exc()}", "ERROR")


def trace_call(category: str = "CALL"):
    """Decorator to trace function calls."""
    def decorator(func):
        if not DEBUG_TRACE:
            return func

        @wraps(func)
        def wrapper(*args, **kwargs):
            func_name = func.__qualname__
            trace(f">>> {func_name}", category)
            try:
                result = func(*args, **kwargs)
                trace(f"<<< {func_name}", category)
                return result
            except Exception as e:
                trace(f"!!! {func_name} raised {type(e).__name__}: {e}", "ERROR")
                raise
        return wrapper
    return decorator


def close_log():
    """Close log file."""
    global _log_file
    if _log_file:
        try:
            _log_file.close()
        except Exception:
            pass
        _log_file = None
