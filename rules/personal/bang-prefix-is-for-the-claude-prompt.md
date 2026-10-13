---
type: rule
---

# A `! command` goes in the Claude Code prompt

When suggesting a `!`-prefixed command, say in the same sentence that it is typed into the Claude Code prompt, and give the plain form for a terminal: in zsh or bash `!` negates the exit status and the rest of a `&&` chain silently never runs. After the owner reports it done, verify the effect before building on it.
