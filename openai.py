"""Minimal openai stub for offline tests."""

class OpenAI:
    def __init__(self, *args, **kwargs):
        pass

    class audio:
        class speech:
            @staticmethod
            def create(*args, **kwargs):
                pass

    class chat:
        class completions:
            @staticmethod
            def create(*args, **kwargs):
                pass
