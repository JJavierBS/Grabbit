# Monitor schedules

> Set how often a monitor runs, run it on demand, pause and resume it, and learn when a monitor pauses itself.

A monitor runs on a fixed interval, from every 10 minutes to once a year. Without a `schedule`, it runs once a day.

## Set the interval

Send `schedule` when you create a monitor, or change it later with `PATCH /v1/monitors/{monitor_id}`:

```json theme={null}
{
  "schedule": { "type": "interval", "frequency": 6, "unit": "hours" }
}
```

| Field | Notes |
| - | - |
| `type` | Always `interval`. |
| `frequency` | Whole number of units between runs, from 1 to 525,600. |
| `unit` | `minutes`, `hours`, or `days`. |

`frequency` × `unit` must come to at least 10 minutes and at most 1 year, so `unit: "minutes"` needs `frequency` of 10 or more and `unit: "days"` allows up to 365. The largest `frequency` the API accepts is 525,600, one year in minutes. Changing the schedule keeps the baseline.

Each monitor runs at its own fixed slot within the interval, derived from its ID, so monitors created together don't all run at the same moment. The first scheduled run can therefore come sooner than one full interval after you create the monitor. After that, runs are one interval apart. `next_run_at` on the monitor shows the next scheduled run.

## Run now

`POST /v1/monitors/{monitor_id}/run` queues a run outside the schedule and returns `202` with its `run_id`. The schedule doesn't move.

```typescript TypeScript theme={null}
import ContextDev from "context.dev";

const client = new ContextDev({ apiKey: process.env.CONTEXT_DEV_API_KEY });

const run = await client.monitors.run("mon_123");
console.log(run.run_id);
```

```python Python theme={null}
import os
from context.dev import ContextDev

client = ContextDev(api_key=os.environ["CONTEXT_DEV_API_KEY"])

run = client.monitors.run("mon_123")
print(run.run_id)
```

```ruby Ruby theme={null}
require "cgi/core"
require "context_dev"

client = ContextDev::Client.new(api_key: ENV.fetch("CONTEXT_DEV_API_KEY"))

run = client.monitors.run("mon_123")
puts run.run_id
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

	run, err := client.Monitors.Run(context.Background(), "mon_123")
	if err != nil {
		panic(err)
	}
	fmt.Println(run.RunID)
}
```

```php PHP theme={null}
<?php
require __DIR__.'/vendor/autoload.php';

use ContextDev\Client;

$client = new Client(apiKey: getenv('CONTEXT_DEV_API_KEY'));

$run = $client->monitors->run("mon_123");
echo $run->runID, PHP_EOL;
```

```bash cURL theme={null}
curl -X POST https://api.context.dev/v1/monitors/mon_123/run \
  -H "Authorization: Bearer $CONTEXT_DEV_API_KEY"
```

```json theme={null}
{ "monitor_id": "mon_123", "run_id": "run_456", "queued": true }
```

Pass `run_id` to [Retrieve a monitor run](https://docs.context.dev/api-reference/monitors/retrieve-run.md) to see the outcome. A paused monitor returns `409 MONITOR_PAUSED`. Runs of one monitor never overlap: if another run is already in progress, the new one is skipped with `skip_reason: "superseded"`.

## Pause and resume

```json theme={null}
{ "status": "paused" }
```

A paused monitor doesn't run, and its `next_run_at` is `null`. Send `{"status": "active"}` to resume it. A resumed monitor runs promptly, and its counts of consecutive failures and skips start over. Paused monitors still count toward your [monitor limit](https://docs.context.dev/monitors/limits-and-errors.md#limits).

## Failures and automatic pauses

When a run fails, the monitor's `status` becomes `failed` and `last_error` explains why, but runs continue on schedule. The next successful run sets the monitor back to `active`. Context.dev pauses a monitor for you, setting `status` to `paused`, after any of these:

* 10 failed runs in a row.
* 3 failed runs in a row before the monitor has a baseline.
* 3 runs in a row skipped because your organization didn't have enough credits.

Fix the cause, then resume the monitor. [Runs and changes](https://docs.context.dev/monitors/runs-and-changes.md#runs) lists the error codes and skip reasons.

## Related

* [Targets](https://docs.context.dev/monitors/targets): what a baseline run captures.
* [Events and alerts](https://docs.context.dev/monitors/webhooks.md): get a `run.completed` event after every completed run.
* [Run a monitor now reference](https://docs.context.dev/api-reference/monitors/run.md) and [Update a monitor reference](https://docs.context.dev/api-reference/monitors/update.md)


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.