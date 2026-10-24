---
name: audit-broken-onboarding
tags: [positive, audit-repo]
runs: 1
max_turns: 12
timeout_seconds: 240
allowed_tools: [Read, Glob, Grep, Skill]
---
Can you assess the onboarding and local documentation links in the synthetic repository at `resources/`? Give the smallest repair and how to verify it. Don't edit any files; distinguish inspected evidence from checks you could not run.
