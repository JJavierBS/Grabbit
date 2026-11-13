# Content filtering

> Select the page regions used by text and image outputs.

Use `sharedParams` to keep useful content and remove navigation, footers, or repeated blocks. Filters affect HTML, Markdown, images, parsed fields, highlights, and JSON.

## Keep the article

Send this body to `POST /web/scrape`. See the [Quickstart](https://docs.context.dev/quickstart.md) for authentication and SDK setup.

```json theme={null}
{
  "url": "https://example.com/article",
  "formats": {
    "markdown": true,
    "images": true
  },
  "sharedParams": {
    "includeSelectors": [
      "article"
    ],
    "excludeSelectors": [
      ".newsletter",
      ".advertisement"
    ]
  }
}
```

## Options

| Field | Default | Effect |
| - | - | - |
| `mainContentOnly` | `false` | Strip detected page chrome and keep the main content. |
| `includeSelectors` | None | Keep matching subtrees. |
| `excludeSelectors` | None | Remove matching subtrees; exclusions win. |
| `includeFrames` | `false` | Include iframe content in HTML and text extraction. |

Selector lists contain 1–50 unique selectors, each up to 2,048 characters. Use CSS; XPath is unsupported. For a gallery, set `includeSelectors` to its container and request `images`.

## Which outputs change

Screenshots, original bytes, product extraction, and metadata headings use the page independently of these filters. Screenshots show visible frames even when `includeFrames` is false.

If a selector matches nothing, the output can succeed with an empty string or list. Inspect the page’s HTML and adjust the selector before retrying. [Custom parser](https://docs.context.dev/scrape/parse-fields.md) rules run on the filtered HTML.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.