from datetime import datetime
from typing import Any


def serialize_value(value: Any) -> Any:
    """Serialize a value to JSON-compatible format.

    Args:
        value: Value to serialize

    Returns:
        JSON-serializable value
    """
    if isinstance(value, (str, int, float, bool)):
        return value
    elif value is None:
        return None
    elif isinstance(value, datetime):
        return value.isoformat()
    # Convert any other non-built-in type to string
    return str(value)
