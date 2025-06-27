import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import yaml
import json
import tempfile
from pathlib import Path
from unittest import mock
from text2cast.config import load_config
from text2cast.script_generator import brief_to_script
from text2cast.utils import wash_json
import os

os.environ.setdefault('OPENAI_API_KEY', 'test')
os.environ.setdefault('VOLCENGINE_TOKEN', 'token')
os.environ.setdefault('VOLCENGINE_APP_ID', 'appid')


class DummyResp:
    def __init__(self, content):
        self.choices = [type('c', (), {'message': type('m', (), {'content': content})})]


@mock.patch('openai.OpenAI')
def test_brief_to_script(mock_openai):
    tmp = tempfile.TemporaryDirectory()
    brief_path = Path(tmp.name) / 'brief.txt'
    script_path = Path(tmp.name) / 'script.json'
    brief_path.write_text('brief')
    cfg_data = {
        'tts_engine': 'openai',
        'chat_engine': 'openai',
        'models': {
            'summary': {'openai': 'model'},
            'script': {'openai': 'model'},
            'tts': {'openai': 'tts'}
        },
        'paths': {
            'input': str(Path(tmp.name)/'input.txt'),
            'brief': str(brief_path),
            'script': str(script_path),
            'audio': str(Path(tmp.name)/'audio')
        },
        'speaker_voice': {'openai': {'0': 'a', '1': 'b'}}
    }
    cfg_file = Path(tmp.name) / 'cfg.yaml'
    cfg_file.write_text(yaml.dump(cfg_data))
    script_content = '[{"speaker": "0", "text": "hello"}]'
    mock_openai.return_value.chat.completions.create.return_value = DummyResp(script_content)
    cfg = load_config(cfg_file)
    out = brief_to_script(cfg)
    assert out == json.loads(script_content)
    assert json.loads(script_path.read_text()) == json.loads(script_content)
    tmp.cleanup()


@mock.patch('openai.OpenAI')
def test_brief_to_script_markdown(mock_openai):
    tmp = tempfile.TemporaryDirectory()
    brief_path = Path(tmp.name) / 'brief.txt'
    script_path = Path(tmp.name) / 'script.json'
    brief_path.write_text('brief')
    cfg_data = {
        'tts_engine': 'openai',
        'chat_engine': 'openai',
        'models': {
            'summary': {'openai': 'model'},
            'script': {'openai': 'model'},
            'tts': {'openai': 'tts'}
        },
        'paths': {
            'input': str(Path(tmp.name)/'input.txt'),
            'brief': str(brief_path),
            'script': str(script_path),
            'audio': str(Path(tmp.name)/'audio')
        },
        'speaker_voice': {'openai': {'0': 'a', '1': 'b'}}
    }
    cfg_file = Path(tmp.name) / 'cfg.yaml'
    cfg_file.write_text(yaml.dump(cfg_data))
    base = '[{"speaker": "0", "text": "hello"}]'
    script_content = f"```json\n{base}\n```"
    mock_openai.return_value.chat.completions.create.return_value = DummyResp(script_content)
    cfg = load_config(cfg_file)
    out = brief_to_script(cfg)
    assert out == json.loads(base)
    assert json.loads(script_path.read_text()) == json.loads(base)
    tmp.cleanup()


@mock.patch('openai.OpenAI')
def test_brief_to_script_plain_block(mock_openai):
    tmp = tempfile.TemporaryDirectory()
    brief_path = Path(tmp.name) / 'brief.txt'
    script_path = Path(tmp.name) / 'script.json'
    brief_path.write_text('brief')
    cfg_data = {
        'tts_engine': 'openai',
        'chat_engine': 'openai',
        'models': {
            'summary': {'openai': 'model'},
            'script': {'openai': 'model'},
            'tts': {'openai': 'tts'}
        },
        'paths': {
            'input': str(Path(tmp.name)/'input.txt'),
            'brief': str(brief_path),
            'script': str(script_path),
            'audio': str(Path(tmp.name)/'audio')
        },
        'speaker_voice': {'openai': {'0': 'a', '1': 'b'}}
    }
    cfg_file = Path(tmp.name) / 'cfg.yaml'
    cfg_file.write_text(yaml.dump(cfg_data))
    base = '[{"speaker": "0", "text": "hello"}]'
    script_content = f"```\n{base}\n```"
    mock_openai.return_value.chat.completions.create.return_value = DummyResp(script_content)
    cfg = load_config(cfg_file)
    out = brief_to_script(cfg)
    assert out == json.loads(base)
    assert json.loads(script_path.read_text()) == json.loads(base)
    tmp.cleanup()
