# Runs and changes

> Read a monitor's changes and runs, including run statuses, error codes, and skip reasons, per monitor or across your account.

Every check is a run. A run that finds a difference that counts creates a change. You can read both through the API whether or not you use webhooks.

## List changes

`GET /v1/monitors/{monitor_id}/changes` lists a monitor's changes, newest first.

```typescript TypeScript theme={null}
import ContextDev from "context.dev";

const client = new ContextDev({ apiKey: process.env.CONTEXT_DEV_API_KEY });

const page = await client.monitors.listChanges("mon_123", { limit: 20 });
for (const change of page.data) console.log(change.detected_at, change.title);
```

```python Python theme={null}
import os
from context.dev import ContextDev

client = ContextDev(api_key=os.environ["CONTEXT_DEV_API_KEY"])

page = client.monitors.list_changes("mon_123", limit=20)
for change in page.data:
    print(change.detected_at, change.title)
```

```ruby Ruby theme={null}
require "cgi/core"
require "context_dev"

client = ContextDev::Client.new(api_key: ENV.fetch("CONTEXT_DEV_API_KEY"))

page = client.monitors.list_changes("mon_123", limit: 20)
page.data.each { |change| puts "#{change.detected_at} #{change.title}" }
```

```go Go theme={null}
package main

import (
	"context"
	"fmt"
	"os"

	contextdev "github.com/context-dot-dev/context-go-sdk/v2"
	"github.com/context-dot-dev/context-go-sdk/v2/option"
)

func main() {
	client := contextdev.NewClient(option.WithAPIKey(os.Getenv("CONTEXT_DEV_API_KEY")))

	page, err := client.Monitors.ListChanges(context.Background(), "mon_123", contextdev.MonitorListChangesParams{
		Limit: contextdev.Int(20),
	})
	if err != nil {
		panic(err)
	}
	for _, change := range page.Data {
		fmt.Println(change.DetectedAt, change.Title)
	}
}
```

```php PHP theme={null}
<?php
require __DIR__.'/vendor/autoload.php';

use ContextDev\Client;

$client = new Client(apiKey: getenv('CONTEXT_DEV_API_KEY'));

$page = $client->monitors->listChanges("mon_123", limit: 20);
foreach ($page->data as $change) {
    echo $change->detectedAt->format(DATE_ATOM), " ", $change->title, PHP_EOL;
}
```

```bash cURL theme={null}
curl -G https://api.context.dev/v1/monitors/mon_123/changes \
  -H "Authorization: Bearer $CONTEXT_DEV_API_KEY" \
  --data-urlencode "limit=20"
```

A semantic page change (trimmed):

```json theme={null}
{
  "data": [
    {
      "id": "chg_123",
      "monitor_id": "mon_123",
      "run_id": "run_456",
      "target_type": "page",
      "change_detection_type": "semantic",
      "title": "Webhook signing added",
      "summary": "A new changelog entry says webhooks are now signed with HMAC-SHA256.",
      "importance": "medium",
      "confidence": 0.92,
      "url": "https://example.com/changelog",
      "diff": "+ Webhooks are now signed with HMAC-SHA256.",
      "detected_at": "2026-09-26T09:14:02.000Z",
      "tags": []
    }
  ],
  "has_more": false,
  "next_cursor": null
}
```

Every change has `title`, `summary`, `url`, `detected_at`, and `tags`. For search monitors, `url` is the first newly reported result. The other fields depend on the monitor:

| Monitor | `title` and `summary` | Other fields |
| - | - | - |
| Exact page | Fixed text, such as `example.com/legal/terms changed` | `diff`, `before_text_excerpt`, `after_text_excerpt` |
| Semantic page | Written by the judge | `importance`, `confidence`, `diff`, both text excerpts, `evidence`, `matched_urls` |
| Extract | Written by the judge | `importance`, `confidence`, `diff` with one section per page, `evidence` for up to 20 pages, `matched_urls`, and `removed_urls` for tracked pages that disappeared |
| Sitemap | Fixed text, such as `example.com sitemap changed`, with the counts | `added_urls`, `removed_urls`, and their counts |
| Exact search | Fixed text, `New results for "<query>"`, listing up to three result titles | `matched_urls`, `matched_url_count`, and `evidence` with one entry per new result |
| Semantic search | Written by the judge | `importance`, `confidence`, `matched_urls`, `matched_url_count`, and `evidence` with one entry per reported result |

`importance` is `low`, `medium`, or `high`, and `confidence` runs from 0 to 1. `diff` holds the changed lines, each prefixed with `+` or `-`, capped at 400 lines, 2,000 characters per line, and 100,000 characters in total. URL lists hold the first 500 URLs, and the `*_url_count` fields are always exact.

## Runs

`GET /v1/monitors/{monitor_id}/runs` lists a monitor's runs, newest first.

| `status` | Meaning |
| - | - |
| `queued` | Waiting to start. |
| `running` | In progress. |
| `completed` | Finished. `change_detected` and `change_id` say whether it found a change. `baseline_created` is `true` when it captured a new baseline instead of comparing. |
| `failed` | Didn't finish. `error.code` says why. |
| `skipped` | Never ran. `skip_reason` says why. |

`run_type` is `baseline` for the run queued when a monitor is created or its target or detection changes, and `scheduled` for scheduled runs and Run now. Each run also records:

| Field | Meaning |
| - | - |
| `started_at`, `completed_at` | When the run started and finished. Both can be null. |
| `credits_charged` | Credits charged for the run; 0 for skipped and failed runs. |
| `error` | For failed runs, the `code` from the table below and a `message` describing the failure; null otherwise. |
| `webhook_deliveries` | Every webhook delivery the run attempted, one per subscribed event that fired, each with `delivery_id`, `event_id`, `event`, `status`, `http_status`, `attempted_at`, and `error`. Omitted when no webhook was attempted. See [Events and alerts](https://docs.context.dev/monitors/webhooks.md). |
| `webhook_delivery_ids` | The delivery IDs for this run. |

| `error.code` | Meaning |
| - | - |
| `fetch_failed` | The page or sitemap couldn't be fetched, or the page had no usable text. |
| `extract_failed` | An extract monitor couldn't read the site. |
| `access_policy_denied` | An [access policy](https://docs.context.dev/optimization/access-policies.md) now blocks the target. |
| `judge_failed` | The semantic judge didn't return a verdict. |
| `config_changed` | The target or detection changed while the run was in progress. |
| `monitor_deleted` | The monitor was deleted during the run. |
| `enqueue_failed` | The run couldn't be queued. |
| `run_failed` | Any other failure. |

| `skip_reason` | Meaning |
| - | - |
| `insufficient_credits` | Your organization didn't have enough credits for the run. |
| `monitor_paused` | The monitor was paused after the run was queued. |
| `superseded` | Another run of the monitor was in progress, or the monitor was deleted before the run started. |

Failed and skipped runs don't send webhooks, so a missing event doesn't mean nothing changed. Check runs for failures, or see [Schedules](https://docs.context.dev/monitors/schedules.md#failures-and-automatic-pauses) for when repeated failures pause a monitor.

## Account-wide lists

| Endpoint | Filters |
| - | - |
| `GET /v1/monitors/{monitor_id}/changes` | `tag`, `since`, `until` |
| `GET /v1/monitors/{monitor_id}/runs` | `status` |
| `GET /v1/monitors/changes` (all monitors) | `monitor_id`, `target_type`, `change_detection_type`, `tag`, `since`, `until` |
| `GET /v1/monitors/runs` (all monitors) | `status` |

Every list returns 25 items by default and up to 100 with `limit`. While `has_more` is `true`, request the next page with `cursor` set to `next_cursor`. Change lists return full change records, the same as [Retrieve a monitor change](https://docs.context.dev/api-reference/monitors/change.md). Deleting a monitor also deletes its runs and changes.

`GET /v1/monitors/{monitor_id}` includes `baseline`, the snapshot that runs compare against. It's `null` until a baseline run completes.

## Credit usage

`GET /v1/monitors/credit-usage` sums settled credits per monitor over a window set with `since` and `until`. `data` holds one entry per monitor with `monitor_id`, `name` (the ID when the monitor was deleted), `credits` charged over the window, and the number of billed `runs`, sorted highest first. `total_credits` is the sum across all monitors in the window. [Limits and errors](https://docs.context.dev/monitors/limits-and-errors.md#runs-and-usage) describes the window cap.

## Related

* [Events and alerts](https://docs.context.dev/monitors/webhooks.md): get changes as they happen.
* [Targets](https://docs.context.dev/monitors/targets): how each target detects changes.
* [List monitor changes reference](https://docs.context.dev/api-reference/monitors/changes.md) and [List monitor runs reference](https://docs.context.dev/api-reference/monitors/runs.md)


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.