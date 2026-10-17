---
description: "Bring a deck whose styles define a deck-local dark palette onto a design system that provides dark."
tags: [delivery-comms, com-slide-deck]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Our board-update deck in docs/communication/slides/board-update stopped building after we pinned our design system. Get it building again without changing what it says: the results section slide stays dark and its highlighted words stay highlighted, the other two slides stay light. Do not wait for more input. Deliver the built deck as out/deck.html in the current directory.
