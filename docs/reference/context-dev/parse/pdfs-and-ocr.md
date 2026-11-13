# PDFs and OCR

> Read scanned PDFs and images, with optional PDF page ranges.

OCR is off by default. PDF text layers are read directly; `ocr=true` recovers text from scanned pages and image inputs.

## Select PDF pages

Add `ocr=true`, `pdf[start]=1`, and `pdf[end]=5` to the Parse request query. Page numbers are inclusive and start at 1. The end must be at least the start.

For example, use the [Parse upload request](https://docs.context.dev/parse/overview) with the query `?extension=pdf&ocr=true&pdf[start]=1&pdf[end]=5`. URL-encode bracketed parameter names when your client requires it.

## Text layers and scans

OCR runs on selected PDF pages without usable text; pages with text retain their existing extraction. It is not a general description of every chart or photograph. A scanned PDF with OCR off returns `400 PDF_IMAGES_ONLY` from Parse.

By default, PDF Markdown joins pages without separators, drops page numbers, and keeps only the first copy of headers and footers repeated across pages. With `ocr=true`, a large image on the first 20 pages of a text PDF appears as an `[image]` line unless OCR reads that page.

## Mark page numbers

Add `includeNumberedPages=true` to the query to start each PDF page in the Markdown with a `<!-- page N -->` line. N is the page's original 1-based number, so with `pdf[start]=3` the first marker is `<!-- page 3 -->`. Pages are separated by a blank line, and blank pages keep their marker. Markers work with and without OCR.

For example, `?extension=pdf&includeNumberedPages=true&pdf[start]=3&pdf[end]=4` returns Markdown shaped like this:

```markdown theme={null}
<!-- page 3 -->

## Results

Revenue grew in every region.

<!-- page 4 -->

## Outlook
```

Use the markers to cite page numbers or split the document by page. They are HTML comments, so they don't show when the Markdown is rendered.

Standalone images return metadata without OCR. Enable `ocr=true` when you need the image’s text.

The [Scrape URL workflow](https://docs.context.dev/scrape/pdfs-and-documents.md) uses different option names: `sharedParams.parsers.pdf.ocr: "auto"`, `startPage`, `endPage`, and `includeNumberedPages`. Its text outputs can fail inside HTTP 200. ZDR disables OCR where supported; see [zero data retention](https://docs.context.dev/optimization/zero-data-retention.md).


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.