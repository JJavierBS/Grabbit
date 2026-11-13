# Usage and request logs

> Label requests and investigate their metadata, input, and results.

Use `tags` to group requests by environment, workflow, or customer account identifier. Keep secrets and personal data out of labels.

## Tag requests

For JSON endpoints, add:

```json theme={null}
{"tags":["production","site-import"]}
```

GET endpoints accept comma-separated `tags`, such as `production,site-import`. A request accepts up to 20 tags, each 1–50 characters. ZDR requests omit tags from retained logs.

## Inspect usage

The dashboard usage page filters charts and request logs together by key and tags. Monitors have persistent tags that label their runs and changes; request tags label a single API call.

## Check credits and usage history

[Retrieve credit usage](https://docs.context.dev/api-reference/usage/retrieve.md) returns your balance, current-period usage, and next refill. It needs `logs:read` and costs no credits.

| Field | Meaning |
| - | - |
| `credits_remaining` | Credits available to your organization right now. |
| `period` | The current monthly credit period: its `start` and the `credits_used` since then. `null` when your organization has no monthly credits or billing is paused. |
| `next_refill` | The next monthly refill: `at`, and the `credits` your balance resets to. Unused credits don't carry over. `null` when no refill is scheduled; while billing is paused, this is when billing resumes. |
| `auto_topup` | Auto-Topup settings and spend: `enabled`, `credits_used_this_period` (credits added by Auto-Topup in the current period), and `monthly_budget_credits` (the monthly budget you're alerted against, or `null` when none is set). |

[Retrieve usage history](https://docs.context.dev/api-reference/usage/history.md) returns credits and requests over time, bucketed by hour, day, or month. History is kept for one year. It also needs `logs:read` and costs no credits.

| Parameter | Values |
| - | - |
| `interval` | `hour`, `day` (default), or `month`. `hour` covers up to 7 days; `day` and `month` cover up to 366 days. Buckets start on UTC boundaries. |
| `from`, `to` | ISO 8601 timestamps. `to` defaults to now. `from` defaults to 24 hours before `to` for `hour`, 30 days for `day`, and 366 days for `month`. |
| `group_by` | `path`, `key_id`, or `status_code`. Splits each bucket by endpoint path, API key, or HTTP status code. |

`data` holds one bucket per interval, oldest first, each with `start`, `credits_used`, and `request_count`; intervals without usage are included with zero totals. With `group_by`, each bucket adds `groups`, highest credits first, each with the `value` it covers, `credits_used`, and `request_count`. `total_credits_used` and `total_request_count` cover the whole range.

## Read request logs

[List request logs](https://docs.context.dev/api-reference/logs/list.md) needs `logs:read` and returns entries newest first, including batch settlements and monitor runs.

| Parameter | Values |
| - | - |
| `from`, `to` | ISO 8601 timestamps. `to` defaults to now; `from` defaults to 24 hours before `to`. |
| `path` | Endpoint path, with or without the `/v1` prefix. 1–200 characters. |
| `key_id` | The API key that made the request. 1–200 characters. |
| `status_code` | Exact HTTP status code, 100–599. |
| `error_code` | The `error_code` returned in the response. |
| `errors_only` | `true` keeps only requests that returned a 4xx or 5xx status. Defaults to `false`. |
| `tags` | Comma-separated request tags; matches requests carrying any of them. Up to 20 tags, each 1–50 characters. |
| `search` | Case-insensitive substring match against the request query and body, such as a domain. 1–200 characters. |
| `page` | Page number, starting at 1, up to 1,000. |
| `limit` | Entries per page, 1–100. Defaults to 50. |

Each entry has `request_id`, `timestamp` (when the request completed), `method`, `path`, `status_code`, `error_code` (`null` on success), `latency_ms` (server-side processing time), `credits_used`, `key_id`, `tags`, and `zdr` (whether the request was made under zero data retention). The response's `page`, `limit`, and `has_more` drive pagination.

[Retrieve a request log](https://docs.context.dev/api-reference/logs/retrieve.md) returns the same entry plus `input.query` (query parameters as sent), `input.body` (the request body with credentials and uploaded content redacted), `response` (the retained JSON response with credentials redacted, or `null` when unavailable), and `user_agent`. An entry becomes retrievable a few seconds after its request completes, so a `404 NOT_FOUND` for a request that just finished means ingestion has not caught up yet; retry after a few seconds.

Entries include HTTP requests and synthetic `MONITOR` and `BATCH` rows for runs and settlements. Their `method` is not always an HTTP verb, and their `key_id` can be null.

Logs are kept for up to one year. Retained input and response fields redact recognized credentials; redaction does not remove every kind of sensitive content. [ZDR](https://docs.context.dev/optimization/zero-data-retention.md) retains operational metadata only for web-content requests. Brand retrieval and Styleguide requests with ZDR enabled create no request-log entry.

Save `request_id` with application errors so you can match them to the API logs and support reports.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.