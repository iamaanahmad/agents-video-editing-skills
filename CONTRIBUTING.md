# Contributing

Thanks for helping. Good skills are specific, correct and short.

## Add or improve a skill

1. Copy the layout of an existing skill: `skills/<name>/SKILL.md`.
2. Frontmatter: only `name` (same as the folder) and `description` (what it does, when to use it, trigger words).
3. Write the body as a playbook: when to use, steps, copy-pasteable commands, pitfalls, checks.
4. Test every command you add. Say which tool version you tested if the API is version-sensitive.
5. Run `python scripts/validate.py`.
6. Open a pull request describing what changed and how you tested it.

## Style

- Plain, direct sentences. Commands in fenced code blocks with the language set.
- Give both bash and PowerShell notes when they differ.
- Tables for decisions, lists for steps.
- No claims you cannot support. If a limit or API may change, say to check the official docs.

## Not accepted

- Tool-specific frontmatter or paths inside skill bodies.
- Copied text from sources with incompatible licenses.
- Skills that help deceive viewers (deepfakes of real people without consent, fake endorsements).
- Secrets or personal data.

## Helper scripts

Python standard library only, `--help` support, clear errors, non-zero exit on failure. Keep them small.
