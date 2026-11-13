# Answers

> Research a question and receive structured JSON with source URLs.

Give Answers a task and it researches with company and profile lookups, web searches, and page reads. Name a domain or page URL and Answers reads that page before searching, or, for company and profile questions, looks up those records first.

## Ask a question

```typescript TypeScript theme={null}
import ContextDev from "context.dev";

const client = new ContextDev({ apiKey: process.env.CONTEXT_DEV_API_KEY });

const response = await client.web.answers({
  mode: "fast",
  task: "Find the pricing page URL and plan names for context.dev.",
  json_format: {
    pricing_page_url: "",
    plans: [{ name: "" }],
  },
  timeoutOpts: { milliseconds: 30000, behavior: "return-partial" },
});

console.log(response.json_content, response.sources, response.partial ?? false);
```

```python Python theme={null}
import os
from context.dev import ContextDev

client = ContextDev(api_key=os.environ["CONTEXT_DEV_API_KEY"])

response = client.web.answers(
    mode="fast",
    task="Find the pricing page URL and plan names for context.dev.",
    json_format={"pricing_page_url": "", "plans": [{"name": ""}]},
    timeout_opts={"milliseconds": 30000, "behavior": "return-partial"},
)

print(response.json_content, response.sources, response.partial or False)
```

```ruby Ruby theme={null}
require "context_dev"

client = ContextDev::Client.new(api_key: ENV.fetch("CONTEXT_DEV_API_KEY"))

response = client.web.answers(
  mode: "fast",
  task: "Find the pricing page URL and plan names for context.dev.",
  json_format: {pricing_page_url: "", plans: [{name: ""}]},
  timeout_opts: {milliseconds: 30000, behavior: "return-partial"}
)

pp response.json_content, response.sources, response.partial
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

	response, err := client.Web.Answers(context.Background(), contextdev.WebAnswersParams{
		Mode: contextdev.WebAnswersParamsModeFast,
		Task: "Find the pricing page URL and plan names for context.dev.",
		JsonFormat: map[string]any{
			"pricing_page_url": "",
			"plans":            []any{map[string]any{"name": ""}},
		},
		TimeoutOpts: contextdev.WebAnswersParamsTimeoutOpts{Milliseconds: 30000, Behavior: "return-partial"},
	})
	if err != nil {
		panic(err)
	}

	fmt.Println(response.JsonContent, response.Sources, response.Partial)
}
```

```php PHP theme={null}
<?php
require __DIR__.'/vendor/autoload.php';

use ContextDev\Client;

$client = new Client(apiKey: getenv('CONTEXT_DEV_API_KEY'));

$response = $client->web->answers(
    task: 'Find the pricing page URL and plan names for context.dev.',
    mode: 'fast',
    jsonFormat: [
        'pricing_page_url' => '',
        'plans' => [['name' => '']],
    ],
    timeoutOpts: ['milliseconds' => 30000, 'behavior' => 'return-partial'],
);

print_r($response->jsonContent);
print_r($response->sources);
var_dump($response->partial ?? false);
```

```bash cURL theme={null}
curl https://api.context.dev/v1/web/answers \
  --request POST \
  --header "Authorization: Bearer $CONTEXT_DEV_API_KEY" \
  --header "Content-Type: application/json" \
  --data '{
  "mode": "fast",
  "task": "Find the pricing page URL and plan names for context.dev.",
  "json_format": {
    "pricing_page_url": "",
    "plans": [
      {
        "name": ""
      }
    ]
  },
  "timeoutOpts": {
    "milliseconds": 30000,
    "behavior": "return-partial"
  }
}'
```

Abridged response:

```json theme={null}
{"json_content":{"pricing_page_url":"https://www.context.dev/pricing","plans":[{"name":"Developer"},{"name":"Pro"},{"name":"Growth"},{"name":"Scale"}]},"sources":["https://www.context.dev/pricing"]}
```

## Choose a mode

| Mode | Research budget | Use |
| - | - | - |
| `fast` | Up to 30 seconds | Speed-first lookups that answer from explicit search snippets and cross-check people and company details. |
| `ultra` (default) | Up to 50 seconds | Deeper questions or several sources. |

Choose [the answer shape](https://docs.context.dev/answers/answer-shape.md), then handle [sources and deadlines](https://docs.context.dev/answers/sources-and-deadlines.md). See [credits](https://docs.context.dev/account/credits.md) when selecting a mode.

## Other request fields

| Field | Values |
| - | - |
| `timeoutOpts` | `milliseconds`, 1,000–300,000, and `behavior`: `fail` (default) returns 408 at the deadline; `return-partial` returns available results, so inspect `partial`. See [Sources and deadlines](https://docs.context.dev/answers/sources-and-deadlines.md#deadlines-and-partial-answers). |
| `zdr` | `enabled` turns on [zero data retention](https://docs.context.dev/optimization/zero-data-retention.md). Returns `403 ZDR_NOT_ENABLED` unless your organization has ZDR. |
| `policies` | [Access policy](https://docs.context.dev/optimization/access-policies.md) IDs. A URL must pass every policy, and blocked pages are never used as sources. |
| `tags` | Up to 20 [request tags](https://docs.context.dev/optimization/usage-and-logs.md), each 1–50 characters. |

For extraction from a known page with JSON Schema, use [Scrape JSON](https://docs.context.dev/scrape/json.md). The [Answers reference](https://docs.context.dev/api-reference/web-extraction/answers.md) documents the full contract.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.