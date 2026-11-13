# Sources and deadlines

> Use source URLs, partial answers, and research time limits correctly.

`sources` lists the pages and company or profile records read for the answer, followed by URLs cited in `json_content`. Search results seen only as snippets are listed only when `json_content` cites them. It is not a field-by-field citation map. Cited URLs that research never encountered are removed from `json_content`.

## Freshness

Answers can reuse a cached page read: up to 30 days old in `fast` and 7 days in `ultra`. Source publication dates and the evidence’s own age still matter when asking about current facts.

## Deadlines and partial answers

`timeoutOpts.milliseconds` can shorten research but cannot extend the mode’s 30- or 50-second budget. It accepts 1,000–300,000 ms. Set the client timeout longer than the request deadline.

With `behavior: "return-partial"`, a valid answer from the evidence collected so far may be returned with `partial: true` when the deadline is reached or a model step fails after evidence was gathered. If no usable answer can be formed, the request fails. Treat absent or null facts as unresolved.

## Failures

Correct invalid tasks or answer shapes after 400. Handle 408 by reducing the task or allowing more time within the mode budget. A 504 `REQUEST_TIMEOUT` means research reached the mode’s time limit; narrow the task or use `return-partial`. Retry 500 `INTERNAL_ERROR` with backoff. Use [rate-limit headers](https://docs.context.dev/optimization/rate-limits.md) after 429.

[Zero data retention](https://docs.context.dev/optimization/zero-data-retention.md) is available when enabled for the organization. Save `request_id` for support without storing content your application does not need.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.