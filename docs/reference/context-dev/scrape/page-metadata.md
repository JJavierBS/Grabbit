# Page metadata

> Read the title, description, social tags, headings, and structured data extracted from a scraped page.

Every `POST /web/scrape` response includes a `metadata` object, whatever you enable in `formats`. It describes the page itself rather than one output: the title, description, language, social preview tags, headings, and JSON-LD blocks found in the page HTML. Fields are omitted when not found, so read each one defensively.

## Read page metadata

Send this body to `POST /web/scrape`. See the [Quickstart](https://docs.context.dev/quickstart.md) for authentication and SDK setup.

```json theme={null}
{
  "url": "https://example.com",
  "formats": {
    "markdown": true
  }
}
```

Abridged response:

```json theme={null}
{
  "metadata": {
    "title": "Example Domain",
    "description": "This domain is for use in illustrative examples in documents.",
    "language": "en",
    "canonicalUrl": "https://example.com/",
    "siteName": "Example",
    "image": "https://example.com/og-image.png",
    "favicon": "https://example.com/favicon.ico",
    "openGraph": {"title": "Example Domain", "type": "website"},
    "twitter": {"card": "summary"},
    "alternates": [{"href": "https://example.com/fr/", "hreflang": "fr"}],
    "headings": [{"level": 1, "text": "Example Domain"}],
    "jsonLd": [{"@context": "https://schema.org", "@type": "WebSite", "name": "Example"}],
    "additionalMeta": {"viewport": "width=device-width, initial-scale=1"}
  }
}
```

The [Scrape overview](https://docs.context.dev/scrape/overview) reads `metadata.title` next to `markdown.data`; the same object is there for every format, including screenshots and bytes.

## Fields

| Field | Notes |
| - | - |
| `title` | String. Best title extracted from the page. |
| `description` | String. Best description extracted from standard, Open Graph, or Twitter metadata. |
| `language` | String. Language extracted from `html lang` or language meta tags. |
| `keywords` | Array of strings. Keywords extracted from the page’s keywords meta tag. |
| `canonicalUrl` | String. Resolved canonical URL, when present. |
| `author` | String. Author metadata, when present. |
| `siteName` | String. Site or application name from page metadata. |
| `image` | String. Primary resolved preview image from Open Graph, Twitter, or image metadata. |
| `favicon` | String. Resolved favicon URL, when present. |
| `publishedTime` | String. Published timestamp or date from page metadata, when present. |
| `modifiedTime` | String. Modified timestamp or date from page metadata, when present. |
| `robots` | String. Robots meta directive, when present. |
| `openGraph` | Object. Open Graph metadata with the `og:` prefix removed and keys camel-cased. Each value is a string or an array of strings. |
| `twitter` | Object. Twitter card metadata with the `twitter:` prefix removed and keys camel-cased. Each value is a string or an array of strings. |
| `alternates` | Array of objects. Resolved alternate links from `link rel=alternate` tags; see [Alternates](#alternates). |
| `headings` | Array of objects. Up to 500 h1–h6 headings in document order, before content filtering; see [Headings](#headings). |
| `jsonLd` | Array of objects. JSON-LD structured data blocks parsed from the page. |
| `additionalMeta` | Object. Additional non-social meta tags not promoted to top-level metadata fields. Each value is a string or an array of strings. |

### Alternates

| Field | Notes |
| - | - |
| `href` | String, always present. Resolved alternate URL. |
| `hreflang` | String. Language or locale for the alternate URL, when present. |
| `type` | String. Alternate resource MIME type, when present. |
| `title` | String. Alternate resource title, when present. |

### Headings

| Field | Notes |
| - | - |
| `level` | Integer from 1 to 6, from `h1` to `h6`. |
| `text` | String. Heading text with whitespace collapsed, truncated to 1,000 characters. |

Headings are collected before [content filtering](https://docs.context.dev/scrape/content-filtering.md) runs, so `mainContentOnly` and selector filters do not change them.

## Related

* [Scrape overview](https://docs.context.dev/scrape/overview): the full response shape and the outputs each format adds.
* [Crawl page metadata](https://docs.context.dev/crawl/page-metadata.md): the same fields on every crawled page, plus crawl-specific ones.
* [Content filtering](https://docs.context.dev/scrape/content-filtering.md): what the filters change and what they leave alone.
* [Freshness and caching](https://docs.context.dev/scrape/freshness-and-caching.md): when a response is served from cache.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.