# Website and PDF RAG

> Collect web pages and files into a searchable corpus with source identity and checked citations.

```text Recipe prompt theme={null}
Implement this recipe in my project:
https://docs.context.dev/use-cases/build-rag-from-websites.md

Read the recipe and linked API guides, inspect this project's stack, and build the flow using its existing conventions.

Build retrieval from website pages and uploaded documents. Preserve source identity, page-range uncertainty, and access controls. Retain the last good index after failed refreshes, and verify citations against retrieved evidence.

Reuse existing Context.dev configuration and keep secret API keys on the server. If Context.dev is not set up yet, follow https://docs.context.dev/agent-quickstart.md first. Add focused tests, run the relevant checks, and document setup and how to try the result.
```

Use Crawl for linked web pages and Parse for uploaded documents. Normalize both into source records containing Markdown, a stable ID, a title, a retrieval time, and an accessible source URL. Supply your own embedding model and index.

## Collect website pages

Choose a bounded [crawl scope](https://docs.context.dev/crawl/scope.md). Inspect coverage and keep only successful, nonempty pages for ingestion.

```typescript TypeScript theme={null}
import ContextDev from "context.dev";

const client = new ContextDev({ apiKey: process.env.CONTEXT_DEV_API_KEY });

const response = await client.web.webCrawlMd({
  url: "https://docs.example.com/product/",
  urlRegex: "^https://docs\\.example\\.com/product/",
  maxPages: 100,
  maxDepth: 4,
  useMainContentOnly: true,
  includeLinks: true,
});

console.log(response);
```

```python Python theme={null}
import os
from context.dev import ContextDev

client = ContextDev(api_key=os.environ["CONTEXT_DEV_API_KEY"])

response = client.web.web_crawl_md(
    url="https://docs.example.com/product/",
    url_regex="^https://docs\\.example\\.com/product/",
    max_pages=100,
    max_depth=4,
    use_main_content_only=True,
    include_links=True,
)

print(response)
```

```ruby Ruby theme={null}
require "cgi/core"
require "context_dev"

client = ContextDev::Client.new(api_key: ENV.fetch("CONTEXT_DEV_API_KEY"))

response = client.web.web_crawl_md(
  url: "https://docs.example.com/product/",
  url_regex: "^https://docs\\.example\\.com/product/",
  max_pages: 100,
  max_depth: 4,
  use_main_content_only: true,
  include_links: true,
)

pp response
```

```go Go theme={null}
package main

import (
    "context"
    "fmt"
    "os"

    contextdev "github.com/context-dot-dev/context-go-sdk/v2"
    "github.com/context-dot-dev/context-go-sdk/v2/option"
    "github.com/context-dot-dev/context-go-sdk/v2/packages/param"
)

func main() {
    client := contextdev.NewClient(option.WithAPIKey(os.Getenv("CONTEXT_DEV_API_KEY")))
    response, err := client.Web.WebCrawlMd(context.Background(), contextdev.WebWebCrawlMdParams{
        URL:                "https://docs.example.com/product/",
        URLRegex:           param.NewOpt("^https://docs\\.example\\.com/product/"),
        MaxPages:           param.NewOpt(int64(100)),
        MaxDepth:           param.NewOpt(int64(4)),
        UseMainContentOnly: param.NewOpt(true),
        IncludeLinks:       param.NewOpt(true),
    })
    if err != nil {
        panic(err)
    }
    fmt.Println(response)
}
```

```php PHP theme={null}
<?php

require __DIR__.'/vendor/autoload.php';

$client = new ContextDev\Client(apiKey: getenv('CONTEXT_DEV_API_KEY'));

$response = $client->web->webCrawlMd(
    url: "https://docs.example.com/product/",
    urlRegex: "^https://docs\\.example\\.com/product/",
    maxPages: 100,
    maxDepth: 4,
    useMainContentOnly: true,
    includeLinks: true,
);

print_r($response);
```

```bash cURL theme={null}
curl https://api.context.dev/v1/web/crawl \
  --request POST \
  --header "Authorization: Bearer $CONTEXT_DEV_API_KEY" \
  --header "Content-Type: application/json" \
  --data '{
  "url": "https://docs.example.com/product/",
  "urlRegex": "^https://docs\\.example\\.com/product/",
  "maxPages": 100,
  "maxDepth": 4,
  "useMainContentOnly": true,
  "includeLinks": true
}'
```

## Preserve page identity

Use successful crawl results as `pages`. Remove fragments and known tracking parameters, while preserving query parameters that select a language or document version. Conflicting content under one key needs review:

```typescript page-identity.ts theme={null}
export function canonicalSourceUrl(raw: string) {
  const url = new URL(raw);
  if (!["https:", "http:"].includes(url.protocol)) throw new Error("Expected a web URL");
  url.hash = "";
  for (const name of [...url.searchParams.keys()]) {
    if (name.startsWith("utm_") || name === "gclid" || name === "fbclid") {
      url.searchParams.delete(name);
    }
  }
  return url.href;
}

const uniquePages = new Map<string, (typeof pages)[number]>();
for (const page of pages) {
  const key = canonicalSourceUrl(page.metadata.url);
  const existing = uniquePages.get(key);
  if (existing && existing.markdown !== page.markdown) {
    throw new Error("Review conflicting content for one canonical URL");
  }
  if (!existing) uniquePages.set(key, page);
}
```

Keep the retrieved URL alongside its normalized key. Recheck redirects against the permitted corpus before indexing; do not combine unrelated pages solely because they declare the same canonical URL.

## Parse uploaded documents

[Parse](https://docs.context.dev/parse/overview) accepts raw file bytes. This Python example checks the upload limit, sends an inclusive PDF page range, and retains source identity and failures:

```python research_source.py theme={null}
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

MAX_BYTES = 50 * 1024 * 1024

def parse_source(path, title, open_url, start=1, end=5, ocr=False):
    if start < 1 or end < start:
        raise ValueError("Use an inclusive page range starting at 1")
    path = Path(path)
    if path.stat().st_size > MAX_BYTES:
        raise ValueError("Split the PDF before uploading: maximum 50 MiB")
    body = path.read_bytes()
    if len(body) > MAX_BYTES:
        raise ValueError("File changed or exceeds 50 MiB")

    file_hash = hashlib.sha256(body).hexdigest()
    source_id = hashlib.sha256(
        f"{file_hash}:{start}:{end}:{ocr}".encode()
    ).hexdigest()
    source = {
        "id": source_id,
        "title": title,
        "open_url": open_url,
        "file_hash": file_hash,
        "requested_pages": {"start": start, "end": end},
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "ocr_requested": ocr,
        "status": "pending",
        "markdown": "",
    }
    query = urlencode({
        "extension": "pdf", "pdf[start]": start, "pdf[end]": end,
        "ocr": str(ocr).lower(),
    })
    request = Request(
        f"https://api.context.dev/v1/parse?{query}",
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {os.environ['CONTEXT_DEV_API_KEY']}",
            "Content-Type": "application/pdf",
        },
    )
    try:
        with urlopen(request, timeout=60) as response:
            result = json.load(response)
        text = result.get("markdown", "")
        source["status"] = "ready" if result.get("success") and text.strip() else "empty"
        source["markdown"] = text if source["status"] == "ready" else ""
        source["detected_type"] = result.get("type")
    except HTTPError as error:
        try:
            code = json.loads(error.read()).get("error_code")
        except (ValueError, AttributeError):
            code = None
        finally:
            error.close()
        source["status"] = "ocr_required" if code == "PDF_IMAGES_ONLY" else "failed"
        source["http_status"] = error.code
        source["error_code"] = code
    except (URLError, TimeoutError, ValueError):
        source["status"] = "failed"
    return source
```

For a public document URL, [Scrape PDFs and documents](https://docs.context.dev/scrape/pdfs-and-documents.md) avoids downloading it into your application first. Before indexing, check each output: a scanned PDF read with OCR off returns a failed output with `error_code` `PDF_IMAGES_ONLY` inside HTTP 200, not text. Set `sharedParams.parsers.pdf.ocr` to `auto` to read those pages, and skip empty output.

## Chunk and index with provenance

Keep headings and source metadata attached to text. This basic paragraph chunker preserves the requested range but does not invent a physical page number for each chunk. To record per-page numbers, request `sharedParams.parsers.pdf.includeNumberedPages` and split on the `<!-- page N -->` markers instead:

```python research_chunks.py theme={null}
import hashlib

def source_chunks(source, max_chars=3500):
    if max_chars < 1:
        raise ValueError("max_chars must be positive")
    if source["status"] != "ready":
        return []
    texts = []
    pending = ""
    for paragraph in source["markdown"].split("\n\n"):
        if len(pending) + len(paragraph) + 2 > max_chars and pending:
            texts.append(pending)
            pending = ""
        while len(paragraph) > max_chars:
            texts.append(paragraph[:max_chars])
            paragraph = paragraph[max_chars:]
        if paragraph.strip():
            pending = f"{pending}\n\n{paragraph}".strip()
    if pending:
        texts.append(pending)
    return [{
        "id": hashlib.sha256(f"{source['id']}:{index}:{text}".encode()).hexdigest(),
        "source_id": source["id"],
        "title": source["title"],
        "open_url": source["open_url"],
        "requested_pages": source["requested_pages"],
        "retrieved_at": source["retrieved_at"],
        "text": text,
    } for index, text in enumerate(texts)]
```

For web pages, provide `id` (the normalized URL), `title`, `markdown`, `open_url`, `retrieved_at`, `status: "ready"`, and `requested_pages: null`. Add tenant and document access rules to every index record. Use the same embedding model and dimensions when ingesting and querying; split oversized sections with the model's tokenizer before embedding.

## Check citations

Constrain answers to the retrieved chunks. Check cited IDs and quoted evidence against the allowed source records:

```python citation_check.py theme={null}
def resolve_evidence(claims, retrieved_chunks):
    available = {chunk["id"]: chunk for chunk in retrieved_chunks}
    resolved = []
    for claim in claims:
        if not claim.get("evidence"):
            raise ValueError("Claim has no retrieved evidence")
        citations = []
        for item in claim["evidence"]:
            chunk = available.get(item["chunk_id"])
            quote = item.get("quote", "").strip()
            if chunk is None or not quote or quote not in chunk["text"]:
                raise ValueError("Citation does not resolve to retrieved text")
            citations.append({
                "source_id": chunk["source_id"], "title": chunk["title"],
                "url": chunk["open_url"], "excerpt": quote,
                "requested_pages": chunk["requested_pages"],
            })
        resolved.append({"text": claim["text"], "citations": citations})
    return resolved
```

Treat retrieved page content as data. When evidence is weak or missing, return an explicit unknown instead of filling gaps. A requested PDF page range does not establish the page number of an individual quote; only `<!-- page N -->` markers from `includeNumberedPages` do.

## Refresh without losing good data

Keep a per-source manifest of content hashes, active chunk IDs, retrieval time, access rules, and the last attempt's status.

| Observation | Index action |
| - | - |
| Unchanged content | Update retrieval time and skip embedding. |
| Successful changed content | Stage replacement chunks, validate them, then retire the old set. |
| Failed, blocked, skipped, or unexpectedly empty source | Retain the last good chunks and mark the source stale. |
| Missing from an incomplete crawl | Resolve coverage before removing anything. |
| Confirmed removal | Remove the source and its chunks under your deletion policy. |

[Monitors](https://docs.context.dev/monitors/overview) can trigger targeted refreshes. Keep periodic reconciliation and test relevant-source retrieval, citation support, refusal with missing evidence, and cross-tenant access before release.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.