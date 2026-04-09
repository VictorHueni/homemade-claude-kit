# Homemade Agent Skills

Reusable skills for Claude Code. Single source of truth — symlinked into
projects and synced across machines via dotfiles.

## Skills

| Skill | Description |
|-------|-------------|
| [bug-rca](./bug-rca/) | Systematic bug root cause analysis and fix recommendations |
| [docs-auditor](./docs-auditor/) | Scan repo docs for stale, outdated, and dead documentation |
| [git-commit](./git-commit/) | Conventional commit message analysis and generation |
| [idea-generator](./idea-generator/) | Create and manage structured idea files |
| [pr-creator](./pr-creator/) | Create PRs following repo templates and standards |
| [ralph-loop-runner](./ralph-loop-runner/) | Autonomous implementation loop: implement, test, commit, repeat |
| [slide-builder-skill](./slide-builder-skill/) | Build single-file HTML slide decks from modular partials |
| [spec-adr-manager](./spec-adr-manager/) | Architecture Decision Records (MADR 4.x) |
| [spec-implementation-planner](./spec-implementation-planner/) | Small-step, testable implementation roadmaps from PRDs |
| [spec-peer-reviewer](./spec-peer-reviewer/) | Review PRDs and plans for gaps and delivery risks |
| [spec-prd-creator](./spec-prd-creator/) | Generate Product Requirements Documents |
| [using-git-worktrees](./using-git-worktrees/) | Guide for Git worktree workflows |

## Install

```bash
# Clone once
git clone git@github.com:VictorHueni/homemade-agents-skills.git ~/projets/homemade-agents-skills

# Symlink all skills globally (~/.claude/skills/)
./install.sh

# Or symlink into a specific project
./install.sh /path/to/my-project
```

## Update

```bash
cd ~/projets/homemade-agents-skills
git pull
# Symlinks already point here — done.
```

## Workflow

1. **Edit** a skill from any project (symlinks point to this repo)
2. **Commit** the change here (the source of truth)
3. **Pull** on other machines — every project sees the update instantly

## Adding a new skill

1. Create a directory: `my-skill/SKILL.md` + supporting files
2. Run `./install.sh` to symlink it
3. Commit and push
