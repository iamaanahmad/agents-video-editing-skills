---
name: moviepy-python-video
description: Compose and edit video in pure Python with moviepy 2.x - overlay text, lower thirds and captions on footage, cut and join clips, add audio, build short single-file build.py videos without Node. Use when the user wants Python-based video editing or deterministic text over AI-generated video.
---

# moviepy (Python Video Composition)

Best for short, scripted videos and for putting exact text on top of footage. For long, design-heavy, reusable videos prefer Remotion.

| Use moviepy when | Use Remotion when |
|---|---|
| The project is a single Python script | You need React components and a design system |
| Overlaying text on existing or AI-generated clips | Complex animated graphics and charts |
| Batch edits over many files | Hot-reload preview matters |
| No Node toolchain available | Long-form, templated videos |

## Setup

```bash
pip install "moviepy>=2" pillow
# or: uv add moviepy pillow
```

This skill targets **moviepy 2.x**. Its API differs from 1.x: imports come from `moviepy` directly, and methods are `with_*`/`subclipped`/`resized`, not `set_*`/`subclip`/`resize`.

## Basics

```python
from moviepy import (VideoFileClip, AudioFileClip, ImageClip, TextClip,
                     CompositeVideoClip, CompositeAudioClip, concatenate_videoclips, vfx, afx)

clip = VideoFileClip("in.mp4").subclipped(5, 20)           # 15 s excerpt
clip = clip.resized(height=1080)                            # keep aspect
clip = clip.with_effects([vfx.FadeIn(0.5), vfx.FadeOut(0.5)])

joined = concatenate_videoclips([clip, VideoFileClip("b.mp4")], method="compose")
joined.write_videofile("out/result.mp4", fps=30, codec="libx264", audio_codec="aac")
```

Always call `.close()` on clips in long scripts, or use them in a `with` block, to release file handles.

## Text overlay (deterministic text on footage)

```python
title = (TextClip(font="C:/Windows/Fonts/arial.ttf",     # a real font file path
                  text="Dr. Jane Doe\nChief Scientist",
                  font_size=56, color="white",
                  stroke_color="black", stroke_width=2,
                  method="caption", size=(900, None))
         .with_start(1.0).with_duration(4.0)
         .with_position(("left", 860))
         .with_effects([vfx.CrossFadeIn(0.3), vfx.CrossFadeOut(0.3)]))

final = CompositeVideoClip([clip, title])
```

Notes:
- `TextClip` needs a font file path (TTF/OTF). Ship the brand font in the project.
- Clip times are in seconds, relative to the composite's start.
- For heavily styled text (rounded pills, gradients), render a PNG with Pillow and use `ImageClip`.
- Keep text inside the safe area: at least 5% from each edge.

## Audio

```python
voice = AudioFileClip("voiceover.mp3")
music = AudioFileClip("music.mp3").with_effects([afx.MultiplyVolume(0.12), afx.AudioFadeOut(2)])
music = music.with_duration(voice.duration + 1)
final = clip.with_audio(CompositeAudioClip([music, voice.with_start(0.5)]))
```

Let the voiceover decide the timeline: set the clip duration to `voice.duration + padding`, not the other way round.

## Audio-anchored pattern

```python
scenes = [("scene1.mp3", "intro.png"), ("scene2.mp3", "chart.png")]
parts = []
for audio_path, image_path in scenes:
    a = AudioFileClip(audio_path)
    v = ImageClip(image_path).with_duration(a.duration + 0.6).with_audio(a)
    parts.append(v)
concatenate_videoclips(parts).write_videofile("out/explainer.mp4", fps=30)
```

## Ken Burns on stills

```python
img = ImageClip("photo.jpg").with_duration(6)
img = img.resized(lambda t: 1.0 + 0.04 * t).with_position("center")
CompositeVideoClip([img], size=(1920, 1080)).write_videofile("out/kb.mp4", fps=30)
```

## Performance

- Preview with `fps=12` and `preset="ultrafast"`; render final at 30 fps.
- `write_videofile(..., threads=4)`.
- Avoid per-frame Python lambdas on long clips. Pre-process with FFmpeg when possible.

## Pitfalls

| Problem | Cause and fix |
|---|---|
| `ImportError: cannot import name 'editor'` | moviepy 2 removed `moviepy.editor`; import from `moviepy` |
| `AttributeError: set_duration` | Use `with_duration`; same for `with_start`, `with_position` |
| Text clip crashes | Pass a real font file path |
| Out-of-sync audio after joining | Ensure all clips share fps; apply audio after concatenation |
| Slow render | Lower resolution for drafts; avoid large `resized` lambdas |
