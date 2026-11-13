# Styleguide

> Extract colors, typography, spacing, and component styles from a website.

Styleguide reads a website’s visual properties to help you build a theme or review an existing design. Send exactly one of `domain` or `directUrl`.

## Extract a styleguide

```typescript TypeScript theme={null}
import ContextDev from "context.dev";

const client = new ContextDev({
  apiKey: process.env.CONTEXT_DEV_API_KEY,
});

const response = await client.web.extractStyleguide({
  domain: "example.com",
  colorScheme: "light",
});

console.log(response.styleguide?.colors);
console.log(response.styleguide?.typography.headings.h1);
```

```python Python theme={null}
import os
from context.dev import ContextDev

client = ContextDev(api_key=os.environ["CONTEXT_DEV_API_KEY"])

response = client.web.extract_styleguide(
    domain="example.com",
    color_scheme="light",
)

print(response.styleguide.colors)
print(response.styleguide.typography.headings.h1)
```

```ruby Ruby theme={null}
require "cgi/core"
require "context_dev"

client = ContextDev::Client.new(
  api_key: ENV.fetch("CONTEXT_DEV_API_KEY")
)

response = client.web.extract_styleguide(
  domain: "example.com",
  color_scheme: :light
)

puts response.styleguide.colors.inspect
puts response.styleguide.typography.headings.h1.inspect
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

    response, err := client.Web.ExtractStyleguide(
        context.Background(),
        contextdev.WebExtractStyleguideParams{
            Domain: contextdev.String("example.com"),
            ColorScheme: contextdev.WebExtractStyleguideParamsColorSchemeLight,
        },
    )
    if err != nil {
        panic(err)
    }

    fmt.Println(response.Styleguide.Colors)
    fmt.Println(response.Styleguide.Typography.Headings.H1)
}
```

```php PHP theme={null}
<?php

require __DIR__.'/vendor/autoload.php';

use ContextDev\Client;

$client = new Client(apiKey: getenv('CONTEXT_DEV_API_KEY'));

$response = $client->web->extractStyleguide(
    domain: 'example.com',
    colorScheme: 'light',
);

var_dump($response->styleguide->colors);
var_dump($response->styleguide->typography->headings->h1);
```

```bash cURL theme={null}
curl --get https://api.context.dev/v1/web/styleguide \
  --header "Authorization: Bearer $CONTEXT_DEV_API_KEY" \
  --data-urlencode "domain=example.com" \
  --data-urlencode "colorScheme=light"
```

## Use the result

| Data | Use |
| - | - |
| Colors | Review background, text, and accent choices. |
| Typography | Choose families, sizes, weights, and line heights. |
| Spacing and radii | Seed layout and component tokens. |
| Shadows and component styles | Reproduce observed UI treatment. |

Extracted values need review: check contrast, responsive typography, and interactive states before using them as a design system.

## Options

Use `directUrl=https://example.com/pricing` to inspect a specific page. `colorScheme=dark` emulates dark mode; light and dark results are cached separately. `maxAgeMs` defaults to three months (90 days, 7,776,000,000 ms), is clamped to 0–1 year, and `0` refreshes.

`timeoutOpts` and `tags` use the shared [deadline](https://docs.context.dev/optimization/timeouts.md) and [usage](https://docs.context.dev/optimization/usage-and-logs.md) behavior. Pass `policies` as comma-separated [access policy](https://docs.context.dev/optimization/access-policies.md) IDs; a URL must pass every policy.

The response’s `finalDOMState` is `loaded`, or `still-loading` when capture ended before the page finished loading.

With ZDR access, add `zdr=enabled` to suppress application logs, request-log entries, and exported traces. Cached styleguides and hosted assets can still be read and saved. Confirm `X-Context-ZDR: true`; cache metadata may still report a hit. See [Brand and Styleguide retention](https://docs.context.dev/optimization/zero-data-retention.md#brand-retrieval-and-styleguide).

## Fonts

Fonts come back in the same response. Join typography family names to `fontLinks` entries to find available files. A missing file URL can mean the font could not be resolved. Verify its license before shipping font files in your application.

Access failures return target-specific error codes. A 403 can indicate missing key permissions or ZDR entitlement. See the [Styleguide reference](https://docs.context.dev/api-reference/brand-intelligence/styleguide.md).


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.