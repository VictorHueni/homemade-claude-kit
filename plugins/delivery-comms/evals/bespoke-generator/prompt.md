---
description: "A bespoke script that builds an on-brand HTML table, outside the kit's renderers."
tags: [delivery-comms, generator]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Write a Python script, make_table.py in the current directory, that builds an HTML table of the figures in data/figures.csv in our brand. Run it so the page is saved as out/figures.html.
