# Context.dev: the web data API

> Fast web scraping with browsers, proxies, retries, batches, and monitors built in.

Get data from the internet, fast. Context.dev handles the scraping infrastructure so you can turn web pages into Markdown, structured JSON, screenshots, and more through one API.

Start with one URL, scrape thousands of pages in a batch, or monitor sites for changes.

**Quality comes standard.** JavaScript rendering and managed proxies are always on for web scraping, with no opt-out. We keep both enabled by design to maximize data quality and reliability, so you can focus on building.

> [card] [Quickstart](https://docs.context.dev/quickstart.md)
>
> Get an API key and make your first request.

> [card] [Agent quickstart](https://docs.context.dev/agent-quickstart.md)
>
> Paste one prompt into your coding agent to set up Context.dev.

> [card] [API reference](https://docs.context.dev/api-reference/web-scraping/scrape.md)
>
> Check each endpoint's parameters and response fields.

## Make a request

This request scrapes `example.com` and returns its main content as Markdown. The examples read your API key from `CONTEXT_DEV_API_KEY`; the [Quickstart](https://docs.context.dev/quickstart.md) covers getting a key and installing an SDK.

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

The page text is in `markdown.data`. The page title and description are in `metadata`.

## Scraping infrastructure, handled

* **Browsers.** JavaScript rendering comes built in. Use [browser actions](https://docs.context.dev/scrape/browser-actions.md) to click, type, and scroll before capturing a page.
* **Proxies and retries.** Context.dev manages proxy selection and fetch retries. Choose a [fetch country](https://docs.context.dev/scrape/location-and-headers.md) when location matters.
* **Fast results.** Get multiple formats from one page visit. Reuse [cached outputs](https://docs.context.dev/scrape/freshness-and-caching.md) for repeated reads, with control over freshness.
* **Batches.** [Process thousands of URLs](https://docs.context.dev/batches/overview) as a background job with queuing, progress tracking, and downloadable results.
* **Monitors.** [Watch pages and sites](https://docs.context.dev/monitors/overview) on a schedule and receive changes by webhook.

## Choose an API

| You have | You want | Use |
| - | - | - |
| A URL | Page content, structured data, or screenshots | [Scrape](https://docs.context.dev/scrape/overview) |
| A list of URLs, or a site to crawl | Results from a background job | [Batches](https://docs.context.dev/batches/overview) |
| A page or site to watch | A webhook when it changes | [Monitors](https://docs.context.dev/monitors/overview) |
| A domain | Its URLs, with available titles and descriptions | [Map URLs](https://docs.context.dev/map/overview) |
| A starting URL | Linked pages as Markdown in one response | [Crawl](https://docs.context.dev/crawl/overview) |
| A search query | Ranked web results, with page content if you ask for it | [Search](https://docs.context.dev/search/overview) |
| A research question and a JSON shape | An answer in that shape, with source URLs | [Answers](https://docs.context.dev/answers/overview) |
| A PDF, Office document, image, or other file | Its content as Markdown | [Parse](https://docs.context.dev/parse/overview) |

The same API also provides [brand data](https://docs.context.dev/brand/overview), [people search](https://docs.context.dev/people/search.md) and [enrichment](https://docs.context.dev/people/enrich.md), [company search](https://docs.context.dev/companies/search.md), and [company news](https://docs.context.dev/news/overview).

## Use Context.dev from an agent

The [Agent quickstart](https://docs.context.dev/agent-quickstart.md) gives your coding agent one prompt that picks a setup, connects your account, and verifies a first result. To set up one piece yourself, connect the [MCP server](https://docs.context.dev/install-mcp.md) for live tools, install the [agent skill](https://docs.context.dev/install-skill.md) to teach the agent the API, or use the [CLI](https://docs.context.dev/install-cli.md) in scripts.

## Before you ship

Context.dev is a hosted API with [SDKs](https://docs.context.dev/sdks) for TypeScript, Python, Ruby, Go, and PHP. The [production checklist](https://docs.context.dev/optimization/best-practices.md) covers timeouts, retries, and API key permissions. See [Credits and pricing](https://docs.context.dev/account/credits.md) for usage costs and each guide for limits and failure handling.

## APIs

> [card] [Scrape](https://docs.context.dev/scrape/overview)
>
> Turn any page into usable data.

> [card] [Map](https://docs.context.dev/map/overview)
>
> Discover the URLs on a website.

> [card] [Crawl](https://docs.context.dev/crawl/overview)
>
> Follow links and collect page content.

> [card] [Search](https://docs.context.dev/search/overview)
>
> Search the web for relevant results.

> [card] [Answers](https://docs.context.dev/answers/overview)
>
> Research questions with cited sources.

> [card] [Parse](https://docs.context.dev/parse/overview)
>
> Extract content from documents and images.

> [card] [Brand](https://docs.context.dev/brand/overview)
>
> Get logos, colors, fonts, and more.

> [card] [People](https://docs.context.dev/people/search.md)
>
> Find people and enrich their profiles.

> [card] [Companies](https://docs.context.dev/companies/search.md)
>
> Find companies by name or description.

> [card] [News](https://docs.context.dev/news/overview)
>
> Find the latest coverage of companies.

> [card] [Batches](https://docs.context.dev/batches/overview)
>
> Process thousands of URLs in parallel.

> [card] [Monitors](https://docs.context.dev/monitors/overview)
>
> Track changes across pages and sites.

## Account and operations

> [card] [API keys](https://docs.context.dev/account/api-keys.md)
>
> Create keys and control API access.

> [card] [Plans and billing](https://docs.context.dev/account/billing.md)
>
> Manage your plan and payment details.

> [card] [Team access](https://docs.context.dev/account/team.md)
>
> Invite teammates and manage their roles.

> [card] [ZDR usage](https://docs.context.dev/optimization/zero-data-retention.md)
>
> Keep request content out of retained logs.

> [card] [Request logs](https://docs.context.dev/optimization/usage-and-logs.md)
>
> Inspect requests and track your usage.

> [card] [Timeouts](https://docs.context.dev/optimization/timeouts.md)
>
> Set time limits for your requests.

> [card] [Rate limits](https://docs.context.dev/optimization/rate-limits.md)
>
> Plan throughput and handle rate limits.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.