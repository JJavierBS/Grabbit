# Credits and pricing

> Understand operation prices, request charges, and your organization’s credit balance.

Your organization shares one credit balance across its API keys and managed workloads. Read `key_metadata.credits_consumed` and `credits_remaining` in JSON responses; `X-Credits-Used` reports request usage in the response headers.

## Operation prices

| Operation | Credits |
| - | - |
| [Scrape](https://docs.context.dev/scrape/overview) | 1 base; 2 with browser actions. See modifiers below. |
| [Map](https://docs.context.dev/map/overview) | 1; 2 with `search`. |
| [Crawl](https://docs.context.dev/crawl/overview) | 1 per successful page; no extra OCR charge. |
| [Search](https://docs.context.dev/search/overview) | 1 per 10 returned results, rounded up. Highlights add 1 per 10 results when at least one result returns them. Markdown adds 1 per result returned with Markdown. |
| [Answers](https://docs.context.dev/answers/overview) | 10 for `fast`; 100 for `ultra` (default), on success. |
| [Brand](https://docs.context.dev/brand/overview) | 10. |
| [Brand search](https://docs.context.dev/brand/search.md) | 1 on Free and Developer; free on Pro, Growth, and Scale. |
| [Styleguide](https://docs.context.dev/brand/styleguide.md) | 10. |
| [People Search](https://docs.context.dev/people/search.md) | 10 per page in `fast` mode; 50 per page in `ultra` mode. Pages with no matches are free. |
| [People Enrich](https://docs.context.dev/people/enrich.md) | 20 per returned match; `not_found` is free. |
| [Company Search](https://docs.context.dev/companies/search.md) | 2 per page in `fast` mode; 10 per page in `ultra` mode. Pages with no matches are free. |
| [News](https://docs.context.dev/news/overview) | 1 per 10 returned results, rounded up; an unknown company’s 404 costs 1. |
| [Parse](https://docs.context.dev/parse/overview) | 1, plus 1 per page recovered by OCR. |
| [Batches](https://docs.context.dev/batches/overview) | Scrape pricing per successful page: 1 base, or 2 with browser actions, plus the [Scrape modifiers](#scrape-modifiers) for the selected formats. OCR adds 1 per recovered PDF page. |
| [Monitor runs](https://docs.context.dev/monitors/overview) | 1 for page or sitemap; 2 for a page with browser actions or a search; 10 for extract. Baseline runs count. Failed and skipped runs are free. |
| Prefetch, batch/monitor management, logs, webhook deliveries, agent feedback | 0. |

## Scrape modifiers

| Result or option | Additional credits |
| - | - |
| Highlights with at least one passage | +1. |
| JSON extraction that runs and succeeds | +4. |
| Successful product result, including `isProductPage: false` | +1. |
| PDF OCR on a fresh fetch | +1 per recovered page. |

The base applies when at least one output succeeds, including cache hits. If every output fails, no charge applies, except when the target is missing: a target 404 retains the base charge, plus 1 when product was requested, even though the product output fails with `NOT_FOUND`.

## When requests are charged

Successful and partial results are charged. Processed 404s on priced data APIs are charged at their applicable price. Validation, authentication, permission, 408, 429, and server errors are not. Brand `400 NOT_FOUND` and People `not_found` are not charged. Tags and ZDR do not change prices.

Batches reserve credits at submission for accepted URLs, or the crawl’s `maxUrls` ceiling. Unsuccessful or unused pages are refunded when the batch settles; OCR is added then. See `credits.reserved`, `refunded`, `ocr_charged`, and `net` on the batch.

## Free balance and refills

Free organizations receive 1,000 credits monthly on their grant-anchor day, whether they signed up with a work or personal email. Only one unpaid organization is allowed per person. Extra grants above the Free allowance are preserved at refill.

Paid balances reset to the monthly allowance after a paid refill; unused credits normally do not roll over. See [plans and billing](https://docs.context.dev/account/billing.md) for upgrades, pauses, and the exception for remaining balance during an upgrade.

Use **Earn free credits** or **Redeem a code** in the dashboard when available. Paid plans can enable [Auto-Topup](https://docs.context.dev/account/billing.md#auto-topup-and-spend-alerts). Dollar prices and Logo Link allowances are on the [pricing page](https://www.context.dev/pricing).


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.