---
name: video-editing-router
description: Entry point for any video creation or editing request. Use first when the user wants to make, edit, cut, caption, dub, resize, export, or automate a video, and you must pick the right route and the right companion skills (ffmpeg, Remotion, moviepy, captions, voiceover, screen recording, shorts).
---

# Video Editing Router

Pick the lightest route that gets the result. Then load the companion skill for that route.

## Step 1: Classify the request

| The user wants... | Route | Skills to load |
|---|---|---|
| Trim, join, convert, resize, compress, extract audio, speed change | **Direct FFmpeg** | `ffmpeg-essentials` |
| Export for YouTube, X, LinkedIn, Instagram, TikTok, web | **Export** | `platform-export` |
| Captions or subtitles on existing footage | **Captions** | `captions-subtitles` |
| Text, labels, lower thirds over existing or AI-made footage | **Python overlay** | `moviepy-python-video` |
| Explainer, product demo, sprint review, data chart, branded motion graphics | **Programmatic video** | `remotion-programmatic-video`, `motion-design-craft` |
| Walkthrough of a web app | **Screen recording** | `screen-recording-demos` |
| 9:16 clips for Shorts, Reels, TikTok | **Vertical** | `vertical-shorts` |
| Narration or dubbing | **Voiceover** | `voiceover-tts`, `audio-mixing` |
| Thumbnail or cover image | **Thumbnails** | `thumbnails` |
| Anything new from scratch | **Plan first** | `video-planning`, then the route above |

Always finish with `video-qa` before handing a file to the user.

## Step 2: Check the environment

Run these before promising anything:

```bash
ffmpeg -version | head -1
ffprobe -version | head -1
node --version      # only for Remotion
python --version    # only for moviepy / scripts
```

If FFmpeg is missing, tell the user how to install it (`winget install Gyan.FFmpeg`, `brew install ffmpeg`, `apt install ffmpeg`) and stop. Do not guess at output.

## Step 3: Rules that apply to every route

1. **Never overwrite the source.** Write to a new path (`out/`, `build/`). Keep raw footage read-only.
2. **Probe before processing.** Resolution, fps, codec, duration, audio streams. Many failures come from odd inputs (variable frame rate, odd dimensions, no audio track).
3. **Draft first, final second.** Render a low-quality or short preview, confirm with the user, then render the master.
4. **Text must be deterministic.** AI video models garble in-frame text. Add names, prices, and captions as an overlay step.
5. **One master, many exports.** Render one high-quality master, then derive platform versions from it.
6. **Report what you made.** Give the path, duration, resolution, and file size.

## Step 4: Ask only what is missing

Needed inputs: goal and audience, target platform and aspect ratio, length, source assets, voice and music preference, brand (colors, fonts, logo). Assume sensible defaults (1920x1080, 30 fps, H.264 + AAC) and say so, rather than asking about each.
