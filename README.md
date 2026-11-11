# Agent Video Editing Skills: AI video editing and Remotion skills for Claude, Codex, Kiro and more

[![validate](https://github.com/iamaanahmad/agents-video-editing-skills/actions/workflows/validate.yml/badge.svg)](https://github.com/iamaanahmad/agents-video-editing-skills/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**agents-video-editing-skills** is an open-source collection of video editing skills for AI coding agents. It works as a video editing skill for Claude Code, and as an AI video editing skill for OpenAI Codex, Kiro, GitHub Copilot, Antigravity, Windsurf, Cursor, Gemini CLI, Cline, OpenCode and Zed.

Each skill is an open-standard `SKILL.md` folder. One installer puts them where each agent looks for them. Your agent then gets practical playbooks for FFmpeg, Remotion, moviepy, captions, voiceover, audio mixing, screen recordings, vertical shorts, platform export and quality checks.

**Jump to:** [Quick start](#quick-start) · [Skills](#skills) · [Remotion agent skill](#remotion-agent-skill) · [Supported agents](#where-each-agent-reads-from) · [FAQ](#faq)

## What you can ask your agent to do

- "Trim the first 10 seconds, add captions, and export for LinkedIn."
- "Turn this 16:9 recording into a 9:16 Short with burned-in word captions."
- "Build a 30 second Remotion explainer from this script, synced to the voiceover."
- "Mix music under the narration and normalize the loudness to -14 LUFS."
- "Record a scripted demo of my web app and cut out the dead time."
- "Check this render before I send it: resolution, audio, black frames."

## Quick start

Requires Python 3.9+ (standard library only). Skills themselves use FFmpeg, and some use Node.js or Python packages. Each skill says which.

```bash
git clone https://github.com/iamaanahmad/agents-video-editing-skills
cd agents-video-editing-skills

# See what will be written, without writing anything
python scripts/install.py --agent claude,kiro,codex --project /path/to/your/project --dry-run

# Install into a project (skills + instruction files)
python scripts/install.py --agent claude,kiro,codex,copilot --rules --project /path/to/your/project

# Install for every project on your machine
python scripts/install.py --agent claude,kiro --scope user

# Everything, kept in sync with this repo via symlinks
python scripts/install.py --agent all --rules --symlink --project /path/to/your/project
```

Then restart the agent or reload the window, and ask for a video task, for example: "Trim the first 10 seconds off `demo.mp4`, add captions, and export for LinkedIn."

Windows PowerShell works the same way; use `python` and forward-slash or quoted paths, for example `--project "C:\work\my-app"`.

Verify an install by listing the target folder (for example `.claude/skills/ffmpeg-essentials/SKILL.md` should exist), restarting the agent, and asking for a video task.

## Skills

| Skill | What it covers |
|---|---|
| `video-editing-router` | Start here. Picks the route and companion skills |
| `video-planning` | Brief, script, scene list, frame math |
| `ffmpeg-essentials` | Trim, join, resize, compress, speed, fades, GIF, troubleshooting |
| `platform-export` | YouTube, X, LinkedIn, Instagram, TikTok, web. Ships `export_platforms.py` |
| `remotion-programmatic-video` | Videos as React code, narration-synced scenes |
| `moviepy-python-video` | Python composition (moviepy 2.x), text overlays |
| `captions-subtitles` | Whisper, SRT/ASS, burned-in and word-highlight captions |
| `voiceover-tts` | TTS engines, per-scene audio, pacing, cleanup |
| `audio-mixing` | Ducking, loudness (LUFS), noise cleanup, music |
| `screen-recording-demos` | Scripted Playwright recordings, polish, sync |
| `vertical-shorts` | 9:16 reframing, safe zones, hooks |
| `motion-design-craft` | Timing, easing, springs, hierarchy, anti-"AI look" rules |
| `thumbnails` | Frame picking, contact sheets, text compositing |
| `video-qa` | Probe, detectors, pass criteria. Ships `probe.py` |

## Remotion agent skill

`remotion-programmatic-video` is a Remotion skill for Claude Code, Codex, Kiro and the other supported agents. It teaches an agent to build videos as React code: compositions, sequences, springs and `interpolate`, `staticFile` assets, scene lengths derived from the voiceover, transitions, and CLI rendering. `motion-design-craft` adds timing and easing rules so the result does not look generated.

**Using it with the official skills.** [remotion-dev/skills](https://github.com/remotion-dev/skills) is Remotion's own agent skill repository and the right source for deep, version-accurate Remotion API knowledge. This project does not replace it. It covers the surrounding workflow: planning, voiceover, captions, audio mixing, platform export and QA. Install both:

```bash
# Official Remotion skills
npx skills add remotion-dev/skills

# This repo's video editing workflow skills
python scripts/install.py --agent claude,codex,kiro --rules --project /path/to/your/project
```

Check the official repository's README for its current install command.

## Where each agent reads from

| Agent | Skills (project) | Instruction file written by `--rules` |
|---|---|---|
| Claude Code | `.claude/skills/` | `CLAUDE.md` |
| OpenAI Codex | `.agents/skills/` | `AGENTS.md` |
| Kiro | `.kiro/skills/` | `.kiro/steering/video-editing-skills.md` |
| GitHub Copilot | `.github/skills/` | `.github/copilot-instructions.md` |
| Antigravity | `.agents/skills/` | `AGENTS.md`, `GEMINI.md` |
| Windsurf | `.windsurf/skills/` | `.windsurf/rules/video-editing-skills.md` |
| Cursor | `.cursor/skills/` | `AGENTS.md` |
| Gemini CLI | `.gemini/skills/` | `GEMINI.md` |
| Cline | `.cline/skills/` | `AGENTS.md` |
| OpenCode | `.opencode/skills/` | `AGENTS.md` |
| Zed | `.agents/skills/` | `AGENTS.md` (Zed has no skill folders; the rules point to them) |

Tools change their paths. `python scripts/install.py --list` shows what the installer will use. See [docs/compatibility.md](docs/compatibility.md) for details and how to add an agent.

## Repository layout

```
skills/<name>/SKILL.md     canonical skills (the only source of truth)
skills/<name>/scripts/     small helper scripts a skill can run
scripts/install.py         installer for all agents
scripts/validate.py        checks every skill against the portable core
AGENTS.md                  instructions for working on this repo
docs/                      compatibility notes
```

## Design rules

- **Portable core only.** Frontmatter has `name` and `description`, nothing else. Works in every agent.
- **Progressive disclosure.** Short description to trigger, full playbook on activation, scripts and references on demand.
- **Safe by default.** Skills probe inputs, never overwrite sources, and end with QA.
- **No lock-in.** Skills prefer free, standard tools (FFmpeg, Python, Node). Paid APIs are options, never requirements.

## Requirements

| Tool | Needed for |
|---|---|
| Python 3.9+ | installer, validator, helper scripts (standard library only) |
| FFmpeg and ffprobe | most skills |
| Node.js (current LTS) | Remotion |
| `moviepy>=2`, `pillow` | moviepy skill |
| `openai-whisper` or `faster-whisper` | transcription in the captions skill |
| `playwright` | scripted screen recordings |

Skills check for what they need and say so before running.

## FAQ

### What is an agent video editing skill?

A skill is a folder with a `SKILL.md` file: a name, a description of when to use it, and a step-by-step playbook. The agent reads only the name and description at startup, loads the full instructions when your request matches, and opens bundled scripts only when needed. A video editing skill gives the agent tested FFmpeg commands, render settings and checks instead of letting it guess.

### Is this a video editing skill for Claude Code?

Yes. Install with `--agent claude` and the skills land in `.claude/skills/`. The same folders also work in Codex, Kiro, Copilot and the other agents listed above, so you write nothing twice.

### Is this a Remotion skill for Claude?

The `remotion-programmatic-video` skill works in Claude Code and every other supported agent. For the most complete Remotion API reference, also install the official [remotion-dev/skills](https://github.com/remotion-dev/skills).

### Does it edit video itself?

No. It instructs your agent, which then runs FFmpeg, Remotion, moviepy or Playwright on your machine. Nothing is uploaded by this project.

### Which tools do I need?

FFmpeg for most skills, plus Node.js for Remotion or Python packages for moviepy and Whisper. See [Requirements](#requirements).

### Are there paid services involved?

No. Voiceover and music skills list cloud options (such as ElevenLabs) and local ones (Kokoro, Piper). Cloud services are optional and need your own API keys.

### How do I add another agent or skill?

See [docs/compatibility.md](docs/compatibility.md) and [CONTRIBUTING.md](CONTRIBUTING.md).

## Related projects

- [remotion-dev/skills](https://github.com/remotion-dev/skills): official Remotion agent skills.
- [claude-code-video-toolkit](https://github.com/digitalsamba/claude-code-video-toolkit): the Claude Code video toolkit that inspired this project.
- [Agent Skills specification](https://agentskills.io): the open format these skills follow.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Run `python scripts/validate.py` before opening a pull request. Stars and issues help others find the project.

## License and credits

MIT. Started from ideas and workflows in [claude-code-video-toolkit](https://github.com/digitalsamba/claude-code-video-toolkit) by Digital Samba (MIT). See [NOTICE.md](NOTICE.md).
