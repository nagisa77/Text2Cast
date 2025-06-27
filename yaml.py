import json
from typing import Any, Tuple, List

__all__ = ["safe_load", "dump"]


def safe_load(stream: Any) -> Any:
    """Parse a small subset of YAML. Fallback to JSON parsing first."""
    if hasattr(stream, 'read'):
        stream = stream.read()
    try:
        return json.loads(stream)
    except Exception:
        return _parse_yaml(stream.splitlines())[0]


def _parse_yaml(lines: List[str], indent: int = 0) -> Any:
    obj = {}
    idx = 0
    while idx < len(lines):
        line = lines[idx]
        if not line.strip() or line.lstrip().startswith('#'):
            idx += 1
            continue
        current_indent = len(line) - len(line.lstrip())
        if current_indent < indent:
            break
        if ':' not in line:
            idx += 1
            continue
        key, rest = line.strip().split(':', 1)
        if rest.strip() == "":
            sub, consumed = _parse_yaml(lines[idx + 1:], current_indent + 2)
            obj[key] = sub
            idx += consumed + 1
        else:
            value = rest.strip()
            if value.lower() in ("true", "false"):
                value = value.lower() == "true"
            else:
                try:
                    value = int(value)
                except ValueError:
                    pass
            obj[key] = value
            idx += 1
    return obj, idx

def dump(data: Any) -> str:
    return json.dumps(data)
