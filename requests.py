"""Minimal requests stub for offline tests."""

class Response:
    def __init__(self, data=None):
        self._data = data or {}

    def raise_for_status(self):
        pass

    def json(self):
        return self._data

post = lambda *a, **k: Response()
