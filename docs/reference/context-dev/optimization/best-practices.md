# Production checklist

> Prepare authentication, output handling, deadlines, and observability for production.

Start with a representative success case, a target that cannot be read, and an empty or partial result. Verify the behavior your product depends on before increasing traffic.

## Keep credentials on the server

Store keys in a secret manager and give each integration the [permissions](https://docs.context.dev/account/api-keys.md) it needs. Keep source-site credentials out of application logs.

## Choose outputs and validate results

Combine the Scrape formats you need in one request. Check each output’s `success`; handle empty lists, missing Brand fields, and low-confidence People matches explicitly. Preserve user corrections outside refreshed API data.

## Set cache freshness

Choose freshness by workload. Use `maxAgeMs: 0` when a Scrape result must reflect a new visit; accept older data for infrequently changing pages. See [Scrape caching](https://docs.context.dev/scrape/freshness-and-caching.md) and [Brand options](https://docs.context.dev/brand/overview#options).

## Bound work and retries

Set [API and client timeouts](https://docs.context.dev/optimization/timeouts.md), restrict crawl scope, and cap concurrent work. Honor `Retry-After` after 429. Retry transient failures with bounded exponential backoff and jitter; fix invalid inputs before retrying.

Use an idempotency key for [batch submission](https://docs.context.dev/batches/submit.md#idempotency). Monitor [webhook deliveries](https://docs.context.dev/webhooks.md#delivery-history-and-replay) and deduplicate events before applying changes.

## Reduce transfer size

Request only needed outputs and apply [content filters](https://docs.context.dev/scrape/content-filtering.md). Avoid preserving base64 images in Markdown unless needed. Use `Accept-Encoding: gzip` or your client’s compression support; SDKs generally decompress responses automatically.

## Observe the integration

Record `request_id`, latency, response status, and stable error codes. Use [tags and logs](https://docs.context.dev/optimization/usage-and-logs.md) to locate regressions without retaining unnecessary page content. Test [ZDR confirmation](https://docs.context.dev/optimization/zero-data-retention.md#confirm-zdr-was-honored) when using retention controls.

Pin SDK versions, review the [changelog](https://docs.context.dev/changelog.md), and follow the [API stability policy](https://docs.context.dev/optimization/trust.md#api-versioning) when upgrading.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.