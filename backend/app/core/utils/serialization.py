
import math
from typing import Any, Dict, List, Union

def sanitize_for_json(obj: Any) -> Any:
    """
    Recursively sanitize object to ensure it is JSON compliant.
    Converts NaN and Infinity to None.
    """
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    elif isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_json(v) for v in obj]
    elif isinstance(obj, tuple):
        return tuple(sanitize_for_json(v) for v in obj)
    return obj
