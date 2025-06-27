import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import yaml
import tempfile
from pathlib import Path
from unittest import mock
from text2cast.config import load_config
from text2cast.summarizer import input_to_brief
import os

os.environ.setdefault('OPENAI_API_KEY', 'test')
os.environ.setdefault('VOLCENGINE_TOKEN', 'token')
os.environ.setdefault('VOLCENGINE_APP_ID', 'appid')


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
        'tts_engine': 'openai',
        'chat_engine': 'openai',
        'models': {
            'summary': {'openai': 'model'},
            'script': {'openai': 'model'},
            'tts': {'openai': 'tts'}
        },
        'paths': {
            'input': str(input_path),
            'brief': str(brief_path),
            'script': str(Path(tmp.name) / 'script.json'),
            'audio': str(Path(tmp.name) / 'audio')
        },
        'speaker_voice': {
            'openai': {'0': 'a', '1': 'b'}
        }
    }
    cfg_file = Path(tmp.name) / 'cfg.yaml'
    cfg_file.write_text(yaml.dump(cfg_data))
    mock_openai.return_value.chat.completions.create.return_value = DummyResp('summary')
    cfg = load_config(cfg_file)
    out = input_to_brief(cfg)
    assert out == 'summary'
    assert brief_path.read_text() == 'summary'
    tmp.cleanup()
