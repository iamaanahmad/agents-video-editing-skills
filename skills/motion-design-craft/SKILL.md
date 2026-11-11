---
name: motion-design-craft
description: Motion design rules for programmatic and edited video - durations, easing, springs, staggering, read time for on-screen text, beat grids, transitions and visual hierarchy, plus the defaults that make a video look AI-generated. Use when animating scenes, choosing timings, or reviewing a video that feels off.
---

# Motion Design Craft

Good motion is invisible: it directs attention and gets out of the way.

## Durations (at 30 fps)

| Motion | Frames | Seconds |
|---|---|---|
| Micro feedback (button press, highlight) | 4 to 8 | 0.15 to 0.25 |
| Element enter or exit | 10 to 18 | 0.35 to 0.6 |
| Scene transition | 12 to 20 | 0.4 to 0.7 |
| Large move across the screen | 20 to 30 | 0.7 to 1.0 |
| Stagger between list items | 3 to 6 | 0.1 to 0.2 |

Exits are faster than entrances (about 70 percent of the enter time). Longer than a second feels sluggish unless it is a deliberate reveal.

## Easing

Pick the ease by what the object is doing:

- **Entering** the frame: ease-out (fast start, soft landing).
- **Leaving** the frame: ease-in (slow start, accelerates away).
- **Moving between positions on screen:** ease-in-out.
- **Continuous** (loops, progress bars): linear.

Never use plain linear for UI-like motion; it reads as robotic.

## Springs

Use critically damped or slightly under-damped springs for natural settle. In Remotion, `damping: 200` is smooth with no bounce; lower damping (10 to 20) adds overshoot, appropriate for playful content only. Keep overshoot under about 10 percent.

## Read time for text

```
seconds_on_screen = max(1.5, words * 0.35 + 0.5)
```

A 6 word title needs about 2.6 seconds. If the voiceover reads the text, show it slightly before the voice says it.

## Rhythm

- Choose a beat (for example 0.5 s or one bar of the music) and align cuts and entrances to multiples of it. Misaligned motion feels sloppy even if viewers cannot say why.
- Vary scene length; identical durations feel mechanical.
- Cut on action: begin the next shot while motion from the previous one is still happening.

## Hierarchy

- One focal element at a time. Dim or blur what is not the subject.
- Body text at least 36 px on 1080p; titles 72 px or more. Phone viewers need larger.
- Contrast ratio at least 4.5:1 for text over backgrounds; add a scrim or outline over video.
- Margins: keep content inside the central 90 percent (safe area), 80 percent for vertical video.

## Transitions with a cause

Use a transition only when it says something: a wipe for a time shift, a push for the next step, a cross-fade for a gentle topic change. Otherwise use a straight cut. Do not mix more than two transition styles in one video.

## What makes a video look generated

Avoid these defaults unless chosen on purpose:

1. Everything fades in from 0 opacity with the same duration.
2. Centered text on a dark gradient with floating blobs.
3. A purple-blue gradient for every brand.
4. Every element bouncing with a spring.
5. Identical scene length and the same transition between all scenes.
6. Stock emoji used as icons.
7. Text that appears all at once, long before it is spoken.

Fixes: use the brand palette and real assets, vary motion by role, stagger meaningfully, and let some scenes just cut.

## Review checklist

- Can you pause any frame and see a clear subject?
- Does anything move without a reason?
- Is text readable at phone size?
- Does the last 2 seconds hold still long enough to read the call to action?
