# PDFs and documents

> Extract text from a public document URL and optionally keep the original file.

Pass a public document URL to Scrape and request `markdown` or `html`. Add `bytes` to retain the original file. Use [Parse](https://docs.context.dev/parse/overview) for a local file or upload.

## Read selected PDF pages

Send this body to `POST /web/scrape`. See the [Quickstart](https://docs.context.dev/quickstart.md) for authentication and SDK setup.

```json theme={null}
{
  "url": "https://example.com/report.pdf",
  "formats": {
    "markdown": true,
    "bytes": true
  },
  "sharedParams": {
    "parsers": {
      "pdf": {
        "startPage": 1,
        "endPage": 5,
        "ocr": "auto"
      }
    }
  }
}
```

## PDF options

| `sharedParams.parsers.pdf` field | Meaning |
| - | - |
| `startPage` | First page, starting at 1. |
| `endPage` | Last page, inclusive; at least `startPage`. |
| `ocr` | `off` (default) or `auto` for scanned pages. |
| `includeNumberedPages` | `true` starts each page in the Markdown with a `<!-- page N -->` line; default `false`. |

OCR reads selected pages that lack usable text and leaves existing text layers intact. With OCR off, a scanned PDF returns failed text outputs with `error_code` `PDF_IMAGES_ONLY` inside HTTP 200. [Zero data retention](https://docs.context.dev/optimization/zero-data-retention.md) skips OCR.

By default, PDF Markdown joins pages without separators, drops page numbers, and keeps only the first copy of headers and footers repeated across pages. On text PDFs, each large image on the first 20 pages read appears as an `[image]` line.

## Mark page numbers

Set `includeNumberedPages: true` to start each page in the Markdown with a `<!-- page N -->` line, where N is the page's original 1-based number. With `startPage: 3`, the first marker is `<!-- page 3 -->`. Pages are separated by a blank line, and blank pages keep their marker. Use the markers to cite page numbers or split the document by page; they don't show when the Markdown is rendered.

Responses with page markers are never served from cache. [Batches](https://docs.context.dev/batches/submit.md) accept the same option in `sharedParams.parsers.pdf`, and [Parse](https://docs.context.dev/parse/pdfs-and-ocr.md#mark-page-numbers) accepts `includeNumberedPages=true` for uploaded files.

## Other documents

Scrape supports HTML, XML, PDF, DOC/DOCX, XLS/XLSX, and PPT/PPTX at URLs. Spreadsheets become tables; presentations become slide content. Use [Parse formats](https://docs.context.dev/parse/formats.md) to compare upload support.

Documents and original bytes are limited to 50 MiB. See [Scrape limits](https://docs.context.dev/scrape/timeouts-and-errors.md) before combining large text and binary outputs.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.