#!/usr/bin/env python3
"""PreToolUse hook on Bash: block or annotate commands with a known trap.

Each tripwire replaces an always-on rule that only mattered for one command.
Kinds:
  deny  - always blocked; the reason says what to do instead.
  ack   - blocked until the command ends with `# tripwire-ack`, so the
          checklist is read before a one-shot, hard-to-undo call.
  note  - allowed; the text reaches the model alongside the tool result.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

ACK = "# tripwire-ack"

_HEREDOC = re.compile(r"<<-?\s*(['\"]?)(\w+)\1.*?^\s*\2\s*$", re.S | re.M)
_QUOTED = re.compile(r"'[^']*'|\"(?:\\.|[^\"\\])*\"")
_SHELL_ARG = re.compile(r"\b(?:(?:ba|z|da)?sh\s+-c|eval)\s+('[^']*'|\"(?:\\.|[^\"\\])*\")")
_COMMENT = re.compile(r"(?:^|\s)#.*$", re.M)
# A word in command position: after a separator or a prefix such as `sudo`, not inside arguments.
_START = r"(?:^|[;&|(`{]|\$\(|\b(?:then|do|else|sudo|env|time|xargs|exec|nohup)\b)\s*(?:\w+=\S*\s+)*"


def _strip(command: str) -> str:
    """Drop quoted text, heredoc bodies and comments, keeping `sh -c`/`eval` payloads."""
    command = command.replace("\\\n", " ")
    payloads = [m.group(1)[1:-1] for m in _SHELL_ARG.finditer(command)]
    stripped = _COMMENT.sub("", _QUOTED.sub("''", _HEREDOC.sub("", command)))
    return "\n".join([stripped, *payloads])


def _at_start(word: str) -> re.Pattern[str]:
    return re.compile(_START + word, re.M)


_GIT_AMEND = re.compile(_START + r"git\b[^;&|\n]*\bcommit\b[^;&|\n]*\s--amend\b", re.M)
_LOOP_HEAD = re.compile(r"\b(?:until|while)\b(.*?)(?:;|\n)\s*do\b", re.S)
_PGREP_FULL = re.compile(r"\bpgrep\b[^;&|\n]*\s(?:-[A-Za-z]*f|--full)\b")
_GH_TRANSFER = _at_start(r"gh\s+issue\s+transfer\b")
_GRAPHQL_CALL = _at_start(r"(?:gh\s+api\s+graphql|curl)\b")
_OSV = _at_start(r"osv-scanner\b(?!\.)")


def _pgrep_wait(command: str, stripped: str) -> bool:
    unheredoc = _HEREDOC.sub("", command.replace("\\\n", " "))
    return any(_PGREP_FULL.search(m.group(1)) for m in _LOOP_HEAD.finditer(unheredoc))


def _single_select_mutation(command: str, stripped: str) -> bool:
    # The mutation name sits inside the quoted GraphQL query, so match the raw command.
    return bool(_GRAPHQL_CALL.search(stripped)) and "updateProjectV2Field" in command


def _on_wsl() -> bool:
    try:
        return "microsoft" in Path("/proc/version").read_text().lower()
    except OSError:
        return False


def docker_desktop_context_on_wsl() -> bool:
    """True when Docker Desktop's Windows-pipe context is active on WSL (on macOS it works)."""
    return _on_wsl() and _docker_desktop_context() is not None


def _docker_desktop_context() -> str | None:
    config_dir = os.environ.get("DOCKER_CONFIG") or str(Path.home() / ".docker")
    try:
        context = json.loads((Path(config_dir) / "config.json").read_text()).get("currentContext")
    except (OSError, ValueError, AttributeError):
        return None
    return context if context == "desktop-linux" else None


_TEST_RUN = _at_start(r"(?:pytest|uv\s+run\s+(?:python\s+-m\s+)?pytest|python3?\s+-m\s+pytest|make\s+\S*test\S*|make\s+\S*ci-local|mvn\S*\s+\S*(?:test|verify)|\./mvnw\s+\S*(?:test|verify)|\./gradlew\s+\S*test|npm\s+(?:run\s+)?test|npx\s+vitest)")


def _tests_under_desktop_context(command: str, stripped: str) -> bool:
    return bool(_TEST_RUN.search(stripped)) and docker_desktop_context_on_wsl()


DOCKER_CONTEXT_MESSAGE = (
    "Docker Desktop's `desktop-linux` context is active (`currentContext` in the docker config). It is a "
    "Windows pipe: the `docker` CLI keeps working, but docker-py and Testcontainers fail with `npipe:// "
    "protocol is only supported on Windows` in under a second, or integration tests skip silently. Do not "
    "debug the tests. Ask the user to run `docker context use default` (again after every Docker Desktop "
    "restart) and to set `tc.host=unix:///var/run/docker.sock` in `~/.testcontainers.properties`. "
    "Testcontainers never reads `DOCKER_CONTEXT`, and `~/.bashrc` never reaches non-interactive runs (an "
    "`unset DOCKER_HOST` there removes a fallback). Probe with a clean environment: `env -i HOME=\"$HOME\" …`."
)

# (name, kind, matcher(command, stripped), message)
TRIPWIRES = [
    (
        "git-amend",
        "deny",
        lambda command, stripped: bool(_GIT_AMEND.search(stripped)),
        "Never `git commit --amend`: make a new commit. A failed pre-commit hook means no commit "
        "happened: fix, re-stage, commit again. If the user explicitly asked for an amend, ask them "
        "to run it themselves.",
    ),
    (
        "pgrep-f-wait",
        "deny",
        _pgrep_wait,
        "`pgrep -f <pattern>` in a wait loop matches the waiting shell itself, so the loop never ends. "
        "Record the exit code at launch and wait on an artefact the job writes on completion "
        "(`echo \"EXIT=$?\" >> log`, then `until grep -q '^EXIT=' log`) or on a PID with `kill -0`.",
    ),
    (
        "gh-issue-transfer",
        "ack",
        lambda command, stripped: bool(_GH_TRANSFER.search(stripped)),
        "Bulk `gh issue transfer` loses one parent link per epic. Between repos of the same owner a "
        "transfer keeps comments, assignees, Projects v2 items and their field values, same-name labels "
        "and sub-issue links, and old URLs redirect; labels missing in the target are dropped, and the "
        "sub-issue transferred just before its parent epic loses its parent link. Before the loop: create "
        "the target's labels, transfer one issue as a canary, keep an old-to-new map, record each epic's "
        "`subIssues.totalCount`. Afterwards: re-attach every null parent with the `addSubIssue` mutation "
        "and compare each epic's count, with no sub-issue left in a foreign repo.",
    ),
    (
        "gh-project-single-select",
        "ack",
        _single_select_mutation,
        "`updateProjectV2Field` replaces the field's whole option array: send every existing option "
        "(name, colour, description) plus the new one, or the missing ones are deleted. Even then it "
        "regenerates every option id, so every item loses its value. Before the mutation, snapshot each "
        "item's id and option *name*; afterwards restore the values by name and diff a fresh snapshot "
        "against the old one (same item count, same per-option distribution). Without a snapshot, add "
        "the option in the web UI instead.",
    ),
    (
        "osv-scanner-ignored",
        "note",
        lambda command, stripped: bool(_OSV.search(stripped)),
        "osv-scanner honours the enclosing repository's `.gitignore`: a worktree or checkout inside a "
        "parent repo's ignored folder scans nothing and fails with `No package sources found` (exit 128). "
        "It is not a lockfile problem. Tell: `git -C <parent> check-ignore -q <path>` succeeds. Pass "
        "`--no-ignore`, or keep worktrees outside the parent repository.",
    ),
    (
        "docker-desktop-context",
        "note",
        _tests_under_desktop_context,
        DOCKER_CONTEXT_MESSAGE,
    ),
]


def evaluate(command: str) -> dict | None:
    """Return the hook output for a Bash command, or None when nothing matches."""
    stripped = _strip(command)
    acked = command.rstrip().endswith(ACK)
    notes = []
    for name, kind, matches, message in TRIPWIRES:
        if not matches(command, stripped):
            continue
        if kind == "deny" or (kind == "ack" and not acked):
            reason = f"[tripwire {name}] {message}"
            if kind == "ack":
                reason += f" Once this is in place, rerun the command with a trailing `{ACK}`."
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            }
        if kind == "note":
            notes.append(f"[tripwire {name}] {message}")
    if notes:
        # No permissionDecision: the normal permission flow still applies.
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "additionalContext": "\n".join(notes),
            }
        }
    return None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return 0
    if not isinstance(payload, dict) or payload.get("tool_name") != "Bash":
        return 0
    tool_input = payload.get("tool_input")
    command = tool_input.get("command") if isinstance(tool_input, dict) else None
    if not isinstance(command, str):
        return 0
    result = evaluate(command)
    if result is not None:
        json.dump(result, sys.stdout)
    return 0


if __name__ == "__main__":
    sys.exit(main())
