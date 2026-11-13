# Monitor targets

> Choose a page, sitemap, extract, or search target, understand how changes are detected, and update a target without losing settings.

`target` says what a monitor watches, and `change_detection` says how a difference becomes a change. Only `name` and `target` are required.

```typescript TypeScript theme={null}
import ContextDev from "context.dev";

const client = new ContextDev({ apiKey: process.env.CONTEXT_DEV_API_KEY });

const monitor = await client.monitors.create({
  name: "Terms of service",
  target: { type: "page", url: "https://example.com/legal/terms" },
});
console.log(monitor.id, monitor.change_detection.type);
```

```python Python theme={null}
import os
from context.dev import ContextDev

client = ContextDev(api_key=os.environ["CONTEXT_DEV_API_KEY"])

monitor = client.monitors.create(
    name="Terms of service",
    target={"type": "page", "url": "https://example.com/legal/terms"},
)
print(monitor.id, monitor.change_detection.type)
```

```ruby Ruby theme={null}
require "cgi/core"
require "context_dev"

client = ContextDev::Client.new(api_key: ENV.fetch("CONTEXT_DEV_API_KEY"))

monitor = client.monitors.create(
  name: "Terms of service",
  target: {type: "page", url: "https://example.com/legal/terms"},
)
puts monitor.id, monitor.change_detection.type
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

	monitor, err := client.Monitors.New(context.Background(), contextdev.MonitorNewParams{
		Name: "Terms of service",
		Target: contextdev.MonitorNewParamsTargetUnion{
			OfPage: &contextdev.MonitorNewParamsTargetPage{
				Type: "page",
				URL:  "https://example.com/legal/terms",
			},
		},
	})
	if err != nil {
		panic(err)
	}
	fmt.Println(monitor.ID, monitor.ChangeDetection.Type)
}
```

```php PHP theme={null}
<?php
require __DIR__.'/vendor/autoload.php';

use ContextDev\Client;

$client = new Client(apiKey: getenv('CONTEXT_DEV_API_KEY'));

$monitor = $client->monitors->create(
    name: "Terms of service",
    target: ["type" => "page", "url" => "https://example.com/legal/terms"],
);
echo $monitor->id, " ", $monitor->changeDetection->type, PHP_EOL;
```

```bash cURL theme={null}
curl https://api.context.dev/v1/monitors \
  -H "Authorization: Bearer $CONTEXT_DEV_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Terms of service",
    "target": { "type": "page", "url": "https://example.com/legal/terms" }
  }'
```

This page target has no `instructions`, so detection is inferred as `exact`, and the monitor runs daily.

## Targets

> [card] [Page monitors](https://docs.context.dev/monitors/targets/page.md)
>
> Watch the visible text of one page. Focus with CSS selectors, add instructions for semantic detection, and run browser actions before capture.

> [card] [Sitemap monitors](https://docs.context.dev/monitors/targets/sitemap.md)
>
> Watch a sitemap for URLs that are added or removed, filtered by path patterns.

> [card] [Extract monitors](https://docs.context.dev/monitors/targets/extract.md)
>
> Watch the pages of a site that matter for your instructions, with an optional JSON Schema.

> [card] [Search monitors](https://docs.context.dev/monitors/targets/search.md)
>
> Search the web on every run and report results you haven't seen before, judged against your instructions.

## Change detection

| Target | Detection |
| - | - |
| `page` without `instructions` | `exact` |
| `page` with `instructions` | `semantic` |
| `sitemap` | `exact` |
| `extract` | `semantic` |
| `search` | `semantic`; `exact` allowed |

Omit `change_detection` and it's inferred as shown. Any other pair returns `400`, including `exact` with page `instructions` and `semantic` without them. Search targets accept either type regardless of `instructions`. Semantic detection takes an optional `confidence_threshold` from 0 to 1 (default `0.75`). The judge rates each confirmed difference:

* It matters, with confidence at or above the threshold: reported as a change, and the baseline moves to the new content.
* It matters, with confidence below the threshold: not reported yet. The baseline stays, so the next run checks the same difference again.
* It doesn't matter: not reported, and the baseline takes the new content silently.

Search monitors judge each new result instead of a diff. See [Search monitors](https://docs.context.dev/monitors/targets/search.md) for that rule.

## Update a target

`PATCH /v1/monitors/{monitor_id}` replaces `target` as a whole, so send every field you want to keep, including `instructions` and selectors. Send `change_detection` together with `target`. If you leave it out, the monitor keeps its current detection type even when the new target implies another one. For example, adding `instructions` to an exact monitor without `"change_detection": {"type": "semantic"}` leaves it exact.

```json theme={null}
{
  "target": {
    "type": "page",
    "url": "https://example.com/legal/terms",
    "instructions": "Report changes to data retention, liability, or termination terms.",
    "include_selectors": ["article"]
  },
  "change_detection": { "type": "semantic" }
}
```

Any change to `target` or `change_detection`, including `confidence_threshold`, discards the baseline and queues a new baseline run, which reports no change. Updating `name`, `tags`, `schedule`, `status`, or `webhook` keeps the baseline.

## Limits and errors

An unsupported target and detection pair, or a target URL that isn't public, returns `400 INPUT_VALIDATION_ERROR` with a `details` list of each problem. See [Limits and errors](https://docs.context.dev/monitors/limits-and-errors.md) for every limit and error code.

## Related

* [Page monitors](https://docs.context.dev/monitors/targets/page.md), [Sitemap monitors](https://docs.context.dev/monitors/targets/sitemap.md), [Extract monitors](https://docs.context.dev/monitors/targets/extract.md), and [Search monitors](https://docs.context.dev/monitors/targets/search.md): fields and examples for each target.
* [Monitors overview](https://docs.context.dev/monitors/overview): create a monitor with a webhook.
* [Runs and changes](https://docs.context.dev/monitors/runs-and-changes.md): what each target's changes contain.
* [Update a monitor reference](https://docs.context.dev/api-reference/monitors/update.md)


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.