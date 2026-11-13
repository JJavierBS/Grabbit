# Timeouts

> Set an API deadline and keep client retries from multiplying unfinished work.

`timeoutOpts` sets the API’s processing deadline. A client timeout controls how long your application waits for the response; configure both.

## Request deadline

For JSON endpoints, send:

```json theme={null}
{"timeoutOpts":{"milliseconds":30000,"behavior":"return-partial"}}
```

GET endpoints accept `timeoutOpts[milliseconds]=30000` and `timeoutOpts[behavior]=return-partial`, or a JSON-encoded `timeoutOpts` value. Use the endpoint reference for its minimum; the maximum is 300,000 ms.

| Behavior | Result |
| - | - |
| `fail` | Return 408 when the overall deadline is reached. |
| `return-partial` | Return usable work completed by the deadline when supported. |

Most endpoints use `partial: true`. Scrape uses `isPartial` and per-output `success`; [Scrape deadlines](https://docs.context.dev/scrape/timeouts-and-errors.md) describe its output-level failures. Prefetch supports only `fail`.

## Endpoint limits

Scrape defaults to 90 seconds, and `return-partial` needs at least five seconds. Fixed waits must leave room to return the response.

An uncached Brand domain/email lookup with `fail` and less than ten seconds returns `422 COLD_DOMAIN_TIMEOUT_TOO_LOW`. Use a longer budget, partial results, or [prefetch](https://docs.context.dev/brand/prefetching.md).

Answers deadlines can shorten but cannot extend the selected research budget. Crawl also has a soft `stopAfterMs` budget. Neither setting replaces the overall request deadline.

## Client timeout and retries

Keep the client timeout longer than the API deadline plus network overhead. SDK timeout and retry defaults are listed on [SDKs](https://docs.context.dev/sdks). A timed-out client can retry while the earlier request is still running; review retries for expensive or long tasks.

Scrape and Parse observe client disconnects. Other work may continue after your client stops waiting. For durable long-running jobs, use [Batches](https://docs.context.dev/batches/overview) and poll their status.

Do not cache a partial response as a complete result. Save its completion flag with the data and retry missing work when your product needs it.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.