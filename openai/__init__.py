class OpenAI:
    def __init__(self, *args, **kwargs):
        pass

    class Chat:
        class Completions:
            def create(self, *args, **kwargs):
                return None
        completions = Completions()
    chat = Chat()

    class Audio:
        class Speech:
            def create(self, *args, **kwargs):
                return type('resp', (), {'content': b''})
        speech = Speech()
    audio = Audio()
