# YouTube videos

> Read video metadata, descriptions, and available transcripts as Markdown.

Scrape a YouTube URL with `formats.markdown` to get a video document. It includes the title, channel, duration, views, description, and available captions with timestamps.

## Read a video

```typescript TypeScript theme={null}
import ContextDev from "context.dev";

const client = new ContextDev({
  apiKey: process.env.CONTEXT_DEV_API_KEY,
});

const page = await client.web.scrape({
  url: "https://www.youtube.com/watch?v=VIDEO_ID",
  formats: { markdown: true },
});

console.log(page.markdown.data);
```

```python Python theme={null}
import os
from context.dev import ContextDev

client = ContextDev(api_key=os.environ["CONTEXT_DEV_API_KEY"])

page = client.web.scrape(
    url="https://www.youtube.com/watch?v=VIDEO_ID",
    formats={"markdown": True},
)

print(page.markdown.data)
```

```ruby Ruby theme={null}
require "cgi/core"
require "context_dev"

client = ContextDev::Client.new(api_key: ENV.fetch("CONTEXT_DEV_API_KEY"))

page = client.web.scrape(
  url: "https://www.youtube.com/watch?v=VIDEO_ID",
  formats: {markdown: true},
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
    client := contextdev.NewClient(
        option.WithAPIKey(os.Getenv("CONTEXT_DEV_API_KEY")),
    )

    page, err := client.Web.Scrape(context.Background(), contextdev.WebScrapeParams{
        URL:     "https://www.youtube.com/watch?v=VIDEO_ID",
        Formats: contextdev.WebScrapeParamsFormats{Markdown: contextdev.Bool(true)},
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
    url: 'https://www.youtube.com/watch?v=VIDEO_ID',
    formats: ['markdown' => true],
);

echo $page->markdown->data, PHP_EOL;
```

```bash cURL theme={null}
curl https://api.context.dev/v1/web/scrape \
  -H "Authorization: Bearer $CONTEXT_DEV_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "formats": { "markdown": true }
  }'
```

## Supported URLs

Video URLs include `/watch`, `youtu.be`, `/shorts`, `/embed`, and `/live`. Channel URLs include `/channel/…`, `/@handle`, `/c/…`, and `/user/…`; they return a channel profile with subscriber and video counts.

A video without accessible captions still returns metadata and its description. Caption preference is English author-provided, English automatic, another automatic track, then another available track.

## Include images or ask a question

Set `markdownParams.includeImages: true` to include a video thumbnail or channel avatar. Request [Highlights](https://docs.context.dev/scrape/highlights.md) with a question to select relevant transcript passages. [JSON extraction](https://docs.context.dev/scrape/json.md) can structure the video document using your schema.

Transcript availability depends on what YouTube exposes for the video. Check the returned document before treating it as a complete transcript.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.