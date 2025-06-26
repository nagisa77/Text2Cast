import json
import yaml
import tempfile
from pathlib import Path
from unittest import mock
from text2cast.config import load_config
from text2cast.tts import script_to_audio


@mock.patch('openai.OpenAI')
def test_script_to_audio(mock_openai):
    tmp = tempfile.TemporaryDirectory()
    script_path = Path(tmp.name) / 'script.json'
    audio_dir = Path(tmp.name) / 'audio'
    script_path.write_text(json.dumps([{"speaker": "0", "text": "hello"}]))
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
    mock_openai.return_value.audio.speech.create.return_value.content = b'voice'
    cfg = load_config(cfg_file)
    paths = script_to_audio(cfg)
    assert Path(paths[0]).exists()
    assert Path(paths[0]).read_bytes() == b'voice'
    tmp.cleanup()
