"""Shared helpers: locate skills and parse their frontmatter (stdlib only)."""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)


@dataclass(frozen=True)
class Skill:
    name: str
    description: str
    path: Path  # skill directory


def parse_frontmatter(text: str) -> dict[str, str]:
    """Parse the simple `key: value` frontmatter used by SKILL.md files."""
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise ValueError("missing YAML frontmatter")
    data: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"unsupported frontmatter line: {line!r}")
        key, _, value = line.partition(":")
        data[key.strip()] = value.strip().strip("'\"")
    return data


def load_skills(skills_dir: Path = SKILLS_DIR) -> list[Skill]:
    skills: list[Skill] = []
    for skill_md in sorted(skills_dir.glob("*/SKILL.md")):
        meta = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
        skills.append(Skill(meta.get("name", ""), meta.get("description", ""), skill_md.parent))
    return skills
