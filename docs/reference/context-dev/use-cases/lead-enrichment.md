# Enrich signups and leads

> Suggest company fields, enrich CRM records, and preserve user edits.

```text Recipe prompt theme={null}
Implement this recipe in my project:
https://docs.context.dev/use-cases/lead-enrichment.md

Read the recipe and linked API guides, inspect this project's stack, and build the flow using its existing conventions.

Use a work email to suggest company fields during signup or enrich a CRM lead. Preserve edits, handle personal emails and missing profiles, deduplicate events, and keep tenant data separate. Add People enrichment only when person data is needed.

Reuse existing Context.dev configuration and keep secret API keys on the server. If Context.dev is not set up yet, follow https://docs.context.dev/agent-quickstart.md first. Add focused tests, run the relevant checks, and document setup and how to try the result.
```

Use a work email to suggest company details during signup or fill gaps in a CRM record. Treat the result as a suggestion: let people confirm or replace it. [Brand](https://docs.context.dev/brand/overview) describes the company; [People](https://docs.context.dev/people/enrich.md) describes a person.

## Look up the company

Use a server-side key from the [Quickstart](https://docs.context.dev/quickstart.md). Send the work email to Brand.

```typescript TypeScript theme={null}
import ContextDev from "context.dev";

const client = new ContextDev({ apiKey: process.env.CONTEXT_DEV_API_KEY });

const response = await client.brand.retrieve({
  type: "by_email",
  email: "founder@stripe.com",
  timeoutOpts: { milliseconds: 15000, behavior: "fail" },
});

console.log(response.brand?.title);
```

```python Python theme={null}
import os
from context.dev import ContextDev

client = ContextDev(api_key=os.environ["CONTEXT_DEV_API_KEY"])

response = client.brand.retrieve(
    type="by_email",
    email="founder@stripe.com",
    timeout_opts={"milliseconds": 15000, "behavior": "fail"},
)

print(response.brand.title if response.brand else None)
```

```ruby Ruby theme={null}
require "cgi/core"
require "context_dev"

client = ContextDev::Client.new(api_key: ENV.fetch("CONTEXT_DEV_API_KEY"))

response = client.brand.retrieve(
  body: {
    type: :by_email,
    email: "founder@stripe.com",
    timeout_opts: {milliseconds: 15000, behavior: "fail"},
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
	client := contextdev.NewClient(option.WithAPIKey(os.Getenv("CONTEXT_DEV_API_KEY")))
	response, err := client.Brand.Get(context.Background(), contextdev.BrandGetParams{
		OfByEmail: &contextdev.BrandGetParamsBodyByEmail{
			Email: "founder@stripe.com",
			TimeoutOpts: contextdev.BrandGetParamsBodyByEmailTimeoutOpts{
				Milliseconds: 15000,
				Behavior:     "fail",
			},
		},
	})
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

// Use the SDK's low-level request: its generated Brand helper cannot express a single lookup type.
$raw = $client->request(
    method: 'post',
    path: 'brand/retrieve',
    body: [
        "type" => "by_email",
        "email" => "founder@stripe.com",
        "timeoutOpts" => [
            "milliseconds" => 15000,
            "behavior" => "fail",
        ],
    ],
);

$response = json_decode((string) $raw->getBody(), true, flags: JSON_THROW_ON_ERROR);
echo $response['brand']['title'] ?? 'No match', PHP_EOL;
```

```bash cURL theme={null}
curl https://api.context.dev/v1/brand/retrieve \
  --request POST \
  --header "Authorization: Bearer $CONTEXT_DEV_API_KEY" \
  --header "Content-Type: application/json" \
  --data '{
  "type": "by_email",
  "email": "founder@stripe.com",
  "timeoutOpts": {
    "milliseconds": 15000,
    "behavior": "fail"
  }
}'
```

## Fill blanks and preserve edits

Map `brand.title`, `brand.domain`, `brand.description`, and a suitable logo into your application. Keep the raw response and retrieval time separately from confirmed fields.

For a form, apply a response only if it belongs to the current email and tenant. Fill blank fields without overwriting edits made while the request was running. Let signup continue after an empty or failed lookup.

For a CRM worker, key jobs by tenant, normalized email, and lookup version. Use a durable queue, save successful fields, and skip duplicate events. Maintain separate `matched`, `unmatched`, `partial`, and `retryable_error` states; an API error must not become an empty successful profile.

| Response | Next step |
| - | - |
| Personal or disposable email (`422`) | Ask for a work email or let the user enter company details. |
| `NOT_FOUND` | Keep the original record and allow manual entry. |
| `408`, `429`, or `5xx` | Retry later with a bounded policy; honor `Retry-After`. |
| `401` / `402` / `403` | Read `error_code`: repair credentials for authentication failures, inspect usage and refills for `USAGE_EXCEEDED`, or review permissions and entitlement for 403. |
| Partial profile | Use present fields and leave missing values unset. |

## Keep workspace branding editable

Store automatic suggestions separately from saved choices. An explicit logo removal must survive a later enrichment:

```typescript workspace-theme.ts theme={null}
type Branding = { accent: string | null; logoUrl: string | null };
type ThemeChoices = { accent?: string; logoUrl?: string | null };

export function workspaceTheme(suggested: Branding, saved: ThemeChoices) {
  const candidate = saved.accent ?? suggested.accent;
  const accent = candidate && /^#[0-9a-f]{6}$/i.test(candidate)
    ? candidate : "#334155";
  return {
    accent,
    background: "#ffffff",
    surface: "#f8fafc",
    text: "#171717",
    logoUrl: saved.logoUrl !== undefined ? saved.logoUrl : suggested.logoUrl,
  };
}
```

Use the accent for decoration until you have checked contrast for text and controls. Save choices against the tenant ID and reapply them after refreshing the Brand snapshot. [Branded content](https://docs.context.dev/use-cases/branded-documents.md) shows theme validation and rendering.

## Add person data and research when needed

Send identity clues to [People](https://docs.context.dev/people/enrich.md) when the workflow needs a person's profile:

```json People enrichment request body theme={null}
{
  "email": "person@example.com",
  "company": { "domain": "example.com" }
}
```

A match score is evidence to review, not proof of employment or identity. Keep the person and company records separate. For account research, use [Answers](https://docs.context.dev/answers/overview) and retain the source URLs with each claim; missing evidence should remain unknown.

If you know the company identifier ahead of time, [prefetch](https://docs.context.dev/brand/prefetching.md) can prepare a later lookup. The later Brand response determines whether the profile is ready.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.