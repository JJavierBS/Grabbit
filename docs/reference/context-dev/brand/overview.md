# Brand

> Retrieve logos, colors, company details, and social links using one identifier.

Retrieve a Brand profile using a domain, company name, work email, stock ticker, transaction descriptor, or page URL. All lookup types use `POST /brand/retrieve` and return the same profile shape.

## Choose a lookup

| You have | Lookup |
| - | - |
| Website domain | [By domain](https://docs.context.dev/brand/lookup-by-domain.md) |
| Company name | [By name](https://docs.context.dev/brand/lookup-by-name.md) |
| Work email | [By email](https://docs.context.dev/brand/lookup-by-email.md) |
| Stock symbol | [By ticker](https://docs.context.dev/brand/lookup-by-ticker.md) |
| Bank or card descriptor | [By transaction](https://docs.context.dev/brand/lookup-by-transaction.md) |
| Exact page to inspect | [By page URL](https://docs.context.dev/brand/lookup-by-url.md) |

## Make a request

```typescript TypeScript theme={null}
import ContextDev from "context.dev";

const client = new ContextDev({
  apiKey: process.env.CONTEXT_DEV_API_KEY,
});

const response = await client.brand.retrieve({
  type: "by_domain",
  domain: "stripe.com",
});

console.log(response.brand?.title);
```

```python Python theme={null}
import os
from context.dev import ContextDev

client = ContextDev(api_key=os.environ["CONTEXT_DEV_API_KEY"])

response = client.brand.retrieve(
    type="by_domain",
    domain="stripe.com",
)

print(response.brand.title if response.brand else None)
```

```ruby Ruby theme={null}
require "cgi/core"
require "context_dev"

client = ContextDev::Client.new(
  api_key: ENV.fetch("CONTEXT_DEV_API_KEY")
)

response = client.brand.retrieve(
  body: {
    type: :by_domain,
    domain: "stripe.com",
  }
)

puts response.brand&.title
```

```go Go theme={null}
package main

import (
    "context"
    "fmt"
    "os"

    contextdev "github.com/context-dot-dev/context-go-sdk/v2"
    "github.com/context-dot-dev/context-go-sdk/v2/option"
)

func main() {
    client := contextdev.NewClient(
        option.WithAPIKey(os.Getenv("CONTEXT_DEV_API_KEY")),
    )

    response, err := client.Brand.Get(
        context.Background(),
        contextdev.BrandGetParams{
            OfByDomain: &contextdev.BrandGetParamsBodyByDomain{
                Domain: "stripe.com",
            },
        },
    )
    if err != nil {
        panic(err)
    }

    fmt.Println(response.Brand.Title)
}
```

```php PHP theme={null}
<?php

require __DIR__.'/vendor/autoload.php';

use ContextDev\Client;

$client = new Client(apiKey: getenv('CONTEXT_DEV_API_KEY'));

// The generated Brand helper requires fields from multiple lookup types, so send the request directly.
$raw = $client->request(
    method: 'post',
    path: 'brand/retrieve',
    body: [
        'type' => 'by_domain',
        'domain' => 'stripe.com',
    ],
);

$response = json_decode((string) $raw->getBody(), true, flags: JSON_THROW_ON_ERROR);
echo $response['brand']['title'] ?? 'No brand found', PHP_EOL;
```

```bash cURL theme={null}
curl https://api.context.dev/v1/brand/retrieve \
  --request POST \
  --header "Authorization: Bearer $CONTEXT_DEV_API_KEY" \
  --header "Content-Type: application/json" \
  --data '{
    "type": "by_domain",
    "domain": "stripe.com"
  }'
```

The request stays open until the lookup finishes. PHP-specific request details live on the [PHP SDK page](https://docs.context.dev/sdks/php.md).

## Read the profile

Abridged response:

```json theme={null}
{"status":"ok","code":200,"brand":{"domain":"stripe.com","title":"Stripe","colors":[{"hex":"#635BFF","source":"site"}],"logos":[],"socials":[],"industries":{"eic":[{"industry":"Finance","subindustry":"Payments & Money Movement"}]}}}
```

Collections can be empty. Choose a logo by `type`, `mode`, and resolution. Store the canonical `brand.domain` alongside your input, and let users correct uncertain company details. Treat discovered addresses and contact information as data to verify when accuracy matters.

### Profile fields

| Field | Contents |
| - | - |
| `domain`, `title`, `description`, `slogan` | The brand’s domain, name, brief description, and slogan. |
| `colors[]` | `hex`, `name`, and `source` (`site` for the website’s own theme signals, `logo` for logo image pixels). |
| `logos[]` | `url`, `type` (`icon` or `logo`), `mode`, `colors[]`, and `resolution` with `width`, `height`, and `aspect_ratio` (width/height). `mode` is `light` (best for light mode), `dark` (best for dark mode), or `has_opaque_background` (usable in either because the image has its own background). An SVG variant is returned ahead of a similarly shaped raster equivalent. |
| `backdrops[]` | `url`, `colors[]`, and `resolution` with `width`, `height`, and `aspect_ratio`. |
| `socials[]` | `type` (such as `x`, `linkedin`, `github`, `appstore`) and `url`. |
| `address` | `street`, `city`, `state_province`, `state_code`, `postal_code`, `country`, and `country_code`. |
| `stock` | `ticker` and `exchange`; `null` when the company is not publicly traded. |
| `employees` | `range` and `exact`; `null` when unknown. `range` is one of `1 to 10`, `11 to 50`, `51 to 200`, `201 to 500`, `501 to 1000`, `1001 to 5000`, `5001 to 10000`, or `10001+`. |
| `email`, `phone` | Company email address and phone number. |
| `industries.eic[]` | `industry` and `subindustry` classifications. |
| `links` | `careers`, `privacy`, `terms`, `contact`, `blog`, and `pricing` page URLs, each `null` when not found. |
| `primary_language` | Language of the website content, such as `english`, detected from the HTML `lang` tag, page content, or social media descriptions; `null` when undetected. |
| `is_nsfw` | Whether the brand content is not safe for work. |

## Options

| Field | Accepted by | Effect |
| - | - | - |
| `maxAgeMs` | Domain, name, email, ticker | Cache freshness; defaults to 3 months, clamped to 0–1 year. `0` refreshes. |
| `maxSpeed` | All except page URL | Skip slower enrichment for a less detailed response. |
| `force_language` | All except page URL | Return text in a supported language. |
| `timeoutOpts` | All lookup types | [Deadline](https://docs.context.dev/optimization/timeouts.md) and what to return when it passes. See the limits below. |
| `tags` | All lookup types | [Usage labels](https://docs.context.dev/optimization/usage-and-logs.md) for filtering in the dashboard. |
| `policies` | All lookup types | [Access policy](https://docs.context.dev/optimization/access-policies.md) IDs to apply; a URL must pass every policy. |
| `zdr` | All lookup types | Set `"enabled"` to suppress application logs, request-log entries, and exported traces. Requires ZDR access; brand records, caches, and hosted assets may still persist. |

See [zero data retention](https://docs.context.dev/optimization/zero-data-retention.md#brand-retrieval-and-styleguide) for confirmation headers and the difference from web-content retention controls.

### Limits

| Field | Limit |
| - | - |
| `timeoutOpts.milliseconds` | 1,000 to 300,000 ms. |
| `name` | 3 to 30 characters. |
| `ticker` | 1 to 15 characters; letters, digits, and dots. |
| `transaction_info` | 3 to 500 characters. |
| `tags` | Up to 20 labels of 1 to 50 characters each. |

## Expected failures

No-match results return `400 NOT_FOUND`. An inaccessible domain can return `WEBSITE_NOT_FOUND`, `WEBSITE_ACCESS_ERROR`, or `WEBSITE_BLOCKED`.

Email rejection and short cold-domain deadlines return 422. See the lookup guides for recovery. When `partial: true`, unfinished fields are omitted; do not treat the result as a complete profile.

The [Brand reference](https://docs.context.dev/api-reference/brand-intelligence/brand.md) lists every field. For visual tokens, use [Styleguide](https://docs.context.dev/brand/styleguide.md); for a direct image embed, use [Logo Link](https://docs.context.dev/brand/logo-link.md).


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.