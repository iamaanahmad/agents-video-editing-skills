---
name: platform-export
description: Export a finished master video for YouTube, YouTube Shorts, X/Twitter, LinkedIn, Instagram, TikTok, or website embeds with correct codec, size, loudness and aspect ratio. Use when the user asks to prepare, optimize, compress, or publish a video for a specific platform.
---

# Platform Export

Render one high-quality master, then derive each platform file from it. Do not re-render the project per platform.

## Master settings

H.264 (`libx264`), `yuv420p`, 30 fps (or source fps), CRF 16 to 18, AAC 192 to 256 kbps at 48 kHz, `-movflags +faststart`.

## Targets

Limits change over time. Treat these as safe defaults and confirm against the platform's current help page if the file is near a limit.

| Platform | Aspect | Resolution | Safe length | Safe size | Notes |
|---|---|---|---|---|---|
| YouTube | 16:9 | 1920x1080 | any | any | Upload high quality; YouTube re-encodes |
| YouTube Shorts | 9:16 | 1080x1920 | up to 60 s (longer allowed) | any | Keep the key content out of the bottom UI area |
| X / Twitter | 16:9 or 1:1 | up to 1280x720 | 140 s | under 512 MB | Smaller files upload faster |
| LinkedIn | 16:9, 1:1, 4:5 | 1920x1080 | up to 10 min | under 5 GB | Captions matter: most views are muted |
| Instagram Reels | 9:16 | 1080x1920 | up to 90 s | 4 GB | |
| Instagram feed | 4:5 | 1080x1350 | up to 60 s | 4 GB | |
| TikTok | 9:16 | 1080x1920 | up to 10 min | ~287 MB | |
| Website | 16:9 | 1280x720 | any | small | MP4 plus WebM fallback |

## Recipes

```bash
# YouTube
ffmpeg -i master.mp4 -c:v libx264 -preset slow -crf 18 -profile:v high -c:a aac -b:a 192k -ar 48000 -movflags +faststart out/youtube.mp4

# Vertical (Shorts, Reels, TikTok): letterbox fit; see vertical-shorts for smart reframing
ffmpeg -i master.mp4 -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" -c:v libx264 -crf 18 -c:a aac -b:a 192k -movflags +faststart out/vertical.mp4

# X / Twitter (cap at 720p, smaller)
ffmpeg -i master.mp4 -vf "scale='min(1280,iw)':-2" -c:v libx264 -preset medium -crf 24 -profile:v main -c:a aac -b:a 128k -ar 44100 -movflags +faststart out/x.mp4

# LinkedIn
ffmpeg -i master.mp4 -vf "scale='min(1920,iw)':-2" -c:v libx264 -crf 22 -c:a aac -b:a 192k -ar 48000 -movflags +faststart out/linkedin.mp4

# Web embed
ffmpeg -i master.mp4 -vf scale=1280:-2 -c:v libx264 -crf 26 -c:a aac -b:a 128k -movflags +faststart out/web.mp4
ffmpeg -i master.mp4 -vf scale=1280:-2 -c:v libvpx-vp9 -crf 32 -b:v 0 -c:a libopus -b:a 96k out/web.webm
```

## Loudness

Normalize speech content to about -14 LUFS integrated (streaming norm), true peak -1.5 dB:

```bash
ffmpeg -i master.mp4 -c:v copy -af loudnorm=I=-14:TP=-1.5:LRA=11 -c:a aac -b:a 192k out/normalized.mp4
```

For broadcast, use -23 LUFS. For best accuracy, run `loudnorm` twice (measure with `print_format=json`, then apply the measured values).

## Batch script

`scripts/export_platforms.py` in this skill folder exports several targets in one run:

```bash
python scripts/export_platforms.py master.mp4 --targets youtube,x,linkedin,web --out out/
python scripts/export_platforms.py master.mp4 --targets vertical --dry-run
```

## Checklist

- Output opens in a browser `<video>` tag (H.264, yuv420p, faststart).
- File size is under the target limit (check with `ffprobe` or `ls -lh`).
- Captions are burned in for muted platforms, or an SRT is delivered alongside.
- Thumbnail exported separately (`thumbnails` skill).
