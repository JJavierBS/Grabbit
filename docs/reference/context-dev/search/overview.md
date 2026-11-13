# Search

> Find web pages from a query and optionally read each result’s content.

Search returns ranked URLs with titles, descriptions, and relevance information. Enable page content when you want Markdown alongside the results.

## Search the web

Start with a query and the number of results. See the [Quickstart](https://docs.context.dev/quickstart.md) for authentication and SDK setup.

```typescript TypeScript theme={null}
import ContextDev from "context.dev";

const client = new ContextDev({ apiKey: process.env.CONTEXT_DEV_API_KEY });
const search = await client.web.search({ query: "Stripe API authentication", numResults: 10 });

console.log(search.results);
```

```python Python theme={null}
import os
from context.dev import ContextDev

client = ContextDev(api_key=os.environ["CONTEXT_DEV_API_KEY"])
search = client.web.search(query="Stripe API authentication", num_results=10)

print(search.results)
```

```ruby Ruby theme={null}
require "cgi/core"
require "context_dev"

client = ContextDev::Client.new(api_key: ENV.fetch("CONTEXT_DEV_API_KEY"))
search = client.web.search(query: "Stripe API authentication", num_results: 10)

pp search.results
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
    search, err := client.Web.Search(context.Background(), contextdev.WebSearchParams{
        Query:      "Stripe API authentication",
        NumResults: contextdev.Int(10),
    })
    if err != nil {
        panic(err)
    }

    fmt.Printf("%+v\n", search.Results)
}
```

```php PHP theme={null}
<?php

require __DIR__.'/vendor/autoload.php';

use ContextDev\Client;

$client = new Client(apiKey: getenv('CONTEXT_DEV_API_KEY'));
$search = $client->web->search(query: 'Stripe API authentication', numResults: 10);

print_r($search->results);
```

```bash cURL theme={null}
curl https://api.context.dev/v1/web/search \
  -H "Authorization: Bearer $CONTEXT_DEV_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "Stripe API authentication", "numResults": 10}'
```

Read `results` for ranked pages. Request fields and the complete response are in the [Search reference](https://docs.context.dev/api-reference/web-scraping/search.md).

## Choose what to return

`numResults` ranges from 1 to 100 and defaults to 10. The actual number returned can be smaller. Use [filters](https://docs.context.dev/search/filters.md) to restrict domains, recency, and location. [Result content](https://docs.context.dev/search/page-content.md) covers page reads and per-result failures.

Set `descriptionMaxCharacters` to cap each result’s `description`; it defaults to `null` (no cap). When `descriptionMaxCharacters` is above 0, the request has no `includeDomains` or `excludeDomains` filter, and the query uses no search operator, news-index results fill that space with the article passages that best match your query.

Set `timeoutOpts.behavior` to `return-partial` if a subset of results is useful at your deadline, and inspect `partial`.

Add `policies` to apply [access policies](https://docs.context.dev/optimization/access-policies.md); a URL must pass every policy. Use `tags` to label requests for [usage filtering](https://docs.context.dev/optimization/usage-and-logs.md), and set `zdr` to `"enabled"` for [zero data retention](https://docs.context.dev/optimization/zero-data-retention.md) when your organization has ZDR access.

## Read the response

Each result carries a `relevance` of `high`, `medium`, or `low` relative to your query. `cache_metadata.status` is `hit`, `miss`, or `zdr`, and `cache_metadata.age_ms` is the age of the cached data in milliseconds; it is `0` for a miss or ZDR response.

## Research papers

Research-style queries, such as "transformer models for protein folding", can also return indexed research papers alongside web pages. A paper result's `url` links to the paper, and its `description` is a passage from the paper that matches your query. `freshness` filters papers by publication date, and `languages` applies to them too.

Papers are left out when you set `includeDomains` or `excludeDomains`, or when the query uses an operator such as `site:`, `OR`, a quoted phrase, or a `-` exclusion.

Use [Scrape](https://docs.context.dev/scrape/overview) when you already know the URL. Use [Answers](https://docs.context.dev/answers/overview) when you want a researched answer in a specific JSON shape.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.