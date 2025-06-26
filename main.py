import argparse
import logging
from text2cast.config import load_config
from text2cast.summarizer import input_to_brief
from text2cast.script_generator import brief_to_script
from text2cast.tts import script_to_audio

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def run_all(cfg_path: str):
    logger.info("Running full pipeline with config %s", cfg_path)
    cfg = load_config(cfg_path)
    input_to_brief(cfg)
    brief_to_script(cfg)
    script_to_audio(cfg)


def main():
    parser = argparse.ArgumentParser(description='Text2Cast pipeline')
    parser.add_argument('config', help='Path to config.yaml')
    sub = parser.add_subparsers(dest='command')
    sub.add_parser('summary')
    sub.add_parser('script')
    sub.add_parser('tts')
    sub.add_parser('all')
    args = parser.parse_args()
    cfg = load_config(args.config)
    if args.command == 'summary':
        logger.info("Running summarization step")
        input_to_brief(cfg)
    elif args.command == 'script':
        logger.info("Running script generation step")
        brief_to_script(cfg)
    elif args.command == 'tts':
        logger.info("Running TTS step")
        script_to_audio(cfg)
    else:
        run_all(args.config)


if __name__ == '__main__':
    main()
