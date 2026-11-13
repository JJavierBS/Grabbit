# Rate limits

> Stay within your plan's concurrency limit and the separate organization limits for management APIs.

Core API limits cap how many requests your organization can have in flight at once. [Plan limits](https://docs.context.dev/account/billing.md#plan-limits) give the concurrency for each plan. New Free organizations also have a limit of 10 requests per minute across the organization. Organizations created before concurrency limits keep per-minute limits per API key; the dashboard shows which limit applies to you.

## Rate limits

| Bucket | Scope | Limit |
| - | - | - |
| Core data APIs | Organization | Plan concurrency; each in-flight request uses one slot until its response finishes. |
| Core data APIs on Free | Organization | 10 requests per minute, in addition to concurrency; every call weighs 1. |
| Core data APIs on older per-minute plans | API key | Plan allowance per minute; most calls weigh 1, Crawl weighs 10. |
| Batches | Organization | 1,000 units per minute; submit weighs 50, other calls 1. |
| Monitors | Organization | 1,000 requests per minute. |
| Webhook deliveries | Organization | 600 requests per minute. |
| Request logs, usage, access policies, and browser profiles | Organization | 60 requests per minute, shared. |
| Agent feedback | Organization | 10 requests per minute. |

All keys in an organization share its concurrency limit and credit balance. On older per-minute plans, each key has its own core rate window. Management limits apply across the organization on every plan.

## Headers and 429

A request that arrives while every concurrency slot is in use returns `429` with these headers:

```text theme={null}
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 0
X-RateLimit-Mode: concurrency
Retry-After: 1
```

Wait for one of your in-flight requests to finish, or at least `Retry-After` seconds, before trying again. The `429` message also states how many requests can run at once.

When a per-minute limit is reached, the `429` returns per-minute headers without `X-RateLimit-Mode`:

```text theme={null}
X-RateLimit-Limit: 200
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1790470860
Retry-After: 12
```

`X-RateLimit-Reset` is a Unix timestamp in seconds. Per-minute retry delays range from 1 to 60 seconds. The `429` message also states the limit, the request's weight, and the wait in seconds, for clients that cannot read headers.

Size your worker pool to your concurrency limit, and add jitter to retries. Missing or invalid credentials can also trigger authentication protection; fix credentials instead of increasing retry traffic.

Concurrency caps for [batches](https://docs.context.dev/batches/limits-and-errors.md) and the number of [monitors](https://docs.context.dev/monitors/limits-and-errors.md) are separate from these request limits.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.