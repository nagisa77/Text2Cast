import os
from dataclasses import dataclass
from typing import Dict
from dotenv import load_dotenv
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

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
VOLCENGINE_TOKEN = os.getenv('VOLCENGINE_TOKEN')
VOLCENGINE_APP_ID = os.getenv('VOLCENGINE_APP_ID')