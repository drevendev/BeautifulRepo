---
name: trust-unrelated-code
tags: [negative, trust-surfaces]
runs: 1
max_turns: 6
timeout_seconds: 120
allowed_tools: [Read, Glob, Grep, Skill]
---
For a Python loop, when should I use `sorted(values)` rather than `values.sort()`? Please answer briefly.
