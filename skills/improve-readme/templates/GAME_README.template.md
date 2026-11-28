# {{GAME_NAME}}

{{ONE_SENTENCE_PLAYER_ACTION_AND_VISIBLE_RESULT}}

> **Status:** {{PROTOTYPE_DEMO_RELEASED_OR_ARCHIVED}}
> **Source commit:** {{VERIFIED_FULL_SHA}}
> **Last checked:** {{YYYY_MM_DD}}

## Play the current build

- Browser URL: {{VERIFIED_URL_OR_NOT_AVAILABLE}}
- Download builds: {{TESTED_PLATFORM_URLS_OR_NOT_AVAILABLE}}
- Build/version tested: {{VERSION_AND_TEST_DATE}}
- Platforms actually tested: {{OS_BROWSER_DEVICE_VERSIONS}}
- Known limitations: {{REAL_INPUT_NETWORK_OR_ACCESSIBILITY_LIMITATIONS}}

A published page is not proof of a launched game. Document the observed
launch result and do not pretend a source-only project has a live demo.

## See one gameplay moment

{{REAL_CAPTURE_WITH_ACTION_SPECIFIC_ALT_TEXT_OR_TEXT_ONLY_OUTPUT}}

{{CAPTURED_BUILD_AND_DATE_WITH_TEXT_EQUIVALENT}}

Do not label concept art, stock imagery or mockups as captured gameplay.

## First minute: controls and goal

Start: {{OBSERVED_INITIAL_STATE}}

1. {{FIRST_PLAYER_CONTROL_AND_ACTION}}
2. {{SECOND_PLAYER_CONTROL_AND_ACTION}}
3. {{EXPECTED_VISIBLE_RESULT_AND_TEXT_EQUIVALENT}}

Restart/quit: {{ACTUAL_CONTROLS}}

Progress/save/reset: {{OBSERVED_PERSISTENCE_AND_MIGRATION_BEHAVIOR}}

## Build from source

Prerequisites: {{TESTED_ENGINE_RUNTIME_AND_DEPENDENCY_VERSIONS}}

```text
{{CLEAN_CHECKOUT_AND_BUILD_COMMANDS}}
{{LOCAL_LAUNCH_COMMAND}}
```

Expected launch result: {{OBSERVED_SCREEN_OR_OUTPUT}}

```text
{{VERIFIED_TEST_COMMAND}}
```

Tested and untested: {{UNIT_BROWSER_DEVICE_AND_ACCESSIBILITY_COVERAGE}}

A CI badge is not evidence that the hosted/downloadable game works.

## Data, assets and permissions

- Network, accounts and telemetry: {{OBSERVED_BEHAVIOR}}
- Local saves and logs: {{PATHS_RESET_AND_PRIVACY_BOUNDARIES}}
- Code license: {{EXACT_LICENSE_FILE_OR_NOT_LICENSED}}
- Art/music/fonts/sounds: {{PATH_SCOPED_RIGHTS_AND_PROVENANCE}}
- Third-party dependencies/assets: {{VERIFIED_NOTICES_AND_TERMS}}

A public code license does **not** automatically license all bundled assets.

## Changes, support and contributions

Verified playable version: {{BUILD_ID_SOURCE_SHA_AND_DATE}}

Patch notes: {{ACTUAL_CHANGELOG_OR_DEVLOG_OR_NONE}}

Bug reports: {{EXISTING_ISSUE_ROUTE_WITH_BUILD_PLATFORM_AND_REPRO}}

Contributor route: {{REAL_CONTRIBUTING_GUIDE_OR_NOT_ACCEPTING_CHANGES}}

Maintenance status: {{OBSERVED_SUPPORT_STATUS_WITHOUT_INVENTED_SLA}}

Remove placeholders and instructional prose before publishing. Follow the
[game repository guide](../guides/game-repositories.md).
