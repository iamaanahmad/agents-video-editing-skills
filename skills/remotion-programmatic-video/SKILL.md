---
name: remotion-programmatic-video
description: Build videos as React code with Remotion - compositions, sequences, springs, interpolation, audio sync, data-driven props, studio preview and rendering to MP4. Use for explainers, product demos, release notes, data charts, branded templates, or any video that should be reproducible from code.
---

# Remotion (Programmatic Video)

Remotion renders React components frame by frame. Every frame is a pure function of the frame number, so animation is deterministic and re-renderable.

> Remotion's API changes between major versions. Read the installed version (`npm ls remotion`) and the official docs at remotion.dev before using an API you are unsure about. Check Remotion's license terms for commercial use by companies.

## Setup

```bash
npx create-video@latest          # choose the blank template (TypeScript)
cd my-video && npm install
npx remotion studio              # live preview
npx remotion render MyComp out/video.mp4
npx remotion still MyComp out/thumb.png --frame=45
```

## The mental model

- `useCurrentFrame()` gives the current frame, starting at 0.
- `useVideoConfig()` gives `fps`, `width`, `height`, `durationInFrames`.
- Nothing animates by itself. You compute style from the frame.
- Never use CSS transitions, `setTimeout`, `Math.random()` or `Date.now()` for animation. They break render determinism. Use `random('seed')` from remotion instead.

## Composition

```tsx
// src/Root.tsx
import {Composition} from 'remotion';
import {Explainer} from './Explainer';

export const RemotionRoot = () => (
  <Composition
    id="Explainer"
    component={Explainer}
    durationInFrames={30 * 20}   // 20 s at 30 fps
    fps={30}
    width={1920}
    height={1080}
    defaultProps={{title: 'Hello'}}
  />
);
```

## Animation primitives

```tsx
import {AbsoluteFill, Sequence, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';

export const Title: React.FC<{text: string}> = ({text}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const opacity = interpolate(frame, [0, 15], [0, 1], {extrapolateRight: 'clamp'});
  const scale = spring({frame, fps, config: {damping: 200}});   // smooth, no bounce

  return (
    <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center'}}>
      <h1 style={{opacity, transform: `scale(${0.9 + 0.1 * scale})`, fontSize: 96}}>{text}</h1>
    </AbsoluteFill>
  );
};

export const Explainer = () => (
  <AbsoluteFill style={{backgroundColor: '#0b1020', color: 'white'}}>
    <Sequence from={0} durationInFrames={90}><Title text="Intro" /></Sequence>
    <Sequence from={90} durationInFrames={120}><Title text="Main point" /></Sequence>
  </AbsoluteFill>
);
```

Always pass `extrapolateLeft/Right: 'clamp'` to `interpolate` unless you want values to run past the range.

## Media

```tsx
import {staticFile, Audio, OffthreadVideo, Img} from 'remotion';

<Audio src={staticFile('voiceover.mp3')} />
<Audio src={staticFile('music.mp3')} volume={0.12} />
<OffthreadVideo src={staticFile('demo.mp4')} />
<Img src={staticFile('logo.png')} />
```

Put assets in `public/` and reference them with `staticFile()`. Use `<Img>` rather than `<img>` so rendering waits for the image. Newer Remotion versions provide updated media components; check the docs for the installed version.

## Sync scenes to narration

Do not hardcode scene lengths. Derive them from the audio.

1. Generate per-scene voiceover files (`voiceover-tts` skill).
2. Measure each duration with `ffprobe` and write `scenes.json` with `{id, audio, seconds}`.
3. In the composition, convert with `Math.ceil((seconds + 0.5) * fps)` and lay out `<Sequence>` by cumulative offset.
4. Use `calculateMetadata` on the `<Composition>` to set the total `durationInFrames` from that data.

If the voice is re-recorded, the video retimes itself.

## Transitions

Install `@remotion/transitions` and use `TransitionSeries` with `fade()`, `slide()`, `wipe()`. A transition overlaps its two scenes, so total length shrinks by the transition duration. Keep transitions 12 to 20 frames at 30 fps.

## Fonts and brand

Load fonts with `@remotion/google-fonts` or `@remotion/fonts` so they are ready before the first frame. Keep colors, fonts and logo in one `brand.ts` so a rebrand is a one-file change.

## Performance and rendering

- Preview in the studio; render from the CLI.
- `--concurrency=50%` limits CPU use. `--codec=h264` is default; use `--codec=prores` for editing handoff.
- Heavy blur, shadows and large SVG filters are slow. Prefer pre-rendered assets for those.
- Use `<OffthreadVideo>` instead of `<video>` for source footage to get frame-accurate extraction.
- For quick drafts: `--scale=0.5` and a `--frames=0-90` range.

## Common mistakes

| Mistake | Fix |
|---|---|
| Flicker or missing image at render | Use `<Img>`, `staticFile`, and `delayRender` for async data |
| Animation differs between preview and render | Remove non-deterministic code (time, random) |
| Text overflows on different locales | Set explicit widths; test the longest string |
| Video too long after adding transitions | Subtract transition frames from the total |
| Audio is silent in render | Check the file path and that the `<Audio>` is inside an active `<Sequence>` |

Pair with `motion-design-craft` for timing and easing choices.
