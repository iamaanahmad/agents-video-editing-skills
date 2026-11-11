# AGENTS.md

Instructions for AI agents working on **this repository** (not for end users; users install skills with `scripts/install.py`).

## What this repo is

A collection of agent-neutral video editing skills. `skills/<name>/SKILL.md` is the single source of truth. Everything else (installer, validator, docs) supports it.

## Rules for changes

1. A skill is a folder `skills/<name>/` with `SKILL.md`. Optional: `scripts/`, `references/`, `assets/`.
2. Frontmatter is exactly `name` and `description`. No other keys (portability).
   - `name` equals the folder name: lowercase letters, digits, hyphens, at most 64 chars.
   - `description` says what the skill does and when to use it, at most 1024 chars.
3. Keep `SKILL.md` under 500 lines. Move depth to `references/` and link to it with a relative path.
4. Skills must be agent-neutral: no tool-specific slash commands or paths (`.claude/...`) in skill bodies.
5. Commands must be correct for the stated tool version. Prefer FFmpeg, Python and Node; mark paid or cloud services as optional.
6. Helper scripts use only the Python standard library, accept `--help`, and return meaningful exit codes.
7. Never add secrets, real API keys, or personal data.

## Verify before finishing

```bash
python scripts/validate.py
python scripts/install.py --agent all --rules --project <temp dir> --dry-run
```

If you changed a bundled script, run it against a small generated clip, for example:

```bash
ffmpeg -f lavfi -i testsrc=duration=3:size=1280x720:rate=30 -pix_fmt yuv420p test.mp4
```

## Adding an agent

Add an entry to `AGENTS` in `scripts/install.py` (project skills directory, user skills directory, instruction files) and a row in `README.md` and `docs/compatibility.md`.
