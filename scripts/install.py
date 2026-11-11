#!/usr/bin/env python3
"""Install the video editing skills into the agents and IDEs you use.

Examples:
    python scripts/install.py --list
    python scripts/install.py --agent claude,kiro,codex --project C:/work/my-app
    python scripts/install.py --agent all --rules --project .
    python scripts/install.py --agent claude --scope user
    python scripts/install.py --agent copilot --dry-run

What it does
  1. Copies (or symlinks) every folder in skills/ into each agent's skills directory.
  2. With --rules, writes a managed block that lists the skills into the instruction
     file each agent reads (AGENTS.md, CLAUDE.md, GEMINI.md, copilot-instructions.md,
     Kiro steering, Windsurf rules). The block is replaced on re-run, never duplicated.

Only the standard library is used.
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

from skills_lib import Skill, load_skills

BEGIN = "<!-- BEGIN agents-video-editing-skills (managed) -->"
END = "<!-- END agents-video-editing-skills (managed) -->"
HOME = Path.home()


@dataclass(frozen=True)
class Agent:
    key: str
    label: str
    project_skills: str          # relative to project root
    user_skills: Path | None     # absolute
    rule_files: tuple[str, ...]  # relative to project root, instruction files to manage
    note: str = ""


# Skills locations follow each tool's documented convention. Tools change; run --list
# to see what will be written, and use --dry-run before the first install.
AGENTS: dict[str, Agent] = {
    "claude": Agent("claude", "Claude Code", ".claude/skills", HOME / ".claude/skills", ("CLAUDE.md",)),
    "codex": Agent("codex", "OpenAI Codex", ".agents/skills", HOME / ".agents/skills", ("AGENTS.md",)),
    "kiro": Agent("kiro", "Kiro", ".kiro/skills", HOME / ".kiro/skills", (".kiro/steering/video-editing-skills.md",)),
    "copilot": Agent("copilot", "GitHub Copilot", ".github/skills", HOME / ".copilot/skills", (".github/copilot-instructions.md",)),
    "antigravity": Agent("antigravity", "Google Antigravity", ".agents/skills", HOME / ".gemini/config/skills", ("AGENTS.md", "GEMINI.md")),
    "windsurf": Agent("windsurf", "Windsurf", ".windsurf/skills", HOME / ".codeium/windsurf/skills", (".windsurf/rules/video-editing-skills.md",)),
    "cursor": Agent("cursor", "Cursor", ".cursor/skills", HOME / ".cursor/skills", ("AGENTS.md",)),
    "gemini": Agent("gemini", "Gemini CLI", ".gemini/skills", HOME / ".gemini/skills", ("GEMINI.md",)),
    "cline": Agent("cline", "Cline", ".cline/skills", HOME / ".cline/skills", ("AGENTS.md",)),
    "opencode": Agent("opencode", "OpenCode", ".opencode/skills", HOME / ".config/opencode/skills", ("AGENTS.md",)),
    "zed": Agent("zed", "Zed", ".agents/skills", None, ("AGENTS.md",),
                 "Zed reads AGENTS.md rules, not skill folders; the block points the agent at .agents/skills."),
}


def md_block(skills: list[Skill], skills_rel: str) -> str:
    lines = [
        BEGIN,
        "## Video editing skills",
        "",
        "For any video creation or editing task, start with `video-editing-router`, then read the",
        "matching skill file below before acting. Probe inputs first, never overwrite sources, and",
        "run `video-qa` before delivering.",
        "",
        "| Skill | Use when | File |",
        "|---|---|---|",
    ]
    for s in skills:
        desc = s.description.replace("|", "\\|")
        short = desc if len(desc) <= 140 else desc[:137].rsplit(" ", 1)[0] + "..."
        lines.append(f"| `{s.name}` | {short} | `{skills_rel}/{s.name}/SKILL.md` |")
    lines += ["", END]
    return "\n".join(lines) + "\n"


def wrap_special(path: str, block: str) -> tuple[str, str]:
    """Return (header, block) with any front matter an agent-specific file needs."""
    if path.startswith(".kiro/steering/"):
        header = ("---\ninclusion: auto\nname: video-editing-skills\n"
                  "description: Video creation and editing workflows - FFmpeg, Remotion, moviepy, captions, voiceover, export, QA.\n---\n\n")
        return header, block
    if path.startswith(".windsurf/rules/"):
        header = ("---\ntrigger: model_decision\n"
                  "description: Video creation and editing workflows - FFmpeg, Remotion, moviepy, captions, voiceover, export, QA.\n---\n\n")
        return header, block
    return "", block


def merge_block(existing: str, header: str, block: str) -> str:
    if BEGIN in existing and END in existing:
        start = existing.index(BEGIN)
        end = existing.index(END) + len(END)
        tail = existing[end:].lstrip("\n")
        merged = existing[:start] + block.rstrip("\n") + ("\n\n" + tail if tail else "\n")
        return merged
    if existing.strip():
        return existing.rstrip("\n") + "\n\n" + block
    return header + block


def copy_skill(src: Path, dest: Path, symlink: bool, dry: bool) -> str:
    if dry:
        return "would link" if symlink else "would copy"
    if dest.is_symlink() or dest.is_file():
        dest.unlink()
    elif dest.exists():
        shutil.rmtree(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if symlink:
        try:
            os.symlink(src, dest, target_is_directory=True)
            return "linked"
        except OSError:
            print(f"  note: symlink failed for {dest.name} (on Windows enable Developer Mode); copying instead")
    shutil.copytree(src, dest, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    return "copied"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--agent", default="", help=f"comma list or 'all'. Choices: {', '.join(AGENTS)}")
    ap.add_argument("--scope", choices=("project", "user"), default="project", help="install into a project or your home directory")
    ap.add_argument("--project", type=Path, default=Path.cwd(), help="project root for --scope project (default: current directory)")
    ap.add_argument("--only", default="", help="comma list of skill names to install (default: all)")
    ap.add_argument("--rules", action="store_true", help="also write the managed instruction block (project scope only)")
    ap.add_argument("--symlink", action="store_true", help="symlink instead of copy (stays in sync with this repo)")
    ap.add_argument("--dry-run", action="store_true", help="show what would happen")
    ap.add_argument("--list", action="store_true", help="list skills and agent targets, then exit")
    args = ap.parse_args()

    skills = load_skills()
    if args.only:
        wanted = {n.strip() for n in args.only.split(",") if n.strip()}
        missing = wanted - {s.name for s in skills}
        if missing:
            print(f"error: unknown skill(s): {', '.join(sorted(missing))}", file=sys.stderr)
            return 2
        skills = [s for s in skills if s.name in wanted]

    if args.list:
        print(f"{len(skills)} skills:")
        for s in skills:
            print(f"  {s.name}")
        print("\nAgents (project skills dir | user skills dir | rule files):")
        for a in AGENTS.values():
            user = str(a.user_skills) if a.user_skills else "-"
            print(f"  {a.key:<12} {a.project_skills:<20} {user:<45} {', '.join(a.rule_files)}")
        return 0

    if not args.agent:
        print("error: choose --agent (for example --agent claude,kiro) or --agent all. See --list.", file=sys.stderr)
        return 2
    keys = list(AGENTS) if args.agent.strip() == "all" else [k.strip() for k in args.agent.split(",") if k.strip()]
    bad = [k for k in keys if k not in AGENTS]
    if bad:
        print(f"error: unknown agent(s): {', '.join(bad)}. Choices: {', '.join(AGENTS)}", file=sys.stderr)
        return 2

    project = args.project.resolve()
    if args.scope == "project" and not project.is_dir():
        print(f"error: project directory not found: {project}", file=sys.stderr)
        return 2
    if project == Path(__file__).resolve().parent.parent and args.scope == "project" and not args.dry_run:
        print("error: --project points at this repo itself. Pass your own project path with --project.", file=sys.stderr)
        return 2

    done_dirs: set[Path] = set()
    done_rules: set[Path] = set()
    for key in keys:
        agent = AGENTS[key]
        if args.scope == "user":
            if agent.user_skills is None:
                print(f"[{agent.label}] no user-level skills directory; use --scope project")
                continue
            target = agent.user_skills
            rel = str(target)
        else:
            target = project / agent.project_skills
            rel = agent.project_skills

        print(f"[{agent.label}] {target}")
        if agent.note:
            print(f"  note: {agent.note}")
        if target in done_dirs:
            print("  shared directory already handled")
        else:
            done_dirs.add(target)
            for s in skills:
                result = copy_skill(s.path, target / s.name, args.symlink, args.dry_run)
                print(f"  {result}: {s.name}")

        if args.rules and args.scope == "project":
            for rule in agent.rule_files:
                rule_path = project / rule
                if rule_path in done_rules:
                    continue
                done_rules.add(rule_path)
                header, block = wrap_special(rule, md_block(skills, rel))
                existing = rule_path.read_text(encoding="utf-8") if rule_path.exists() else ""
                new = merge_block(existing, header, block)
                if args.dry_run:
                    print(f"  would write rules: {rule}")
                else:
                    rule_path.parent.mkdir(parents=True, exist_ok=True)
                    rule_path.write_text(new, encoding="utf-8", newline="\n")
                    print(f"  wrote rules: {rule}")
        elif args.rules:
            print("  note: --rules is ignored with --scope user")

    print("\nDone." if not args.dry_run else "\nDry run only. Nothing written.")
    print("Restart your agent or reload the window so it rediscovers skills.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
