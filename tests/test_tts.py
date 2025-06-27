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
        'models': {'summary': 'model', 'script': 'model', 'tts': 'tts'},
        'paths': {
            'input': str(Path(tmp.name)/'input.txt'),
            'brief': str(Path(tmp.name)/'brief.txt'),
            'script': str(script_path),
            'audio': str(audio_dir)
        },
        'speaker_voice': {'0': 'a', '1': 'b'}
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


@mock.patch('volcengine.tls.TTSService.TTSService')
def test_script_to_audio_volc(mock_tts):
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
        'models': {'summary': 'model', 'script': 'model', 'tts': 'cn_zhiyan_emo'},
        'paths': {
            'input': str(Path(tmp.name)/'input.txt'),
            'brief': str(Path(tmp.name)/'brief.txt'),
            'script': str(script_path),
            'audio': str(audio_dir)
        },
        'speaker_voice': {'0': 'a', '1': 'b'}
    }
    cfg_file = Path(tmp.name) / 'cfg.yaml'
    cfg_file.write_text(yaml.dump(cfg_data))
    mock_client = mock_tts.return_value
    mock_client.synthesize.side_effect = [
        type('r', (), {'audio_data': b'voice1'}),
        type('r', (), {'audio_data': b'voice2'}),
    ]
    cfg = load_config(cfg_file)
    paths = script_to_audio(cfg)
    assert Path(paths[0]).exists()
    assert Path(paths[0]).read_bytes() == b'voice1'
    assert Path(paths[1]).exists()
    assert Path(paths[1]).read_bytes() == b'voice2'
    assert Path(paths[-1]).exists()
    assert Path(paths[-1]).read_bytes() == b'voice1voice2'
    tmp.cleanup()
