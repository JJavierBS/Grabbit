# G2 reviews

> Get the 25 most recent G2 reviews for a product, optionally filtered by star rating.

Use `POST /web/scrape` with `formats.parse: true` and `parseParams: {"type": "prebuilt", "parser": "g2-reviews"}`. Read the result in `parsed.data`, with `parsed.type: "g2-reviews"`. See the [Quickstart](https://docs.context.dev/quickstart.md) for authentication and SDK setup.

Don't send custom `rules` with this parser. For CSS selectors and rules, use the [Custom parser](https://docs.context.dev/scrape/parse-fields.md).

## Request

Use any G2 product URL on `g2.com` or `www.g2.com` with the form `g2.com/products/<slug>/...`, such as `https://www.g2.com/products/slack/reviews`, a reviews page copied from your browser, or a single review URL. Requests with other URLs, including G2 pages that aren't products, are rejected with `INPUT_VALIDATION_ERROR`. Renamed products are followed.

The parser returns the 25 most recently published reviews and cannot page further back. There are no request parameters for pagination, review count, or sorting.

G2's star-rating filter in the URL is kept: `filters[nps_score][]` with a value from `1` to `5`, repeatable. For example, `https://www.g2.com/products/slack/reviews?filters%5Bnps_score%5D%5B%5D=1&filters%5Bnps_score%5D%5B%5D=2` returns the latest 1- and 2-star reviews, still at most 25. Other G2 filters, sort orders, and `page` are ignored.

```json theme={null}
{
  "url": "https://www.g2.com/products/monday-crm/reviews",
  "formats": {
    "parse": true
  },
  "parseParams": {
    "type": "prebuilt",
    "parser": "g2-reviews"
  }
}
```

Requests take about 1 to 3 seconds.

## Output

When `parsed.success` is `true`, the `parsed` output has this shape:

```typescript theme={null}
interface G2ReviewsOutput {
  type: "g2-reviews";
  requested: true;
  success: true;
  data: {
    product: {
      slug: string;
      name: string;
    };
    reviews: G2Review[];
  };
}
```

`product.slug` is the product's current slug, so a renamed product returns its new slug. For example, `intercom` resolves to `fin`.

## Review fields

```typescript theme={null}
interface G2Review {
  id: string;
  url: string;
  title: string;
  rating: number | null;
  published_at: string;
  reviewer: {
    name: string | null;
    role: string | null;
    company_size: string | null;
    industry: string | null;
  };
  likes: string | null;
  dislikes: string | null;
  problems_solved: string | null;
}
```

All review fields are present. Values G2 doesn't publish are `null`; `company_size` and `industry` often are.

* `rating` is 0 to 5 in half-star steps.
* `published_at` is an ISO 8601 timestamp.
* Anonymous reviewers have `name: "Verified User"`, with their industry in `industry`.
* `likes`, `dislikes`, and `problems_solved` are the answers to G2's three standard questions. Paragraphs are separated by `\n`.

Reviews follow G2's own order, which is mostly newest first. An older review that G2 re-published can appear among them, so dedupe by `id` when polling.

```json theme={null}
{
  "type": "g2-reviews",
  "requested": true,
  "success": true,
  "data": {
    "product": {
      "slug": "monday-crm",
      "name": "monday CRM"
    },
    "reviews": [
      {
        "id": "13793023",
        "url": "https://www.g2.com/products/monday-crm/reviews/monday-crm-review-13793023",
        "title": "Highly Customizable, Well-Organized, and Easy to Navigate",
        "rating": 4.5,
        "published_at": "2026-10-15T15:01:51.000Z",
        "reviewer": {
          "name": "Verified User",
          "role": "User",
          "company_size": "11-50 employees",
          "industry": "Consulting"
        },
        "likes": "The customization is what I like the most. Also it's very well organized and clear to see",
        "dislikes": "Sometimes it's slow and when you open the tasks of the project sometimes it's hard to see which project is open",
        "problems_solved": "It's helping me not to forget the tasks I need to do in everyday life at work"
      }
    ]
  }
}
```

## Errors

An unknown product fails with `NOT_FOUND`. If G2 can't be reached, the parse fails with `WEBSITE_ACCESS_ERROR`. Read `parsed.success` before using the data. A failed parse has `data: null` and can coexist with successful outputs. `parsed.type` remains `"g2-reviews"` even when parsing fails. See [timeouts and errors](https://docs.context.dev/scrape/timeouts-and-errors.md) for handling failures.

## Request options

This parser fetches source data separately from the rendered page. [Content filters](https://docs.context.dev/scrape/content-filtering.md) and [browser actions](https://docs.context.dev/scrape/browser-actions.md) do not change its results. [Browser profiles](https://docs.context.dev/scrape/browser-profiles.md) are unsupported with this parser. Other Scrape controls, including [caching](https://docs.context.dev/scrape/freshness-and-caching.md), [timeouts](https://docs.context.dev/scrape/timeouts-and-errors.md), and [zero data retention](https://docs.context.dev/optimization/zero-data-retention.md), still apply.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.