import argparse
import logging

from .config import load_config, Config
from .summarizer import input_to_brief
from .script_generator import brief_to_script
from .tts import script_to_audio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def apply_overrides(cfg: Config, args: argparse.Namespace) -> Config:
    """Apply command line overrides to the config object."""
    if args.tts_engine:
        cfg.tts_engine = args.tts_engine
    if args.chat_engine:
        cfg.chat_engine = args.chat_engine
    if args.tts_model:
        cfg.tts_model = args.tts_model
    if args.model_summary:
        cfg.model_summary = args.model_summary
    if args.model_script:
        cfg.model_script = args.model_script
    if args.input_path:
        cfg.input_path = args.input_path
    if args.brief_path:
        cfg.brief_path = args.brief_path
    if args.script_path:
        cfg.script_path = args.script_path
    if args.audio_dir:
        cfg.audio_dir = args.audio_dir

    if args.speaker_voice:
        for item in args.speaker_voice:
            for pair in item.split(','):
                if '=' not in pair:
                    raise ValueError(
                        "speaker_voice must be of the form speaker=voice"
                    )
                k, v = pair.split('=', 1)
                cfg.speaker_voice[k] = v

    return cfg


def run_all(cfg: Config) -> None:
    """Run the full text-to-podcast pipeline."""
    logger.info("Running full pipeline")
    input_to_brief(cfg)
    brief_to_script(cfg)
    script_to_audio(cfg)


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Text2Cast pipeline")
    parser.add_argument("config", help="Path to config.yaml")
    parser.add_argument("--tts_engine")
    parser.add_argument("--chat_engine")
    parser.add_argument("--tts_model")
    parser.add_argument("--model_summary")
    parser.add_argument("--model_script")
    parser.add_argument("--input_path")
    parser.add_argument("--brief_path")
    parser.add_argument("--script_path")
    parser.add_argument("--audio_dir")
    parser.add_argument(
        "--speaker_voice",
        action="append",
        help=(
            "Override speaker to voice mapping, format: speaker=voice. "
            "Can be used multiple times or with comma separated pairs."
        ),
    )
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("summary")
    sub.add_parser("script")
    sub.add_parser("tts")
    sub.add_parser("all")
    args = parser.parse_args()
    cfg = load_config(args.config)
    cfg = apply_overrides(cfg, args)
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
        run_all(cfg)


if __name__ == "__main__":  # pragma: no cover - manual execution
    main()
