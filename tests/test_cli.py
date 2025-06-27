import sys
from pathlib import Path
import yaml
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from text2cast.cli import main


def test_cli_overrides(monkeypatch):
    tmp = tempfile.TemporaryDirectory()
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
            'brief': str(Path(tmp.name)/'brief.txt'),
            'script': str(Path(tmp.name)/'script.json'),
            'audio': str(Path(tmp.name)/'audio')
        },
        'speaker_voice': {'openai': {'0': 'a'}}
    }
    cfg_file = Path(tmp.name) / 'cfg.yaml'
    cfg_file.write_text(yaml.dump(cfg_data))

    called = {}
    def fake_summary(cfg):
        called['voice'] = cfg.speaker_voice['0']
    monkeypatch.setattr('text2cast.cli.input_to_brief', fake_summary)
    monkeypatch.setattr('text2cast.cli.brief_to_script', lambda cfg: None)
    monkeypatch.setattr('text2cast.cli.script_to_audio', lambda cfg: None)

    monkeypatch.setattr(sys, 'argv', [
        'text2cast', str(cfg_file), 'summary', '--speaker_voice', '0=voice'
    ])

    main()
    assert called['voice'] == 'voice'
    tmp.cleanup()
