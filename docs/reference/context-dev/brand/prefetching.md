# Prefetch

> Prepare brand or styleguide data before a later request.

Prefetch queues data retrieval so a later request can return sooner. It requires a paid plan and returns a status, not the requested profile.

## Queue a lookup

```typescript TypeScript theme={null}
import ContextDev from "context.dev";

const client = new ContextDev({ apiKey: process.env.CONTEXT_DEV_API_KEY });

const response = await client.utility.prefetch({
  type: "brand",
  identifier: {
    email: "founder@stripe.com",
  },
});

console.log(response);
```

```python Python theme={null}
import os
from context.dev import ContextDev

client = ContextDev(api_key=os.environ["CONTEXT_DEV_API_KEY"])

response = client.utility.prefetch(
    type="brand",
    identifier={
      "email": "founder@stripe.com",
    },
)

print(response)
```

```ruby Ruby theme={null}
require "cgi/core"
require "context_dev"

client = ContextDev::Client.new(api_key: ENV.fetch("CONTEXT_DEV_API_KEY"))

response = client.utility.prefetch(
  type: "brand",
  identifier: {
    "email" => "founder@stripe.com",
  },
)

pp response
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
    response, err := client.Utility.Prefetch(context.Background(), contextdev.UtilityPrefetchParams{
        Type: "brand",
        Identifier: contextdev.UtilityPrefetchParamsIdentifierUnion{
            OfByEmail: &contextdev.UtilityPrefetchParamsIdentifierByEmail{Email: "founder@stripe.com"},
        },
    })
    if err != nil {
        panic(err)
    }
    fmt.Println(response)
}
```

```php PHP theme={null}
<?php

require __DIR__.'/vendor/autoload.php';

$client = new ContextDev\Client(apiKey: getenv('CONTEXT_DEV_API_KEY'));

$response = $client->utility->prefetch(
    type: "brand",
    identifier: [
      "email" => "founder@stripe.com",
    ],
);

print_r($response);
```

```bash cURL theme={null}
curl https://api.context.dev/v1/utility/prefetch \
  --request POST \
  --header "Authorization: Bearer $CONTEXT_DEV_API_KEY" \
  --header "Content-Type: application/json" \
  --data '{
  "type": "brand",
  "identifier": {
    "email": "founder@stripe.com"
  }
}'
```

## Supported inputs

Set `type` to `brand` or `styleguide`. Supply exactly one identifier, `domain` or a work `email`. Prefetch does not prepare Scrape, Crawl, Search, or Answers results.

A useful trigger is a validated work email, a saved company domain, or an earlier step in onboarding. Debounce and deduplicate by normalized domain. Prefetch can still be running or can fail; retain the normal timeout and fallback behavior for the later lookup.

## Errors and measurement

`400 INPUT_VALIDATION_ERROR` means the input needs correction. Free and disposable email addresses return 422. A Free-plan request returns `403 FORBIDDEN`.

Compare cache hits, lookup latency, and timeout rates before and after adding prefetch. Then retrieve the [Brand](https://docs.context.dev/brand/overview) or [Styleguide](https://docs.context.dev/brand/styleguide.md) normally.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.