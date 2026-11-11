---
name: audio-mixing
description: Mix voiceover, background music and sound effects for video - ducking music under speech, fades, loudness normalization (LUFS), noise reduction and music selection. Use when audio sounds uneven, music overpowers speech, or the user asks to add or balance music.
---

# Audio Mixing

Speech must stay intelligible. Everything else supports it.

## Level targets

| Element | Level guide |
|---|---|
| Final mix, online video | about -14 LUFS integrated, true peak at most -1.5 dBTP |
| Final mix, podcast/voice-only | -16 LUFS |
| Final mix, broadcast (EBU R128) | -23 LUFS |
| Voice | Peaks around -6 dBFS before the final normalize |
| Music under speech | 15 to 25 dB below voice, roughly volume 0.08 to 0.2 |
| Music alone (intro/outro) | Raise to about 0.5 to 0.8 |

## Mix voice and music

```bash
ffmpeg -i voice.mp3 -i music.mp3 -filter_complex \
 "[1:a]volume=0.12,afade=t=in:st=0:d=2[m];[0:a][m]amix=inputs=2:duration=first:normalize=0[a]" \
 -map "[a]" -c:a aac -b:a 192k out/mix.m4a
```

`duration=first` ends the mix with the voice. `normalize=0` (recent FFmpeg) keeps your levels instead of dividing by input count.

## Auto-ducking (music dips when voice speaks)

```bash
ffmpeg -i voice.mp3 -i music.mp3 -filter_complex \
 "[0:a]asplit=2[vo][sc];\
  [1:a][sc]sidechaincompress=threshold=0.04:ratio=8:attack=20:release=400[duck];\
  [vo][duck]amix=inputs=2:duration=first:normalize=0[a]" \
 -map "[a]" out/ducked.m4a
```

Tune `threshold` (lower reacts to quieter speech) and `release` (longer is smoother). Set the music base level with `volume=` first so ducking has less to do.

## Put the mix on the video

```bash
ffmpeg -i video.mp4 -i out/mix.m4a -map 0:v -map 1:a -c:v copy -c:a aac -shortest out/final.mp4
```

## Fades

```bash
# Music: 2 s in, 3 s out at a known duration (60 s)
-af "afade=t=in:st=0:d=2,afade=t=out:st=57:d=3"
```

## Normalize loudness

```bash
# Single pass (quick)
ffmpeg -i in.mp4 -c:v copy -af loudnorm=I=-14:TP=-1.5:LRA=11 -c:a aac -b:a 192k out/loud.mp4

# Measure first for accuracy
ffmpeg -i in.mp4 -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null -
# then pass the measured_* values as measured_I, measured_TP, measured_LRA, measured_thresh with linear=true
```

## Clean noisy audio

```bash
ffmpeg -i in.wav -af "highpass=f=80,lowpass=f=12000,afftdn=nf=-25" out.wav
```

Over-denoising makes speech sound underwater. Reduce gently.

## Choosing music

- Pick instrumental tracks for voiceover. Vocals fight the narration.
- Match energy to the content, not to the platform trend.
- Check the license: royalty-free is not the same as free for commercial use. Keep attribution text if required.
- For AI-generated music, review the provider's commercial terms.

## Checks

- Play the first 10 seconds and a quiet passage. Is every word clear?
- Check on laptop speakers and on earbuds.
- Verify no clipping: `ffmpeg -i out.mp4 -af volumedetect -f null -` should show `max_volume` below 0 dB.
