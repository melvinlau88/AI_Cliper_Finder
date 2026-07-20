# AI Short-Form Clip Finder

Finds the best moments in a long video and cuts them into short standalone clips — built as a learning project to understand FFmpeg, Whisper, and Python from the ground up.

## What it does

1. Asks how many clips you want and which Whisper model size to use
2. Extracts the audio track from `video.mp4` using FFmpeg
3. Transcribes the audio locally using OpenAI's Whisper (with timestamps)
4. Picks the best moments using a simple heuristic (longest continuous segments)
5. Cuts those moments into separate clip files, with padding on each side so cuts don't feel abrupt

## Cost: $0

Everything runs locally — no API keys, no cloud costs.
- **FFmpeg** — free, open-source, runs on your machine
- **Whisper** — free, runs locally, no account needed

## Requirements

- Python 3
- [FFmpeg](https://www.gyan.dev/ffmpeg/builds/) installed and added to your system PATH
- `openai-whisper` Python package

## Setup

```bash
pip install openai-whisper
```

Make sure `ffmpeg -version` works in your terminal before running the script — if it doesn't, FFmpeg isn't correctly added to your PATH.

## Usage

1. Put your source video in the project folder, named `video.mp4`
2. Run:
```bash
   python main.py
```
3. You'll be prompted for:
   - **Number of clips** — must be a whole number greater than 0
   - **Model size** — one of `tiny`, `base`, `small`, `medium`, `large` (bigger = more accurate, slower)
4. Check the folder for clips named like `small_clip_1.mp4`, `small_clip_2.mp4`, etc.

## How the transcript caching works

Transcribing with Whisper is the slowest step, so the script saves its output to `transcript_<model_size>.json` (e.g. `transcript_small.json`). If that file already exists, the script loads it instantly instead of re-running Whisper — so switching model sizes only re-transcribes when there's no cached transcript for that specific model yet.

## Output naming

Clips are named `<model_size>_clip_<number>.mp4`, so results from different model sizes don't overwrite each other and can be compared side by side.
