import json

def dump(data, stream=None, **kwargs):
    text = json.dumps(data, indent=2)
    if stream is None:
        return text
    stream.write(text)

def safe_load(stream):
    if hasattr(stream, 'read'):
        text = stream.read()
    else:
        text = stream
    return json.loads(text)
