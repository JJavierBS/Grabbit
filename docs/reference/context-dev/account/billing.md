# Plans and billing

> Review plan limits, refills, plan changes, Auto-Topup, and cancellation.

Owners and Admins manage plans, payment methods, invoices, Auto-Topup, and spend alerts in [Billing](https://context.dev/dashboard/settings). See the [pricing page](https://www.context.dev/pricing) for current dollar prices.

## Plan limits

These are the current self-serve allowances. Legacy and custom plans can differ; the dashboard shows your organization’s entitlement. Enterprise subscriptions are managed by the Context team. For Enterprise subscriptions, plan changes, pauses, cancellation, Auto-Topup, spend alerts, and payment-method updates aren’t available in the dashboard; [contact us](https://www.context.dev/contact) to change them. Invoices stay visible in Billing.

| Plan | Credit allowance | Concurrent requests | Active batches | Monitors | API keys |
| - | -: | -: | -: | -: | -: |
| Free | 1,000/month | 2 | 1 | 10 | 2 |
| Developer | 10,000/month | 10 | 2 | 100 | 50 |
| Pro | 100,000/month | 100 | 5 | 1,000 | 50 |
| Growth | 500,000/month | 250 | 5 | 5,000 | 50 |
| Scale | 1,000,000/month | 500 | 20 | 10,000 | 50 |
| Scale 2.5M | 2,500,000/month | 500 | 20 | 10,000 | 50 |

New Free organizations also have a limit of 10 requests per minute across the organization.

Organizations created before concurrency limits keep per-minute limits per API key on every plan: 30 on Free with a work email, 10 on Free with a personal email, 60 on Developer, 200 on Pro, 600 on Growth, and 700 on Scale.

Paused monitors count toward the limit. Batches in `queued`, `running`, or `cancelling` count as active. [Rate limits](https://docs.context.dev/optimization/rate-limits.md) explains both limit types and the separate management buckets.

## Refills

Paid plans refill monthly, including annual subscriptions, on the billing-anchor day at 00:01 Pacific. A refill resets the balance to the plan allowance; it waits for the renewal invoice to be paid. Resolve payment failures in Billing to release held refills and top-ups.

## Insufficient credits

The API returns **HTTP 402** with `error_code: "USAGE_EXCEEDED"` when authenticated requests cannot pass the credit check or reserve a batch's quoted credits. The rejected operation is not executed or charged. Authentication remains valid; reconnecting or retrying the same request immediately does not restore credits.

Inspect your balance with [`GET /org/usage`](https://docs.context.dev/api-reference/usage/retrieve), or the MCP `get-usage` tool. Both cost no credits and remain available at zero balance, subject to normal authentication, permissions, and request limits. Retry when the balance covers the operation. An available refill may suffice; a subscription purchase is not the only possible recovery. A failed payment or billing pause can delay available credits.

The error envelope contains `message`, `error_code`, `key_metadata`, and `request_id`. `request_id` also appears in the `X-Request-Id` header. Its `error_data` contains:

| Field | Meaning |
| - | - |
| `is_authenticated` | `true`: credentials passed authentication. |
| `credits_remaining` | Organization balance observed by the credit check, clamped to zero. Omitted if unknown. |
| `credits_required` | Credits needed for admission or the batch reservation. Omitted if unknown. |
| `is_credits_required_estimated` | `true` when required credits are provided: this is an admission estimate or reservation quote, not the final bill. |
| `credits_charged` | `0`: the rejected operation was not charged. |
| `should_retry` | `false`: an unchanged request cannot be retried immediately under the observed account state. |
| `retry_condition` | `"sufficient_credits"`: the balance must cover the operation before retrying. |
| `next_refill_at` | ISO 8601 UTC timestamp from a known future refill schedule, adjusted for a known billing pause. Omitted when unavailable. |
| `next_refill_credits` | Known scheduled refill amount; provided with `next_refill_at`. A scheduled refill does not guarantee this operation will become affordable. |
| `info_url` | `https://context.dev/dashboard/subscription`, the account's subscription and billing settings. |

For example, an admission check needing 10 credits with 3 remaining returns:

```json theme={null}
{
  "message": "Insufficient credits: this request needs 10 credits and 3 remain. Authentication is valid. Retrying or reconnecting will not restore credits. Retry once the balance covers the request, for example after an available refill. Review billing settings: https://context.dev/dashboard/subscription",
  "error_code": "USAGE_EXCEEDED",
  "error_data": {
    "is_authenticated": true,
    "credits_remaining": 3,
    "credits_required": 10,
    "is_credits_required_estimated": true,
    "credits_charged": 0,
    "should_retry": false,
    "retry_condition": "sufficient_credits",
    "info_url": "https://context.dev/dashboard/subscription"
  },
  "key_metadata": { "credits_consumed": 0, "credits_remaining": 3 },
  "request_id": "7d13e8f0-1111-4222-8333-444455556666"
}
```

Credit exhaustion differs from `403 PAID_PLAN_REQUIRED` (a feature entitlement), `403 INSUFFICIENT_PERMISSIONS` (key access), and `429 RATE_LIMITED` (temporary throttling). Adding credits does not grant a missing feature entitlement. For temporary throttling, follow `Retry-After`; for genuine credential failures, repair authentication.

## Concurrency limits

Organization concurrency exhaustion returns **429 RATE\_LIMITED**. Its `error_data` reports `is_authenticated`, `limit_type: "concurrency"`, the effective `limit`, available slots in `remaining`, `retry_after_seconds`, known `credits_remaining`, and `credits_charged: 0`.

`should_retry: false` means do not immediately repeat the unchanged request. Follow `Retry-After` and retry when `retry_condition: "available_concurrency"` is met. `recovery_options` lists `"wait_for_in_flight_requests"` and `"increase_concurrency_limit"`; `info_url` opens [subscription settings](https://context.dev/dashboard/subscription). A subscription change may provide a higher limit, depending on the account's plan and custom allowances. Waiting for an in-flight request to finish also restores capacity without changing the subscription.

Rate-limit headers specify when to retry. Concurrency responses set `X-RateLimit-Mode: concurrency` and omit `X-RateLimit-Reset`. Per-minute limits include a reset timestamp.

## Change a plan

An upgrade to more monthly credits takes effect after payment succeeds. The billing term restarts without proration, and the new allowance is added to the remaining balance until the next refill. Outstanding Auto-Topup usage settles at the previous plan’s rate. Annual upgrades refund unused prepaid months.

Downgrades and annual-to-monthly changes take effect at period end. Current limits and monthly refills continue until then. **Undo** a scheduled change in Billing before pausing, cancelling, or choosing another change.

## Auto-Topup and spend alerts

Auto-Topup is enabled by default at checkout. When the balance falls below 1,000 credits, it adds a 1,000-credit block at the plan’s rate. Accrued usage is invoiced each time it reaches \$10 on Developer or \$100 on other plans, and at renewal. With Auto-Topup off or unavailable, insufficient balance returns `402 USAGE_EXCEEDED`.

Spend alerts notify Owners and Admins at selected budget thresholds. They are notifications, not a hard spending cap: requests, monitors, and Auto-Topup keep running. Turning Auto-Topup off clears its alert budget. Payment failure can put both refills and top-ups on hold.

## Pause or cancel

Monthly plans can pause for one, two, or three months. The remaining balance carries over without new allocations; requests and monitors can continue while it lasts. Auto-Topup settles at pause start and is unavailable during the pause.

Cancellation keeps the plan active until period end. It then returns to Free, removes the paid balance, and restores the monthly Free allowance.

## Account emails

Members receive notices about low balances, request errors that disable Free-plan keys, and service-related account issues. A daily rate-limit digest names each limit your organization hit and how many requests it rejected; it is sent only when more than 20% of the organization's requests in the past 24 hours were rate-limited. Billing contacts receive payment and spend-alert messages. Keep those addresses current and fix retry loops before re-enabling disabled keys.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.