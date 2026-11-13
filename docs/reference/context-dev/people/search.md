# Search people

> Find people by role, employer, location, skills, and experience with a natural-language query, then page through the results.

People Search finds professionals who match a plain-language description, such as "VPs of sales at solar companies in California". Each page returns up to 10 people with their current role and employer, location, years of experience, skills, schools, and public profile links. It is available on all plans, including Free.

## Search for people

Describe the people you need. See the [Quickstart](https://docs.context.dev/quickstart.md) for authentication and SDK setup.

```typescript TypeScript theme={null}
import ContextDev from "context.dev";

const client = new ContextDev({ apiKey: process.env.CONTEXT_DEV_API_KEY });
const people = await client.people.search({
  query: "VPs of sales at solar companies in California",
  filters: { countries: ["US"], years_of_experience_min: 5 },
});

console.log(people.results);
```

```python Python theme={null}
import os
from context.dev import ContextDev

client = ContextDev(api_key=os.environ["CONTEXT_DEV_API_KEY"])
people = client.people.search(
    query="VPs of sales at solar companies in California",
    filters={"countries": ["US"], "years_of_experience_min": 5},
)

print(people.results)
```

```ruby Ruby theme={null}
require "cgi/core"
require "context_dev"

client = ContextDev::Client.new(api_key: ENV.fetch("CONTEXT_DEV_API_KEY"))
people = client.people.search(
  query: "VPs of sales at solar companies in California",
  filters: {countries: ["US"], years_of_experience_min: 5},
)

pp people.results
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
    people, err := client.People.Search(context.Background(), contextdev.PersonSearchParams{
        Query: "VPs of sales at solar companies in California",
        Filters: contextdev.PersonSearchParamsFilters{
            Countries:            []string{"US"},
            YearsOfExperienceMin: contextdev.Int(5),
        },
    })
    if err != nil {
        panic(err)
    }

    fmt.Printf("%+v\n", people.Results)
}
```

```php PHP theme={null}
<?php

require __DIR__.'/vendor/autoload.php';

use ContextDev\Client;

$client = new Client(apiKey: getenv('CONTEXT_DEV_API_KEY'));
$people = $client->people->search(
    query: 'VPs of sales at solar companies in California',
    filters: ['countries' => ['US'], 'yearsOfExperienceMin' => 5],
);

print_r($people->results);
```

```bash cURL theme={null}
curl https://api.context.dev/v1/people/search \
  -H "Authorization: Bearer $CONTEXT_DEV_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "VPs of sales at solar companies in California",
    "filters": {"countries": ["US"], "years_of_experience_min": 5}
  }'
```

## Choose a mode

| `mode` | How it searches | Query length |
| - | - | - |
| `fast` (default) | Matches people on basic criteria, such as their role, location, or background. | Up to 500 characters. |
| `ultra` | Plans a deeper search, judges each candidate against every criterion in the query, and adds a `match.confidence` score to each result. | Up to 5,000 characters. |

Use `ultra` for detailed requests that combine several criteria. Complex `ultra` searches can take up to 30 seconds. The SDKs' default timeouts allow for that; if you set your own client timeout, keep it above 30 seconds. `ultra` pages cost more than `fast` pages; see [Credits](https://docs.context.dev/account/credits.md#operation-prices).

```typescript TypeScript theme={null}
import ContextDev from "context.dev";

const client = new ContextDev({ apiKey: process.env.CONTEXT_DEV_API_KEY });
const people = await client.people.search({
  query: "Engineering managers at fintech companies in New York who previously worked at a bank and have led platform teams",
  mode: "ultra",
});

for (const person of people.results) {
  console.log(person.name, person.match?.confidence);
}
```

```python Python theme={null}
import os
from context.dev import ContextDev

client = ContextDev(api_key=os.environ["CONTEXT_DEV_API_KEY"])
people = client.people.search(
    query="Engineering managers at fintech companies in New York who previously worked at a bank and have led platform teams",
    mode="ultra",
)

for person in people.results:
    print(person.name, person.match.confidence if person.match else None)
```

```ruby Ruby theme={null}
require "cgi/core"
require "context_dev"

client = ContextDev::Client.new(api_key: ENV.fetch("CONTEXT_DEV_API_KEY"))
people = client.people.search(
  query: "Engineering managers at fintech companies in New York who previously worked at a bank and have led platform teams",
  mode: :ultra,
)

people.results.each do |person|
  puts "#{person.name} #{person.match&.confidence}"
end
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
    people, err := client.People.Search(context.Background(), contextdev.PersonSearchParams{
        Query: "Engineering managers at fintech companies in New York who previously worked at a bank and have led platform teams",
        Mode:  contextdev.PersonSearchParamsModeUltra,
    })
    if err != nil {
        panic(err)
    }

    for _, person := range people.Results {
        fmt.Println(person.Name, person.Match.Confidence)
    }
}
```

```php PHP theme={null}
<?php

require __DIR__.'/vendor/autoload.php';

use ContextDev\Client;

$client = new Client(apiKey: getenv('CONTEXT_DEV_API_KEY'));
$people = $client->people->search(
    query: 'Engineering managers at fintech companies in New York who previously worked at a bank and have led platform teams',
    mode: 'ultra',
);

foreach ($people->results as $person) {
    echo $person->name, ' ', $person->match?->confidence, PHP_EOL;
}
```

```bash cURL theme={null}
curl https://api.context.dev/v1/people/search \
  -H "Authorization: Bearer $CONTEXT_DEV_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Engineering managers at fintech companies in New York who previously worked at a bank and have led platform teams",
    "mode": "ultra"
  }'
```

## Filter results

Filters apply in addition to your query, and every result must match them.

| `filters` field | Meaning |
| - | - |
| `countries` | Countries people live in, as two-letter codes such as `US` or `GB`. |
| `years_of_experience_min` | Minimum years of professional experience. |
| `years_of_experience_max` | Maximum years of professional experience; at least `years_of_experience_min`. |

To label the request itself for usage charts and request logs, send `tags`: up to 20 labels of 1–50 characters. See [Usage and request logs](https://docs.context.dev/optimization/usage-and-logs.md).

## Match exact phrases

In `fast` mode, put a phrase in double quotes to require it word for word. Quoted phrases are matched against a person's name, headline, current and past job titles, employers, schools, and fields of study.

| Query | Returns people whose profile |
| - | - |
| `"site reliability" engineers in Berlin` | Contains "site reliability". |
| `"Stanford" OR "MIT" founders` | Contains "Stanford" or "MIT". |
| `product designers -"agency"` | Does not contain "agency". |

`OR` only joins quoted phrases: in `"Workday" OR Oracle`, neither name is required. Straight and curly double quotes both work; single quotes are read as plain text.

## Read the results

People are in `results`, most relevant first. Unavailable details are null or empty lists.

```json theme={null}
{
  "results": [
    {
      "name": "Alex Morgan",
      "description": "Sales leader helping solar companies grow.",
      "profiles": ["https://www.linkedin.com/in/alex-morgan-example/"],
      "location": {"country_code": "US", "region": "California", "city": "San Francisco"},
      "role": {
        "title": "VP of Sales",
        "seniority": "executive",
        "functions": ["sales"],
        "started_on": "2023-06-01",
        "company": {"name": "Solstice", "domain": "solstice.example"}
      },
      "years_of_experience": 12,
      "is_founder": false,
      "skills": ["Enterprise Sales", "Sales Leadership", "Renewable Energy"],
      "schools": ["University of California, Berkeley"]
    }
  ],
  "next_cursor": "<opaque cursor>",
  "request_id": "3f1c2a6e-8b4d-4c1e-9f0a-2d7b5e6c8a91"
}
```

| Field | Meaning |
| - | - |
| `name`, `description` | Full name and a short summary of what the person does. |
| `profiles` | Public professional profile URLs. |
| `location` | Where the person lives: `country_code`, `region`, and `city`. |
| `role` | Current `title`, `seniority`, `functions`, `started_on` date, and employer `company` with `name` and `domain`. |
| `years_of_experience`, `is_founder` | Years of professional experience, and whether the person is currently a founder or co-founder. |
| `skills`, `schools` | Professional skills and schools attended. |
| `match.confidence` | `ultra` only: how well the person matches your query, from 0 to 1. |

To get a fuller profile, send a result's `profiles` URL to [People Enrich](https://docs.context.dev/people/enrich.md#enrich-by-profile-url).

## Page through results

Pass `next_cursor` back as `cursor` with the same `query`, `mode`, and `filters` to fetch the next page. A cursor sent with a different query, mode, or filters returns 400.

```json theme={null}
{
  "query": "VPs of sales at solar companies in California",
  "filters": {"countries": ["US"], "years_of_experience_min": 5},
  "cursor": "<next_cursor from the previous response>"
}
```

Stop when `next_cursor` is null or absent; a full page does not guarantee another page. There is no `limit` parameter, and one search can page through up to 1,000 people.

## Zero data retention

Send `"zdr": "enabled"` in the body to keep the query and results out of retained usage logs and traces. It requires [zero data retention](https://docs.context.dev/optimization/zero-data-retention.md) for your organization and is confirmed by `X-Context-ZDR: true`; include it on every page of the search.

## Errors and credits

Each page that returns people is charged at its mode's rate, and pages with no matches are free. See [Credits](https://docs.context.dev/account/credits.md#operation-prices) for prices.

| Status | Cause | What to do |
| - | - | - |
| 400 | Invalid input, such as a `fast` query over 500 characters, a minimum above the maximum, or a cursor from a different search. | Fix the request. Use `ultra` for longer queries. |
| 402 | `USAGE_EXCEEDED`: your balance can't cover the page. | See [insufficient credits](https://docs.context.dev/account/billing.md#insufficient-credits). |
| 408 | The search did not finish in time. | Retry; a shorter or more specific query can help. |
| 429 | `RATE_LIMITED`: your organization hit a request limit. | Wait for `Retry-After`; see [rate limits](https://docs.context.dev/optimization/rate-limits.md). |

Try it in the [API playground](https://www.context.dev/playground/people-search). The [People Search reference](https://docs.context.dev/api-reference/people/search.md) lists every field.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.