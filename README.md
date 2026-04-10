# Homemade Claude Kit

A personal collection of Claude Code extensions — **skills** and **slash commands** —
managed as a single source of truth, symlinked into `~/.claude/` and synced across
machines via dotfiles.

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

## Commands

| Command | Description |
|---------|-------------|
| [ralph-audit](./commands/ralph-audit.md) | Audit an execution plan against Ralph Loop requirements |

## Install

```bash
# Clone once
git clone git@github.com:VictorHueni/homemade-claude-kit.git ~/projets/homemade-claude-kit

# Symlink everything globally (~/.claude/skills/ + ~/.claude/commands/)
./install.sh

# Or symlink into a specific project (.claude/skills/ + .claude/commands/)
./install.sh /path/to/my-project
```

## Update

```bash
cd ~/projets/homemade-claude-kit
git pull
# Symlinks already point here — done.
```

## Workflow

1. **Edit** a skill or command from any project (symlinks point to this repo)
2. **Commit** the change here (the source of truth)
3. **Pull** on other machines — every project sees the update instantly

## Adding a new skill

1. Create a directory: `my-skill/SKILL.md` + supporting files
2. Run `./install.sh` to symlink it
3. Commit and push

## Adding a new command

1. Create a markdown file: `commands/my-command.md` (with the standard slash-command frontmatter)
2. Run `./install.sh` to symlink it
3. Commit and push
