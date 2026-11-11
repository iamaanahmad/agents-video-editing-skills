---
name: screen-recording-demos
description: Record clean product and web app demos - scripted browser recording with Playwright, cursor and zoom polish, speed ramps, trimming dead time and syncing to narration. Use when the user wants a walkthrough, tutorial, UI demo or release video of a web app, or a repeatable recording.
---

# Screen Recording and Demos

A scripted recording is repeatable. When the UI changes you re-run the script instead of re-recording by hand.

## Pick the method

| Situation | Method |
|---|---|
| Web app you can open in a browser | Playwright scripted recording |
| Desktop app or full-screen workflow | OS recorder (OBS Studio, Windows Game Bar, macOS Screenshot) |
| App source is available and a polished, no-glitch result is wanted | Rebuild screens as static components in Remotion (see `remotion-programmatic-video`) |
| CLI | Terminal recorder (asciinema, VHS) or an animated terminal component |

## Playwright recording (Python)

```bash
pip install playwright && playwright install chromium
```

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    ctx = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        record_video_dir="recordings/",
        record_video_size={"width": 1920, "height": 1080},
    )
    page = ctx.new_page()
    page.goto("https://example.com")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(800)                       # let the viewer read
    page.get_by_role("button", name="Sign in").click()
    page.get_by_label("Email").type("demo@example.com", delay=60)   # visible typing
    page.wait_for_timeout(1200)
    ctx.close()                                      # video is finalized on close
    browser.close()
```

Output is WebM. Convert:

```bash
ffmpeg -i recordings/xyz.webm -c:v libx264 -crf 18 -pix_fmt yuv420p -r 30 out/demo.mp4
```

## Make it look good

- **Demo data:** use a seeded demo account with realistic, non-sensitive data. Never record real customer data, tokens, or emails.
- **Window:** fixed 1920x1080 viewport, hide bookmarks bars and notifications, light zoom (110 to 125 percent) so text is readable on a phone.
- **Pace:** pause 0.5 to 1 s after each action. Type with a delay. Avoid instant jumps.
- **Cursor:** Playwright does not draw a cursor. Inject a small DOM cursor, or add one in post (Remotion or an overlay).
- **Determinism:** wait on `expect(locator).to_be_visible()` rather than fixed sleeps, then add deliberate pauses for viewers.
- **Secrets:** blur or mask fields in the page script (`page.add_style_tag`) before recording.

## Post-production

```bash
# Cut dead time: keep 12 s to 41 s
ffmpeg -ss 12 -i demo.mp4 -t 29 -c:v libx264 -crf 18 out/trimmed.mp4

# Speed up boring waits (e.g. 4x from 20 s to 30 s) needs a split; simplest is to cut, speed, rejoin
# Zoom into a region: crop then scale (x:y:w:h in source pixels)
ffmpeg -i demo.mp4 -vf "crop=960:540:480:270,scale=1920:1080" out/zoom.mp4
```

For smooth animated zoom/pan follow the cursor, use Remotion (`interpolate` on `scale` and `translate`).

## Sync to narration

1. Write the script first (`video-planning`), record voiceover (`voiceover-tts`).
2. Record the screen, then adjust per-scene speed so each action lands on its sentence. Compute `speed = recorded_seconds / narration_seconds`.
3. Use `ffmpeg-essentials` speed recipes, or retime inside the composition.

## Checklist

- No personal data, API keys, or internal URLs visible.
- Text readable at 1080p scaled to a phone screen.
- No loading spinners longer than 1 second left in.
- Audio from the machine muted unless wanted.
