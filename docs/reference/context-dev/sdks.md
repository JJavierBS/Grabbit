# SDKs

> Install an official Context.dev SDK for TypeScript, Python, Ruby, Go, or PHP, and learn the key, timeout, and retry defaults they share.

Official SDKs wrap the HTTPS API for server-side code. Each language page shows a first request and language-specific notes.

| Language | Package | Install | Requires |
| - | - | - | - |
| [JavaScript / TypeScript](https://docs.context.dev/sdks/typescript.md) | [`context.dev`](https://www.npmjs.com/package/context.dev) | `npm install context.dev` | Node.js 20+ |
| [Python](https://docs.context.dev/sdks/python.md) | [`context.dev`](https://pypi.org/project/context.dev/) | `pip install context.dev` | Python 3.9+ |
| [Ruby](https://docs.context.dev/sdks/ruby.md) | [`context.dev`](https://rubygems.org/gems/context.dev) | `gem install context.dev` | Ruby 3.2+ |
| [Go](https://docs.context.dev/sdks/go.md) | [`context-go-sdk/v2`](https://github.com/context-dot-dev/context-go-sdk) | `go get github.com/context-dot-dev/context-go-sdk/v2` | Go 1.22+ |
| [PHP](https://docs.context.dev/sdks/php.md) | [`context-dev/context-dev-php`](https://github.com/context-dot-dev/context-php-sdk) | `composer require "context-dev/context-dev-php:^2.37" guzzlehttp/guzzle` | PHP 8.1+ |

Go uses the `/v2` module path, `github.com/context-dot-dev/context-go-sdk/v2`. The unversioned path is the older v1 SDK, which lacks the current Scrape, Map URLs, and Brand methods.

## Set your API key

Every SDK reads `CONTEXT_DEV_API_KEY` when you don't pass a key to the client:

```bash theme={null}
export CONTEXT_DEV_API_KEY="ctxt_secret_..."
```

Keep the key in server-side code. Don't commit it or ship it to a browser. The [Quickstart](https://docs.context.dev/quickstart.md) shows where to get one.

## Timeouts and retries

* TypeScript, Python, Ruby, and PHP wait up to 60 seconds for each attempt. Go has no default request timeout (its default HTTP client waits up to 10 minutes for response headers).
* All five SDKs retry twice, with exponential backoff, after connection errors and `408`, `409`, `429`, or `5xx` responses.

Scrape's own deadline defaults to 90,000 ms, and a request's `timeoutOpts.milliseconds` can be up to 300,000. For Scrape, Crawl (80,000 ms default budget), or any request with a deadline above 60,000 ms, raise the SDK timeout above that deadline. Otherwise the SDK gives up and retries while the first attempt may still be running: only Scrape and Parse stop when the client disconnects. Each language page shows how to change both settings, and [Timeouts](https://docs.context.dev/optimization/timeouts.md) covers server deadlines.

## Use the low-level request method

SDKs are generated from the API spec and released separately, so an installed version can lag the API. If a typed method doesn't accept a field you need, send the request with the SDK's low-level method. It keeps the SDK's authentication, retries, and error handling.

| Language | Low-level request |
| - | - |
| TypeScript | `client.post("/web/scrape", { body })` |
| Python | `client.post("/web/scrape", body=body, cast_to=dict[str, object])` |
| Ruby | `client.request(method: :post, path: "web/scrape", body: body)` |
| Go | `client.Post(ctx, "/web/scrape", body, &response)` |
| PHP | `$client->request(method: 'post', path: 'web/scrape', body: $body)` |

Check the request body against the [API reference](https://docs.context.dev/api-reference/web-scraping/scrape.md) before you send it.

## Billing errors

`402 USAGE_EXCEEDED` means the authenticated account cannot cover the operation's credit cost. Inspect `error_data` for the balance, required credits, retry condition, and available refill details. Save `request_id` when investigating a failed request. Use the free usage endpoint or MCP `get-usage` to inspect the account, and retry once the balance covers the operation. Token refresh and reconnection do not restore credits.

`401` means authentication failed. `403 PAID_PLAN_REQUIRED` identifies a feature entitlement, and `429 RATE_LIMITED` identifies temporary throttling. For concurrency limits, inspect `error_data` and follow `Retry-After` before retrying. See [billing and concurrency errors](https://docs.context.dev/account/billing.md) for response fields and recovery options.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.