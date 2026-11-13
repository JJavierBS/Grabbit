# Bytes

> Download the original response body as base64 with its content type.

Enable `formats.bytes`. `bytes.data` contains `contentType` and `base64` for the original HTTP body after transport decompression. Browser actions, waiting, and content filters do not alter these bytes.

## Download a resource

```typescript TypeScript theme={null}
import ContextDev from "context.dev";
import { writeFile } from "node:fs/promises";

const client = new ContextDev({ apiKey: process.env.CONTEXT_DEV_API_KEY });

const page = await client.web.scrape({
  url: "https://example.com",
  formats: { bytes: true },
  maxAgeMs: 0,
  timeoutOpts: { milliseconds: 30000, behavior: "fail" },
});

const file = page.bytes.data;
if (!file) throw new Error("Bytes were not returned");
const data = Buffer.from(file.base64, "base64");
await writeFile("resource.html", data);
console.log(file.contentType, data.length);
```

```python Python theme={null}
import base64
import os
from pathlib import Path

from context.dev import ContextDev

client = ContextDev(api_key=os.environ["CONTEXT_DEV_API_KEY"])

page = client.web.scrape(
    url="https://example.com",
    formats={"bytes": True},
    max_age_ms=0,
    timeout_opts={"milliseconds": 30000, "behavior": "fail"},
)

file = page.bytes.data
data = base64.b64decode(file.base64, validate=True)
Path("resource.html").write_bytes(data)
print(file.content_type, len(data))
```

```ruby Ruby theme={null}
require "cgi/core"
require "context_dev"
require "base64"

client = ContextDev::Client.new(api_key: ENV.fetch("CONTEXT_DEV_API_KEY"))

page = client.web.scrape(
  url: "https://example.com",
  formats: {bytes: true},
  max_age_ms: 0,
  timeout_opts: {milliseconds: 30000, behavior: "fail"},
)

file = page.bytes.data
data = Base64.strict_decode64(file.base64)
File.binwrite("resource.html", data)
puts file.content_type, data.bytesize
```

```go Go theme={null}
package main

import (
	"context"
	"encoding/base64"
	"fmt"
	"os"

	contextdev "github.com/context-dot-dev/context-go-sdk/v2"
	"github.com/context-dot-dev/context-go-sdk/v2/option"
)

func main() {
	client := contextdev.NewClient(option.WithAPIKey(os.Getenv("CONTEXT_DEV_API_KEY")))

	page, err := client.Web.Scrape(context.Background(), contextdev.WebScrapeParams{
		URL:         "https://example.com",
		Formats:     contextdev.WebScrapeParamsFormats{Bytes: contextdev.Bool(true)},
		MaxAgeMs:    contextdev.Int(0),
		TimeoutOpts: contextdev.WebScrapeParamsTimeoutOpts{Milliseconds: 30000, Behavior: "fail"},
	})
	if err != nil {
		panic(err)
	}

	data, err := base64.StdEncoding.DecodeString(page.Bytes.Data.Base64)
	if err != nil {
		panic(err)
	}
	if err := os.WriteFile("resource.html", data, 0600); err != nil {
		panic(err)
	}
	fmt.Println(page.Bytes.Data.ContentType, len(data))
}
```

```php PHP theme={null}
<?php

require __DIR__.'/vendor/autoload.php';

use ContextDev\Client;

$client = new Client(apiKey: getenv('CONTEXT_DEV_API_KEY'));

$page = $client->web->scrape(
    formats: ['bytes' => true],
    url: 'https://example.com',
    maxAgeMs: 0,
    timeoutOpts: ['milliseconds' => 30000, 'behavior' => 'fail'],
);

$file = $page->bytes->data;
$data = base64_decode($file->base64, true);
if ($data === false || file_put_contents('resource.html', $data) === false) {
    throw new RuntimeException('Could not decode or save the resource');
}
echo $file->contentType, ' ', strlen($data), PHP_EOL;
```

```bash cURL theme={null}
curl https://api.context.dev/v1/web/scrape \
  -H "Authorization: Bearer $CONTEXT_DEV_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "formats": { "bytes": true },
    "maxAgeMs": 0,
    "timeoutOpts": { "milliseconds": 30000, "behavior": "fail" }
  }'
```

Abridged response:

```json theme={null}
{"bytes": {"requested": true, "success": true, "data": {"contentType":"text/plain","base64":"SGVsbG8="}}}
```

Decode `base64` with your language’s base64 decoder and save the resulting bytes without text conversion.

## Keep a file and its text

```json theme={null}
{
  "url": "https://example.com/report.pdf",
  "formats": {
    "bytes": true,
    "markdown": true
  }
}
```

For an image that requires a referring page, set `sharedParams.headers.Referer` to that page’s URL. See [location and headers](https://docs.context.dev/scrape/location-and-headers.md). Request `html` as well as `bytes` to compare rendered HTML with the original response. For an image URL, `html` fails with `UNSUPPORTED_CONTENT` while `bytes` returns the image.

## Limits

The decoded body must fit within 50 MiB; bytes are never returned in a partial form. Targets must be public HTTP(S) URLs. Credentials are removed on cross-origin redirects. Page metadata is available for HTML, not arbitrary binary files.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.