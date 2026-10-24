---
name: release-tagged-history
tags: [positive, draft-release-notes]
runs: 1
max_turns: 10
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---
Create candidate release notes from the synthetic tagged-history inventory in `resources/inventory.json`. Treat the tag as a boundary, not proof the release exists. Trace the change to its exact commit SHA, describe any behavior as unverified without a diff, and make no edits or publication. This fixture is not a Git checkout.
