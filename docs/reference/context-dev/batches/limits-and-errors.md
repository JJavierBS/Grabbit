# Cancel, limits, and errors

> Cancel or delete a batch, stay within batch concurrency and rate limits, and handle each error the Batches API returns.

## Cancel a batch

`POST /v1/batch/{batch_id}/cancel` stops a batch from starting new pages. It returns `202` with `status: "cancelling"`. Pages already in progress finish, then the batch becomes `cancelled`. Pages that never started stay in `progress.pending` and get no result records.

```typescript TypeScript theme={null}
import ContextDev from "context.dev";

const client = new ContextDev({ apiKey: process.env.CONTEXT_DEV_API_KEY });

const batch = await client.batch.cancel("batch_9f2c8a");
console.log(batch.status);
```

```python Python theme={null}
import os
from context.dev import ContextDev

client = ContextDev(api_key=os.environ["CONTEXT_DEV_API_KEY"])

batch = client.batch.cancel("batch_9f2c8a")
print(batch.status)
```

```ruby Ruby theme={null}
require "cgi/core"
require "context_dev"

client = ContextDev::Client.new(api_key: ENV.fetch("CONTEXT_DEV_API_KEY"))

batch = client.batch.cancel("batch_9f2c8a")
puts batch.status
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

	batch, err := client.Batch.Cancel(context.Background(), "batch_9f2c8a")
	if err != nil {
		panic(err)
	}
	fmt.Println(batch.Status)
}
```

```php PHP theme={null}
<?php
require __DIR__.'/vendor/autoload.php';

use ContextDev\Client;

$client = new Client(apiKey: getenv('CONTEXT_DEV_API_KEY'));

$batch = $client->batch->cancel("batch_9f2c8a");
echo $batch->status, PHP_EOL;
```

```bash cURL theme={null}
curl -X POST https://api.context.dev/v1/batch/batch_9f2c8a/cancel \
  -H "Authorization: Bearer $CONTEXT_DEV_API_KEY"
```

```json theme={null}
{
  "id": "batch_9f2c8a",
  "status": "cancelling",
  "progress": { "succeeded": 740, "failed": 3, "pending": 1257 }
}
```

Retrieve the batch for its final state and results once it's `cancelled`. Cancelling a batch that's already final returns `409 BATCH_NOT_CANCELLABLE`.

## Delete a batch

`DELETE /v1/batch/{batch_id}` permanently deletes a finished batch and its result files, and returns `{"id": "batch_9f2c8a", "deleted": true}`.

* While the batch is active, and briefly after it finishes while its usage settles, delete returns `409 BATCH_NOT_COMPLETED`. Cancel it if needed, wait for a final status, and retry.
* Its webhook delivery can no longer be retried or replayed.
* Its `Idempotency-Key` can be used for a new batch.

## Limits

| Limit | Value |
| - | - |
| URLs per batch | 1 to 100,000 |
| Request body | 24 MiB |
| Active batches (`queued`, `running`, or `cancelling`) | Free 1, Developer 2, Pro 5, Growth 5, Scale and Scale 2.5M 20 |
| Batches API rate limit | 1,000 units per minute per organization. A submit uses 50 units; every other batch call uses 1. |

Above the active-batch limit, submit returns `403 BATCH_LIMIT_EXCEEDED`. Wait for a batch to finish, or cancel one. Your organization may have a custom limit. See [Rate limits](https://docs.context.dev/optimization/rate-limits.md) for how rate limits apply across the API.

Submit also needs enough credits to cover every page the batch accepts, or up to `maxUrls` pages for a crawl. When it can't, it returns `402 USAGE_EXCEEDED` and no batch is created. See [credits](https://docs.context.dev/account/credits.md).

## Errors

| Status | `error_code` | Cause | What to do |
| - | - | - | - |
| 400 | `INPUT_VALIDATION_ERROR` | Invalid body, unknown key, no usable URLs, more than 100,000 URLs, `webhook` sent with `webhookUrl`, or a bad `cursor`. | Fix the request. |
| 402 | `USAGE_EXCEEDED` | Not enough credits for the reservation; no batch is created and no credits are reserved. | Inspect free usage, wait for sufficient credits, or submit fewer URLs. |
| 401 | | Missing, invalid, or disabled API key. | Check the key. |
| 403 | `BATCH_LIMIT_EXCEEDED` | Too many active batches. | Wait for one to finish, or cancel one. |
| 403 | `FORBIDDEN` | `sharedParams.profile` was sent, but browser profiles aren't enabled for your organization. | Remove `profile`, or upgrade to a plan with browser profiles. |
| 403 | `ACCESS_POLICIES_NOT_ENABLED` | `policies` was sent, but access policies aren't enabled for your organization. | Remove `policies`, or [contact us](mailto:support@context.dev) to enable them. |
| 403 | `INSUFFICIENT_PERMISSIONS` | A restricted key lacks `batches:read` or `batches:write`. | Use a key with that scope. |
| 404 | `NOT_FOUND` | No batch with that ID in your organization. | Check the ID. |
| 409 | `IDEMPOTENCY_KEY_CONFLICT` | The key was used with a different body, or the first request with this key is still in progress. | Send the original body, or retry in a moment. |
| 409 | `BATCH_NOT_COMPLETED` | Results or delete requested before the batch is final or settled. | Wait for a final status, then retry. |
| 409 | `BATCH_NOT_CANCELLABLE` | Cancel requested for a batch that's already final. | Nothing to cancel. |
| 429 | `RATE_LIMITED` | Batches API rate limit exceeded. | Back off and retry. |
| 500 | `INTERNAL_ERROR` | The batch couldn't be staged or queued. | See below. |
| 503 | `SEARCH_UNAVAILABLE` | Batch list search with `q` or `tags` is unavailable. | Retry, or list without `q` and `tags`. |

A `500` from submit can mean two things. If the batch was never created, retrying with the same `Idempotency-Key` is safe. If it was created but its work couldn't be queued, the same key returns that batch with `status: "failed"` and `failure.code: "enqueue_failed"`, so submit again with a new key.

Failures of individual pages don't produce HTTP errors. They appear as result records with `status: "error"`; see [page error codes](https://docs.context.dev/batches/results.md#read-results).

## Related

* [Status and results](https://docs.context.dev/batches/results.md): progress, results, and retention.
* [Submit a batch](https://docs.context.dev/batches/submit.md): idempotency and submission rules.
* [Cancel a batch reference](https://docs.context.dev/api-reference/batches/cancel.md) and [Delete a batch reference](https://docs.context.dev/api-reference/batches/delete.md)


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.