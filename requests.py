class Response:
    def __init__(self, content=b''):
        self._content = content
    @property
    def content(self):
        return self._content
    def raise_for_status(self):
        pass

def post(*args, **kwargs):
    return Response()
