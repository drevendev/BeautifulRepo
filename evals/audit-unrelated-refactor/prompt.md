---
name: audit-unrelated-refactor
tags: [negative, audit-repo]
runs: 1
max_turns: 6
timeout_seconds: 120
allowed_tools: [Read, Glob, Grep, Skill]
---
In Python, what is a clear name for the loop variable in `for x in range(5)`? Answer briefly. This is a question about code style, not the repository's documentation.
