from typing import Any, Union, Iterable


def dump(data: Any) -> str:
    lines = []
    for key, value in data.items():
        if isinstance(value, dict):
            lines.append(f"{key}:")
            for k, v in value.items():
                lines.append(f"  {k}: {v}")
        else:
            lines.append(f"{key}: {value}")
    return "\n".join(lines)


def safe_load(stream: Union[str, Iterable[str]]) -> Any:
    """Very small YAML loader supporting the subset used in tests."""
    if not isinstance(stream, str):
        stream = ''.join(stream.readlines())
    data = {}
    current = None
    for raw in stream.splitlines():
        line = raw.strip()
        if not line:
            continue
        if not line.startswith(' ') and line.endswith(':'):
            current = line[:-1]
            data[current] = {}
            continue
        if current is None:
            key, val = line.split(':', 1)
            data[key.strip()] = val.strip()
        else:
            key, val = line.split(':', 1)
            data[current][key.strip()] = val.strip()
    return data
