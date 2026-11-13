# Tripadvisor reviews

> Read public Tripadvisor reviews of a hotel, restaurant, or attraction, 20 per page.

Use `POST /web/scrape` with `formats.parse: true` and `parseParams: {"type": "prebuilt", "parser": "tripadvisor-reviews"}`. Read the result in `parsed.data`, with `parsed.type: "tripadvisor-reviews"`. See the [Quickstart](https://docs.context.dev/quickstart.md) for authentication and SDK setup.

Don't send custom `rules` with this parser. For CSS selectors and rules, use the [Custom parser](https://docs.context.dev/scrape/parse-fields.md).

## Request

Use an HTTPS Tripadvisor review URL for a hotel, restaurant, or attraction: `Hotel_Review-g{geo}-d{id}-Reviews-….html`, `Restaurant_Review-…`, or `Attraction_Review-…`. Any Tripadvisor country domain works, such as `tripadvisor.co.uk` or `fr.tripadvisor.ca`. The parser identifies the place by the number after `-d`, so the name in the URL does not matter.

```json theme={null}
{
  "url": "https://www.tripadvisor.com/Hotel_Review-g60763-d93450-Reviews-Hyatt_Grand_Central_New_York-New_York_City_New_York.html",
  "formats": {
    "parse": true
  },
  "parseParams": {
    "type": "prebuilt",
    "parser": "tripadvisor-reviews"
  }
}
```

Each page contains up to 20 reviews. To read further pages, put the offset in the URL as `-or{N}-` after `Reviews`, as Tripadvisor does: `Hotel_Review-g60763-d93450-Reviews-or20-….html` starts at the 21st review. `pagination.next_offset` gives the next value to use.

Reviews in every language are returned, in Tripadvisor's default order, which is close to newest first but not strictly sorted by date. Other Tripadvisor pages, such as search results, city listings, and single-review `ShowUserReviews` links, are rejected.

## Output

When `parsed.success` is `true`, the `parsed` output has this shape:

```typescript theme={null}
interface TripadvisorReviewsOutput {
  type: "tripadvisor-reviews";
  requested: true;
  success: true;
  data: {
    location: {
      id: number;
      name: string;
      type: string | null;
      url: string | null;
      review_count: number;
    } | null;
    pagination: {
      offset: number;
      limit: 20;
      next_offset: number | null;
    };
    reviews: TripadvisorReview[];
  };
}
```

`location.type` is Tripadvisor's place type, such as `ACCOMMODATION`, `EATERY`, or `ATTRACTION`. `location.review_count` is the total number of reviews Tripadvisor has for the place.

## Review fields

```typescript theme={null}
interface TripadvisorReview {
  id: string;
  url: string | null;
  title: string | null;
  text: string | null;
  rating: number;
  language: string | null;
  published_at: string | null;
  visit_month: string | null;
  helpful_votes: number | null;
  subratings: { name: string; rating: number }[];
  photo_urls: string[];
  owner_response: {
    text: string | null;
    published_at: string | null;
    author_name: string | null;
  } | null;
  author: {
    id: string | null;
    username: string | null;
    name: string | null;
    url: string | null;
    contribution_count: number | null;
  };
}
```

`text` is the full review, in its original language. `published_at` is when the review was submitted, in ISO 8601 format. `visit_month` is the month of the stay or visit, as `YYYY-MM`. `subratings` holds the category ratings a reviewer gave, such as Value or Service, and is empty when there are none. `photo_urls` links to each review photo at full size.

`owner_response` is the reply from the business, or `null` when there is none. `author.id` is the reviewer's Tripadvisor user ID; use it, not `name`, to identify a reviewer across places. `author.url` links to the reviewer's profile, and `author.contribution_count` is the number of contributions they have made on Tripadvisor.

`next_offset` is `null` on the last page. An unknown place returns `reviews: []`, `location: null`, and `next_offset: null`.

Illustrative `parsed.data` with one review:

```json theme={null}
{
  "location": {
    "id": 93450,
    "name": "Example Hotel",
    "type": "ACCOMMODATION",
    "url": "https://www.tripadvisor.com/Hotel_Review-g60763-d93450-Reviews-Example_Hotel-New_York_City_New_York.html",
    "review_count": 1
  },
  "pagination": {
    "offset": 0,
    "limit": 20,
    "next_offset": null
  },
  "reviews": [
    {
      "id": "1000000001",
      "url": "https://www.tripadvisor.com/ShowUserReviews-g60763-d93450-r1000000001-Example_Hotel-New_York_City_New_York.html",
      "title": "Great location",
      "text": "Friendly staff and a quiet room close to everything.",
      "rating": 5,
      "language": "en",
      "published_at": "2026-10-01T12:00:00.000Z",
      "visit_month": "2026-09",
      "helpful_votes": 0,
      "subratings": [{ "name": "Service", "rating": 5 }],
      "photo_urls": [],
      "owner_response": {
        "text": "Thank you for staying with us.",
        "published_at": "2026-10-02T09:00:00.000Z",
        "author_name": "Guest Relations"
      },
      "author": {
        "id": "EXAMPLEUSERID",
        "username": "examplereviewer",
        "name": "Example Reviewer",
        "url": "https://www.tripadvisor.com/Profile/examplereviewer",
        "contribution_count": 3
      }
    }
  ]
}
```

## Errors and request options

Unsupported URLs fail with `INPUT_VALIDATION_ERROR`; an unavailable or invalid Tripadvisor response fails with `WEBSITE_ACCESS_ERROR`. Check `parsed.success` before reading `parsed.data`. A failed parse has `data: null` and can coexist with successful outputs. See [timeouts and errors](https://docs.context.dev/scrape/timeouts-and-errors.md).

This parser fetches Tripadvisor data separately from the rendered page. [Content filters](https://docs.context.dev/scrape/content-filtering.md) and [browser actions](https://docs.context.dev/scrape/browser-actions.md) do not change its results. [Browser profiles](https://docs.context.dev/scrape/browser-profiles.md) are unsupported. [Caching](https://docs.context.dev/scrape/freshness-and-caching.md), [timeouts](https://docs.context.dev/scrape/timeouts-and-errors.md), and [zero data retention](https://docs.context.dev/optimization/zero-data-retention.md) still apply.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.