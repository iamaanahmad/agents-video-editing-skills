#!/usr/bin/env python3
"""Probe a video file with ffprobe and flag common delivery problems.

Usage:
    python probe.py video.mp4
    python probe.py video.mp4 --expect-width 1920 --expect-height 1080 --expect-fps 30 --max-mb 50

Exit code 0 when all checks pass, 1 when any check fails, 2 on usage errors.
Only the standard library is used. ffprobe must be on PATH.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from fractions import Fraction
from pathlib import Path


def run_ffprobe(path: Path) -> dict:
    cmd = ["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "ffprobe failed")
    return json.loads(result.stdout)


def parse_fps(value: str | None) -> float | None:
    if not value or value == "0/0":
        return None
    try:
        return float(Fraction(value))
    except (ValueError, ZeroDivisionError):
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("video", type=Path)
    parser.add_argument("--expect-width", type=int)
    parser.add_argument("--expect-height", type=int)
    parser.add_argument("--expect-fps", type=float)
    parser.add_argument("--max-mb", type=float, help="maximum file size in MiB")
    parser.add_argument("--max-seconds", type=float, help="maximum duration")
    args = parser.parse_args()

    if not args.video.is_file():
        print(f"error: file not found: {args.video}", file=sys.stderr)
        return 2
    if shutil.which("ffprobe") is None:
        print("error: ffprobe not found on PATH (install FFmpeg)", file=sys.stderr)
        return 2

    try:
        info = run_ffprobe(args.video)
    except (RuntimeError, json.JSONDecodeError) as exc:
        print(f"FAIL  cannot read file: {exc}")
        return 1

    streams = info.get("streams", [])
    fmt = info.get("format", {})
    video = next((s for s in streams if s.get("codec_type") == "video"), None)
    audio = next((s for s in streams if s.get("codec_type") == "audio"), None)

    duration = float(fmt.get("duration", 0) or 0)
    size_mb = int(fmt.get("size", 0) or 0) / 1_048_576

    problems: list[str] = []
    warnings: list[str] = []

    print(f"file      {args.video}")
    print(f"duration  {duration:.2f} s")
    print(f"size      {size_mb:.2f} MiB")

    if video is None:
        problems.append("no video stream")
    else:
        w, h = video.get("width"), video.get("height")
        fps = parse_fps(video.get("avg_frame_rate")) or parse_fps(video.get("r_frame_rate"))
        pix = video.get("pix_fmt")
        codec = video.get("codec_name")
        print(f"video     {codec} {w}x{h} @ {fps:.2f} fps, {pix}" if fps else f"video     {codec} {w}x{h}, {pix}")

        if w and h and (w % 2 or h % 2):
            problems.append(f"odd dimensions {w}x{h} (many players and encoders need even sizes)")
        if pix and pix != "yuv420p":
            warnings.append(f"pixel format {pix} is not yuv420p; some browsers and phones will not play it")
        if codec and codec not in ("h264", "hevc", "vp9", "av1"):
            warnings.append(f"video codec {codec} is uncommon for delivery")
        if args.expect_width and w != args.expect_width:
            problems.append(f"width {w} != expected {args.expect_width}")
        if args.expect_height and h != args.expect_height:
            problems.append(f"height {h} != expected {args.expect_height}")
        if args.expect_fps and fps and abs(fps - args.expect_fps) > 0.05:
            problems.append(f"fps {fps:.2f} != expected {args.expect_fps}")
        r_fps = parse_fps(video.get("r_frame_rate"))
        a_fps = parse_fps(video.get("avg_frame_rate"))
        if r_fps and a_fps and abs(r_fps - a_fps) > 0.5:
            warnings.append("variable frame rate suspected (r_frame_rate differs from avg_frame_rate)")

    if audio is None:
        warnings.append("no audio stream")
    else:
        print(f"audio     {audio.get('codec_name')} {audio.get('sample_rate')} Hz, {audio.get('channels')} ch")
        if audio.get("codec_name") not in ("aac", "opus", "mp3", "vorbis"):
            warnings.append(f"audio codec {audio.get('codec_name')} is uncommon for delivery")

    if duration <= 0:
        problems.append("duration is zero or unknown")
    if args.max_mb and size_mb > args.max_mb:
        problems.append(f"size {size_mb:.1f} MiB exceeds limit {args.max_mb} MiB")
    if args.max_seconds and duration > args.max_seconds:
        problems.append(f"duration {duration:.1f} s exceeds limit {args.max_seconds} s")

    print()
    for w_ in warnings:
        print(f"WARN  {w_}")
    for p_ in problems:
        print(f"FAIL  {p_}")
    if not problems and not warnings:
        print("OK    all checks passed")
    elif not problems:
        print("OK    passed with warnings")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
