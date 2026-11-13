# Timeouts, limits, and errors

> Handle deadlines, failed outputs, and response size limits.

Scrape returns each output independently. Inspect its `success` even after HTTP 200. `isPartial` signals failed or incomplete outputs when at least one requested output succeeds; it is absent when all requested outputs fail.

## Set a deadline

Send this body to `POST /web/scrape`. See the [Quickstart](https://docs.context.dev/quickstart.md) for authentication and SDK setup.

```json theme={null}
{
  "url": "https://example.com",
  "formats": {
    "markdown": true,
    "screenshot": true
  },
  "timeoutOpts": {
    "milliseconds": 30000,
    "behavior": "return-partial"
  }
}
```

The default is 90,000 ms with `behavior: "fail"`. Deadlines range from 1 to 300,000 ms; `return-partial` requires at least 5,000 ms. Keep your [client timeout](https://docs.context.dev/optimization/timeouts.md) longer than the API deadline.

`fail` returns 408 if the overall deadline is reached. Individual outputs can fail earlier while the request returns 200. `return-partial` permits the current page state and available outputs; check the outputs even if none succeeded. Neither behavior guarantees that all dynamic content finished rendering.

Fixed waits must total less than the capture budget. They are the `wait` actions plus the `waitFor` value: a number you set, or the default of 500 ms (2,000 ms with frames or an XML URL) when you omit it. A selector counts as 0 ms. The capture budget depends on `behavior`:

* `fail`: the full `timeoutOpts.milliseconds`.
* `return-partial`: the deadline minus a response reserve. With `formats.json`, the reserve first sets aside the smaller of 10,000 ms and a quarter of the deadline for extraction. It then holds back the smaller of 5,000 ms and a quarter of what remains.

## Size limits

| Output | Limit |
| - | - |
| Documents and original bytes | 50 MiB decoded. |
| Screenshot | 20 MiB and 40 megapixels. |
| Combined response | 80 MiB. |

An oversized output fails with `data: null` and `CONTENT_TOO_LARGE`. If the combined response is too large, the largest outputs are omitted until it fits.

## Failed outputs

A failed output keeps `data: null` and explains the failure:

```json theme={null}
"markdown": {
  "requested": true,
  "success": false,
  "data": null,
  "error_code": "WEBSITE_BLOCKED",
  "message": "The site served an anti-bot challenge or access wall instead of the page. Retrying later or from another sharedParams.country sometimes succeeds."
}
```

| `error_code` | Meaning |
| - | - |
| `WEBSITE_BLOCKED` | The site served an anti-bot challenge or access wall. |
| `NOT_FOUND` | The page returned HTTP 404. The base price still applies. |
| `PDF_IMAGES_ONLY` | The PDF has no text layer. Retry with `sharedParams.parsers.pdf.ocr` set to `auto`. |
| `UNSUPPORTED_CONTENT` | The output does not support the content type at the URL. |
| `CONTENT_TOO_LARGE` | The output exceeded its size limit. |
| `NO_PUBLISHED_MARKDOWN` | `markdownParams.sourcePreference` allows only `markdown-direct` and the page publishes no Markdown. Add `html-conversion` to convert the HTML instead. |
| `REQUEST_TIMEOUT` | The output was not ready before the deadline. |
| `WEBSITE_ACCESS_ERROR` | The page could not be retrieved or had no usable content. |
| `INTERNAL_ERROR` | A temporary failure. Retry the request. |

## Error handling

| Response | Check or action |
| - | - |
| `200`, one or more failed outputs | Read each failed output's `error_code` and `message`. Successful outputs remain usable. |
| `400` | Correct invalid fields, incompatible options, headers, or waits that exceed the deadline. |
| `401` | Check the API key and its status. |
| `403` | Check permissions, paid-plan access for actions or profiles, ZDR entitlement, or domain restrictions. |
| `408` | Shorten the work or increase the deadline. |
| `409`, `PROFILE_BUSY` | Wait for the other request using the browser profile to finish. |
| `410`, `PROFILE_NOT_FOUND` | Check the profile ID and organization, or create a new profile. |
| `422`, `PROFILE_SESSION_EXPIRED` or `PROFILE_REAUTHENTICATION_REQUIRED` | Create a [new browser profile](https://docs.context.dev/scrape/browser-profiles.md) with credentials and save the new `profile.id`. |
| `429` | Wait for `Retry-After`; see [rate limits](https://docs.context.dev/optimization/rate-limits.md). |
| `5xx` | Retry transient failures with bounded backoff. |

Keep `request_id` and `error_code` for [troubleshooting](https://docs.context.dev/optimization/troubleshooting.md). A screenshot failure, unfinished image enrichment, failed product extraction, or near-empty Markdown from a text-heavy page (such as an app shell that never rendered) can set `isPartial` without discarding other outputs.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.