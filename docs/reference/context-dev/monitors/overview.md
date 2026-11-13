# Monitors

> Watch a page, a sitemap, or a site's key pages on a schedule. Get changes by signed webhook or by polling runs and changes.

A monitor captures a baseline of a target, checks the target again on a schedule, and records a change when it finds a difference that counts. Receive changes as signed webhooks, or poll runs and changes through the API.

## Pick a target

| What you want to know | Target | Detection |
| - | - | - |
| Did the visible text on a page change? | `page` | `exact` |
| Did something I care about change on a page? | `page` with `instructions` | `semantic` |
| Were URLs added to or removed from a sitemap? | `sitemap` | `exact` |
| Did something I care about change across a site's key pages? | `extract` | `semantic` |
| Is there new web coverage about a topic that matters to me? | `search` | `semantic` |
| Are there any new web results for a query? | `search` with `exact` detection | `exact` |

These are the only supported pairs. Exact detection reports every text difference. Semantic detection confirms a text difference, then asks an AI judge whether it matters under your `instructions`. When you omit `change_detection`, it's inferred from the target as in the table. Extract monitors cost more per run than page and sitemap monitors. See [credits](https://docs.context.dev/account/credits.md).

## Create a monitor

This monitor watches a changelog page and reports only the changes its instructions describe. Because the target has `instructions`, detection is `semantic`. The examples read your API key from `CONTEXT_DEV_API_KEY`; the [Quickstart](https://docs.context.dev/quickstart.md) shows how to set one up.

```typescript TypeScript theme={null}
import ContextDev from "context.dev";

const client = new ContextDev({ apiKey: process.env.CONTEXT_DEV_API_KEY });

const monitor = await client.monitors.create({
  name: "Changelog announcements",
  target: {
    type: "page",
    url: "https://example.com/changelog",
    instructions: "Report new features, deprecations, and breaking changes. Ignore dates and typo fixes.",
    include_selectors: ["main"],
    exclude_selectors: [".timestamp"],
  },
  webhook: { url: "https://app.example.com/webhooks/context", retry: {} },
});
console.log(monitor.id, monitor.initial_run_id);
```

```python Python theme={null}
import os
from context.dev import ContextDev

client = ContextDev(api_key=os.environ["CONTEXT_DEV_API_KEY"])

monitor = client.monitors.create(
    name="Changelog announcements",
    target={
        "type": "page",
        "url": "https://example.com/changelog",
        "instructions": "Report new features, deprecations, and breaking changes. Ignore dates and typo fixes.",
        "include_selectors": ["main"],
        "exclude_selectors": [".timestamp"],
    },
    webhook={"url": "https://app.example.com/webhooks/context", "retry": {}},
)
print(monitor.id, monitor.initial_run_id)
```

```ruby Ruby theme={null}
require "cgi/core"
require "context_dev"

client = ContextDev::Client.new(api_key: ENV.fetch("CONTEXT_DEV_API_KEY"))

monitor = client.monitors.create(
  name: "Changelog announcements",
  target: {
    type: "page",
    url: "https://example.com/changelog",
    instructions: "Report new features, deprecations, and breaking changes. Ignore dates and typo fixes.",
    include_selectors: ["main"],
    exclude_selectors: [".timestamp"],
  },
  webhook: {url: "https://app.example.com/webhooks/context", retry: {}},
)
puts monitor.id, monitor.initial_run_id
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

	monitor, err := client.Monitors.New(context.Background(), contextdev.MonitorNewParams{
		Name: "Changelog announcements",
		Target: contextdev.MonitorNewParamsTargetUnion{
			OfPage: &contextdev.MonitorNewParamsTargetPage{
				Type:             "page",
				URL:              "https://example.com/changelog",
				Instructions:     contextdev.String("Report new features, deprecations, and breaking changes. Ignore dates and typo fixes."),
				IncludeSelectors: []string{"main"},
				ExcludeSelectors: []string{".timestamp"},
			},
		},
		Webhook: contextdev.MonitorNewParamsWebhook{
			URL:   "https://app.example.com/webhooks/context",
			Retry: param.Override[contextdev.RetryConfigParam](map[string]any{}),
		},
	})
	if err != nil {
		panic(err)
	}
	fmt.Println(monitor.ID, monitor.InitialRunID)
}
```

```php PHP theme={null}
<?php
require __DIR__.'/vendor/autoload.php';

use ContextDev\Client;

$client = new Client(apiKey: getenv('CONTEXT_DEV_API_KEY'));

$monitor = $client->monitors->create(
    name: "Changelog announcements",
    target: [
        "type" => "page",
        "url" => "https://example.com/changelog",
        "instructions" => "Report new features, deprecations, and breaking changes. Ignore dates and typo fixes.",
        "includeSelectors" => ["main"],
        "excludeSelectors" => [".timestamp"],
    ],
    webhook: ["url" => "https://app.example.com/webhooks/context", "retry" => []],
);
echo $monitor->id, " ", $monitor->initialRunID, PHP_EOL;
```

```bash cURL theme={null}
curl https://api.context.dev/v1/monitors \
  -H "Authorization: Bearer $CONTEXT_DEV_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Changelog announcements",
    "target": {
      "type": "page",
      "url": "https://example.com/changelog",
      "instructions": "Report new features, deprecations, and breaking changes. Ignore dates and typo fixes.",
      "include_selectors": ["main"],
      "exclude_selectors": [".timestamp"]
    },
    "webhook": { "url": "https://app.example.com/webhooks/context", "retry": {} }
  }'
```

The API returns `201` with the monitor and `initial_run_id` (trimmed):

```json theme={null}
{
  "id": "mon_123",
  "status": "active",
  "change_detection": { "type": "semantic" },
  "schedule": { "type": "interval", "frequency": 1, "unit": "days" },
  "webhook": {
    "url": "https://app.example.com/webhooks/context",
    "secret": "whsec_…",
    "events": ["change.detected"],
    "retry": { "delays_seconds": [10, 60, 300, 1800, 7200, 21600, 57600] }
  },
  "next_run_at": "2026-09-27T03:14:00.000Z",
  "initial_run_id": "run_123"
}
```

Creating a monitor queues a baseline run right away. The baseline run captures the first snapshot and never reports a change; later runs compare against it. Pass `initial_run_id` to [Retrieve a monitor run](https://docs.context.dev/api-reference/monitors/retrieve-run.md) to confirm the baseline worked. If the run couldn't be queued, `initial_run_id` is `null` and the baseline runs at the next scheduled time.

Save `webhook.secret` in [server-side secret storage](https://docs.context.dev/webhooks.md#store-the-signing-secret), associated with the monitor `id`, and use it to [verify incoming deliveries](https://docs.context.dev/webhooks.md#verify-signatures). With no `schedule`, the monitor runs once a day; see [Schedules](https://docs.context.dev/monitors/schedules.md).

## Monitor fields

Create, retrieve, update, and list all return the monitor object. Besides `name`, `target`, `change_detection`, `schedule`, and `webhook`, it has:

| Field | Meaning |
| - | - |
| `mode` | Always `web`. Optional on create. |
| `status` | `active`, `paused`, or `failed`. Failed monitors keep running; paused monitors must be resumed with `status: "active"`. |
| `last_run_at`, `last_change_at` | When the monitor last ran and when it last recorded a change. Both can be null. |
| `next_run_at` | When the next scheduled run is due; null while paused. |
| `last_error` | `code` and `message` from the most recent failed run; null when the last run succeeded. |
| `webhook_failure` | Present while webhook deliveries are failing consecutively; null when deliveries are healthy or no webhook is configured. See [Events and alerts](https://docs.context.dev/monitors/webhooks.md). |
| `tags` | Up to 20 unique labels of 1–50 characters for filtering monitors, their changes, and their usage. |
| `policies` | [Access policy](https://docs.context.dev/optimization/access-policies.md) IDs applied to every run. On update, send an empty list to remove them. |
| `baseline` | The comparison baseline, included on retrieve. Null until capture completes or after the target changes. |
| `created_at`, `updated_at` | When the monitor was created and last updated. |

The `baseline` shape depends on the target, and every shape has `captured_at`, when it was last captured or replaced:

| Target | `baseline` fields |
| - | - |
| `page` | `text`, the page's visible text as last observed. |
| `sitemap` | `urls`, the sitemap URLs as last observed, sorted and normalized, and `url_count`. |
| `extract` | `data`, the latest structured snapshot matching the extraction schema, refreshed at most daily and `null` before capture, and `urls_analyzed`, the page URLs the monitor tracks. |
| `search` | `results`, each with `url`, `title`, `description`, and `published_at`. |

## List monitors

`GET /v1/monitors` returns your monitors in `data`, 25 per page by default and up to 100 with `limit`. While `has_more` is `true`, request the next page with `cursor` set to `next_cursor`. Filters combine.

| Parameter | Meaning |
| - | - |
| `q` | Free-text search term, up to 200 characters, matched against the fields named in `search_by`. |
| `search_by` | Comma-separated fields to search with `q`: `name`, `url`, `instructions`, and `tags`. Defaults to all fields. `url` also matches a search target's query. |
| `search_type` | `prefix` (default) for as-you-type prefix matching, or `exact` for full-token matching. |
| `status` | `active`, `paused`, or `failed`. |
| `target_type` | `page`, `sitemap`, `extract`, or `search`. |
| `change_detection_type` | `exact` or `semantic`. |
| `tags` | Comma-separated list of up to 20 tags; matches monitors that have any of them. |
| `tag` | One tag the monitor must have. |
| `limit`, `cursor` | Page size from 1 to 100, and the cursor from the previous page. |

If search is temporarily unavailable, a request with `q` returns `503 SEARCH_UNAVAILABLE`; retry, or list without search filters.

## Access

A restricted API key needs `monitors:write` to create, update, delete, or run a monitor, rotate its webhook secret, and replay its webhook deliveries. `monitors:read` covers monitors, runs, changes, limits, credit usage, and delivery history. `webhook.secret` is returned only to keys with `monitors:write`. See [API keys](https://docs.context.dev/account/api-keys.md).

## Before you rely on alerts

* The baseline run completed: `status: "completed"` and `baseline_created: true`.
* `instructions` say what matters and what to ignore.
* Your receiver verifies signatures and deduplicates events on `X-Context-Id`.
* Failed runs send no webhook, so you check runs for failures or subscribe to `run.completed` as a heartbeat.

## Related

* [Targets](https://docs.context.dev/monitors/targets): page, sitemap, extract, and search options, detection, and updates.
* [Schedules](https://docs.context.dev/monitors/schedules.md): intervals, run now, pause, and automatic pauses.
* [Runs and changes](https://docs.context.dev/monitors/runs-and-changes.md): run statuses and change records.
* [Events and alerts](https://docs.context.dev/monitors/webhooks.md): webhook events, delivery failures, and secret rotation.
* [Limits and errors](https://docs.context.dev/monitors/limits-and-errors.md): monitor limits per plan and error codes.
* [Website change digests](https://docs.context.dev/use-cases/website-change-digests.md): an end-to-end recipe.
* [Create a monitor reference](https://docs.context.dev/api-reference/monitors/create.md)


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.