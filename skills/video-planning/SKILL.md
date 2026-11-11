---
name: video-planning
description: Plan a video before building it - brief, script, scene list, voiceover timing, asset checklist. Use when starting a new video from an idea, writing a narration script, storyboarding scenes, or estimating length and frame counts.
---

# Video Planning

Planning is cheaper than re-rendering. Produce these four artifacts before touching a tool.

## 1. Brief (5 lines)

```
Goal:      what the viewer should know or do afterwards
Audience:  who, and what they already know
Platform:  where it plays (sets aspect ratio, length, captions)
Length:    target seconds
Tone:      e.g. calm and precise / energetic / formal
```

## 2. Script

- Speaking pace: about **150 words per minute**, roughly **2.5 words per second**. Use 130 wpm for technical content.
- One idea per sentence. Short sentences. Write for the ear, so spell out numbers as they are spoken.
- Open with the payoff or the problem in the first 3 seconds. No logo sting first.
- End with one clear action.

Length check: `seconds = words / 2.5`. A 45 second video is about 110 words.

## 3. Scene list

Use a table. Each scene has narration, visual, and duration.

| # | Narration (words) | Visual | On-screen text | Sec |
|---|---|---|---|---|
| 1 | "Most builds fail on Friday." (5) | Red CI badge | none | 3 |
| 2 | ... | ... | ... | ... |

Rules:
- Duration of a scene = narration seconds + 0.5 s lead-in + 0.5 s tail. Visuals follow the voice, not the other way round.
- Change something visible every 3 to 6 seconds (cut, zoom, new element). Static frames over 8 seconds read as stalled.
- Leave 1 to 2 seconds of breathing room at the end.

## 4. Asset checklist

List every file needed, who supplies it, and its status: footage, screenshots, logo, fonts, music (license!), voiceover, captions. Flag anything with unclear licensing.

## Frame math (Remotion and similar)

```
frames = round(seconds * fps)          # 4.5 s at 30 fps = 135 frames
seconds = frames / fps
```

Decide fps once (30 is the safe default; 24 for cinematic; 60 only for screen motion).

## Hand-off

Save the plan as `PLAN.md` next to the project so it survives across sessions, then move to the build route chosen in `video-editing-router`.
