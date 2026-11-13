# Quickstart

> Get an API key, install an SDK, scrape your first page, and check the response.

Make your first Context.dev request with cURL or an official SDK, then check the result. To have a coding agent do the setup, use the [Agent quickstart](https://docs.context.dev/agent-quickstart.md).

## 1. Get an API key

[Create an account](https://context.dev/signup), then copy a secret key from the [API keys](https://context.dev/dashboard/api-keys) page. Set it in the shell where you'll run the example:

```bash theme={null}
export CONTEXT_DEV_API_KEY="ctxt_secret_..."
```

Keep the key on your server. Don't commit it or put it in browser code. [API keys](https://docs.context.dev/account/api-keys.md) covers permissions and rotation.

## 2. Choose your client

cURL needs no installation. For an SDK, run the matching command; [SDKs](https://docs.context.dev/sdks) lists runtime requirements and shared defaults. These commands work on macOS, Linux, or WSL.

```bash TypeScript theme={null}
npm install context.dev
npm install --save-dev tsx
```

```bash Python theme={null}
python3 -m venv .venv
source .venv/bin/activate
python -m pip install context.dev
```

```bash Ruby theme={null}
gem install context.dev
```

```bash Go theme={null}
go mod init example.com/context-quickstart
go get github.com/context-dot-dev/context-go-sdk/v2
```

```bash PHP theme={null}
composer require "context-dev/context-dev-php:^2.37" guzzlehttp/guzzle
```

```bash cURL theme={null}
curl --version
```

Skip `go mod init` if your project already has a `go.mod`. Save the SDK example in a file and run it with the matching command:

| Client | File | Run |
| - | - | - |
| cURL | No file needed | Paste the command into your terminal. |
| TypeScript | `example.mts` | `npx tsx example.mts` |
| Python | `example.py` | `python example.py` |
| Ruby | `example.rb` | `ruby example.rb` |
| Go | `main.go` | `go run main.go` |
| PHP | `example.php`, beside `vendor` | `php example.php` |

## 3. Make a request

This request fetches `example.com` and returns its main content as Markdown. `formats` chooses the outputs, and one request can combine several.

```typescript TypeScript theme={null}
import ContextDev from "context.dev";

const client = new ContextDev({ apiKey: process.env.CONTEXT_DEV_API_KEY });

const page = await client.web.scrape({
  url: "https://example.com",
  formats: { markdown: true },
  sharedParams: { mainContentOnly: true },
});

console.log(page.markdown.data);
```

```python Python theme={null}
import os
from context.dev import ContextDev

client = ContextDev(api_key=os.environ["CONTEXT_DEV_API_KEY"])

page = client.web.scrape(
    url="https://example.com",
    formats={"markdown": True},
    shared_params={"main_content_only": True},
)

print(page.markdown.data)
```

```ruby Ruby theme={null}
require "cgi/core"
require "context_dev"

client = ContextDev::Client.new(api_key: ENV.fetch("CONTEXT_DEV_API_KEY"))

page = client.web.scrape(
  url: "https://example.com",
  formats: {markdown: true},
  shared_params: {main_content_only: true},
)

puts page.markdown.data
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

    page, err := client.Web.Scrape(context.Background(), contextdev.WebScrapeParams{
        URL:          "https://example.com",
        Formats:      contextdev.WebScrapeParamsFormats{Markdown: contextdev.Bool(true)},
        SharedParams: contextdev.WebScrapeParamsSharedParams{MainContentOnly: contextdev.Bool(true)},
    })
    if err != nil {
        panic(err)
    }

    fmt.Println(page.Markdown.Data)
}
```

```php PHP theme={null}
<?php

require __DIR__.'/vendor/autoload.php';

use ContextDev\Client;

$client = new Client(apiKey: getenv('CONTEXT_DEV_API_KEY'));

$page = $client->web->scrape(
    formats: ['markdown' => true],
    url: 'https://example.com',
    sharedParams: ['mainContentOnly' => true],
);

echo $page->markdown->data, PHP_EOL;
```

```bash cURL theme={null}
curl https://api.context.dev/v1/web/scrape \
  --request POST \
  --header "Authorization: Bearer $CONTEXT_DEV_API_KEY" \
  --header "Content-Type: application/json" \
  --data '{
    "url": "https://example.com",
    "formats": { "markdown": true },
    "sharedParams": { "mainContentOnly": true }
  }'
```

## 4. Check the result

The SDK examples print the page's Markdown, which starts with `# Example Domain`. cURL prints the whole JSON response. It always contains all nine outputs, and each one has `requested`, `success`, and `data`:

```json Response (trimmed) theme={null}
{
  "url": "https://example.com",
  "markdown": {
    "requested": true,
    "success": true,
    "data": "# Example Domain\n\nThis domain is for use in documentation examples without needing permission."
  },
  "html": { "requested": false, "success": null, "data": null },
  "metadata": { "title": "Example Domain" },
  "cache_metadata": { "status": "miss", "age_ms": 0 },
  "request_id": "3f1c2a6e-8b4d-4c1e-9f0a-2d7b5e6c8a91"
}
```

A `200` response can still contain a failed output, so check `success` before you read `data`. A failed output has `success: false`, `data: null`, and an `error_code` and `message` that explain the failure; the other outputs are unaffected. Outputs you didn't request have `success: null`.

Cached outputs can be up to three days old by default. Set `maxAgeMs: 0` to fetch a fresh copy; [Freshness and caching](https://docs.context.dev/scrape/freshness-and-caching.md) has the details.

## Try another API

Every endpoint uses the same key and `Authorization` header. Send one of these, then follow its guide for options:

| API | Send | Guide |
| - | - | - |
| Scrape, other formats | Add `html`, `screenshot`, `images`, `bytes`, `parse`, `highlights`, `json`, or `product` to `formats` | [Scrape](https://docs.context.dev/scrape/overview) |
| Map URLs | `GET /web/urls` with `domain=stripe.com` | [Map URLs](https://docs.context.dev/map/overview) |
| Crawl | `POST /web/crawl` with `url` and `maxPages` | [Crawl](https://docs.context.dev/crawl/overview) |
| Search | `POST /web/search` with `query` | [Search](https://docs.context.dev/search/overview) |
| Answers | `POST /web/answers` with `task` and an example object in `json_format` | [Answers](https://docs.context.dev/answers/overview) |
| Parse | `POST /parse` with the file's bytes as the body | [Parse](https://docs.context.dev/parse/overview) |
| Brand | `POST /brand/retrieve` with `"type": "by_domain"` and `domain` | [Brand](https://docs.context.dev/brand/overview) |
| Styleguide | `GET /web/styleguide` with `domain=stripe.com` | [Styleguide](https://docs.context.dev/brand/styleguide.md) |
| People Search | `POST /people/search` with a `query` describing the people | [People Search](https://docs.context.dev/people/search.md) |
| People Enrich (beta) | `POST /people/enrich` with a person's `email` | [People Enrich](https://docs.context.dev/people/enrich.md) |
| Company Search | `POST /company/search` with a `query` describing the companies | [Company Search](https://docs.context.dev/companies/search.md) |
| News | `POST /news/search` with `searchBy` naming a company | [News](https://docs.context.dev/news/overview) |
| Batches | `POST /batch/submit` with `input` listing URLs | [Batches](https://docs.context.dev/batches/overview) |
| Monitors | `POST /monitors` with `name` and `target` | [Monitors](https://docs.context.dev/monitors/overview) |

## If the request fails

| Status | What to do |
| - | - |
| `402` | `USAGE_EXCEEDED`: inspect free usage and [billing information](https://docs.context.dev/account/billing.md); wait for sufficient credits before retrying. |
| `401` | Read `error_code`. `NOT_FOUND` means the key is missing or wrong in this process, and `DISABLED` means the key was turned off. |
| `400` | Read `message` and `error_code`, fix the request, and don't retry it unchanged. |
| `408` | The request reached its `timeoutOpts` deadline. See [Timeouts](https://docs.context.dev/optimization/timeouts.md). |
| `429` | Your organization hit its concurrency limit or the Free plan's 10 requests per minute, or this API key hit its per-minute limit on older plans. Wait for the `Retry-After` window, then retry. |

[Troubleshooting](https://docs.context.dev/optimization/troubleshooting.md) covers other statuses and error codes.

## Next steps

> [card] [Scrape](https://docs.context.dev/scrape/overview)
>
> Combine formats, filter page content, and handle dynamic pages.

> [card] [Brand](https://docs.context.dev/brand/overview)
>
> Look up company logos, colors, and profile details.

> [card] [Production checklist](https://docs.context.dev/optimization/best-practices.md)
>
> Plan timeouts, retries, and key permissions before launch.

> [card] [API reference](https://docs.context.dev/api-reference/web-scraping/scrape.md)
>
> Check every parameter and response field.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.