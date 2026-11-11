# Compatibility

## How it works

Most current agents read the **Agent Skills** format: a folder with `SKILL.md` (YAML frontmatter with `name` and `description`, then a Markdown body). The agent loads only the name and description at startup, reads the body when a request matches, and opens bundled files on demand.

This repo uses only that portable core, so the same folder works everywhere. The installer copies the folders to each agent's directory. Agents that read plain instruction files get a short managed index that points to the skill files.

## Install targets

| Agent | Project skills dir | User skills dir | Instruction file(s) |
|---|---|---|---|
| Claude Code | `.claude/skills/` | `~/.claude/skills/` | `CLAUDE.md` |
| OpenAI Codex | `.agents/skills/` | `~/.agents/skills/` | `AGENTS.md` |
| Kiro | `.kiro/skills/` | `~/.kiro/skills/` | `.kiro/steering/video-editing-skills.md` |
| GitHub Copilot | `.github/skills/` | `~/.copilot/skills/` | `.github/copilot-instructions.md` |
| Antigravity | `.agents/skills/` | `~/.gemini/config/skills/` | `AGENTS.md`, `GEMINI.md` |
| Windsurf | `.windsurf/skills/` | `~/.codeium/windsurf/skills/` | `.windsurf/rules/video-editing-skills.md` |
| Cursor | `.cursor/skills/` | `~/.cursor/skills/` | `AGENTS.md` |
| Gemini CLI | `.gemini/skills/` | `~/.gemini/skills/` | `GEMINI.md` |
| Cline | `.cline/skills/` | `~/.cline/skills/` | `AGENTS.md` |
| OpenCode | `.opencode/skills/` | `~/.config/opencode/skills/` | `AGENTS.md` |
| Zed | `.agents/skills/` | none | `AGENTS.md` |

Project paths for Claude Code, Codex, Kiro and Copilot follow their published documentation. User-level paths for Copilot, Antigravity, Windsurf, Cursor, Cline and OpenCode are less settled and may differ by version. Run `--dry-run`, and if your tool looks elsewhere, edit the `AGENTS` table in `scripts/install.py` or copy the folders by hand.

Several tools also read `.agents/skills/` or `.claude/skills/` as a shared location, so one copy can serve more than one agent.

## Notes per agent

- **Kiro:** the default agent loads `.kiro/skills/` automatically. A custom agent must list skills in its `resources`, for example `skill://.kiro/skills/*/SKILL.md`. Skills also appear as slash commands.
- **Claude Code:** skills load by description match or by name as a slash command. `CLAUDE.md` is only written when you pass `--rules`.
- **Codex:** reads `AGENTS.md` and `.agents/skills/`. The managed block is appended to an existing `AGENTS.md`, never overwriting it.
- **Copilot:** reads `.github/copilot-instructions.md` and skill folders. Skills require a Copilot version that supports agent skills.
- **Windsurf:** the rules file uses `trigger: model_decision`, so the agent pulls it in when the task matches.
- **Zed:** has no skill folders. It reads `AGENTS.md`; the managed block lists the files under `.agents/skills/` for the agent to open.
- **Re-running** the installer replaces only the managed block (between the BEGIN and END comments). Your own content in the same file is untouched.

## Verify an install

1. List the target folder and confirm `<skill>/SKILL.md` exists.
2. Restart the agent or reload the window.
3. Ask something that should match, such as "make this video 9:16 with captions", and confirm the agent opens `vertical-shorts` or `video-editing-router`.

## Add another agent

Add an `Agent(...)` entry to `AGENTS` in `scripts/install.py`, then add a row to this table and to the README.
