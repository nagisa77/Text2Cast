import os
from dataclasses import dataclass
from typing import Dict
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
    tts_engine: str = "openai"


def load_config(path: str) -> Config:
    logger.debug("Loading config from %s", path)
    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    load_env_vars()
    return Config(
        model_summary=data['models']['summary'],
        model_script=data['models']['script'],
        tts_model=data['models']['tts'],
        input_path=data['paths']['input'],
        brief_path=data['paths']['brief'],
        script_path=data['paths']['script'],
        audio_dir=data['paths']['audio'],
        speaker_voice=data['speaker_voice'],
        tts_engine=data.get('tts_engine', 'openai'),
    )

def load_env_vars() -> None:
    global OPENAI_API_KEY, VOLCENGINE_TOKEN, VOLCENGINE_APP_ID
    global MINIMAX_API_KEY, MINIMAX_GROUP_ID
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    VOLCENGINE_TOKEN = os.getenv('VOLCENGINE_TOKEN')
    VOLCENGINE_APP_ID = os.getenv('VOLCENGINE_APP_ID')
    MINIMAX_API_KEY = os.getenv('MINIMAX_API_KEY')
    MINIMAX_GROUP_ID = os.getenv('MINIMAX_GROUP_ID')

load_env_vars()
