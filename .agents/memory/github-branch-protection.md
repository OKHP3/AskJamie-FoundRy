---
name: GitHub branch protection API
description: User-owned repository constraints when applying branch protection through GitHub's REST API.
---

When protecting a branch in a user-owned GitHub repository, omit
`dismissal_restrictions` from `required_pull_request_reviews`. User and team
restriction lists are organization-only, and sending either an empty object or
`null` is rejected by the API schema.

**Why:** The branch-protection endpoint reports a validation error for
user/team restrictions on user-owned repositories, including payloads that
appear to mean "no restrictions."

**How to apply:** Keep the review count and stale-review settings in the
review object, leave reviewer dismissal unrestricted, and verify the final
settings with a GET request after the PUT.