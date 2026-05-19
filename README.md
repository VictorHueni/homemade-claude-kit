# Homemade Claude Kit

A personal collection of Claude Code extensions — **skills** and **slash commands** —
managed as a single source of truth, symlinked into `~/.claude/` and synced across
machines via dotfiles.

## Skills

| Skill | Description |
|-------|-------------|
| [ops-bug-rca](./ops-bug-rca/) | Systematic bug root cause analysis and fix recommendations |
| [util-docs-audit](./util-docs-audit/) | Scan repo docs for stale, outdated, and dead documentation |
| [dev-git-commit](./dev-git-commit/) | Conventional commit message analysis and generation |
| [spec-idea](./spec-idea/) | Create and manage structured idea files |
| [dev-pr](./dev-pr/) | Create PRs following repo templates and standards |
| [dev-ralph-loop](./dev-ralph-loop/) | Autonomous implementation loop: implement, test, commit, repeat |
| [dev-slide-deck](./dev-slide-deck/) | Build single-file HTML slide decks from modular partials |
| [spec-adr-manager](./spec-adr-manager/) | Architecture Decision Records (MADR 4.x) |
| [spec-implementation-plan](./spec-implementation-plan/) | Small-step, testable implementation roadmaps from PRDs |
| [spec-peer-review](./spec-peer-review/) | Review PRDs and plans for gaps and delivery risks |
| [spec-prd](./spec-prd/) | Generate Product Requirements Documents |
| [dev-git-worktree](./dev-git-worktree/) | Guide for Git worktree workflows |

## Commands

| Command | Description |
|---------|-------------|
| [ralph-audit](./commands/ralph-audit.md) | Audit an execution plan against Ralph Loop requirements |

## Install

```bash
# Clone once
git clone git@github.com:VictorHueni/homemade-claude-kit.git ~/projects/homemade-claude-kit

# Symlink everything globally (~/.claude/skills/ + ~/.claude/commands/)
./install.sh

# Or symlink into a specific project (.claude/skills/ + .claude/commands/)
./install.sh /path/to/my-project
```

## Update

```bash
cd ~/projects/homemade-claude-kit
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
