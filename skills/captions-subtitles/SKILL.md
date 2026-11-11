---
name: captions-subtitles
description: Create, edit, translate and burn in captions and subtitles - transcribe speech with Whisper, write SRT/VTT/ASS files, style them, and hard-burn word-highlight captions for Shorts, Reels and TikTok. Use for any captioning, subtitle, transcript or accessibility request.
---

# Captions and Subtitles

Most social video is watched muted. Captions are part of the edit, not an extra.

## 1. Transcribe

```bash
# openai-whisper (pip install openai-whisper)
whisper audio.mp3 --model small --language en --output_format srt --output_dir captions/

# faster-whisper (pip install faster-whisper): faster, lower memory, word timestamps
python - <<'PY'
from faster_whisper import WhisperModel
model = WhisperModel("small", compute_type="int8")
segments, info = model.transcribe("audio.mp3", word_timestamps=True, vad_filter=True)
for s in segments:
    for w in s.words:
        print(f"{w.start:.2f}\t{w.end:.2f}\t{w.word}")
PY
```

Extract clean audio first for better results:

```bash
ffmpeg -i video.mp4 -vn -ac 1 -ar 16000 audio.wav
```

Model size trades accuracy for speed: `base` < `small` < `medium` < `large`. Use `small` or `medium` for English, `large` for hard accents or other languages.

**If the script already exists** (you generated the voiceover from it), do not trust the transcript's wording. Use the script text and use Whisper only for timing (forced alignment). This keeps names and numbers exact.

## 2. Fix the text

Proofread proper nouns, product names, numbers. Whisper often mishears these. Ask the user for a glossary when the topic is technical.

## 3. Write caption files

SRT:

```
1
00:00:00,000 --> 00:00:02,400
Most builds fail on Friday.

2
00:00:02,400 --> 00:00:05,100
Here is why.
```

Readability rules:
- Max 2 lines, about 42 characters per line (about 20 for vertical video).
- Reading speed under 17 characters per second; minimum cue length 1 second.
- Break at phrases, not mid-phrase. Never split a name across cues.
- Cues must not overlap. Keep a 2 frame gap or none.

## 4. Burn in

```bash
# Soft styling through force_style (SRT)
ffmpeg -i in.mp4 -vf "subtitles=captions.srt:force_style='FontName=Arial,FontSize=22,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,Alignment=2,MarginV=60'" -c:a copy out/captioned.mp4

# ASS gives full control (karaoke word highlight, positions, animation)
ffmpeg -i in.mp4 -vf "ass=captions.ass" -c:a copy out/captioned.mp4
```

Windows path gotcha: in filters, escape the drive colon and use forward slashes (`subtitles='C\:/work/captions.srt'`), or run FFmpeg from the folder containing the file and use a relative path.

## 5. Word-highlight style for short-form

Generate an ASS file with one event per word group (2 to 4 words), and use the `\k` karaoke tag or per-word color override so the active word changes color. Typical look: bold sans-serif, white text, 3 to 4 px black outline, active word in a brand accent, placed in the lower-middle third, not the very bottom (platform UI covers it).

Minimal ASS header to start from:

```
[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Default,Arial,72,&H00FFFFFF,&H0000D7FF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,4,0,2,60,60,520,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
Dialogue: 0,0:00:00.00,0:00:01.20,Default,,0,0,0,,{\k30}Most {\k40}builds {\k30}fail
```

Colors in ASS are `&HAABBGGRR` (blue-green-red order, alpha first).

## 6. Deliver

- Burned-in version for social platforms.
- A separate `.srt` or `.vtt` for YouTube, LinkedIn, and web players (viewers can toggle and translate).
- Soft subtitle track in MP4: `-i captions.srt -c copy -c:s mov_text`.

## Translate

Translate cue text, not timing. Keep line limits per language (German and Finnish run longer, so re-wrap). Have a native reader check when the video is public.
