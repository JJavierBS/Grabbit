# Google Maps

> Get business records from a Google Maps search or place ID.

Use `POST /web/scrape` with `formats.parse: true` and `parseParams: {"type": "prebuilt", "parser": "google-maps"}`. Both search and place ID requests return business records in `parsed.data.results`. See the [Quickstart](https://docs.context.dev/quickstart.md) for authentication and SDK setup.

Don't send custom `rules` with this parser. For CSS selectors and rules, use the [Custom parser](https://docs.context.dev/scrape/parse-fields.md).

## Search

Set `url` to a Google Maps search URL. Include the business type or name and location in the search, such as `pizza in New York`:

```json theme={null}
{
  "url": "https://www.google.com/maps/search/pizza+in+New+York/",
  "formats": {
    "parse": true
  },
  "parseParams": {
    "type": "prebuilt",
    "parser": "google-maps"
  }
}
```

### Search output

When `parsed.success` is `true`, the `parsed` output has this shape. Each result uses the [business fields](#business-fields) below.

```typescript theme={null}
interface GoogleMapsSearchOutput {
  type: "google-maps";
  requested: true;
  success: true;
  data: {
    results: GoogleMapsBusiness[];
  };
}
```

## Place ID

To look up a specific place, set the URL query parameter `q` to `place_id:YOUR_PLACE_ID`:

```json theme={null}
{
  "url": "https://www.google.com/maps/place/?q=place_id:ChIJifIePKtZwokRVZ-UdRGkZzs",
  "formats": {
    "parse": true
  },
  "parseParams": {
    "type": "prebuilt",
    "parser": "google-maps"
  }
}
```

### Place ID output

When `parsed.success` is `true`, the `parsed` output has this shape. Place ID lookups use the same `results` array and [business fields](#business-fields) as searches.

```typescript theme={null}
interface GoogleMapsPlaceOutput {
  type: "google-maps";
  requested: true;
  success: true;
  data: {
    results: GoogleMapsBusiness[];
  };
}
```

## Business fields

```typescript theme={null}
interface GoogleMapsBusiness {
  place_id: string;
  name: string | null;
  rating: number | null;
  number_of_reviews: number;
  website: string | null;
  google_maps_url: string;
  about: string | null;
  cid: string | null;
  google_category: string[];
  google_description: string | null;
  google_hours: {
    day: string | null;
    times: string[];
  }[] | null;
  google_image: string | null;
  google_phone: string | null;
  google_price_range_dollar_sign: string | null;
  google_reviews_url: string;
  claimed: boolean;
  latitude: number | null;
  longitude: number | null;
  google_orders_urls: {
    link: string;
    platform_name: string | null;
  }[];
  order_online_url: string | null;
  borough: string | null;
  street_addr: string | null;
  street_addr_supplement: string | null;
  city: string | null;
  postal_code: string | null;
  state: string | null;
  country: string | null;
  address: string | null;
  primary_tags: string[];
  open_status: "PERMANENTLY_CLOSED" | "TEMPORARILY_CLOSED" | null;
}
```

All 30 business fields are present. Fields marked nullable can be `null` when Google doesn't provide a value. Missing categories, order links, and primary tags are `[]`; a missing review count is `0`. `about` is a JSON-encoded string of categories and their options, and `cid` is a string so it preserves 64-bit values. URL fields can include relative links.

## Empty results and errors

No matches produce an empty `results` array. Read `parsed.success` before using the data. A failed parse has `data: null` and can coexist with successful outputs. `parsed.type` remains `"google-maps"` even when parsing fails. See [timeouts and errors](https://docs.context.dev/scrape/timeouts-and-errors.md) for handling failures.

## Request options

[Browser profiles](https://docs.context.dev/scrape/browser-profiles.md) cannot be combined with the Google Maps parser. Content filters and browser actions do not affect Maps results, which are fetched separately using a US exit. Other Scrape controls, including [caching](https://docs.context.dev/scrape/freshness-and-caching.md), [timeouts](https://docs.context.dev/scrape/timeouts-and-errors.md), and [zero data retention](https://docs.context.dev/optimization/zero-data-retention.md), still apply.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.