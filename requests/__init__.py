class Response:
    def __init__(self):
        self.content = b''
    def raise_for_status(self):
        pass
    def json(self):
        return {}

def post(*args, **kwargs):
    return Response()
