# Troubleshooting

> Diagnose request errors, partial results, and empty data.

Save the HTTP status, `error_code`, `request_id`, and a redacted copy of the input. Compare the request with the endpoint reference before retrying.

## Start with the response

| Status | What to check |
| - | - |
| `200` with missing data | Output-level success and `error_code`, filters, match status, and partial flags. |
| `400` | Invalid or conflicting fields; some lookup APIs also use `NOT_FOUND`. |
| `401` | Missing, invalid, revoked, or disabled key. |
| `402` | `USAGE_EXCEEDED`: authenticated account lacks credits for admission or a batch reservation. |
| `403` | Key permissions, paid-plan requirement, ZDR entitlement, or a resource allowance. |
| `404` | Endpoint path, resource ID, unknown company, or a missing target. |
| `408` | API deadline. |
| `409` | Resource state or idempotency conflict. |
| `413` / `415` | Payload size / unsupported format. |
| `422` | Free/disposable email or an insufficient cold-domain deadline. |
| `429` | Concurrency, per-minute, or management rate limit, or authentication protection. |
| `5xx` | Transient service error. |

## Authentication and access

Send `Authorization: Bearer <API_KEY>` to `https://api.context.dev/v1`. A missing or unknown key can currently return `401 NOT_FOUND` with an endpoint-not-found message; check the key before changing a valid route.

For `DISABLED`, inspect the key in the dashboard. Free organizations can have all keys disabled after repeated failed requests; stop the retry loop and follow the account email or contact support.

For `402 USAGE_EXCEEDED`, inspect usage with the free [`GET /org/usage`](https://docs.context.dev/api-reference/usage/retrieve) or MCP `get-usage`. Explain the known balance, required credits, and refill details from `error_data`. Wait until credits cover the operation; do not reconnect or repeatedly retry. See [credit and entitlement information](https://docs.context.dev/account/billing.md). For `INSUFFICIENT_PERMISSIONS`, grant the required scope; repeated unchanged requests will still fail.

## Empty and partial outputs

Scrape can return HTTP 200 with failed outputs; each failed output carries an `error_code` and `message`. Empty successful text may mean selectors matched nothing. Inspect [Scrape errors](https://docs.context.dev/scrape/timeouts-and-errors.md) and verify page readiness.

A Brand profile can have empty collections. People can return `not_found` or a weak candidate. Answers can have null facts. Handle these as product states rather than assuming every successful request contains complete data.

## Target access and documents

`WEBSITE_BLOCKED` can mean an anti-bot page, CAPTCHA, or login shell. Confirm the URL and access requirements, then use a bounded recovery strategy. Avoid an unchanged retry loop.

A scanned upload with OCR off returns `PDF_IMAGES_ONLY` from Parse. Scrape marks its failed text outputs with the same code. See [PDFs and OCR](https://docs.context.dev/parse/pdfs-and-ocr.md).

## Async work

Batch results expire after 180 days; expired signed links can be refreshed only while the files remain. After an idempotent submit returns a failed batch, inspect its failure code before submitting a new key. See [batch errors](https://docs.context.dev/batches/limits-and-errors.md).

For missing monitor alerts, inspect runs, event subscriptions, delivery history, and retry configuration. Omitting `webhook.retry` requests best-effort delivery. See [Webhooks](https://docs.context.dev/webhooks.md).

## Retry or report

Honor `Retry-After`, use bounded backoff for transient failures, and keep client timeouts longer than [API deadlines](https://docs.context.dev/optimization/timeouts.md). Report reproducible API or documentation issues through [Agent feedback](https://docs.context.dev/optimization/agent-feedback.md), or email [support@context.dev](mailto:support@context.dev) with the request ID.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.