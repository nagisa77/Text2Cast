# Text2Cast

A pipeline that converts long text into a podcast script and audio.

## Usage

1. Copy `config.yaml.example` to `config.yaml` and edit paths and voices.
2. Copy `.env.example` to `.env` and fill in `OPENAI_API_KEY` or
   `VOLCENGINE_TOKEN`/`VOLCENGINE_APP_ID` depending on the TTS engine.
3. Place your input text at the configured input path.
4. Run the full pipeline:

```bash
python main.py config.yaml all
```

Or run individual steps:

```bash
python main.py config.yaml summary
python main.py config.yaml script
python main.py config.yaml tts
```

The TTS step produces individual MP3 files for each script entry and
automatically concatenates them into `combined.mp3` inside the configured
audio directory.

## Configuration

`config.yaml` specifies model names, file paths and voice mapping.

```
tts_engine: openai
models:
  summary: gpt-4o-mini
  script: gpt-4o-mini
  tts: tts-1
paths:
  input: input.txt
  brief: brief.txt
  script: script.json
  audio: audio
speaker_voice:
  "0": alloy
  "1": echo
```
