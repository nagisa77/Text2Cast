class Response:
    def __init__(self, *args, **kwargs):
        pass
    def raise_for_status(self):
        pass
    def json(self):
        return {}

def post(*args, **kwargs):
    return Response()
