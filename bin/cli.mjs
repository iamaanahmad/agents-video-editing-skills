#!/usr/bin/env node
// Installer CLI for agents-video-editing-skills. Zero dependencies, Node 18+.
// Mirrors scripts/install.py. Agent targets come from agents.json.
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseArgs } from 'node:util';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const SKILLS_DIR = path.join(ROOT, 'skills');
const BEGIN = '<!-- BEGIN agents-video-editing-skills (managed) -->';
const END = '<!-- END agents-video-editing-skills (managed) -->';
const PKG = JSON.parse(fs.readFileSync(path.join(ROOT, 'package.json'), 'utf8'));
const AGENTS = JSON.parse(fs.readFileSync(path.join(ROOT, 'agents.json'), 'utf8'));

const HELP = `agents-video-editing-skills ${PKG.version}
Install video editing skills into Claude Code, Codex, Kiro, Copilot, Antigravity,
Windsurf, Cursor, Gemini CLI, Cline, OpenCode and Zed.

Usage:
  npx agents-video-editing-skills --agent <list|all> [options]
  npx agents-video-editing-skills list

Options:
  --agent <names>     comma list or "all": ${Object.keys(AGENTS).join(', ')}
  --scope <scope>     "project" (default) or "user" (your home directory)
  --project <dir>     project root for --scope project (default: current directory)
  --only <skills>     comma list of skill names (default: all)
  --rules             also write the managed instruction block (project scope only)
  --symlink           link instead of copy (stays in sync with the package)
  --dry-run           show what would happen, write nothing
  --list              list skills and agent targets
  -v, --version       print version
  -h, --help          show this help

Examples:
  npx agents-video-editing-skills --agent claude,kiro,codex --rules
  npx agents-video-editing-skills --agent all --rules --project ./my-app --dry-run
  npx agents-video-editing-skills --agent claude --scope user
`;

function fail(message) {
  console.error(`error: ${message}`);
  process.exit(2);
}

function parseFrontmatter(text) {
  const m = /^---\r?\n([\s\S]*?)\r?\n---\r?\n/.exec(text);
  if (!m) throw new Error('missing YAML frontmatter');
  const data = {};
  for (const line of m[1].split(/\r?\n/)) {
    if (!line.trim() || line.trimStart().startsWith('#')) continue;
    const i = line.indexOf(':');
    if (i < 0) throw new Error(`unsupported frontmatter line: ${line}`);
    data[line.slice(0, i).trim()] = line.slice(i + 1).trim().replace(/^['"]|['"]$/g, '');
  }
  return data;
}

function loadSkills() {
  return fs
    .readdirSync(SKILLS_DIR, { withFileTypes: true })
    .filter((d) => d.isDirectory() && fs.existsSync(path.join(SKILLS_DIR, d.name, 'SKILL.md')))
    .map((d) => d.name)
    .sort()
    .map((dir) => {
      const meta = parseFrontmatter(fs.readFileSync(path.join(SKILLS_DIR, dir, 'SKILL.md'), 'utf8'));
      return { name: meta.name ?? '', description: meta.description ?? '', path: path.join(SKILLS_DIR, dir) };
    });
}

function mdBlock(skills, skillsRel) {
  const lines = [
    BEGIN,
    '## Video editing skills',
    '',
    'For any video creation or editing task, start with `video-editing-router`, then read the',
    'matching skill file below before acting. Probe inputs first, never overwrite sources, and',
    'run `video-qa` before delivering.',
    '',
    '| Skill | Use when | File |',
    '|---|---|---|',
  ];
  for (const s of skills) {
    const desc = s.description.replaceAll('|', '\\|');
    const short = desc.length <= 140 ? desc : desc.slice(0, 137).replace(/\s+\S*$/, '') + '...';
    lines.push(`| \`${s.name}\` | ${short} | \`${skillsRel}/${s.name}/SKILL.md\` |`);
  }
  lines.push('', END);
  return lines.join('\n') + '\n';
}

const DESC = 'Video creation and editing workflows - FFmpeg, Remotion, moviepy, captions, voiceover, export, QA.';
function wrapSpecial(rulePath, block) {
  if (rulePath.startsWith('.kiro/steering/')) {
    return [`---\ninclusion: auto\nname: video-editing-skills\ndescription: ${DESC}\n---\n\n`, block];
  }
  if (rulePath.startsWith('.windsurf/rules/')) {
    return [`---\ntrigger: model_decision\ndescription: ${DESC}\n---\n\n`, block];
  }
  return ['', block];
}

function mergeBlock(existing, header, block) {
  if (existing.includes(BEGIN) && existing.includes(END)) {
    const start = existing.indexOf(BEGIN);
    const end = existing.indexOf(END) + END.length;
    const tail = existing.slice(end).replace(/^\n+/, '');
    return existing.slice(0, start) + block.replace(/\n+$/, '') + (tail ? `\n\n${tail}` : '\n');
  }
  if (existing.trim()) return existing.replace(/\n+$/, '') + '\n\n' + block;
  return header + block;
}

function installSkill(src, dest, symlink, dry) {
  if (dry) return symlink ? 'would link' : 'would copy';
  fs.rmSync(dest, { recursive: true, force: true });
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  if (symlink) {
    try {
      fs.symlinkSync(src, dest, process.platform === 'win32' ? 'junction' : 'dir');
      return 'linked';
    } catch {
      console.log(`  note: symlink failed for ${path.basename(dest)}; copying instead`);
    }
  }
  fs.cpSync(src, dest, {
    recursive: true,
    filter: (p) => !/__pycache__|\.pyc$/.test(p),
  });
  return 'copied';
}

function expandHome(p) {
  return p ? path.join(os.homedir(), p.replace(/^~[\\/]/, '')) : null;
}

function main() {
  let values;
  let positionals;
  try {
    ({ values, positionals } = parseArgs({
      allowPositionals: true,
      options: {
        agent: { type: 'string', default: '' },
        scope: { type: 'string', default: 'project' },
        project: { type: 'string' },
        only: { type: 'string', default: '' },
        rules: { type: 'boolean', default: false },
        symlink: { type: 'boolean', default: false },
        'dry-run': { type: 'boolean', default: false },
        list: { type: 'boolean', default: false },
        version: { type: 'boolean', short: 'v', default: false },
        help: { type: 'boolean', short: 'h', default: false },
      },
    }));
  } catch (err) {
    fail(err.message);
  }

  if (values.version) return console.log(PKG.version);
  if (values.help || (positionals.length === 0 && !values.agent && !values.list)) return console.log(HELP);
  if (positionals.length > 0 && positionals[0] !== 'list') fail(`unknown command: ${positionals[0]}. Use --help.`);
  if (!['project', 'user'].includes(values.scope)) fail('--scope must be "project" or "user"');

  let skills = loadSkills();
  if (values.only) {
    const wanted = new Set(values.only.split(',').map((s) => s.trim()).filter(Boolean));
    const missing = [...wanted].filter((n) => !skills.some((s) => s.name === n));
    if (missing.length) fail(`unknown skill(s): ${missing.sort().join(', ')}`);
    skills = skills.filter((s) => wanted.has(s.name));
  }

  if (values.list || positionals[0] === 'list') {
    console.log(`${skills.length} skills:`);
    for (const s of skills) console.log(`  ${s.name}`);
    console.log('\nAgents (project skills dir | user skills dir | rule files):');
    for (const [key, a] of Object.entries(AGENTS)) {
      const user = a.userSkills ? expandHome(a.userSkills) : '-';
      console.log(`  ${key.padEnd(12)} ${a.projectSkills.padEnd(20)} ${String(user).padEnd(45)} ${a.ruleFiles.join(', ')}`);
    }
    return;
  }

  if (!values.agent) fail('choose --agent (for example --agent claude,kiro) or --agent all. See --list.');
  const keys = values.agent.trim() === 'all'
    ? Object.keys(AGENTS)
    : values.agent.split(',').map((k) => k.trim()).filter(Boolean);
  const bad = keys.filter((k) => !(k in AGENTS));
  if (bad.length) fail(`unknown agent(s): ${bad.join(', ')}. Choices: ${Object.keys(AGENTS).join(', ')}`);

  const dry = values['dry-run'];
  const project = path.resolve(values.project ?? process.cwd());
  if (values.scope === 'project') {
    if (!fs.existsSync(project) || !fs.statSync(project).isDirectory()) fail(`project directory not found: ${project}`);
    if (project === ROOT && !dry) fail('--project points at this package itself. Pass your own project path with --project.');
  }

  const doneDirs = new Set();
  const doneRules = new Set();
  for (const key of keys) {
    const agent = AGENTS[key];
    let target;
    let rel;
    if (values.scope === 'user') {
      if (!agent.userSkills) {
        console.log(`[${agent.label}] no user-level skills directory; use --scope project`);
        continue;
      }
      target = expandHome(agent.userSkills);
      rel = target;
    } else {
      target = path.join(project, agent.projectSkills);
      rel = agent.projectSkills;
    }

    console.log(`[${agent.label}] ${target}`);
    if (agent.note) console.log(`  note: ${agent.note}`);
    if (doneDirs.has(target)) {
      console.log('  shared directory already handled');
    } else {
      doneDirs.add(target);
      for (const s of skills) {
        console.log(`  ${installSkill(s.path, path.join(target, s.name), values.symlink, dry)}: ${s.name}`);
      }
    }

    if (values.rules && values.scope === 'project') {
      for (const rule of agent.ruleFiles) {
        const rulePath = path.join(project, rule);
        if (doneRules.has(rulePath)) continue;
        doneRules.add(rulePath);
        const [header, block] = wrapSpecial(rule, mdBlock(skills, rel));
        if (dry) {
          console.log(`  would write rules: ${rule}`);
          continue;
        }
        const existing = fs.existsSync(rulePath) ? fs.readFileSync(rulePath, 'utf8') : '';
        fs.mkdirSync(path.dirname(rulePath), { recursive: true });
        fs.writeFileSync(rulePath, mergeBlock(existing, header, block), 'utf8');
        console.log(`  wrote rules: ${rule}`);
      }
    } else if (values.rules) {
      console.log('  note: --rules is ignored with --scope user');
    }
  }

  console.log(dry ? '\nDry run only. Nothing written.' : '\nDone.');
  console.log('Restart your agent or reload the window so it rediscovers skills.');
}

main();
