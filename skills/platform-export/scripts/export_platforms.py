#!/usr/bin/env python3
"""Export a master video to several platform targets with FFmpeg.

Usage:
    python export_platforms.py master.mp4 --targets youtube,x,linkedin,web --out out/
    python export_platforms.py master.mp4 --targets vertical --dry-run

Only the standard library is used. FFmpeg must be on PATH.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

AAC = ["-c:a", "aac", "-b:a", "192k", "-ar", "48000"]
FAST = ["-movflags", "+faststart"]

# name -> (suffix, video filter or None, extra args)
TARGETS: dict[str, tuple[str, str | None, list[str]]] = {
    "youtube": (
        "youtube.mp4",
        None,
        ["-c:v", "libx264", "-preset", "slow", "-crf", "18", "-profile:v", "high", *AAC, *FAST],
    ),
    "vertical": (
        "vertical.mp4",
        "scale=1080:1920:force_original_aspect_ratio=decrease,"
        "pad=1080:1920:(ow-iw)/2:(oh-ih)/2",
        ["-c:v", "libx264", "-crf", "18", *AAC, *FAST],
    ),
    "x": (
        "x.mp4",
        "scale='min(1280,iw)':-2",
        ["-c:v", "libx264", "-preset", "medium", "-crf", "24", "-profile:v", "main",
         "-c:a", "aac", "-b:a", "128k", "-ar", "44100", *FAST],
    ),
    "linkedin": (
        "linkedin.mp4",
        "scale='min(1920,iw)':-2",
        ["-c:v", "libx264", "-crf", "22", *AAC, *FAST],
    ),
    "web": (
        "web.mp4",
        "scale=1280:-2",
        ["-c:v", "libx264", "-crf", "26", "-c:a", "aac", "-b:a", "128k", *FAST],
    ),
    "webm": (
        "web.webm",
        "scale=1280:-2",
        ["-c:v", "libvpx-vp9", "-crf", "32", "-b:v", "0", "-c:a", "libopus", "-b:a", "96k"],
    ),
}


def build_command(src: Path, dest: Path, vf: str | None, extra: list[str]) -> list[str]:
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-stats", "-y", "-i", str(src)]
    if vf:
        cmd += ["-vf", vf]
    cmd += extra + [str(dest)]
    return cmd


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("source", type=Path, help="master video file")
    parser.add_argument("--targets", default="youtube", help=f"comma list from: {', '.join(TARGETS)}")
    parser.add_argument("--out", type=Path, default=Path("out"), help="output directory (default: out)")
    parser.add_argument("--dry-run", action="store_true", help="print commands without running them")
    args = parser.parse_args()

    if not args.source.is_file():
        print(f"error: source not found: {args.source}", file=sys.stderr)
        return 2
    if not args.dry_run and shutil.which("ffmpeg") is None:
        print("error: ffmpeg not found on PATH", file=sys.stderr)
        return 2

    names = [t.strip() for t in args.targets.split(",") if t.strip()]
    unknown = [n for n in names if n not in TARGETS]
    if unknown:
        print(f"error: unknown target(s): {', '.join(unknown)}. Choose from: {', '.join(TARGETS)}", file=sys.stderr)
        return 2

    args.out.mkdir(parents=True, exist_ok=True)
    stem = args.source.stem
    failures = 0
    for name in names:
        suffix, vf, extra = TARGETS[name]
        dest = args.out / f"{stem}-{suffix}"
        if dest.resolve() == args.source.resolve():
            print(f"skip {name}: would overwrite the source", file=sys.stderr)
            failures += 1
            continue
        cmd = build_command(args.source, dest, vf, extra)
        print(f"[{name}] {dest}")
        if args.dry_run:
            print("  " + " ".join(cmd))
            continue
        result = subprocess.run(cmd)
        if result.returncode != 0:
            print(f"  failed: {name}", file=sys.stderr)
            failures += 1
        else:
            print(f"  ok: {dest.stat().st_size / 1_048_576:.1f} MB")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
