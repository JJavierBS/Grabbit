# Images

> Collect page image URLs and optionally add dimensions, classifications, and hosted files.

Enable `formats.images` to collect page images, including responsive sources, CSS backgrounds, SVGs, and video posters. Read `images.data`; an empty array is a valid result.

## Extract images

```typescript TypeScript theme={null}
import ContextDev from "context.dev";

const client = new ContextDev({
  apiKey: process.env.CONTEXT_DEV_API_KEY,
});

const page = await client.web.scrape({
  url: "https://example.com",
  formats: { images: true },
});

console.log(page.images.data);
```

```python Python theme={null}
import os
from context.dev import ContextDev

client = ContextDev(api_key=os.environ["CONTEXT_DEV_API_KEY"])

page = client.web.scrape(
    url="https://example.com",
    formats={"images": True},
)

print(page.images.data)
```

```ruby Ruby theme={null}
require "cgi/core"
require "context_dev"

client = ContextDev::Client.new(api_key: ENV.fetch("CONTEXT_DEV_API_KEY"))

page = client.web.scrape(
  url: "https://example.com",
  formats: {images: true},
)

puts page.images.data
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
    client := contextdev.NewClient(
        option.WithAPIKey(os.Getenv("CONTEXT_DEV_API_KEY")),
    )

    page, err := client.Web.Scrape(context.Background(), contextdev.WebScrapeParams{
        URL:     "https://example.com",
        Formats: contextdev.WebScrapeParamsFormats{Images: contextdev.Bool(true)},
    })
    if err != nil {
        panic(err)
    }

    for _, image := range page.Images.Data {
        fmt.Println(image.URL, image.Alt)
    }
}
```

```php PHP theme={null}
<?php

require __DIR__.'/vendor/autoload.php';

use ContextDev\Client;

$client = new Client(apiKey: getenv('CONTEXT_DEV_API_KEY'));

$page = $client->web->scrape(
    formats: ['images' => true],
    url: 'https://example.com',
);

print_r($page->images->data);
```

```bash cURL theme={null}
curl https://api.context.dev/v1/web/scrape \
  -H "Authorization: Bearer $CONTEXT_DEV_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "formats": { "images": true }
  }'
```

Abridged response:

```json theme={null}
{"images": {"requested": true, "success": true, "data": [{"url":"https://example.com/photo.jpg","alt":"Team photo"}]}}
```

## Enrich and deduplicate

```json theme={null}
{
  "url": "https://example.com",
  "formats": {
    "images": true
  },
  "imageParams": {
    "enrich": [
      "dimensions",
      "classification",
      "file"
    ],
    "dedupe": "visual"
  }
}
```

| `imageParams` field | Default | Effect |
| - | - | - |
| `enrich` | None | Select `dimensions`, `classification`, or `file`. |
| `dedupe` | `none` | `visual` keeps the largest copy of visually duplicate images. |

Enrichment can add `width`, `height`, `classification`, and `fileUrl`. `classification` is one of `photography`, `illustration`, `logo`, `wordmark`, `icon`, `pattern`, `graphic`, or `other`. Fields can be absent when an image cannot be processed; `alt` can be `null`. Each image has up to 30 seconds to process within the request deadline. Early results may set `isPartial`.

## Hosted files and lazy galleries

Hosted `fileUrl` links expire 24 hours after capture and are omitted under [zero data retention](https://docs.context.dev/optimization/zero-data-retention.md). Cached hosted files refresh after 23 hours. Save copies you need to retain.

Use [scroll actions](https://docs.context.dev/scrape/browser-actions.md) for a lazy-loaded gallery and [content filters](https://docs.context.dev/scrape/content-filtering.md) to restrict images to that gallery. To download an original image, pass its URL to [Bytes](https://docs.context.dev/scrape/bytes.md). A classification describes an image; it does not establish usage rights.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.