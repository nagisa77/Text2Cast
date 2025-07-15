import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional
try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover - fallback when dotenv is missing
    def load_dotenv(*args, **kwargs):
        return None
import yaml
import logging

logger = logging.getLogger(__name__)

load_dotenv()

@dataclass
class Config:
    model_summary: str
    model_script: str
    tts_model: str
    input_path: str
    brief_path: str
    script_path: str
    audio_dir: str
    speaker_voice: Dict[str, str]
    sound_effects: Dict[str, str] = field(default_factory=dict)
    voice_clone_samples: List[str] = field(default_factory=list)
    voice_clone_name: Optional[str] = None
    tts_engine: str = "openai"
    chat_engine: str = "openai"


def load_config(path: str) -> Config:
    logger.debug("Loading config from %s", path)
    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    load_env_vars()
    tts_engine = data.get('tts_engine', 'openai')
    logger.debug("Selected tts_engine: %s", tts_engine)
    chat_engine = data.get('chat_engine', 'openai')
    logger.debug("Selected chat_engine: %s", chat_engine)

    tts_model = None
    if isinstance(data.get('models', {}).get('tts'), dict):
        tts_model = data['models']['tts'].get(tts_engine)
    else:
        tts_model = data['models'].get('tts')
    logger.debug("tts_model resolved to: %s", tts_model)

    speaker_voice = data.get('speaker_voice', {})
    if isinstance(speaker_voice, dict) and tts_engine in speaker_voice:
        speaker_voice = speaker_voice[tts_engine]

    model_summary = data['models']['summary']
    if isinstance(model_summary, dict):
        model_summary = model_summary.get(chat_engine)

    model_script = data['models']['script']
    if isinstance(model_script, dict):
        model_script = model_script.get(chat_engine)

    vc = data.get('voice_clone', {})
    voice_clone_name = vc.get('name')
    voice_clone_samples = vc.get('samples', []) if isinstance(vc, dict) else []

    sound_effects = data.get('sound_effects', {})

    return Config(
        model_summary=model_summary,
        model_script=model_script,
        tts_model=tts_model,
        input_path=data['paths']['input'],
        brief_path=data['paths']['brief'],
        script_path=data['paths']['script'],
        audio_dir=data['paths']['audio'],
        speaker_voice=speaker_voice,
        sound_effects=sound_effects,
        voice_clone_samples=voice_clone_samples,
        voice_clone_name=voice_clone_name,
        tts_engine=tts_engine,
        chat_engine=chat_engine,
    )

def load_env_vars() -> None:
    global OPENAI_API_KEY, VOLCENGINE_TOKEN, VOLCENGINE_APP_ID
    global MINIMAX_API_KEY, MINIMAX_GROUP_ID, DEEPSEEK_API_KEY
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    VOLCENGINE_TOKEN = os.getenv('VOLCENGINE_TOKEN')
    VOLCENGINE_APP_ID = os.getenv('VOLCENGINE_APP_ID')
    MINIMAX_API_KEY = os.getenv('MINIMAX_API_KEY')
    MINIMAX_GROUP_ID = os.getenv('MINIMAX_GROUP_ID')
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')

load_env_vars()
