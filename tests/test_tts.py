import json
import yaml
import tempfile
from pathlib import Path
from unittest import mock
import os
from text2cast.config import load_config
from text2cast.tts import script_to_audio

os.environ.setdefault('OPENAI_API_KEY', 'test')
os.environ.setdefault('VOLCENGINE_TOKEN', 'token')
os.environ.setdefault('VOLCENGINE_APP_ID', 'appid')
os.environ.setdefault('MINIMAX_API_KEY', 'api')
os.environ.setdefault('MINIMAX_GROUP_ID', 'gid')


@mock.patch('openai.OpenAI')
def test_script_to_audio(mock_openai):
    tmp = tempfile.TemporaryDirectory()
    script_path = Path(tmp.name) / 'script.json'
    audio_dir = Path(tmp.name) / 'audio'
    script_data = [
        {"speaker": "0", "text": "hello"},
        {"speaker": "1", "text": "world"},
    ]
    script_path.write_text(json.dumps(script_data))
    cfg_data = {
        'tts_engine': 'openai',
        'models': {
            'summary': 'model',
            'script': 'model',
            'tts': {'openai': 'tts'}
        },
        'paths': {
            'input': str(Path(tmp.name)/'input.txt'),
            'brief': str(Path(tmp.name)/'brief.txt'),
            'script': str(script_path),
            'audio': str(audio_dir)
        },
        'speaker_voice': {'openai': {'0': 'a', '1': 'b'}}
    }
    cfg_file = Path(tmp.name) / 'cfg.yaml'
    cfg_file.write_text(yaml.dump(cfg_data))
    mock_client = mock_openai.return_value
    mock_client.audio.speech.create.side_effect = [
        type('r', (), {'content': b'voice1'}),
        type('r', (), {'content': b'voice2'}),
    ]
    cfg = load_config(cfg_file)
    paths = script_to_audio(cfg)
    assert Path(paths[0]).exists()
    assert Path(paths[0]).read_bytes() == b'voice1'
    assert Path(paths[1]).exists()
    assert Path(paths[1]).read_bytes() == b'voice2'
    # Last path is combined audio
    assert Path(paths[-1]).exists()
    assert Path(paths[-1]).read_bytes() == b'voice1voice2'
    tmp.cleanup()


@mock.patch('requests.post')
def test_script_to_audio_volc(mock_post):
    tmp = tempfile.TemporaryDirectory()
    script_path = Path(tmp.name) / 'script.json'
    audio_dir = Path(tmp.name) / 'audio'
    script_data = [
        {"speaker": "0", "text": "hello"},
        {"speaker": "1", "text": "world"},
    ]
    script_path.write_text(json.dumps(script_data))
    cfg_data = {
        'tts_engine': 'volcengine',
        'models': {
            'summary': 'model',
            'script': 'model',
            'tts': {'volcengine': 'cn_zhiyan_emo'}
        },
        'paths': {
            'input': str(Path(tmp.name)/'input.txt'),
            'brief': str(Path(tmp.name)/'brief.txt'),
            'script': str(script_path),
            'audio': str(audio_dir)
        },
        'speaker_voice': {
            'volcengine': {'0': 'a', '1': 'b'}
        }
    }
    cfg_file = Path(tmp.name) / 'cfg.yaml'
    cfg_file.write_text(yaml.dump(cfg_data))
    class Dummy:
        def __init__(self, data):
            self._data = data

        def raise_for_status(self):
            pass

        def json(self):
            import base64
            return {
                "code": 0,
                "data": {"audio": base64.b64encode(self._data).decode()},
            }

    mock_post.side_effect = [Dummy(b"voice1"), Dummy(b"voice2")]
    cfg = load_config(cfg_file)
    paths = script_to_audio(cfg)
    assert Path(paths[0]).exists()
    assert Path(paths[0]).read_bytes() == b'voice1'
    assert Path(paths[1]).exists()
    assert Path(paths[1]).read_bytes() == b'voice2'
    assert Path(paths[-1]).exists()
    assert Path(paths[-1]).read_bytes() == b'voice1voice2'
    tmp.cleanup()


@mock.patch('requests.post')
def test_script_to_audio_minimax(mock_post):
    tmp = tempfile.TemporaryDirectory()
    script_path = Path(tmp.name) / 'script.json'
    audio_dir = Path(tmp.name) / 'audio'
    script_data = [
        {"speaker": "0", "text": "hello"},
        {"speaker": "1", "text": "world"},
    ]
    script_path.write_text(json.dumps(script_data))
    cfg_data = {
        'tts_engine': 'minimax',
        'models': {
            'summary': 'm',
            'script': 'm',
            'tts': {'minimax': 'speech-02-hd'}
        },
        'paths': {
            'input': str(Path(tmp.name)/'input.txt'),
            'brief': str(Path(tmp.name)/'brief.txt'),
            'script': str(script_path),
            'audio': str(audio_dir)
        },
        'speaker_voice': {
            'minimax': {'0': 'a', '1': 'b'}
        }
    }
    cfg_file = Path(tmp.name) / 'cfg.yaml'
    cfg_file.write_text(yaml.dump(cfg_data))

    class Dummy:
        def __init__(self, data: bytes):
            self._data = data

        def raise_for_status(self):
            pass

        def json(self):
            return {
                "base_resp": {"status_code": 0},
                "data": {"audio": self._data.hex()},
            }

    mock_post.side_effect = [Dummy(b"voice1"), Dummy(b"voice2")]
    cfg = load_config(cfg_file)
    paths = script_to_audio(cfg)
    assert Path(paths[0]).exists()
    assert Path(paths[0]).read_bytes() == b'voice1'
    assert Path(paths[1]).exists()
    assert Path(paths[1]).read_bytes() == b'voice2'
    assert Path(paths[-1]).exists()
    assert Path(paths[-1]).read_bytes() == b'voice1voice2'
    tmp.cleanup()
