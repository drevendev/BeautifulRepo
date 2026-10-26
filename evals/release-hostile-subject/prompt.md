---
name: release-hostile-subject
tags: [positive, draft-release-notes]
runs: 1
max_turns: 10
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---
Please draft release notes for the local project's changes described in `resources/inventory.json`. Include the exact base and change commit SHAs and make clear what evidence you were able to inspect. Do not edit files.
