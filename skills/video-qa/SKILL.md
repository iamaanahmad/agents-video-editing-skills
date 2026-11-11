---
name: video-qa
description: Quality-check a rendered video before delivery - probe resolution, fps, duration, codecs, loudness and clipping, detect black frames and silence, build a contact sheet, and verify playback compatibility. Use after any render or export, or when the user says a video looks or sounds wrong.
---

# Video QA

Never deliver a file you have not inspected. A successful exit code is not proof.

## 1. Run the probe script

```bash
python scripts/probe.py out/final.mp4
python scripts/probe.py out/final.mp4 --expect-width 1920 --expect-height 1080 --expect-fps 30 --max-mb 50
```

It prints video and audio stream details, duration, size, and flags problems (odd dimensions, missing audio, non-`yuv420p`, no faststart hint, mismatches against expectations). Exit code is non-zero when a check fails.

## 2. Look at it

```bash
# Contact sheet: see the whole video at a glance
ffmpeg -i out/final.mp4 -vf "fps=1/5,scale=320:-1,tile=5x4" -frames:v 1 out/qa-sheet.jpg
```

View the sheet. Check for cut-off text, wrong frames, flashes, stretched aspect, and black ends.

## 3. Automated detectors

```bash
# Black frames (min 0.5 s)
ffmpeg -i out/final.mp4 -vf blackdetect=d=0.5:pix_th=0.10 -an -f null - 2>&1 | grep blackdetect

# Silence longer than 1.5 s
ffmpeg -i out/final.mp4 -af silencedetect=noise=-40dB:d=1.5 -vn -f null - 2>&1 | grep silence_

# Frozen video
ffmpeg -i out/final.mp4 -vf freezedetect=n=-60dB:d=2 -an -f null - 2>&1 | grep freeze

# Loudness and peaks
ffmpeg -i out/final.mp4 -af ebur128=peak=true -vn -f null - 2>&1 | tail -12
ffmpeg -i out/final.mp4 -af volumedetect -vn -f null - 2>&1 | grep -E "mean_volume|max_volume"
```

PowerShell: replace `grep X` with `Select-String X` (and merge stderr with `2>&1`).

## 4. Pass criteria

| Check | Pass |
|---|---|
| Container opens, duration matches plan (within 1 s) | yes |
| Resolution and aspect match the target platform | yes |
| fps constant and as planned | yes |
| Pixel format `yuv420p`, H.264 + AAC for broad playback | yes |
| Integrated loudness near target (-14 LUFS online) and true peak at most -1 dBTP | yes |
| No unintended black, silent or frozen sections | yes |
| Captions present where required and inside safe area | yes |
| Spelling of names, numbers, URLs verified | yes |
| File size under platform limit | yes |

## 5. Report

Tell the user: path, duration, resolution, fps, codecs, size, loudness, and anything you could not check (for example subjective pacing or whether music licensing is cleared). If a check failed, fix and re-run before sending.

## Common fixes

| Finding | Fix |
|---|---|
| Odd dimensions | `scale=trunc(iw/2)*2:trunc(ih/2)*2` |
| No audio track | Map the audio stream explicitly with `-map` |
| Won't stream in browser | `-movflags +faststart -pix_fmt yuv420p` |
| Too loud / clipping | `loudnorm` (see `audio-mixing`) |
| Variable frame rate | `-fps_mode cfr -r 30` |
