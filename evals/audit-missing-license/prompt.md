---
name: audit-missing-license
tags: [positive, audit-repo]
runs: 1
max_turns: 12
timeout_seconds: 240
allowed_tools: [Read, Glob, Grep, Skill]
---
Please review the README and first-use experience of the synthetic local repository in `resources/`. Prioritize concrete newcomer blockers with file references. Don't change anything. If a check cannot be run with the available tools, mark it not verified instead of inventing a result.
