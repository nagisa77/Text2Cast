import argparse
import logging

from .config import load_config
from .summarizer import input_to_brief
from .script_generator import brief_to_script
from .tts import script_to_audio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_all(cfg_path: str) -> None:
    """Run the full text-to-podcast pipeline."""
    logger.info("Running full pipeline with config %s", cfg_path)
    cfg = load_config(cfg_path)
    input_to_brief(cfg)
    brief_to_script(cfg)
    script_to_audio(cfg)


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Text2Cast pipeline")
    parser.add_argument("config", help="Path to config.yaml")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("summary")
    sub.add_parser("script")
    sub.add_parser("tts")
    sub.add_parser("all")
    args = parser.parse_args()
    cfg = load_config(args.config)
    if args.command == "summary":
        logger.info("Running summarization step")
        input_to_brief(cfg)
    elif args.command == "script":
        logger.info("Running script generation step")
        brief_to_script(cfg)
    elif args.command == "tts":
        logger.info("Running TTS step")
        script_to_audio(cfg)
    else:
        run_all(args.config)


if __name__ == "__main__":  # pragma: no cover - manual execution
    main()
