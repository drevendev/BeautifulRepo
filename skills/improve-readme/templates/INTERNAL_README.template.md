# {{INTERNAL_PROJECT_NAME}}

<!-- Internal-only scaffold. Replace all placeholders, remove unused sections,
verify actual commands and links, and check approved sharing before publishing.
Do not copy this template unchanged into a production repository. -->

> **Visibility:** {{PRIVATE_OR_INTERNAL_AUDIENCE}}  
> **Status:** {{ACTIVE_PILOT_MAINTENANCE_OR_ARCHIVED}}  
> **Data classification:** {{APPROVED_CLASSIFICATION}}

## Purpose and status

{{ONE_SENTENCE_PURPOSE_AND_EXPECTED_RESULT_FOR_AUTHORIZED_READERS}}

{{WHAT_WORKS_NOW_AND_KNOWN_LIMITATIONS}}

## Owner and contact

- **Owning team:** {{VERIFIED_TEAM_OR_ROLE}}
- **Support/contact:** {{APPROVED_INTERNAL_CHANNEL_OR_TRACKER}}
- **Escalation/on-call (optional):** {{REAL_VERIFIED_ROUTE_OR_NOT_APPLICABLE}}

Do not invent a private security mailbox, escalation roster or response guarantee.

## Get access

{{WHO_MAY_ACCESS_AND_HOW_TO_REQUEST_APPROVAL}}

{{WHERE_TO_FIND_THE_APPROVED_ACCESS_POLICY_WITHOUT_PUBLISHING_PRIVATE_URLS}}

Never paste invite links, access tokens or customer-specific details into a public copy.

## Set up with internal dependencies

Prerequisites: {{TESTED_RUNTIME_OS_AND_REQUIRED_TOOLS}}

Source: {{APPROVED_INTERNAL_CLONE_OR_MIRROR_INSTRUCTIONS}}

Dependencies: {{APPROVED_REGISTRY_OR_MIRROR_NAME_AND_EXACT_PINNED_VERSION}}

Credentials must come from the organization's approved secret manager or
short-lived identity mechanism. Describe the approved tool's retrieval method
without pasting a credential, token-bearing URL, `.env` contents or sample secret.

Use an organization-approved command here **after testing it**. Do not imply that
a hypothetical private registry is reachable from outside the organization.

## Verify a first success

Command: {{ACTUALLY_TESTED_VERIFICATION_COMMAND}}

Expected observable result: {{EXACT_TESTED_OUTPUT_AND_FAILURE_RECOVERY}}

## Runbooks

{{RELATIVE_LINKS_TO_CHECKED_IN_RUNBOOKS_AND_TROUBLESHOOTING}}

Use repository-relative Markdown links to existing checked-in files, not
unverified internal web addresses.

## Data classification and handling

- **Classification:** {{ACTUAL_APPROVED_CLASSIFICATION_AND_POLICY_OWNER}}
- **Inputs/outputs:** {{WHAT_DATA_IS_ACCEPTED_STORED_OR_EXPORTED}}
- **Logs/CI/artifacts:** {{WHAT_MAY_BE_RETAINED_AND_WHO_CAN_READ_IT}}
- **External services/agents:** {{APPROVED_DESTINATIONS_OR_EXPLICITLY_NONE}}

Check actual repository visibility, inherited files and Pages separately.
The [confidentiality checklist](../checklists/confidentiality.md) is a
public reference, not a substitute for organization policy.

## Usage terms

{{ACTUAL_ORGANIZATION_APPROVED_INTERNAL_USE_TERMS_OR_POLICY_REFERENCE}}

Do not add a public open-source license by default or imply that missing
`LICENSE` means unrestricted use. Name third-party code/data terms separately.
