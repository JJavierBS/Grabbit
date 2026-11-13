# Webhooks

> Store signing secrets, verify incoming requests, and confirm, retry, or replay batch and monitor deliveries.

Batches send a final-status event. Monitors send `change.detected` by default and can also send `run.completed`. Use a public HTTP(S) receiver and enable retries explicitly.

## Events

| `event` | Source | Sent when |
| - | - | - |
| `batch.completed` | Batch | The batch completes. |
| `batch.failed` | Batch | The batch fails. |
| `batch.cancelled` | Batch | The batch is cancelled. |
| `change.detected` | Monitor | A run detects a change. |
| `run.completed` | Monitor | A run completes, including runs that find no change. |

Every payload has `event`, `id`, `created_at`, and `data`. `event` mirrors the `X-Context-Event` header and `id` mirrors `X-Context-Id`. [Status and results](https://docs.context.dev/batches/results.md#check-status) describes the batch in `data.batch`; [Monitor events and alerts](https://docs.context.dev/monitors/webhooks.md#events) describes `data.change` and `data.run`.

## Configure delivery

```json theme={null}
{"webhook":{"url":"https://app.example.com/webhooks/context","retry":{}}}
```

Omitting `retry` means best-effort delivery. Use HTTPS for your receiver in production.

Slack and GovSlack incoming-webhook URLs receive formatted messages instead of the JSON event envelope.

## Store the signing secret

Context.dev generates a **signing secret** when you configure a webhook. Save this secret on your server. Each incoming request carries a **signature** in `X-Context-Signature`, calculated using that secret and the request body. You verify each request's signature; you do not save it as a credential for future requests.

| Source | Where to get the secret | When to save it |
| - | - | - |
| Batch | `webhook_secret` in the [submit response](https://docs.context.dev/batches/submit.md), when you submit with `webhook` | Immediately after submission, alongside the batch `id`. Only the submit response returns it. |
| Monitor | `webhook.secret` in the monitor response, visible with full access or `monitors:write` (Manage) permission | When you add a webhook, change its URL, or [rotate its secret](https://docs.context.dev/monitors/webhooks.md#rotate-the-signing-secret). Associate it with the monitor `id`. |

For one source, inject the secret into your receiver as a server-side environment variable such as `CONTEXT_WEBHOOK_SECRET`. For multiple batches or monitors, keep a separate secret for each source in a secret manager or encrypted database field. Store a reference to it with the source ID and your application's receiver configuration. Sources that share a receiver URL still need their own secrets.

Keep the exact returned string, including any `whsec_` prefix. Use that full string as the HMAC key; do not Base64-decode it or hash it before storage. Your receiver needs the original value to verify requests. This secret is separate from `CONTEXT_DEV_API_KEY`: the API key authorizes API calls, and the webhook secret verifies incoming events.

Restrict secret access to the services that configure and receive webhooks. Keep it out of browser code, source control, URLs, and logs, including logs of API responses that contain it.

### Select the right secret

For multiple sources, give each receiver configuration an application-generated ID, for example `/webhooks/context/watch_123`. Use that route ID to look up the expected source and its secret before verifying the request. The route ID is a lookup key, not authentication. After verification, check that the payload belongs to the expected batch or monitor before processing it. Do not trust an unverified body or header to select a customer or authorize work.

Save the returned secret promptly: a delivery can arrive before your setup code finishes storing it. If a batch secret was not saved, later retrieval responses cannot recover it; use [batch status and results](https://docs.context.dev/batches/results.md) to reconcile the work. For a monitor, retrieve it with Manage permission or rotate the secret, then replay any rejected deliveries.

## Verify signatures

`X-Context-Signature` contains `t=<unix>,v1=<hex>`:

* `t` is the delivery attempt's Unix timestamp in **seconds**.
* `v1` is the hexadecimal HMAC-SHA256 digest of `t.rawRequestBody`, keyed with the signing secret.

For each request, read the original body bytes, prepend the timestamp string and a literal period, and compute the digest. Compare it with `v1` using a constant-time comparison. Reject missing or malformed signatures and timestamps outside your tolerance. The helper below uses five minutes in either direction; keep your receiver's clock synchronized.

Each attempt is signed with its current timestamp, including retries and manual replays. Check the header's `t`, not the payload's `created_at`, which remains the original event time.

```typescript verify-webhook.ts theme={null}
import { createHmac, timingSafeEqual } from "node:crypto";

export function verifyWebhook(rawBody: Buffer, header: string, secret: string): boolean {
  if (!secret || !Buffer.isBuffer(rawBody)) return false;
  const parts: Record<string, string> = Object.create(null);
  for (const part of header.split(",")) {
    const pair = part.trim().split("=");
    if (pair.length !== 2 || Object.hasOwn(parts, pair[0])) return false;
    parts[pair[0]] = pair[1];
  }
  if (!/^[0-9]{1,12}$/.test(parts.t ?? "") || !/^[a-f0-9]{64}$/i.test(parts.v1 ?? "")) return false;
  const timestamp = Number(parts.t);
  if (Math.abs(Date.now() / 1000 - timestamp) > 300) return false;
  const expected = createHmac("sha256", secret)
    .update(`${parts.t}.`).update(rawBody).digest();
  const actual = Buffer.from(parts.v1, "hex");
  return actual.length === expected.length && timingSafeEqual(actual, expected);
}
```

Verify **before parsing JSON**. Parsing and then calling `JSON.stringify` changes the bytes when whitespace, escaping, or key order differs, so a valid signature can fail. In Express, register the webhook route with `express.raw` before `express.json`. In a Fetch API handler, read `await request.arrayBuffer()` before calling any JSON parser. A [Python verification example](https://docs.context.dev/use-cases/website-change-digests.md#verify-and-persist-before-acknowledging) uses the same protocol.

### Connect verification to your receiver

This Express example handles one source using `CONTEXT_WEBHOOK_SECRET`. Save the helper above as `verify-webhook.ts`. Supply `persistEventOnce` from your own storage module: it must atomically save the verified event in a durable inbox with a unique constraint on `id`, succeed for an already-saved ID, and throw if storage fails. A worker can then process pending inbox entries. The [monitor digest recipe](https://docs.context.dev/use-cases/website-change-digests.md#verify-and-persist-before-acknowledging) shows an inbox implementation in Python.

```typescript receiver.ts theme={null}
import express from "express";
import { verifyWebhook } from "./verify-webhook.js";
import { persistEventOnce } from "./webhook-store.js";

const secret = process.env.CONTEXT_WEBHOOK_SECRET;
if (!secret) throw new Error("Set CONTEXT_WEBHOOK_SECRET before starting the receiver");

const app = express();
app.post("/webhooks/context", express.raw({ type: "application/json" }), async (req, res) => {
  if (!verifyWebhook(req.body, req.get("X-Context-Signature") ?? "", secret)) {
    res.status(401).send("Invalid webhook signature");
    return;
  }

  let event;
  try {
    event = JSON.parse(req.body.toString("utf8"));
  } catch {
    res.status(400).send("Invalid JSON");
    return;
  }
  if (!event || typeof event.id !== "string" || !event.id ||
      event.id !== req.get("X-Context-Id") ||
      typeof event.event !== "string" || event.event !== req.get("X-Context-Event")) {
    res.status(400).send("Invalid event envelope");
    return;
  }

  try {
    await persistEventOnce(event);
  } catch {
    res.status(503).send("Could not persist event");
    return;
  }
  res.sendStatus(204);
});

app.use(express.json());
app.listen(3000);
```

Validate the event's `data` against the [payload reference](#events) for the event types you handle before performing business actions. For multiple sources, replace the single environment variable with the route-based lookup described above.

The signature authenticates the timestamp and raw body, not the other headers independently. Use the verified body's `id` as your deduplication key and check that it matches `X-Context-Id`, as above. The ID stays the same across retries and replays; the signature and attempt number can change. Keep `X-Context-Delivery-Id` and `X-Context-Attempt` for troubleshooting, not as authentication or deduplication keys.

## Acknowledge and retry

Return any 2xx response within 15 seconds. Persist or enqueue verified events before acknowledging, then process them asynchronously. Redirects are not followed.

`retry: {}` uses delays of 10 seconds, 1 minute, 5 minutes, 30 minutes, 2 hours, 6 hours, and 16 hours, with up to 10% jitter. A custom `delays_seconds` list permits up to ten delays of 1–86,400 seconds, totaling at most 72 hours. An empty list disables automatic retries.

Network errors, 408, 429, and 5xx responses are retryable. Other 4xx and 3xx responses are final. `Retry-After` is honored.

## Confirm delivery

Signature verification confirms authenticity and body integrity. A `delivered` status confirms your receiver returned a 2xx response; it does not confirm that your background worker finished processing the event.

1. Configure the receiver and store the source's secret. For a monitor setup check, subscribe to `run.completed` so a completed run without changes also sends an event.
2. Complete a batch or [run the monitor](https://docs.context.dev/api-reference/monitors/run.md). Record the verified event `id` in your inbox and the delivery ID in your operational logs. Avoid logging the secret or full signature header.
3. [List deliveries](https://docs.context.dev/api-reference/webhooks/list.md) for that source and [retrieve the delivery](https://docs.context.dev/api-reference/webhooks/retrieve.md). Confirm `status: "delivered"`, then inspect its [attempts](https://docs.context.dev/api-reference/webhooks/attempts.md) for the HTTP status returned by your receiver.
4. Check your inbox and worker state separately to confirm processing. After correcting a receiver problem, [replay](#replay) the delivery. An already-saved event should return 2xx without repeating business actions.

### Troubleshoot verification

| Symptom | Check |
| - | - |
| Missing signature | Confirm the source was configured with `webhook` and your proxy forwards `X-Context-Signature`. Reject unsigned requests. |
| Digest mismatch | Use this source's full signing secret, not an API key or another source's secret. Preserve the raw body; disable JSON parsing before this route. |
| Timestamp rejected | Compare Unix seconds, synchronize the server clock, and use the attempt header's `t`, not `created_at`. Use a fresh replay instead of reusing an old captured header. |
| Failures after a URL change or rotation | Save the new monitor secret and reload it in every receiver instance. See [rotation](https://docs.context.dev/monitors/webhooks.md#rotate-the-signing-secret). |
| No automatic retry after a 401 or 400 | These responses are final. Fix verification or payload handling, then request a manual replay within the replay window. |
| Delivered but no business action | Check durable storage and worker errors. Delivery success only records your receiver's 2xx response. |

## Delivery history and replay

Each event creates one delivery, identified by a `whd_` ID, and every attempt to send it is recorded under that delivery. Delivery history lasts 30 days. [Retrieve a webhook delivery](https://docs.context.dev/api-reference/webhooks/retrieve.md) returns every field below; [search results](#search-deliveries) omit `event_id`, `retry`, and `last_attempt`.

| Delivery field | Meaning |
| - | - |
| `id` | Delivery ID. |
| `event` | One of the [events](#events) above. |
| `event_id` | Stable event ID for deduplicating received webhooks. |
| `source` | What produced the event: `type` is `batch` with a `batch_id`, or `monitor` with a `monitor_id` and `run_id`. |
| `url` | Webhook destination URL. |
| `status` | `pending`, `delivering`, `retrying`, `delivered`, `failed`, or `cancelled`. `cancelled` means the source or its webhook was removed. |
| `created_at` | Event creation time. |
| `delivered_at` | Last successful delivery time, or `null` if never delivered. |
| `next_attempt_at` | Next scheduled attempt, or `null` if none. |
| `retry_expires_at` | Last time you can retry manually, 7 days after the event. |
| `last_error` | Latest delivery error as `code` and `message`, or `null` if none. |
| `retry` | Automatic retry settings for this event, as `delays_seconds`. |
| `last_attempt` | Latest attempt, or `null` if none. |

### Attempts

[List webhook delivery attempts](https://docs.context.dev/api-reference/webhooks/attempts.md) returns a delivery’s attempts, newest first, 25 per page and up to 100 with `limit`. Page with `cursor` set to `next_cursor`.

| Attempt field | Meaning |
| - | - |
| `attempt` | Attempt number, starting at 1. |
| `trigger` | `initial`, `automatic` (a scheduled retry), or `manual` (the Retry endpoint). |
| `url` | URL used for this attempt. |
| `started_at`, `completed_at` | Attempt start and completion times. `completed_at` is `null` while in progress. |
| `http_status` | HTTP response status, or `null` if no response was received. |
| `error` | Attempt error as `code` and `message`, or `null` if none. |

### Search deliveries

[List webhook deliveries](https://docs.context.dev/api-reference/webhooks/list.md) is a `POST` whose body picks the source with `type` and returns deliveries from the last 30 days as summaries, with `has_more` and `next_cursor` for paging.

| Filter | Source | Notes |
| - | - | - |
| `type` | Both | Required. `batch` or `monitor`. |
| `batch_id` | `batch` | Filter by batch ID. |
| `monitor_id` | `monitor` | Filter by monitor ID. |
| `run_id` | `monitor` | Filter by monitor run ID. |
| `status` | Both | One delivery status. |
| `created_after` | Both | Only events created after this ISO 8601 timestamp. |
| `limit` | Both | 1–100. Defaults to 25. |
| `cursor` | Both | The `next_cursor` from the previous response. |

The body also accepts `tags`, which label the search request itself in [usage](https://docs.context.dev/optimization/usage-and-logs.md) rather than filter deliveries.

### Replay

[Retry a webhook delivery](https://docs.context.dev/api-reference/webhooks/retry.md) resends the original payload using the source’s current URL and signing secret. It returns `202` with the delivery `id` and a `Location` header for its status, and the resend appears as a `manual` attempt. The optional body takes `force: true` to resend a delivery that already succeeded. An optional `Idempotency-Key` header, up to 200 characters, prevents duplicate retry requests.

Manual replay is available for 7 days after the event (`retry_expires_at`); after that, retry returns `410`. A `409` means the delivery can’t be retried or the idempotency key conflicts. A source that was deleted or no longer has a webhook cannot be replayed. Replayed batch payloads resend their original result links; see [Download files](https://docs.context.dev/batches/results.md#download-files).

The delivery endpoints share a rate limit of 600 requests per minute per organization.

## Permissions and rotation

Read operations need the source’s `batches:read` or `monitors:read`; retries need its write scope. A monitor URL change regenerates its secret. Secret rotation takes effect immediately; update the receiver after the call returns and replay rejected events when needed. See [monitor events](https://docs.context.dev/monitors/webhooks.md#rotate-the-signing-secret).


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.