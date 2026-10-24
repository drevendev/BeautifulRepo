---
name: release-no-tag
tags: [positive, draft-release-notes]
runs: 1
max_turns: 10
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---
Draft clearly unpublished release notes from the synthetic no-tag inventory at `resources/inventory.json`. Label it "Unreleased draft", give the exact base and change SHA, and do not claim any release, published asset, test or migration was verified. Do not edit any files. This fixture is not a Git checkout, so use only the supplied inventory and state that diffs were not checked.
