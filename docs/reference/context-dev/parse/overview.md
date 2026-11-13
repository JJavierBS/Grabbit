# Parse documents

> Upload file bytes and convert them into Markdown or HTML.

Send a file to `POST /parse` as raw bytes, without multipart encoding or a JSON wrapper. Files can be up to 50 MiB. For a public document URL, use [Scrape documents](https://docs.context.dev/scrape/pdfs-and-documents.md).

## Convert a file

```typescript TypeScript theme={null}
import { readFile } from "node:fs/promises";
import ContextDev, { toFile } from "context.dev";

const client = new ContextDev({apiKey: process.env.CONTEXT_DEV_API_KEY});
const file = await toFile(await readFile("report.pdf"), "report.pdf", {
  type: "application/pdf",
});

const result = await client.parse.handle(file, {
  extension: "pdf"
}, {
  headers: {"Content-Type": "application/pdf"},
});

console.log(result.markdown);
```

```python Python theme={null}
import os
from pathlib import Path
from context.dev import ContextDev

client = ContextDev(api_key=os.environ["CONTEXT_DEV_API_KEY"])

result = client.parse.handle(
    body=Path("report.pdf").read_bytes(),
    extension="pdf",
    extra_headers={"Content-Type": "application/pdf"},
)

print(result.markdown)
```

```ruby Ruby theme={null}
require "cgi/core"
require "context_dev"

client = ContextDev::Client.new(api_key: ENV.fetch("CONTEXT_DEV_API_KEY"))

result = client.parse.handle(
  body: File.binread("report.pdf"),
  extension: :pdf,
  request_options: {extra_headers: {"Content-Type" => "application/pdf"}},
)

puts result.markdown
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

    file, err := os.Open("report.pdf")
    if err != nil {
        panic(err)
    }
    defer file.Close()
    result, err := client.Parse.Handle(
        context.Background(),
        file,
        contextdev.ParseHandleParams{},
        option.WithQuery("extension", "pdf"),
        option.WithHeader("Content-Type", "application/pdf"),
    )
    if err != nil {
        panic(err)
    }

    fmt.Println(result.Markdown)
}
```

```php PHP theme={null}
<?php

require __DIR__.'/vendor/autoload.php';

use ContextDev\Client;

$client = new Client(apiKey: getenv('CONTEXT_DEV_API_KEY'));

$bytes = file_get_contents('report.pdf');
if ($bytes === false) {
    throw new RuntimeException('Could not read report.pdf');
}

// Use the SDK's request method: the generated Parse helper drops the file bytes.
$raw = $client->request(
    method: 'post',
    path: 'parse',
    query: ['extension' => 'pdf'],
    headers: ['Content-Type' => 'application/pdf'],
    body: $bytes,
);

$result = json_decode((string) $raw->getBody(), true, flags: JSON_THROW_ON_ERROR);
echo $result['markdown'], PHP_EOL;
```

```bash cURL theme={null}
curl -X POST "https://api.context.dev/v1/parse?extension=pdf" \
  -H "Authorization: Bearer $CONTEXT_DEV_API_KEY" \
  -H "Content-Type: application/pdf" \
  --data-binary @report.pdf
```

Read `markdown` for the text and the returned type for the detected format. Request `includeLinks`, `includeImages`, `shortenBase64Images`, or `useMainContentOnly` as query options when they apply to your input.

## File types and OCR

Supply `extension` when the input type needs a hint; see [supported formats](https://docs.context.dev/parse/formats.md). [PDFs and OCR](https://docs.context.dev/parse/pdfs-and-ocr.md) covers scanned pages, images, and page ranges.

An oversized upload returns 413 and an unsupported format returns 415. A scanned PDF with OCR disabled returns `400 PDF_IMAGES_ONLY`; retry it with OCR enabled if text recovery is needed. A file that can't be read or has no extractable content returns `400 INPUT_VALIDATION_ERROR`. The [Parse reference](https://docs.context.dev/api-reference/utility/parse.md) lists all options and errors.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.