import yaml
import tempfile
from pathlib import Path
from unittest import mock
from text2cast.config import load_config
from text2cast.summarizer import input_to_brief


class DummyResp:
    def __init__(self, content):
        self.choices = [type('c', (), {'message': type('m', (), {'content': content})})]


@mock.patch('openai.OpenAI')
def test_input_to_brief(mock_openai):
    tmp = tempfile.TemporaryDirectory()
    input_path = Path(tmp.name) / 'input.txt'
    brief_path = Path(tmp.name) / 'brief.txt'
    input_path.write_text('hello')
    cfg_data = {
        'models': {'summary': 'model', 'script': 'model', 'tts': 'tts'},
        'paths': {
            'input': str(input_path),
            'brief': str(brief_path),
            'script': str(Path(tmp.name) / 'script.json'),
            'audio': str(Path(tmp.name) / 'audio')
        },
        'speaker_voice': {'0': 'a', '1': 'b'}
    }
    cfg_file = Path(tmp.name) / 'cfg.yaml'
    cfg_file.write_text(yaml.dump(cfg_data))
    mock_openai.return_value.chat.completions.create.return_value = DummyResp('summary')
    cfg = load_config(cfg_file)
    out = input_to_brief(cfg)
    assert out == 'summary'
    assert brief_path.read_text() == 'summary'
    tmp.cleanup()
