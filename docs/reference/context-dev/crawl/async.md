# Large crawls

> Crawl a site in the background with your choice of Scrape Anything outputs.

Submit a crawl through `POST /batch/submit` when it is too large for one synchronous response. A batch returns an ID immediately and scrapes each discovered page with your selected Scrape Anything formats and parameters.

## Start from a URL

```typescript TypeScript theme={null}
import ContextDev from "context.dev";

const client = new ContextDev({ apiKey: process.env.CONTEXT_DEV_API_KEY });

const response = await client.batch.submit({
  input: {
    mode: "crawl",
    data: {
      formats: { markdown: true, html: true },
      source: {
        type: "start_url",
        url: "https://docs.context.dev/introduction",
        controls: {
          maxUrls: 100,
          maxDepth: 3,
          followSubdomains: false,
          regex: "^https://docs\\.context\\.dev/",
        },
      },
      sharedParams: {
        mainContentOnly: true,
      },
    },
  },
  tags: ["docs-crawl"],
  "Idempotency-Key": "docs-crawl-v1",
});
console.log(response);
```

```python Python theme={null}
import os
from context.dev import ContextDev

client = ContextDev(api_key=os.environ["CONTEXT_DEV_API_KEY"])

response = client.batch.submit(
    input={
        "mode": "crawl",
        "data": {
            "formats": {"markdown": True, "html": True},
            "source": {
                "type": "start_url",
                "url": "https://docs.context.dev/introduction",
                "controls": {
                    "max_urls": 100,
                    "max_depth": 3,
                    "follow_subdomains": False,
                    "regex": "^https://docs\\.context\\.dev/",
                },
            },
            "shared_params": {
                "main_content_only": True,
            },
        },
    },
    tags=["docs-crawl"],
    idempotency_key="docs-crawl-v1",
)
print(response)
```

```ruby Ruby theme={null}
require "cgi/core"
require "context_dev"

client = ContextDev::Client.new(api_key: ENV.fetch("CONTEXT_DEV_API_KEY"))

response = client.batch.submit(
  input: {
    mode: "crawl",
    data: {
      formats: {markdown: true, html: true},
      source: {
        type: "start_url",
        url: "https://docs.context.dev/introduction",
        controls: {
          max_urls: 100,
          max_depth: 3,
          follow_subdomains: false,
          regex: "^https://docs\\.context\\.dev/",
        },
      },
      shared_params: {
        main_content_only: true,
      },
    },
  },
  tags: ["docs-crawl"],
  idempotency_key: "docs-crawl-v1",
)
puts response.inspect
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
	body := map[string]any{
		"input": map[string]any{
			"mode": "crawl",
			"data": map[string]any{
				"formats": map[string]bool{"markdown": true, "html": true},
				"source": map[string]any{
					"type": "start_url",
					"url":  "https://docs.context.dev/introduction",
					"controls": map[string]any{
						"maxUrls":          100,
						"maxDepth":         3,
						"followSubdomains": false,
						"regex":            "^https://docs\\.context\\.dev/",
					},
				},
				"sharedParams": map[string]any{"mainContentOnly": true},
			},
		},
		"tags": []string{"docs-crawl"},
	}
	var response map[string]any
	err := client.Post(context.Background(), "/batch/submit", body, &response, option.WithHeader("Idempotency-Key", "docs-crawl-v1"))
	if err != nil { panic(err) }
	fmt.Println(response["id"], response["status"])
}
```

```php PHP theme={null}
<?php
require __DIR__.'/vendor/autoload.php';

use ContextDev\Client;

$client = new Client(apiKey: getenv('CONTEXT_DEV_API_KEY'));

$response = $client->batch->submit(
    input: [
        "mode" => "crawl",
        "data" => [
            "formats" => ["markdown" => true, "html" => true],
            "source" => [
                "type" => "start_url",
                "url" => "https://docs.context.dev/introduction",
                "controls" => [
                    "maxURLs" => 100,
                    "maxDepth" => 3,
                    "followSubdomains" => false,
                    "regex" => "^https://docs\\.context\\.dev/",
                ],
            ],
            "sharedParams" => [
                "mainContentOnly" => true,
            ],
        ],
    ],
    tags: ["docs-crawl"],
    idempotencyKey: "docs-crawl-v1",
);
var_dump($response);
```

```bash cURL theme={null}
curl -X POST https://api.context.dev/v1/batch/submit \
  -H "Authorization: Bearer $CONTEXT_DEV_API_KEY" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: docs-crawl-v1" \
  -d '{
    "input": {
      "mode": "crawl",
      "data": {
        "formats": { "markdown": true, "html": true },
        "source": {
          "type": "start_url",
          "url": "https://docs.context.dev/introduction",
          "controls": {
            "maxUrls": 100,
            "maxDepth": 3,
            "followSubdomains": false,
            "regex": "^https://docs\\.context\\.dev/"
          }
        },
        "sharedParams": {
          "mainContentOnly": true
        }
      }
    },
    "tags": ["docs-crawl"]
  }'
```

## Crawl controls

| `input.data.source.controls` field | Default | Limit |
| - | - | - |
| `maxUrls` | 100 | 1–100,000. |
| `maxDepth` | Unset | 0–50 for a start-URL crawl. |
| `regex` | None | RE2 pattern over normalized full URLs; up to 256 characters. The start URL is included. |
| `excludeRegex` | None | RE2 pattern for normalized full URLs to skip; up to 256 characters. Wins over `regex`; the start URL is still scraped. |
| `followSubdomains` | `false` | Start-URL crawls only. |
| `languages` | Every language | Start-URL crawls only. `same_as_start_url` follows only the start page's language; a list of codes such as `["en"]` follows those languages. |

Start-URL crawls stay on the same host, ignoring `www.`, unless subdomains are enabled. They do not follow non-page files or system paths. Out-of-scope redirects fail that page.

`languages` keeps translated copies of a site from using up `maxUrls` and credits. Links whose language cannot be determined are followed.

## Start from an inventory

For sitemap discovery, set `input.data.source` to `{"type":"sitemap","domain":"example.com"}` and choose `maxUrls`, `regex`, and `excludeRegex`. Discovery happens at submission and excludes subdomain sitemaps. `maxDepth` and `followSubdomains` apply only to the start-URL source.

Put formats and per-page extraction settings under `input.data`, using the same parameters as Scrape Anything; see [Submit a batch](https://docs.context.dev/batches/submit.md). Continue with [status and results](https://docs.context.dev/batches/results.md), [webhooks](https://docs.context.dev/webhooks.md), and [cancellation and limits](https://docs.context.dev/batches/limits-and-errors.md).


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.