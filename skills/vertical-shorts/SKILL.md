---
name: vertical-shorts
description: Turn video into 9:16 vertical clips for YouTube Shorts, Instagram Reels and TikTok - smart reframing, blurred-background fill, safe zones, hook structure, clipping long videos into shorts, and caption placement. Use when the user wants shorts, reels, vertical versions or repurposed clips.
---

# Vertical Shorts (9:16)

Canvas: **1080x1920**, 30 fps, H.264 + AAC. Captions on by default.

## Reframe a 16:9 source

```bash
# 1. Center crop (fast; fine when the subject is centered)
ffmpeg -i in.mp4 -vf "crop=ih*9/16:ih,scale=1080:1920" -c:v libx264 -crf 18 -c:a aac out/crop.mp4

# 2. Crop with a manual horizontal offset (x = pixels from left of source)
ffmpeg -i in.mp4 -vf "crop=ih*9/16:ih:x=600:y=0,scale=1080:1920" -c:v libx264 -crf 18 -c:a aac out/crop-x.mp4

# 3. Blurred-background fill: whole frame stays visible (good for screen recordings)
ffmpeg -i in.mp4 -filter_complex \
 "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30:5[bg];\
  [0:v]scale=1080:-2[fg];\
  [bg][fg]overlay=(W-w)/2:(H-h)/2" \
 -c:v libx264 -crf 18 -c:a aac out/blurfill.mp4
```

Choose by content:
- Talking head: crop to the face, with a manual `x` offset.
- Screen recording: blur-fill, or zoom into the active region with keyframed crops.
- Two speakers: stack them vertically (top and bottom) with `vstack` after cropping each.

```bash
ffmpeg -i in.mp4 -filter_complex "[0:v]crop=iw/2:ih:0:0,scale=1080:960[a];[0:v]crop=iw/2:ih:iw/2:0,scale=1080:960[b];[a][b]vstack" -c:a copy out/stack.mp4
```

## Safe zones

App UI covers parts of the frame. Keep text and faces inside the safe area:

- Top: about 150 px clear.
- Bottom: about 380 px clear (caption, username, buttons).
- Right edge: about 120 px clear (like/share column).
- Place captions at roughly 55 to 70 percent of the frame height.

Exact values vary per app and change; treat these as conservative defaults.

## Cutting a short from a long video

1. Transcribe (`captions-subtitles`) and read the transcript for self-contained moments: a claim, a story, a surprising number, a clear how-to.
2. Choose 20 to 60 seconds that make sense without context. Start on the sentence that carries the point, not on "so".
3. Trim with re-encoding (`ffmpeg-essentials`), remove long pauses, tighten ums.
4. Reframe, caption, add a small progress bar or title if useful.
5. Export with `platform-export` (vertical target).

## Hook and structure

- **0 to 3 s:** the hook. A question, a bold claim, or the result first. No intro, no greeting, no logo.
- **3 to 40 s:** one idea, with a visual change every 2 to 4 seconds (zoom, cut, caption highlight).
- **Last 3 s:** payoff or loop back to the opening so a replay feels seamless.

## Captions

- Large (about 70 to 90 px at 1080 wide), bold, high contrast, 2 to 4 words at a time.
- Highlight the spoken word.
- Generate from the real script where possible. See `captions-subtitles`.

## Batch idea

For many clips, keep a `clips.json` with `{source, start, end, title}` and loop over it in a script, so re-runs are cheap.

## Checks

- Plays full-screen on a phone with no important content hidden by UI.
- Audible with sound on, understandable with it off.
- File under the platform size limit, under the intended duration.
