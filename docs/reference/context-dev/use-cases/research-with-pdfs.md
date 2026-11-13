# Research papers and PDFs with citations

> Turn selected documents into retrievable evidence, preserve source metadata, and verify generated citations against the text you obtained.

```text Recipe prompt theme={null}
Implement this recipe in my project:
https://docs.context.dev/use-cases/research-with-pdfs.md

Read the recipe and linked API guides, inspect this project's stack, and build the complete flow using its existing conventions.

Build a research flow for selected public pages, PDF URLs, and uploaded documents. Send uploaded files as raw bytes, enforce the documented size and page-range limits, and make OCR configurable. Preserve source and chunk IDs, retrieve evidence, and verify citation IDs and quoted passages against extracted text. Show partial or failed parses, and include page numbers only when supported by the source.

Reuse existing Context.dev configuration and keep secret API keys on the server. If Context.dev is not set up yet, follow https://docs.context.dev/agent-quickstart.md first. Add focused tests, run the relevant checks, and document setup and how to try the result.
```

Build a research assistant that can show the passage behind a finding. Context.dev turns pages and files into Markdown; your application tracks source identity, creates chunks, retrieves evidence, and verifies the answer.

[Sourcely uses Context.dev for journal and PDF crawling](https://www.context.dev/blog/sourcely-powers-academic-journal-and-pdf-crawling-with-context-dev). This recipe covers user-selected papers, including documents that need OCR.

## Choose the document input

| Starting point | Collection path |
| - | - |
| Research question | [Search](https://docs.context.dev/api-reference/web-scraping/search.md), optionally restricted to relevant publishers or repositories |
| Known public page or PDF URL | [Scrape](https://docs.context.dev/scrape/overview) with `formats.markdown`, plus `sharedParams.parsers.pdf` for PDFs |
| Uploaded PDF or file in your storage | [Parse](https://docs.context.dev/parse/overview), sending raw file bytes |

Store a source ID, title, original URL or internal document link, retrieval time, and selected page range before chunking. A file upload does not inherently contain its source URL; your application must retain that association.

Parse returns Markdown and the detected file type. It does not return a citation graph. To cite PDF pages, set `includeNumberedPages=true` on Parse or `sharedParams.parsers.pdf.includeNumberedPages` on Scrape: each page then starts with a `<!-- page N -->` line, so record the current page as you chunk.

## Parse a bounded selection

Start with a server-side key from the [Quickstart](https://docs.context.dev/quickstart.md). The Parse guide includes [requests in every SDK](https://docs.context.dev/parse/overview). This Python worker uses the standard library to make file-size checks, raw-byte upload, and failure states explicit.

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

`start` and `end` are inclusive and start at 1. Limiting pages does not reduce the uploaded file's byte size: the entire request must still fit within 50 MiB. Split oversized files first and record how each part maps to the original document.

For a public PDF URL, request `formats.markdown` from the Scrape API and set `sharedParams.parsers.pdf` with `startPage`, `endPage`, and `ocr` (`off` or `auto`). Follow [Scrape PDFs and documents](https://docs.context.dev/scrape/pdfs-and-documents.md) and the [API reference](https://docs.context.dev/api-reference/web-scraping/scrape.md) for the request format. See [OCR pricing](https://docs.context.dev/account/credits.md#scrape-modifiers) before processing scanned documents.

## Handle OCR and partial evidence

When a PDF has no usable text layer, Parse can return `PDF_IMAGES_ONLY`. If OCR is appropriate for your task and budget, retry with `ocr=True`. OCR applies to PDF pages without usable text and to standalone images; it is not a general interpretation of all charts, equations, or images. Standalone image uploads return image metadata unless you set `ocr=true`.

Keep `empty`, `ocr_required`, and `failed` sources visible in the research view. Even a `ready` result needs inspection when a finding depends on a table, formula, or scanned passage. A nonempty Markdown response is not proof that every selected page was recovered completely.

## Attach source identity to chunks

The next function splits retrieved paragraphs into bounded text chunks and preserves the requested range. It does not infer a page number from a chunk's position.

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

Add your embedding model's token limit before indexing. This small splitter may divide a long table or formula; use structure-aware splitting and inspect those cases when they matter. See [website RAG](https://docs.context.dev/use-cases/build-rag-from-websites.md) for indexing and retrieval.

## Verify the answer's citations

Give the model only the selected chunks and require a source chunk ID plus a supporting excerpt for each claim. Treat document text as evidence, never as instructions that change tool access or the task.

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

This check rejects invented IDs and excerpts; it does not establish that the excerpt logically supports the claim. Add a support review before presenting the finding. Render the original source link and excerpt so the reader can inspect them.

Label a range as **Pages requested: 1–5**, not as the exact page of a quote. Show an exact page citation only when the chunk came from a response requested with `includeNumberedPages`, whose `<!-- page N -->` markers map each passage to its original page. Resolve relative document links against the known original URL, and enforce document access when opening internal upload links.

## Try a mixed research set

Run one selectable-text PDF, one scanned PDF, and one empty or unreadable selection. Verify that failed documents remain visible, every citation resolves to retained text, and the answer acknowledges missing evidence. A model should be able to say that the available excerpts do not answer the question.

> [card] [Parse documents](https://docs.context.dev/parse/overview)
>
> Review supported formats, OCR, upload limits, and SDK examples.

> [card] [Live agent web tools](https://docs.context.dev/use-cases/live-web-context-for-agents.md)
>
> Add bounded source discovery and page reads.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.