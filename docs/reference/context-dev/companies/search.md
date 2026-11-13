# Search companies

> Find companies by name or description, with headquarters, headcount, industries, and funding details, then page through the results.

Company Search finds companies from a plain-language description, such as "robotics companies in Germany with 50 to 200 employees", or by name. Ask for "companies like stripe.com" to find similar businesses. Each page returns up to 10 companies with their identity, headquarters, headcount, industries, and known funding. It is available on all plans, including Free.

## Search for companies

Describe the companies you need. See the [Quickstart](https://docs.context.dev/quickstart.md) for authentication and SDK setup. The SDKs don't have a dedicated Company Search method yet, so these examples use each SDK's [low-level request method](https://docs.context.dev/sdks#use-the-low-level-request-method).

```typescript TypeScript theme={null}
import ContextDev from "context.dev";

const client = new ContextDev({ apiKey: process.env.CONTEXT_DEV_API_KEY });
const companies = await client.post<{ results: unknown[]; next_cursor?: string | null }>("/company/search", {
  body: {
    query: "Robotics companies with 50 to 200 employees",
    filters: { countries: ["DE"] },
  },
});

console.log(companies.results);
```

```python Python theme={null}
import os
from context.dev import ContextDev

client = ContextDev(api_key=os.environ["CONTEXT_DEV_API_KEY"])
companies = client.post(
    "/company/search",
    body={
        "query": "Robotics companies with 50 to 200 employees",
        "filters": {"countries": ["DE"]},
    },
    cast_to=dict[str, object],
)

print(companies["results"])
```

```ruby Ruby theme={null}
require "cgi/core"
require "context_dev"

client = ContextDev::Client.new(api_key: ENV.fetch("CONTEXT_DEV_API_KEY"))
companies = client.request(
  method: :post,
  path: "company/search",
  body: {
    query: "Robotics companies with 50 to 200 employees",
    filters: {countries: ["DE"]},
  },
)

pp companies[:results]
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
    client := contextdev.NewClient(option.WithAPIKey(os.Getenv("CONTEXT_DEV_API_KEY")))
    body := map[string]any{
        "query":   "Robotics companies with 50 to 200 employees",
        "filters": map[string]any{"countries": []string{"DE"}},
    }
    var companies map[string]any
    if err := client.Post(context.Background(), "/company/search", body, &companies); err != nil {
        panic(err)
    }

    fmt.Printf("%+v\n", companies["results"])
}
```

```php PHP theme={null}
<?php

require __DIR__.'/vendor/autoload.php';

use ContextDev\Client;

$client = new Client(apiKey: getenv('CONTEXT_DEV_API_KEY'));
$raw = $client->request(
    method: 'post',
    path: 'company/search',
    body: [
        'query' => 'Robotics companies with 50 to 200 employees',
        'filters' => ['countries' => ['DE']],
    ],
);

$companies = json_decode((string) $raw->getBody(), true, flags: JSON_THROW_ON_ERROR);
print_r($companies['results']);
```

```bash cURL theme={null}
curl https://api.context.dev/v1/company/search \
  -H "Authorization: Bearer $CONTEXT_DEV_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Robotics companies with 50 to 200 employees",
    "filters": {"countries": ["DE"]}
  }'
```

## Describe the companies

Name a company, or describe the companies you need by industry or what they sell, headquarters location, headcount, founding year, technology, website traffic, or funding. Queries can be up to 500 characters in `fast` mode and 5,000 in `ultra` mode.

`funding.stage` is the current stage, while `funding.latest_round` and `funding.rounds` describe known historical financing. For example, "Series B companies" asks for the current stage, while "companies that raised a Series B" asks about their history.

## Choose a mode

| `mode` | How it searches | Query length |
| - | - | - |
| `fast` (default) | Returns results in about two seconds. | Up to 500 characters. |
| `ultra` | Searches more thoroughly and checks every result against each criterion in the query. | Up to 5,000 characters. |

Use `ultra` for detailed requests that combine several criteria. `ultra` searches can take up to 20 seconds. The SDKs' default timeouts allow for that; if you set your own client timeout, keep it above 20 seconds. `ultra` pages cost more than `fast` pages; see [Credits](https://docs.context.dev/account/credits.md#operation-prices). The response shape is the same in both modes.

```typescript TypeScript theme={null}
import ContextDev from "context.dev";

const client = new ContextDev({ apiKey: process.env.CONTEXT_DEV_API_KEY });
const companies = await client.post<{ results: unknown[]; next_cursor?: string | null }>("/company/search", {
  body: {
    query: "Fintech companies in Europe that sell payroll software to small businesses, were founded after 2015, and raised a Series A or later",
    mode: "ultra",
  },
});

console.log(companies.results);
```

```python Python theme={null}
import os
from context.dev import ContextDev

client = ContextDev(api_key=os.environ["CONTEXT_DEV_API_KEY"])
companies = client.post(
    "/company/search",
    body={
        "query": "Fintech companies in Europe that sell payroll software to small businesses, were founded after 2015, and raised a Series A or later",
        "mode": "ultra",
    },
    cast_to=dict[str, object],
)

print(companies["results"])
```

```ruby Ruby theme={null}
require "cgi/core"
require "context_dev"

client = ContextDev::Client.new(api_key: ENV.fetch("CONTEXT_DEV_API_KEY"))
companies = client.request(
  method: :post,
  path: "company/search",
  body: {
    query: "Fintech companies in Europe that sell payroll software to small businesses, were founded after 2015, and raised a Series A or later",
    mode: "ultra",
  },
)

pp companies[:results]
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
    client := contextdev.NewClient(option.WithAPIKey(os.Getenv("CONTEXT_DEV_API_KEY")))
    body := map[string]any{
        "query": "Fintech companies in Europe that sell payroll software to small businesses, were founded after 2015, and raised a Series A or later",
        "mode":  "ultra",
    }
    var companies map[string]any
    if err := client.Post(context.Background(), "/company/search", body, &companies); err != nil {
        panic(err)
    }

    fmt.Printf("%+v\n", companies["results"])
}
```

```php PHP theme={null}
<?php

require __DIR__.'/vendor/autoload.php';

use ContextDev\Client;

$client = new Client(apiKey: getenv('CONTEXT_DEV_API_KEY'));
$raw = $client->request(
    method: 'post',
    path: 'company/search',
    body: [
        'query' => 'Fintech companies in Europe that sell payroll software to small businesses, were founded after 2015, and raised a Series A or later',
        'mode' => 'ultra',
    ],
);

$companies = json_decode((string) $raw->getBody(), true, flags: JSON_THROW_ON_ERROR);
print_r($companies['results']);
```

```bash cURL theme={null}
curl https://api.context.dev/v1/company/search \
  -H "Authorization: Bearer $CONTEXT_DEV_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Fintech companies in Europe that sell payroll software to small businesses, were founded after 2015, and raised a Series A or later",
    "mode": "ultra"
  }'
```

## Filter results

Filters apply in addition to your query, and every result must match them.

| `filters` field | Meaning |
| - | - |
| `countries` | Headquarters countries, as two-letter codes such as `US` or `GB`. |
| `employees_min` | Minimum headcount. |
| `employees_max` | Maximum headcount. |

Headcount filters also include companies whose reported employee range overlaps the requested bounds. Companies with conclusive matching headcounts are preferred.

To label the request itself for usage charts and request logs, send `tags`: up to 20 labels of 1–50 characters. See [Usage and request logs](https://docs.context.dev/optimization/usage-and-logs.md).

## Match exact phrases

Put a phrase in double quotes to require it word for word. Quoted phrases are matched against a company's name, former or local names, and description.

| Query | Returns companies whose profile |
| - | - |
| `"vertical farming" startups` | Contains "vertical farming". |
| `"payroll" OR "invoicing" software` | Contains "payroll" or "invoicing". |
| `cybersecurity companies -"consulting"` | Does not contain "consulting". |

`OR` only joins quoted phrases: in `"Workday" OR Oracle`, neither name is required. Straight and curly double quotes both work; single quotes are read as plain text.

## Read the results

Companies are in `results`, most relevant first. Unavailable details are null or empty lists.

```json theme={null}
{
  "results": [
    {
      "name": "Solstice",
      "domain": "solstice.example",
      "socials": {
        "linkedin": "https://www.linkedin.com/company/solstice-example",
        "x": "https://x.com/solstice_example",
        "instagram": null,
        "facebook": null,
        "youtube": null,
        "github": null,
        "crunchbase": "https://www.crunchbase.com/organization/solstice-example",
        "wellfound": null
      },
      "description": "Software for designing and managing solar installations.",
      "organization_type": "privately_held",
      "operating_status": "active",
      "stock_symbols": [],
      "revenue": {"min_usd": null, "max_usd": null},
      "industries": ["Renewable Energy"],
      "founded_year": 2018,
      "headquarters": {
        "country_code": "US",
        "region": "California",
        "city": "San Francisco",
        "street_address": null,
        "postal_code": null
      },
      "employees": {"count": null, "min": 51, "max": 200},
      "funding": {
        "stage": "series_b",
        "total_usd": 40000000,
        "round_count": 3,
        "latest_round": {"type": "series_b", "date": "2026-03-02", "amount_usd": 25000000},
        "rounds": [
          {"type": "series_b", "date": "2026-03-02", "amount_usd": 25000000, "phase": "initial"},
          {"type": "series_a", "date": "2023-09-14", "amount_usd": null, "phase": "initial"},
          {"type": "seed", "date": "2021-05-10", "amount_usd": null, "phase": "initial"}
        ]
      }
    }
  ],
  "next_cursor": "<opaque cursor>",
  "request_id": "3f1c2a6e-8b4d-4c1e-9f0a-2d7b5e6c8a91"
}
```

| Field | Meaning |
| - | - |
| `name`, `domain`, `description` | Company name, website domain, and what the company does. |
| `socials` | Profile URLs on `linkedin`, `x`, `instagram`, `facebook`, `youtube`, `github`, `crunchbase`, and `wellfound`. Each is null when unknown. |
| `organization_type`, `operating_status` | Company type, such as `public_company` or `privately_held`, and status, such as `active`, `acquired`, or `closed`. |
| `stock_symbols` | Known stock listings and ticker symbols. |
| `revenue` | Estimated annual revenue range in US dollars: `min_usd` and `max_usd`. |
| `industries`, `founded_year` | Industries the company operates in, and the year it was founded. |
| `headquarters` | `country_code`, `region`, `city`, `street_address`, and `postal_code`. |
| `employees` | Exact `count` when known, or a headcount range from `min` to `max`. `max` is null for open-ended ranges. |
| `funding` | Current `stage`, disclosed `total_usd`, `round_count`, the `latest_round`, and known `rounds`, newest first, with `type`, `date`, `amount_usd`, and whether each was an initial round or an extension (`phase`). Undisclosed amounts are null. |

## Industries

`industries` values always come from this fixed list of 148 names. Name one of them in your query, such as "biotechnology companies in Boston", to search by industry.

> [accordion] All industry values
>
> ```text theme={null}
> Accounting
> Airlines/Aviation
> Alternative Dispute Resolution
> Alternative Medicine
> Animation
> Apparel & Fashion
> Architecture & Planning
> Arts and Crafts
> Automotive
> Aviation & Aerospace
> Banking
> Biotechnology
> Broadcast Media
> Building Materials
> Business Supplies and Equipment
> Capital Markets
> Chemicals
> Civic & Social Organization
> Civil Engineering
> Commercial Real Estate
> Computer Games
> Computer Hardware
> Computer Networking
> Computer & Network Security
> Computer Software
> Construction
> Consumer Electronics
> Consumer Goods
> Consumer Services
> Cosmetics
> Dairy
> Defense & Space
> Design
> Education Management
> E-Learning
> Electrical/Electronic Manufacturing
> Entertainment
> Environmental Services
> Events Services
> Executive Office
> Facilities Services
> Farming
> Financial Services
> Fine Art
> Fishery
> Food & Beverages
> Food Production
> Fund-Raising
> Furniture
> Gambling & Casinos
> Glass, Ceramics & Concrete
> Government Administration
> Government Relations
> Graphic Design
> Health, Wellness and Fitness
> Higher Education
> Hospital & Health Care
> Hospitality
> Human Resources
> Import and Export
> Individual & Family Services
> Industrial Automation
> Information Services
> Information Technology and Services
> Insurance
> International Affairs
> International Trade and Development
> Internet
> Investment Banking
> Investment Management
> Judiciary
> Law Enforcement
> Law Practice
> Legal Services
> Legislative Office
> Leisure, Travel & Tourism
> Libraries
> Logistics and Supply Chain
> Luxury Goods & Jewelry
> Machinery
> Management Consulting
> Maritime
> Marketing and Advertising
> Market Research
> Mechanical or Industrial Engineering
> Media Production
> Medical Devices
> Medical Practice
> Mental Health Care
> Military
> Mining & Metals
> Mobile Games
> Motion Pictures and Film
> Museums and Institutions
> Music
> Nanotechnology
> Newspapers
> Non-Profit Organization Management
> Oil & Energy
> Online Media
> Outsourcing/Offshoring
> Package/Freight Delivery
> Packaging and Containers
> Paper & Forest Products
> Performing Arts
> Pharmaceuticals
> Philanthropy
> Photography
> Plastics
> Political Organization
> Primary/Secondary Education
> Printing
> Professional Training & Coaching
> Program Development
> Public Policy
> Public Relations and Communications
> Public Safety
> Publishing
> Railroad Manufacture
> Ranching
> Real Estate
> Recreational Facilities and Services
> Religious Institutions
> Renewables & Environment
> Research
> Restaurants
> Retail
> Security and Investigations
> Semiconductors
> Shipbuilding
> Sporting Goods
> Sports
> Staffing and Recruiting
> Supermarkets
> Telecommunications
> Textiles
> Think Tanks
> Tobacco
> Translation and Localization
> Transportation/Trucking/Railroad
> Utilities
> Venture Capital & Private Equity
> Veterinary
> Warehousing
> Wholesale
> Wine and Spirits
> Wireless
> Writing and Editing
> ```

Use a result's `domain` to get logos and colors from [Brand](https://docs.context.dev/brand/lookup-by-domain.md), or to find [company news](https://docs.context.dev/news/overview).

## Page through results

Pass `next_cursor` back as `cursor` with the same `query`, `mode`, and `filters` to fetch the next page.

```json theme={null}
{
  "query": "Robotics companies with 50 to 200 employees",
  "filters": {"countries": ["DE"]},
  "cursor": "<next_cursor from the previous response>"
}
```

Stop when `next_cursor` is null or absent; a full page does not guarantee another page. There is no `limit` parameter, and one search can page through up to 1,000 companies.

## Zero data retention

Send `"zdr": "enabled"` in the body to keep the query and results out of retained usage logs and traces. It requires [zero data retention](https://docs.context.dev/optimization/zero-data-retention.md) for your organization and is confirmed by `X-Context-ZDR: true`; include it on every page of the search.

## Errors and credits

Each page that returns companies is charged at its mode's rate, and pages with no matches are free. See [Credits](https://docs.context.dev/account/credits.md#operation-prices) for prices.

| Status | Cause | What to do |
| - | - | - |
| 400 | Invalid input, such as an empty query, a `fast` query over 500 characters, or an invalid cursor. | Fix the request. Use `ultra` for longer queries. |
| 402 | `USAGE_EXCEEDED`: your balance can't cover the page. | See [insufficient credits](https://docs.context.dev/account/billing.md#insufficient-credits). |
| 408 | The search did not finish in time. | Retry; a shorter or more specific query can help. |
| 429 | `RATE_LIMITED`: your organization hit a request limit. | Wait for `Retry-After`; see [rate limits](https://docs.context.dev/optimization/rate-limits.md). |

Try it in the [API playground](https://www.context.dev/playground/company-search). The [Company Search reference](https://docs.context.dev/api-reference/company/search.md) lists every field.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.