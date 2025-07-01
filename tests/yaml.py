"""Very small YAML subset implementation used for tests."""

import json
from typing import Any


def dump(data: Any) -> str:
    """Serialize *data* to a JSON string as a YAML subset."""
    return json.dumps(data)


def safe_load(stream: Any) -> Any:
    """Parse a JSON string produced by :func:`dump`."""
    if hasattr(stream, 'read'):
        return json.load(stream)
    return json.loads(stream)
