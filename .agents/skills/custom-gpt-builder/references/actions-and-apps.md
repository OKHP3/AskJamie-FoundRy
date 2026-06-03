# Actions and Apps Reference

## The Fundamental Choice

A single Custom GPT can use either **Actions** or **Apps** — not both simultaneously.
This is an explicit OpenAI platform constraint, not a configuration error.

| Surface | What It Is | Build By | Auth |
|---|---|---|---|
| **Actions** | OpenAPI-defined API calls you configure per-GPT | You (OpenAPI schema) | None / API Key / OAuth 2.0 |
| **Apps** | MCP-based pre-built integrations | OpenAI / third parties | User connects |

**When to use Actions:** You own the API, need deterministic operation IDs, require precise control over request/response shape, and can maintain the schema.

**When to use Apps:** Pre-built integrations cover the need, or your org runs enterprise systems already exposed as MCP apps. Apps require Business/Enterprise/Edu for full write capability.

---

## Actions Deep Dive

### OpenAPI Schema Requirements

Actions use OpenAPI 3.0 or 3.1 specs (JSON or YAML). The model reads the schema to decide which endpoint fits the user's request.

**Published limits:**
- 300 characters max per endpoint `summary` or `description`
- 700 characters max per parameter `description`
- Request and response payloads under 100,000 characters each
- Schemas validated in the GPT builder (paste or import by URL)

**Write descriptions for the model, not for humans.** The model reads your descriptions to decide when and how to call each endpoint. Be explicit:

```yaml
paths:
  /quotes/{quoteId}/review:
    post:
      operationId: reviewQuote
      summary: Review a quote for margin risk and policy exceptions.
      description: >
        Use when the user provides a quote ID and wants pricing risk analysis,
        discount policy checking, or approval path guidance.
      x-openai-isConsequential: true
```

### `x-openai-isConsequential`

**Critical flag for mutating endpoints.** Add `x-openai-isConsequential: true` to any POST, PUT, PATCH, or DELETE operation. This tells ChatGPT the action has real-world side effects and triggers a user confirmation before execution. Without it, mutating calls may execute silently.

Read-only endpoints (GET) should use `x-openai-isConsequential: false` or omit the flag.

### Production Constraints

| Constraint | Value |
|---|---|
| TLS | 1.2+ required |
| Port | 443 only |
| Request timeout | 45 seconds |
| Rate limits | Implement 429-aware backoff in your API |
| Payload size | < 100,000 characters |

Design your API to respond within 30 seconds to leave margin before the 45-second cutoff.

### Authentication Setup

**No Auth** — for public APIs or internal tools with no sensitive data. Simplest to configure.

**API Key** — most common for production.
1. Choose header, query parameter, or Basic auth
2. Enter the key value in the GPT builder
3. The key is stored by OpenAI and injected at runtime

**OAuth 2.0** — for user-delegated permissions.
Required configuration:
- Client ID and Client Secret
- Authorization URL
- Token URL
- Scope (space-separated)
- Redirect URL (must be registered with your OAuth provider)
- **The OAuth `state` parameter is required** — OpenAI uses it for CSRF protection. If your provider rejects the `state` parameter, the auth flow will fail.

**OAuth is the most common failure point.** Test the auth flow with a fresh account (not the builder account) before release. Verify token refresh behavior — tokens expire and the GPT must handle refresh transparently.

### Privacy Policy URL

**Required for any published Custom GPT that uses Actions.** If you publish to the GPT Store or share publicly with Actions enabled:
1. Host a publicly accessible Privacy Policy
2. Enter the URL in the GPT builder under Actions configuration
3. Policy must accurately describe what data the Action sends and to whom

Publishing without a valid Privacy Policy URL when Actions are configured will block Store submission.

### Actions Schema: Minimal Working Example

```yaml
openapi: 3.1.0
info:
  title: Quote Review API
  version: 1.0.0
servers:
  - url: https://api.example.com
paths:
  /quotes/{quoteId}:
    get:
      operationId: getQuote
      summary: Retrieve a quote by ID for review and analysis.
      x-openai-isConsequential: false
      parameters:
        - in: path
          name: quoteId
          required: true
          schema:
            type: string
          description: The unique identifier for the quote to retrieve.
      responses:
        "200":
          description: Quote data including line items, discounts, and customer context.
        "404":
          description: Quote not found.
  /quotes/{quoteId}/flag:
    post:
      operationId: flagQuoteForReview
      summary: Flag a quote for human review due to policy exception or anomaly.
      x-openai-isConsequential: true
      parameters:
        - in: path
          name: quoteId
          required: true
          schema:
            type: string
          description: The unique identifier for the quote to flag.
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                reason:
                  type: string
                  description: Plain-language reason for flagging (max 500 chars).
      responses:
        "200":
          description: Flag recorded and review queue updated.
```

### Error Handling in Instructions

Always add instructions for what to do when Actions fail:

```
If the API returns an error or times out, tell the user the service is temporarily
unavailable. Do not fabricate data or guess at API results. Suggest they try again
in a few minutes or contact [support path].
```

Keep schemas minimal — expose only the endpoints the GPT actually uses. Every extra endpoint is a potential misfire.

---

## Apps Deep Dive

Apps (renamed from "Connectors" on December 17, 2025) are MCP-based integrations. Users connect their own accounts; builders do not manage credentials.

**How Apps differ from Actions:**
- Pre-built by OpenAI or third parties — no schema authoring required
- User connects their account at conversation time
- Built on MCP (Model Context Protocol) — open standard
- Custom MCP apps (developer mode) require Business/Enterprise/Edu for full write capability
- Workspace admins can control app availability, write actions, RBAC, connected-account domains, and parameter constraints

**When Apps win over Actions:**
- Integration already exists as an app (saves schema work and maintenance)
- You need enterprise systems the user already has access to
- You want MCP-compatible cross-platform portability (future-proof)

**Apps SDK** is the recommended packaging route for custom app experiences.

---

## Decision Matrix

```
Does your API already exist as an App?
├── YES → Use Apps (no maintenance, user handles auth)
└── NO → Use Actions

Do you need precise control over request/response shape?
├── YES → Use Actions
└── NO → Either works; prefer Apps for maintenance simplicity

Is this a personal or small-team tool?
├── YES → Actions (faster to set up, no org admin required)
└── NO → Apps may be preferred (enterprise admin governance)

Do you need write/mutating operations at enterprise scale?
└── → Apps with Business/Enterprise/Edu license
```

---

## Common Action Failures and Fixes

| Failure | Likely Cause | Fix |
|---|---|---|
| Schema validation error in builder | Invalid OpenAPI 3.0/3.1 syntax | Validate with Swagger editor; check field name casing |
| Auth fails for all users | API key wrong or expired | Regenerate key; re-enter in builder |
| OAuth loop / redirect fails | `state` parameter rejected, or redirect URL mismatch | Confirm redirect URL registered; confirm provider accepts `state` |
| Action triggers on wrong input | Endpoint description too vague | Rewrite description with explicit trigger conditions |
| Action never triggers | Description too narrow or passive | Make description imperative; add trigger phrases |
| 45-second timeout | API response too slow | Optimize API; add async pattern with polling if needed |
| Consequential action runs without confirmation | Missing `x-openai-isConsequential: true` | Add flag to all mutating endpoints |
| GPT Store submission blocked | Missing Privacy Policy URL | Add policy URL in Actions configuration |
