# Monitor events and alerts

> Choose change.detected or run.completed events, turn on retries, track failing deliveries, and rotate a monitor's signing secret.

A monitor with `webhook.url` sends a signed event to that URL after its runs. This page covers what monitors send. [Webhooks](https://docs.context.dev/webhooks.md) covers signature verification, retries, Slack formatting, and replay for monitors and batches.

## Events

| Event | Sent when | Payload |
| - | - | - |
| `change.detected` (default) | A run records a change. | `data.change`: the full change record. |
| `run.completed` | Any run completes, including baseline runs and runs that find no change. | `data.run`: the run. `data.change`: the change, or `null`. |

Set `webhook.events` to one or both. With both, a run that finds a change sends two events, each with its own ID. Deduplicate on the `X-Context-Id` header, which equals the payload's `id` and stays the same across retries and replays. Failed and skipped runs send nothing, so subscribe to `run.completed` if you want a heartbeat. The [`change.detected`](https://docs.context.dev/api-reference/monitors/webhook-payload) and [`run.completed`](https://docs.context.dev/api-reference/monitors/webhook-run-completed) references show the full payloads.

## Configure the webhook

Add `webhook` when you create a monitor, or set it later with `PATCH /v1/monitors/{monitor_id}`. This update subscribes to both events and turns on automatic retries:

```typescript TypeScript theme={null}
import ContextDev from "context.dev";

const client = new ContextDev({ apiKey: process.env.CONTEXT_DEV_API_KEY });

const monitor = await client.monitors.update("mon_123", {
  webhook: {
    url: "https://app.example.com/webhooks/context",
    events: ["change.detected", "run.completed"],
    retry: {},
  },
});
console.log(monitor.id);
```

```python Python theme={null}
import os
from context.dev import ContextDev

client = ContextDev(api_key=os.environ["CONTEXT_DEV_API_KEY"])

monitor = client.monitors.update(
    "mon_123",
    webhook={
        "url": "https://app.example.com/webhooks/context",
        "events": ["change.detected", "run.completed"],
        "retry": {},
    },
)
print(monitor.id)
```

```ruby Ruby theme={null}
require "cgi/core"
require "context_dev"

client = ContextDev::Client.new(api_key: ENV.fetch("CONTEXT_DEV_API_KEY"))

monitor = client.monitors.update(
  "mon_123",
  webhook: {
    url: "https://app.example.com/webhooks/context",
    events: ["change.detected", "run.completed"],
    retry: {},
  },
)
puts monitor.id
```

```go Go theme={null}
package main

import (
	"context"
	"fmt"
	"os"

	contextdev "github.com/context-dot-dev/context-go-sdk/v2"
	"github.com/context-dot-dev/context-go-sdk/v2/option"
	"github.com/context-dot-dev/context-go-sdk/v2/packages/param"
)

func main() {
	client := contextdev.NewClient(option.WithAPIKey(os.Getenv("CONTEXT_DEV_API_KEY")))

	monitor, err := client.Monitors.Update(context.Background(), "mon_123", contextdev.MonitorUpdateParams{
		Webhook: contextdev.MonitorUpdateParamsWebhook{
			URL:    "https://app.example.com/webhooks/context",
			Events: []string{"change.detected", "run.completed"},
			Retry:  param.Override[contextdev.RetryConfigParam](map[string]any{}),
		},
	})
	if err != nil {
		panic(err)
	}
	fmt.Println(monitor.ID)
}
```

```php PHP theme={null}
<?php
require __DIR__.'/vendor/autoload.php';

use ContextDev\Client;

$client = new Client(apiKey: getenv('CONTEXT_DEV_API_KEY'));

$monitor = $client->monitors->update(
    "mon_123",
    webhook: [
        "url" => "https://app.example.com/webhooks/context",
        "events" => ["change.detected", "run.completed"],
        "retry" => [],
    ],
);
echo $monitor->id, PHP_EOL;
```

```bash cURL theme={null}
curl -X PATCH https://api.context.dev/v1/monitors/mon_123 \
  -H "Authorization: Bearer $CONTEXT_DEV_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "webhook": {
      "url": "https://app.example.com/webhooks/context",
      "events": ["change.detected", "run.completed"],
      "retry": {}
    }
  }'
```

Save `monitor.webhook.secret` from the response in server-side secret storage, associated with `monitor.id`; the cURL response uses `webhook.secret` and `id`. Avoid logging the secret or the full response. Follow [Store the signing secret](https://docs.context.dev/webhooks.md#store-the-signing-secret), then connect [signature verification](https://docs.context.dev/webhooks.md#connect-verification-to-your-receiver) to your receiver before processing events.

* `retry: {}` turns on the default retry schedule. If you omit `retry` when you first add a webhook, delivery is best effort: one attempt, plus one quick retry after a network error, `429`, or `5xx`. See [Retries](https://docs.context.dev/webhooks.md#acknowledge-and-retry).
* On update, omitting `retry` or `events` keeps the current setting. For a new webhook, `events` defaults to `["change.detected"]`.
* A new or changed `url` gets a new signing secret, returned in `webhook.secret`. Sending the same `url` keeps the secret.
* `"webhook": null` removes the webhook.

## Delivery failures

When deliveries keep failing, the monitor's `webhook_failure` describes the streak:

```json theme={null}
{
  "webhook_failure": {
    "consecutive_failures": 3,
    "last_status": "rejected",
    "last_message": "Webhook endpoint returned HTTP 500.",
    "last_failed_at": "2026-09-26T09:15:40.000Z"
  }
}
```

`last_status` is `rejected` (a non-`2xx` response), `failed` (no response), or `skipped_unsafe_url` (the URL isn't public). With retries on, a delivery counts as failed only after its last retry fails. `webhook_failure` returns to `null` after a successful delivery or a URL change. After 3 failed deliveries in a row, everyone in your organization gets an email, once per streak. Monitors that share a receiver send at most one email a day between them.

Each run lists its deliveries in `webhook_delivery_ids`. Look one up with [Retrieve a webhook delivery](https://docs.context.dev/api-reference/webhooks/retrieve.md) and [List webhook delivery attempts](https://docs.context.dev/api-reference/webhooks/attempts.md), or [list deliveries](https://docs.context.dev/api-reference/webhooks/list.md) with `{"type": "monitor", "monitor_id": "mon_123"}`, adding `run_id` to narrow to one run or `status` to find `failed` ones. A monitor delivery has `event` set to `change.detected` or `run.completed`, and its `source` carries the `monitor_id` and `run_id`. [Delivery history and replay](https://docs.context.dev/webhooks.md#delivery-history-and-replay) explains delivery statuses, attempt fields, and the 7-day replay window.

A run also records every delivery it attempted in `webhook_deliveries`, one per subscribed event that fired. The field is omitted when no webhook was attempted, including for runs created before event selection was added.

| Field | Meaning |
| - | - |
| `delivery_id` | Delivery ID for status checks and retries, when available. |
| `event_id` | Identifier sent in the `X-Context-Id` header. |
| `event` | `change.detected` or `run.completed`. Deliveries recorded before event selection existed report `change.detected`. |
| `status` | `delivered` (any `2xx` response), `rejected`, `failed`, or `skipped_unsafe_url`. |
| `http_status` | The endpoint's final HTTP response status, or `null` when no response was received. |
| `attempted_at` | When the delivery was attempted. |
| `error` | Error details, or `null`. |

## Rotate the signing secret

`POST /v1/monitors/{monitor_id}/webhook/rotate-secret` issues a new secret and returns the monitor with it in `webhook.secret`. Rotation takes effect immediately: the old secret stops working, and every later attempt is signed with the new one, including retries and replays of earlier events. The new secret exists only once the call returns, so update your receiver right after rotating. Accept both secrets for a few minutes so attempts already in flight still verify, and [replay](https://docs.context.dev/webhooks.md#delivery-history-and-replay) any event your receiver rejected in between. A monitor without a webhook returns `409 MONITOR_NO_WEBHOOK`.

## Related

* [Webhooks](https://docs.context.dev/webhooks.md): verify signatures, retry schedules, Slack, and replay.
* [Runs and changes](https://docs.context.dev/monitors/runs-and-changes.md): poll instead of, or alongside, webhooks.
* [Rotate a monitor webhook secret reference](https://docs.context.dev/api-reference/monitors/rotate-webhook-secret.md)


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.