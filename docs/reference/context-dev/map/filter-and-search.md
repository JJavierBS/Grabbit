# Filter and search

> Limit a URL inventory by path, subdomain, count, or topic.

Pass these query parameters to `GET /web/urls`. Start with a domain, then add only the filters you need.

| Parameter | Default | Use |
| - | - | - |
| `maxLinks` | 10,000 | Return 1–100,000 URLs. |
| `urlRegex` | None | Match complete URLs with an RE2-compatible expression, up to 256 characters. |
| `excludeUrlRegex` | None | Drop complete URLs that match an RE2-compatible expression, up to 256 characters. Wins over `urlRegex`. |
| `includeSubdomains` | `false` | Include URLs on child hosts. |
| `sitemapUrl` | Automatic discovery | Map a specific sitemap on the domain or one of its subdomains. |
| `search` | None | Match a topic, 2–200 characters, ordered by relevance. |

## Find documentation pages

Use `domain=stripe.com`, `includeSubdomains=true`, and `urlRegex=^https?://docs[.]stripe[.]com/`. Encode query values when constructing the URL; RE2 does not support lookarounds or backreferences.

## Choose pages by topic

Set `search=authentication and API keys` to rank relevant URLs. Combine it with `maxLinks=20` to keep a short list. Search and path filtering can be combined.

For a repeatable dataset, save the returned URLs before submitting them to [Batches](https://docs.context.dev/batches/overview). Use [Scrape](https://docs.context.dev/scrape/overview) for screenshots or structured data from selected pages.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.