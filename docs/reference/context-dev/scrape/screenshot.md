# Screenshot

> Capture a viewport, full page, element, or rectangle as an inline image.

Enable `formats.screenshot`. `screenshot.data` is a base64 image data URL that can be used as an image source or decoded into a file. It has no hosted URL.

## Take a screenshot

```typescript TypeScript theme={null}
import ContextDev from "context.dev";
import { writeFile } from "node:fs/promises";

const client = new ContextDev({ apiKey: process.env.CONTEXT_DEV_API_KEY });

const page = await client.web.scrape({
  url: "https://example.com/pricing",
  formats: { screenshot: true },
});

const encoded = page.screenshot.data!.split(",")[1];
await writeFile("screenshot.png", Buffer.from(encoded, "base64"));
console.log(page.url);
```

```python Python theme={null}
import base64
import os
from pathlib import Path
from context.dev import ContextDev

client = ContextDev(api_key=os.environ["CONTEXT_DEV_API_KEY"])

page = client.web.scrape(
    url="https://example.com/pricing",
    formats={"screenshot": True},
)

encoded = page.screenshot.data.split(",", 1)[1]
Path("screenshot.png").write_bytes(base64.b64decode(encoded))
print(page.url)
```

```ruby Ruby theme={null}
require "context_dev"

client = ContextDev::Client.new(api_key: ENV.fetch("CONTEXT_DEV_API_KEY"))

page = client.web.scrape(
  url: "https://example.com/pricing",
  formats: {screenshot: true},
)

encoded = page.screenshot.data.split(",", 2).last
File.binwrite("screenshot.png", encoded.unpack1("m"))
puts page.url
```

```go Go theme={null}
package main

import (
    "context"
    "encoding/base64"
    "fmt"
    "os"
    "strings"

    contextdev "github.com/context-dot-dev/context-go-sdk/v2"
    "github.com/context-dot-dev/context-go-sdk/v2/option"
)

func main() {
    client := contextdev.NewClient(option.WithAPIKey(os.Getenv("CONTEXT_DEV_API_KEY")))

    page, err := client.Web.Scrape(context.Background(), contextdev.WebScrapeParams{
        URL:     "https://example.com/pricing",
        Formats: contextdev.WebScrapeParamsFormats{Screenshot: contextdev.Bool(true)},
    })
    if err != nil {
        panic(err)
    }

    _, encoded, _ := strings.Cut(page.Screenshot.Data, ",")
    image, err := base64.StdEncoding.DecodeString(encoded)
    if err != nil {
        panic(err)
    }
    if err := os.WriteFile("screenshot.png", image, 0o644); err != nil {
        panic(err)
    }
    fmt.Println(page.URL)
}
```

```php PHP theme={null}
<?php

require __DIR__.'/vendor/autoload.php';

use ContextDev\Client;

$client = new Client(apiKey: getenv('CONTEXT_DEV_API_KEY'));

$page = $client->web->scrape(
    formats: ['screenshot' => true],
    url: 'https://example.com/pricing',
);

[, $encoded] = explode(',', $page->screenshot->data, 2);
file_put_contents('screenshot.png', base64_decode($encoded, true));
echo $page->url, PHP_EOL;
```

```bash cURL theme={null}
curl https://api.context.dev/v1/web/scrape \
  -H "Authorization: Bearer $CONTEXT_DEV_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/pricing",
    "formats": { "screenshot": true }
  }' \
  | jq -r '.screenshot.data | split(",")[1]' \
  | base64 --decode > screenshot.png
```

Abridged response (`data` shortened):

```json theme={null}
{"screenshot": {"requested": true, "success": true, "data": "data:image/png;base64,iVBORw0KGgo..."}}
```

## Choose the area and format

| `screenshotParams` field | Default | Values |
| - | - | - |
| `area` | `viewport` | `fullPage`, `{"selector":"main"}`, or `{x, y, width, height}`. |
| `format` | `png` | `png`, `jpeg`, or `webp`. |

An element selector must match exactly one visible element. Rectangle coordinates are in pixels.

## Capture a mobile page

```json theme={null}
{
  "url": "https://example.com",
  "formats": {
    "screenshot": true
  },
  "screenshotParams": {
    "area": "fullPage",
    "format": "webp"
  },
  "sharedParams": {
    "viewport": {
      "width": 390,
      "height": 844
    },
    "theme": "dark"
  }
}
```

For one component, replace `area` with `{"selector":"#pricing"}`. [Waiting and rendering](https://docs.context.dev/scrape/waiting-and-rendering.md) covers page readiness, animations, and popup handling.

## Limits

Screenshots are limited to 40 megapixels and 20 MiB. The full response has a separate [size limit](https://docs.context.dev/scrape/timeouts-and-errors.md#size-limits). Popup removal is heuristic; review captured images when the distinction matters. Authenticated captures can contain private page content.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.