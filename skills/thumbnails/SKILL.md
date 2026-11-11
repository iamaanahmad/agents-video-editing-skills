---
name: thumbnails
description: Create video thumbnails, cover images, contact sheets and poster frames - extract the best frame with FFmpeg, composite text and logo, and size for YouTube and social. Use when the user asks for a thumbnail, cover, poster frame, preview image or a visual overview of a video.
---

# Thumbnails and Poster Frames

## Extract frames

```bash
# One frame at 12.5 s
ffmpeg -ss 12.5 -i in.mp4 -frames:v 1 -q:v 2 out/frame.jpg

# Candidate frames every 5 s
ffmpeg -i in.mp4 -vf "fps=1/5" -q:v 2 out/cand-%03d.jpg

# Contact sheet: one frame every 10 s, 4 columns
ffmpeg -i in.mp4 -vf "fps=1/10,scale=320:-1,tile=4x3" -frames:v 1 out/contact-sheet.jpg
```

Use the contact sheet to review a whole video at a glance (also useful for QA).

## Pick a frame

- Clear single subject, face visible and eyes open, if there is a person.
- Not a transition, blur, or half-faded frame.
- Strong contrast and room for text on one side.

## Size

| Use | Size | Format |
|---|---|---|
| YouTube | 1280x720 (16:9), under 2 MB | JPG or PNG |
| Vertical cover | 1080x1920 | JPG |
| Open Graph / link preview | 1200x630 | JPG or PNG |
| Square | 1080x1080 | JPG |

## Add text with Pillow

```python
from PIL import Image, ImageDraw, ImageFont, ImageFilter

img = Image.open("out/frame.jpg").convert("RGB").resize((1280, 720))
shade = Image.new("RGBA", img.size, (0, 0, 0, 0))
ImageDraw.Draw(shade).rectangle([0, 360, 700, 720], fill=(0, 0, 0, 140))   # scrim for contrast
img = Image.alpha_composite(img.convert("RGBA"), shade).convert("RGB")

font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 96)
d = ImageDraw.Draw(img)
d.text((60, 440), "Fix builds\nin 5 min", font=font, fill="white", stroke_width=4, stroke_fill="black")
img.save("out/thumbnail.jpg", quality=92)
```

## Text rules

- 3 to 5 words, large enough to read at 160 px wide (a phone feed size).
- Do not repeat the title word for word; add a different angle.
- High contrast; use a scrim or outline instead of a thin font on a busy photo.
- Keep the bottom-right corner clear on YouTube (the duration badge sits there).

## Keep it honest

The thumbnail must reflect the video content. Misleading covers harm trust and can break platform rules.

## Optimize

```bash
ffmpeg -i out/thumbnail.png -q:v 3 out/thumbnail.jpg      # shrink under size limits
```
