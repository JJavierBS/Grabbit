# Supported formats

> Choose file types and understand their Markdown output.

Parse detects the uploaded file’s type. Use the `extension` query parameter to disambiguate text or formats without a clear signature.

| Input | Output |
| - | - |
| PDF, DOCX | Structured sections and text. |
| DOC, RTF | Paragraph text. |
| XLSX, XLS, CSV, TSV | Tables by sheet, or preserved delimited data. |
| PPTX, PPT | Slide sections, text, tables, and available notes. |
| HTML, XML, feeds | Structured content with optional links and images. |
| JSON, YAML, SVG | Fenced source data or markup. |
| Text, Markdown, subtitles, code | Preserved text and applicable language-tagged blocks. |
| JPEG, PNG, GIF, BMP, TIFF, WebP, Netpbm | Image metadata; enable OCR to read text. |

The [reference’s extension list](https://docs.context.dev/api-reference/utility/parse.md) is the complete supported set. Unsupported data returns 415; an extension hint cannot convert an unsupported file into a supported one.

Keep the upload under 50 MiB and send the original bytes. See [PDFs and OCR](https://docs.context.dev/parse/pdfs-and-ocr.md) for image-only documents.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.