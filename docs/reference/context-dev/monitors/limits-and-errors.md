# Limits and errors

> Manage monitor allowances and handle state, validation, and access failures.

Use `GET /monitors/limits` to read the organization’s allowance and current count: `monitors_used` is the number of monitors the account currently has, and `monitors_limit` is the most you can have, your plan's allowance or a custom limit. `plan` is `free`, `starter`, `pro`, or `scale`, where `starter` means Developer, `pro` means Pro or Growth, and `scale` means Scale or Enterprise. Paused monitors still count. Current plan defaults are in [Plans and billing](https://docs.context.dev/account/billing.md#plan-limits).

## Limits

Monitor names accept 1–200 characters and tags allow up to 20 values. Targets and webhook receivers must use public HTTP(S) URLs. Target-specific limits are in [Targets](https://docs.context.dev/monitors/targets); schedule limits are in [Schedules](https://docs.context.dev/monitors/schedules.md).

The Monitors API has an organization-wide limit of 1,000 requests per minute. The separate Webhook Deliveries API allows 600. See [rate limits](https://docs.context.dev/optimization/rate-limits.md).

## Errors

| Status and code | Action |
| - | - |
| `400 INPUT_VALIDATION_ERROR` | Correct the target/detection pair, schedule, or fields. |
| `401` | Check the key. Monitor run skips for insufficient credits are a separate execution state. |
| `403 MONITOR_LIMIT_EXCEEDED` | Delete unused monitors or change the allowance; pausing does not free a slot. |
| `403 INSUFFICIENT_PERMISSIONS` | Grant the required monitor scope. |
| `403 PAID_PLAN_REQUIRED` | Browser actions on page monitors need a paid plan. |
| `403 ACCESS_POLICY_DENIED` | An [access policy](https://docs.context.dev/optimization/access-policies.md) blocks the target URL. Change the target or the policy. |
| `403 ACCESS_POLICIES_NOT_ENABLED` | `policies` was sent, but access policies aren't enabled for your organization. [Contact us](mailto:support@context.dev) to enable them. |
| `404 NOT_FOUND` | Check the organization and resource ID. |
| `409 MONITOR_PAUSED` | Resume before requesting Run now. |
| `409 MONITOR_NO_WEBHOOK` | Configure a webhook before rotating its secret. |
| `429 RATE_LIMITED` | Honor `Retry-After`. |
| `503 SEARCH_UNAVAILABLE` | Retry or list without search filters. |

## Runs and usage

A run failure appears in the run record and monitor `last_error`. Failed monitors continue on schedule until they recover or are automatically paused; see [Schedules](https://docs.context.dev/monitors/schedules.md).

`GET /monitors/credit-usage` returns settled usage, sorted highest first, over at most the 10,000 most recent runs in the selected window. Use shorter windows for high-volume accounts. Read [runs and changes](https://docs.context.dev/monitors/runs-and-changes.md) for result states.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.