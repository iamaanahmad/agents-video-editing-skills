---
name: voiceover-tts
description: Generate and time narration with text-to-speech (ElevenLabs, OpenAI TTS, Kokoro, Piper) or prepare a recorded voice - script prep, per-scene audio files, pacing, pronunciation, cleanup and loudness. Use when the user needs a voiceover, narration, dubbing, or voice cloning guidance.
---

# Voiceover and TTS

Voiceover drives the timeline. Generate it before building visuals.

## Choose an engine

| Engine | Where | Strength | Watch out |
|---|---|---|---|
| ElevenLabs | Cloud API | Best naturalness, voice cloning | Paid; clone only voices you have consent for |
| OpenAI TTS | Cloud API | Simple, consistent | Limited voice choice |
| Kokoro | Local | Free, good quality, offline | Needs Python setup |
| Piper | Local | Fast, runs on CPU | Less expressive |
| Recorded human | Mic | Most authentic | Needs cleanup |

Keep API keys in environment variables or a `.env` file that is git-ignored. Never print or commit them.

## Prepare the script for speech

- Write numbers, units and acronyms as spoken: "twenty twenty-six", "A P I" if it should be spelled, "gigabytes".
- Add commas for breathing; use a period for a stop; avoid parentheses.
- Put hard names in a pronunciation list and test them in a short sample first.
- Split into **one file per scene** (`audio/scene-01.mp3`). Per-scene files let you re-record one line and keep timing flexible.

## Generate (example, ElevenLabs REST)

```python
import os, requests, pathlib

def tts(text: str, voice_id: str, out: pathlib.Path) -> None:
    r = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"], "Accept": "audio/mpeg"},
        json={"text": text, "model_id": "eleven_multilingual_v2",
              "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}},
        timeout=120,
    )
    r.raise_for_status()
    out.write_bytes(r.content)
```

Model names and endpoints change. Confirm against the provider's current docs before use.

## Measure and pace

```bash
ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 audio/scene-01.mp3
```

- Target 140 to 160 words per minute (words / seconds * 60). Re-generate with a slightly different delivery or trim the text if a scene is above 180 wpm; it will sound rushed.
- Do not time-stretch speech by more than about 10 percent; it sounds synthetic. Rewrite instead.

## Clean up recorded voice

```bash
# High-pass, gentle noise reduction, compression, loudness
ffmpeg -i raw.wav -af "highpass=f=80,afftdn=nf=-25,acompressor=threshold=-18dB:ratio=3:attack=5:release=80,loudnorm=I=-16:TP=-1.5:LRA=11" -ar 48000 clean.wav
```

Trim leading and trailing silence:

```bash
ffmpeg -i in.wav -af "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse" out.wav
```

## Assemble

```bash
# Join scene files with 0.4 s gaps
python - <<'PY'
import subprocess, pathlib
files = sorted(pathlib.Path("audio").glob("scene-*.mp3"))
parts = []
for i, f in enumerate(files):
    parts += ["-i", str(f)]
n = len(files)
filt = "".join(f"[{i}:a]apad=pad_dur=0.4[a{i}];" for i in range(n)) + "".join(f"[a{i}]" for i in range(n)) + f"concat=n={n}:v=0:a=1[out]"
subprocess.run(["ffmpeg", "-y", *parts, "-filter_complex", filt, "-map", "[out]", "voiceover.mp3"], check=True)
PY
```

Then mix with music in `audio-mixing` and caption using `captions-subtitles`.

## Ethics and rights

- Clone a voice only with the speaker's explicit permission.
- Disclose synthetic voice where platform rules or law require it.
- Check the TTS provider's license for commercial use.
