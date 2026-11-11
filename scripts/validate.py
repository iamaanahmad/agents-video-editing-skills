#!/usr/bin/env python3
"""Validate every skill in skills/ against the portable Agent Skills core.

Checks: frontmatter has exactly `name` and `description`; name matches the folder,
is lowercase-hyphen, max 64 chars; description is non-empty and max 1024 chars;
body is under 500 lines; local markdown links resolve.

Exit code 1 when any skill is invalid.
"""
from __future__ import annotations

import re
import sys

from skills_lib import FRONTMATTER_RE, NAME_RE, SKILLS_DIR, parse_frontmatter

LINK_RE = re.compile(r"\]\((?!https?://|#|mailto:)([^)\s]+)\)")
ALLOWED_KEYS = {"name", "description"}
MAX_BODY_LINES = 500


def main() -> int:
    errors: list[str] = []
    skill_files = sorted(SKILLS_DIR.glob("*/SKILL.md"))
    if not skill_files:
        print("error: no skills found", file=sys.stderr)
        return 1

    seen: set[str] = set()
    for skill_md in skill_files:
        folder = skill_md.parent.name
        text = skill_md.read_text(encoding="utf-8")
        try:
            meta = parse_frontmatter(text)
        except ValueError as exc:
            errors.append(f"{folder}: {exc}")
            continue

        extra = set(meta) - ALLOWED_KEYS
        if extra:
            errors.append(f"{folder}: unsupported frontmatter keys {sorted(extra)}")
        name = meta.get("name", "")
        desc = meta.get("description", "")
        if name != folder:
            errors.append(f"{folder}: name {name!r} must equal folder name")
        if not NAME_RE.match(name) or len(name) > 64:
            errors.append(f"{folder}: invalid name {name!r}")
        if name in seen:
            errors.append(f"{folder}: duplicate name")
        seen.add(name)
        if not desc:
            errors.append(f"{folder}: empty description")
        elif len(desc) > 1024:
            errors.append(f"{folder}: description is {len(desc)} chars (max 1024)")

        body = FRONTMATTER_RE.sub("", text, count=1)
        if len(body.splitlines()) > MAX_BODY_LINES:
            errors.append(f"{folder}: body exceeds {MAX_BODY_LINES} lines; move detail to references/")

        for link in LINK_RE.findall(body):
            target = (skill_md.parent / link.split("#")[0]).resolve()
            if not target.exists():
                errors.append(f"{folder}: broken link {link}")

    for err in errors:
        print(f"FAIL  {err}")
    if errors:
        print(f"\n{len(errors)} problem(s) in {len(skill_files)} skill(s)")
        return 1
    print(f"OK    {len(skill_files)} skills valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
