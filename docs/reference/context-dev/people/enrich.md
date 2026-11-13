# Enrich a person

> Match a person from a work email, profile URL, or name, and evaluate the returned candidate.

People Enrich takes what you already know about a person, such as a work email, a profile URL, or a name and employer, and returns the best available candidate with an identity-match score from 0 to 100. It is a beta API available on all plans, including Free. To find people you don't know yet, use [People Search](https://docs.context.dev/people/search.md).

## Enrich a person

Use a work email as the identity clue. See the [Quickstart](https://docs.context.dev/quickstart.md) for authentication and SDK setup.

```typescript TypeScript theme={null}
import ContextDev from "context.dev";

const client = new ContextDev({ apiKey: process.env.CONTEXT_DEV_API_KEY });
const result = await client.people.enrich({ email: "jane@example.com" });

console.log(result.match);
```

```python Python theme={null}
import os
from context.dev import ContextDev

client = ContextDev(api_key=os.environ["CONTEXT_DEV_API_KEY"])
result = client.people.enrich(email="jane@example.com")

print(result.match)
```

```ruby Ruby theme={null}
require "cgi/core"
require "context_dev"

client = ContextDev::Client.new(api_key: ENV.fetch("CONTEXT_DEV_API_KEY"))
result = client.people.enrich(email: "jane@example.com")

pp result.match
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
    result, err := client.People.Enrich(context.Background(), contextdev.PersonEnrichParams{
        Email: contextdev.String("jane@example.com"),
    })
    if err != nil {
        panic(err)
    }

    fmt.Printf("%+v\n", result.Match)
}
```

```php PHP theme={null}
<?php

require __DIR__.'/vendor/autoload.php';

use ContextDev\Client;

$client = new Client(apiKey: getenv('CONTEXT_DEV_API_KEY'));
$result = $client->people->enrich(email: 'jane@example.com');

print_r($result->match);
```

```bash cURL theme={null}
curl https://api.context.dev/v1/people/enrich \
  -H "Authorization: Bearer $CONTEXT_DEV_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"email": "jane@example.com"}'
```

## Choose identity clues

| Input | Minimum required |
| - | - |
| [Work email](#enrich-by-work-email) | `email`. |
| [Profile URL](#enrich-by-profile-url) | `social_urls`. |
| [Name](#enrich-by-name) | First and last name, plus company, education, or location. |

Clues are additive: supply reliable additional context to improve matching.

### Enrich by work email

Send a work email and any reliable company context to `POST /people/enrich`.

```json theme={null}
{
  "email": "jane@example.com",
  "company": {
    "domain": "example.com"
  }
}
```

Email inputs can be up to 320 characters. Free and disposable email providers return 422. Preserve the original input and handle rejection without a retry loop.

For signup enrichment, show suggestions after [checking the match score](#read-the-result), and keep the user’s corrections. Use [Brand by email](https://docs.context.dev/brand/lookup-by-email.md) if you only need company information.

### Enrich by profile URL

Provide one or more person-profile URLs in `social_urls`. Additional company or location clues can help resolve ambiguous profiles.

```json theme={null}
{
  "social_urls": [
    "https://www.linkedin.com/in/jane-example/"
  ],
  "company": {
    "domain": "example.com"
  }
}
```

Send 1–20 valid URLs. Use person-profile pages, not company pages. Keep the profile URL as an external identifier when merging contacts, and review the [returned score](#read-the-result) before treating two records as the same person.

To enrich a [People Search](https://docs.context.dev/people/search.md) result, send the URL from its `profiles` list as `social_urls`.

### Enrich by name

Names alone are ambiguous. Send both first and last name with at least one company, education, or location clue.

```json theme={null}
{
  "name": {
    "first": "Jane",
    "last": "Example"
  },
  "company": {
    "domain": "example.com"
  },
  "location": {
    "country": "United States",
    "city": "San Francisco"
  }
}
```

Names accept 1–100 characters per part. Company clues can include a name or domain. Education accepts 1–10 entries, each with an `institution` (name or domain), `degree`, `field_of_study`, or `graduation_year`; valid years range from 1900 to 2200.

```json theme={null}
{
  "name": {
    "first": "Jane",
    "last": "Example"
  },
  "education": [
    {
      "institution": { "name": "Example University" },
      "degree": "BSc",
      "field_of_study": "Computer Science",
      "graduation_year": 2015
    }
  ]
}
```

The other string clues have these length limits:

| Field | Characters |
| - | - |
| `company.name`, `education[].institution.name` | 1–200 |
| `company.domain`, `education[].institution.domain` | 1–253 |
| `education[].degree`, `education[].field_of_study` | 1–200 |
| `location.city`, `location.region`, `location.country` | 1–200 |

For attendee lists, send only the context supplied by the source. Do not invent a company or location to satisfy validation. Check the [match score](#read-the-result) and retain an unresolved state for ambiguous people.

## Request options

These fields apply to every enrichment, whichever identity clues you send.

| Field | Meaning |
| - | - |
| `timeoutOpts.milliseconds` | Deadline in milliseconds, from 1,000 to 300,000. |
| `timeoutOpts.behavior` | `fail` (default) returns 408 at the deadline. `return-partial` returns the usable data completed so far and sets `partial: true` in the response. |
| `zdr` | `enabled` turns on [zero data retention](https://docs.context.dev/optimization/zero-data-retention.md). Returns `403 ZDR_NOT_ENABLED` unless your organization has ZDR. |
| `tags` | Up to 20 labels of 1–50 characters for filtering usage in the dashboard. See [Usage and request logs](https://docs.context.dev/optimization/usage-and-logs.md). |

[Timeouts](https://docs.context.dev/optimization/timeouts.md) explains how the API deadline relates to your client timeout.

## Read the result

`match.status: "candidate"` includes a score and `person`. Weak candidates can be returned, so choose a score threshold for your workflow and preserve uncertain matches for review. `match.status: "not_found"` has `score: null` and `person: null`. When `partial` is `true`, the deadline ended processing and the response holds the usable data completed so far; unfinished fields are omitted.

`person.current_role_status` is `present`, `none`, or `unknown`. When it is `unknown`, a missing role is unverified, not evidence that the person has no job.

| `person` field | Meaning |
| - | - |
| `name` | `full`, `first`, and `last`. |
| `email`, `avatar_url`, `bio` | Email address, hosted avatar URL, and bio. |
| `location` | `display`, `city`, `region`, `country`, and `country_code`. |
| `social_urls`, `website_urls` | Public profile URLs, and other website URLs. |
| `current_role` | `title`, `organization` with `name` and `domain`, `location`, `description`, `start_date`, `end_date`, and `is_current`. |
| `experience` | Work history. Each entry has the same fields as `current_role`. |
| `education` | Each entry has `institution` with `name` and `domain`, `degree`, `field_of_study`, `description`, `start_date`, and `end_date`. |
| `skills` | Professional skills. |
| `last_updated`, `checked_at` | When the underlying profile data last changed in the data sources, and when the profile was last refreshed from them, as ISO 8601 timestamps. `last_updated` is omitted when unknown. |

Dates are objects with a `year` and, when known, a `month` (1–12) and `day` (1–31). `social_urls`, `website_urls`, `current_role_status`, `experience`, `education`, and `skills` are always present; the lists can be empty. The other fields are optional.

## Availability and errors

Insufficient clues return 400; free or disposable email inputs return 422. Handle 408 and transient server errors separately from `not_found`.

ZDR omits hosted avatar URLs; see [zero data retention](https://docs.context.dev/optimization/zero-data-retention.md). The [reference](https://docs.context.dev/api-reference/people/enrich.md) describes all fields, and the [lead enrichment recipe](https://docs.context.dev/use-cases/lead-enrichment.md) shows how to use the profile.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.