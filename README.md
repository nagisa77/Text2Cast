# Text2Cast

A pipeline that converts long text into a podcast script and audio.

Install the package with `pip` and run the command line interface `text2cast`.

## Usage

1. Copy `config.yaml.example` to `config.yaml` and edit paths and voices.
2. Copy `.env.example` to `.env` and fill in `OPENAI_API_KEY` or `DEEPSEEK_API_KEY`,
   `VOLCENGINE_TOKEN`/`VOLCENGINE_APP_ID`, or `MINIMAX_API_KEY`/`MINIMAX_GROUP_ID`
   depending on the TTS engine.
3. Install the package (for local development use `pip install -e .`).
4. Place your input text at the configured input path.
5. Run the full pipeline:

```bash
text2cast config.yaml all
```

Or run individual steps:

```bash
text2cast config.yaml summary
text2cast config.yaml script
text2cast config.yaml tts
```

You can override configuration values on the command line, for example

```bash
text2cast config.yaml all --tts_engine openai --speaker_voice 0=alloy,1=echo
```

The TTS step produces individual MP3 files for each script entry and
automatically concatenates them into `combined.mp3` inside the configured
audio directory.

## Configuration

`config.yaml` specifies model names, file paths and voice mapping.

```
tts_engine: openai
chat_engine: openai
models:
  summary:
    openai: gpt-4o-mini
    deepseek: deepseek-reasoner
  script:
    openai: gpt-4o-mini
    deepseek: deepseek-reasoner
  tts:
    openai: tts-1
    volcengine: volcano_tts
    minimax: speech-02-hd
paths:
  input: input.txt
  brief: brief.txt
  script: script.json
  audio: audio
speaker_voice:
  openai:
    "0": alloy
    "1": echo
  volcengine:
    "0": zh_male_beijingxiaoye_moon_bigtts
  minimax:
    "0": Chinese (Mandarin)_Warm_Bestie
```
