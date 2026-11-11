---
name: ffmpeg-essentials
description: Core FFmpeg and ffprobe recipes for trimming, joining, converting, resizing, compressing, speed changes, fades, audio extraction and GIF conversion. Use for any direct media transformation task, or when a video will not play, has odd dimensions, or is out of sync.
---

# FFmpeg Essentials

Always probe first, never overwrite the input, and re-encode when cutting unless told otherwise.

## Probe

```bash
# Human summary
ffprobe -v error -show_entries stream=codec_type,codec_name,width,height,r_frame_rate,sample_rate -show_entries format=duration,size -of default=nw=1 input.mp4

# Machine readable
ffprobe -v quiet -print_format json -show_format -show_streams input.mp4
```

## Trim

```bash
# Start at 30 s, keep 15 s. Re-encode: accurate and safe.
ffmpeg -i input.mp4 -ss 00:00:30 -t 15 -c:v libx264 -crf 20 -c:a aac out/clip.mp4

# Fast, no re-encode. Only lands on keyframes, so the start can be off by seconds.
ffmpeg -ss 00:00:30 -i input.mp4 -t 15 -c copy out/clip.mp4
```

`-ss` before `-i` seeks fast. After `-i` it seeks accurately but slower. For re-encodes, either is fine on modern FFmpeg.

## Join

```bash
# Same codec, resolution, fps: instant, lossless
printf "file 'a.mp4'\nfile 'b.mp4'\n" > list.txt
ffmpeg -f concat -safe 0 -i list.txt -c copy out/joined.mp4

# Different sources: normalize while joining
ffmpeg -i a.mp4 -i b.mp4 -filter_complex \
 "[0:v]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,fps=30,setsar=1[v0];\
  [1:v]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,fps=30,setsar=1[v1];\
  [0:a][1:a]concat=n=2:v=1:a=1[v][a]" \
 -map "[v]" -map "[a]" -c:v libx264 -crf 20 -c:a aac out/joined.mp4
```

PowerShell: write `list.txt` with `Set-Content`, and use backtick line continuation or one long line instead of `\`.

## Resize and reframe

```bash
# Fit inside 1920x1080 with bars
-vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2"
# Fill 1920x1080, crop overflow
-vf "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080"
# Width 1280, height automatic and even
-vf "scale=1280:-2"
```

## Compress

```bash
ffmpeg -i input.mp4 -c:v libx264 -crf 23 -preset medium -c:a aac -b:a 128k -movflags +faststart out/small.mp4
```

| Purpose | CRF | Preset |
|---|---|---|
| Master / archive | 16-18 | slow |
| Production | 20-22 | medium |
| Web / preview | 23-26 | fast |
| Quick draft | 28+ | veryfast |

Lower CRF means higher quality and a bigger file. For a target size, use two-pass `-b:v` instead of CRF.

## Speed

```bash
# 2x faster, video and audio
ffmpeg -i in.mp4 -filter_complex "[0:v]setpts=0.5*PTS[v];[0:a]atempo=2.0[a]" -map "[v]" -map "[a]" out/fast.mp4
# 0.5x slow motion
ffmpeg -i in.mp4 -filter_complex "[0:v]setpts=2.0*PTS[v];[0:a]atempo=0.5[a]" -map "[v]" -map "[a]" out/slow.mp4
# Video only
ffmpeg -i in.mp4 -an -filter:v "setpts=0.25*PTS" out/timelapse.mp4
```

`setpts` multiplier = 1 / speed. `atempo` accepts 0.5 to 2.0 per filter, so chain for more: `atempo=2.0,atempo=2.0` for 4x.

## Fades

```bash
# 1 s in, 1 s out on a 10 s clip
ffmpeg -i in.mp4 -vf "fade=t=in:st=0:d=1,fade=t=out:st=9:d=1" -af "afade=t=in:st=0:d=1,afade=t=out:st=9:d=1" out/faded.mp4
```

## Audio

```bash
ffmpeg -i in.mp4 -vn -c:a libmp3lame -q:a 2 out/audio.mp3      # extract mp3
ffmpeg -i in.mp4 -vn -c:a copy out/audio.m4a                   # extract without re-encode (AAC source)
ffmpeg -i video.mp4 -i voice.wav -map 0:v -map 1:a -c:v copy -c:a aac -shortest out/dubbed.mp4   # replace audio
ffmpeg -i in.mp4 -an -c:v copy out/silent.mp4                  # remove audio
```

## GIF

```bash
ffmpeg -i in.mp4 -t 5 -vf "fps=15,scale=480:-1:flags=lanczos,split[a][b];[a]palettegen[p];[b][p]paletteuse" out/preview.gif
```

## Images

```bash
ffmpeg -ss 5 -i in.mp4 -frames:v 1 -q:v 2 out/frame.jpg          # one frame
ffmpeg -framerate 30 -i frames/%04d.png -c:v libx264 -pix_fmt yuv420p out/from-frames.mp4
ffmpeg -loop 1 -i still.png -t 5 -c:v libx264 -pix_fmt yuv420p -r 30 out/still.mp4
```

## Troubleshooting

| Symptom | Fix |
|---|---|
| `height not divisible by 2` | Add `scale=trunc(iw/2)*2:trunc(ih/2)*2` |
| Plays in VLC, not in browser or phone | `-c:v libx264 -pix_fmt yuv420p -movflags +faststart` |
| Audio drifts after speed change | Use `setpts` and `atempo` together in `filter_complex` |
| Audio drifts on variable frame rate phone clips | Add `-vsync cfr -r 30` (or `-fps_mode cfr`) |
| Black first frames after `-c copy` trim | Re-encode instead of stream copy |
| Output is 0 bytes | Read the full error with `-v error`; check stream mapping |
| Paths with spaces | Quote them: `"my clip.mp4"` |
| Overwrite prompt blocks automation | Add `-y` (overwrite) or `-n` (never) |

## Safety habits

- Write to `out/`, never to the input path.
- Add `-hide_banner -loglevel error` in scripts, `-stats` to see progress.
- Check the result with `ffprobe` and the `video-qa` skill.
