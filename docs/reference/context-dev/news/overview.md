# News

> Search news with a natural-language query or find articles about a company, then page through the results.

News Search finds current and historical articles. Describe what you want in plain language, or identify one company by name, domain, ticker, or ISIN. Results include story identifiers and source metadata.

## Search with natural language

Describe the news you want. See the [Quickstart](https://docs.context.dev/quickstart.md) for authentication and SDK setup.

```typescript TypeScript theme={null}
import ContextDev from "context.dev";

const client = new ContextDev({ apiKey: process.env.CONTEXT_DEV_API_KEY });
const news = await client.news.search({
  searchBy: { type: "natural_language", query: "chip export restrictions to China" },
  limit: 10,
});

console.log(news.data);
```

```python Python theme={null}
import os
from context.dev import ContextDev

client = ContextDev(api_key=os.environ["CONTEXT_DEV_API_KEY"])
news = client.news.search(
    search_by={"type": "natural_language", "query": "chip export restrictions to China"},
    limit=10,
)

print(news.data)
```

```ruby Ruby theme={null}
require "cgi/core"
require "context_dev"

client = ContextDev::Client.new(api_key: ENV.fetch("CONTEXT_DEV_API_KEY"))
news = client.news.search(
  search_by: {type: "natural_language", query: "chip export restrictions to China"},
  limit: 10,
)

pp news.data
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
    news, err := client.News.Search(context.Background(), contextdev.NewsSearchParams{
        SearchBy: contextdev.NewsSearchParamsSearchByUnion{
            OfNaturalLanguage: &contextdev.NewsSearchParamsSearchByNaturalLanguage{Query: "chip export restrictions to China"},
        },
        Limit: contextdev.Int(10),
    })
    if err != nil {
        panic(err)
    }

    fmt.Printf("%+v\n", news.Data)
}
```

```php PHP theme={null}
<?php

require __DIR__.'/vendor/autoload.php';

use ContextDev\Client;

$client = new Client(apiKey: getenv('CONTEXT_DEV_API_KEY'));
$news = $client->news->search(
    searchBy: ['type' => 'natural_language', 'query' => 'chip export restrictions to China'],
    limit: 10,
);

print_r($news->data);
```

```bash cURL theme={null}
curl https://api.context.dev/v1/news/search \
  -H "Authorization: Bearer $CONTEXT_DEV_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "searchBy": {"type": "natural_language", "query": "chip export restrictions to China"},
    "limit": 10
  }'
```

## Find company news

Search by the company’s domain.

```typescript TypeScript theme={null}
import ContextDev from "context.dev";

const client = new ContextDev({ apiKey: process.env.CONTEXT_DEV_API_KEY });
const news = await client.news.search({
  searchBy: { type: "entity", entity: { type: "domain", domain: "stripe.com" } },
  limit: 10,
});

console.log(news.data);
```

```python Python theme={null}
import os
from context.dev import ContextDev

client = ContextDev(api_key=os.environ["CONTEXT_DEV_API_KEY"])
news = client.news.search(
    search_by={"type": "entity", "entity": {"type": "domain", "domain": "stripe.com"}},
    limit=10,
)

print(news.data)
```

```ruby Ruby theme={null}
require "cgi/core"
require "context_dev"

client = ContextDev::Client.new(api_key: ENV.fetch("CONTEXT_DEV_API_KEY"))
news = client.news.search(
  search_by: {type: "entity", entity: {type: "domain", domain: "stripe.com"}},
  limit: 10,
)

pp news.data
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
    news, err := client.News.Search(context.Background(), contextdev.NewsSearchParams{
        SearchBy: contextdev.NewsSearchParamsSearchByUnion{
            OfEntity: &contextdev.NewsSearchParamsSearchByEntity{
                Entity: contextdev.NewsSearchParamsSearchByEntityEntityUnion{
                    OfDomain: &contextdev.NewsSearchParamsSearchByEntityEntityDomain{Domain: "stripe.com"},
                },
            },
        },
        Limit: contextdev.Int(10),
    })
    if err != nil {
        panic(err)
    }

    fmt.Printf("%+v\n", news.Data)
}
```

```php PHP theme={null}
<?php

require __DIR__.'/vendor/autoload.php';

use ContextDev\Client;

$client = new Client(apiKey: getenv('CONTEXT_DEV_API_KEY'));
$news = $client->news->search(
    searchBy: ['type' => 'entity', 'entity' => ['type' => 'domain', 'domain' => 'stripe.com']],
    limit: 10,
);

print_r($news->data);
```

```bash cURL theme={null}
curl https://api.context.dev/v1/news/search \
  -H "Authorization: Bearer $CONTEXT_DEV_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "searchBy": {"type": "entity", "entity": {"type": "domain", "domain": "stripe.com"}},
    "limit": 10
  }'
```

## Choose how to search

| `searchBy.type` | Fields | Results |
| - | - | - |
| `natural_language` | `query`, 2 to 1,000 characters. | Ranked by relevance with a boost for recent articles, up to 100 matches. `match` is `null`. |
| `entity` | `entity`, which identifies the company. | Newest first by default. `match` shows how the article relates to the company. |

Identify the company in `entity` with one of these types:

| `entity.type` | Fields | Limits |
| - | - | - |
| `name` | `name`. | 2–200 characters. |
| `domain` | `domain`. | 1–253 characters, such as `apple.com`. |
| `ticker` | `ticker`, with optional `exchange`. | 1–20 characters: letters, digits, dots, and hyphens. |
| `isin` | `isin`. | Two letters, nine letters or digits, and a check digit. |

Every search also accepts `policies`, a list of [access policy](https://docs.context.dev/optimization/access-policies.md) IDs that each article URL must pass, and `tags`, up to 20 [request tags](https://docs.context.dev/optimization/usage-and-logs.md) of 1–50 characters. Blocked results are removed.

## Match exact phrases

In a natural-language query, put a phrase in double quotes to require it word for word in the article's title, description, or text.

| Query | Returns articles that |
| - | - |
| `"export controls" on AI chips` | Contain "export controls". |
| `"Series A" OR "seed round" for climate startups` | Contain "Series A" or "seed round". |
| `semiconductor tariffs -"opinion"` | Do not contain "opinion". |

`OR` only joins quoted phrases: in `"Nvidia" OR AMD`, neither name is required. Straight and curly double quotes both work; single quotes are read as plain text.

## Read the articles

Articles are in `data`. `has_more` and `next_cursor` indicate another page; `meta.count` is the number of articles on it. Pages hold ten articles by default. Company searches return newest first by default; natural-language searches are ranked by relevance, with a boost for recent articles.

| Article field | Meaning |
| - | - |
| `id` | Stable identifier for the article. Use it to deduplicate or reference an article across requests. |
| `story_id` | Shared by articles covering the same story on the same day. Use it to group or collapse syndicated copies of one announcement. |
| `url`, `title`, `description` | Publisher link, headline, and summary. Natural-language search descriptions include matching passages and are capped at 2,000 characters. |
| `language` | Lowercase ISO 639-1 code, or `null` when unknown. |
| `authors` | Bylined authors; empty when no byline is available. |
| `image_url` | Lead image, or `null` when none is available. |
| `published_at` | ISO 8601 timestamp, or `null` when the publisher doesn't state a reliable date. |
| `type` | `editorial`, `press_release`, `regulatory_filing`, or `advisory`. |
| `source` | The publication's `name` and `domain`, and `direct`, which is `true` when Context observed the article in the publisher-owned feed. |
| `match` | For company searches: `level` is `primary` when the article is mainly about the company or `secondary` when it's mentioned but isn't the main subject, and `confidence` is 0–1 or `null`. `null` for natural-language searches. |

Use [filters and sorting](https://docs.context.dev/news/filter-and-sort.md) to select a source category or date window, and [pagination](https://docs.context.dev/news/paginate.md) for longer histories. An unknown company can return 404; invalid filters return 400. The [News reference](https://docs.context.dev/api-reference/news/search.md) lists the response fields.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.