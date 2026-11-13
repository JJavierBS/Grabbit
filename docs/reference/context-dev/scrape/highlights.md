# Highlights

> Return Markdown passages relevant to a question or topic.

Enable `formats.highlights` and supply `highlightsParams.query`. The response contains relevant passages in page order, retaining useful Markdown formatting. Bracketed headings add context and ellipses mark omitted text.

To use Highlights while your agent works, [make Context your default search and scrape tool](https://docs.context.dev/default-search-scrape.md). The guide includes a setup prompt for Claude Code, Codex, and other agents.

## Ask about one page

Send this body to `POST /web/scrape`. See the [Quickstart](https://docs.context.dev/quickstart.md) for authentication and SDK setup.

```json theme={null}
{
  "url": "https://example.com",
  "formats": {
    "highlights": true,
    "markdown": true
  },
  "highlightsParams": {
    "query": "What is this domain used for?",
    "maxCharacters": 1500
  }
}
```

Abridged response:

```json theme={null}
{"highlights":{"requested":true,"success":true,"data":["[Example Domain] This domain is for use in illustrative examples in documents."]}}
```

## Options

| Field | Default | Limit |
| - | - | - |
| `highlightsParams.query` | Required | 1–2,000 characters. |
| `highlightsParams.maxCharacters` | 4,000 | 100–20,000 characters across returned passages. |

Ask a concrete question and use `maxCharacters` to fit your context budget. Request Markdown alongside highlights when you want the surrounding text for review.

## Videos and limits

A [YouTube video URL](https://docs.context.dev/scrape/youtube.md) can use the same request shape to find passages in its transcript. Highlights read the first 400,000 characters of page Markdown after content filters. A page without text returns an empty array. Check `highlights.success` before reading the passages.

For an answer synthesized across several pages, use [Answers](https://docs.context.dev/answers/overview).


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.