import os
from dataclasses import dataclass
from typing import Dict
import yaml
from dotenv import load_dotenv

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


def load_config(path: str) -> Config:
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
    )


OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
