# PHP

> Install the PHP SDK, scrape a page, look up a brand with the low-level request method, and set timeouts and retries.

The PHP SDK requires PHP 8.1 or later and Composer. [SDKs](https://docs.context.dev/sdks) covers the API key and the defaults all SDKs share.

## Install

```bash theme={null}
composer require "context-dev/context-dev-php:^2.37" guzzlehttp/guzzle
```

Guzzle is the HTTP transport. If your project already has a PSR-18 client and PSR-17 factories, you can use those instead.

## Scrape a page

Save this as `scrape.php` beside your `vendor` directory and run `php scrape.php`. It prints the page as Markdown, starting with `# Example Domain`.

```php scrape.php theme={null}
<?php

require __DIR__.'/vendor/autoload.php';

use ContextDev\Client;

$client = new Client(apiKey: getenv('CONTEXT_DEV_API_KEY'));

$page = $client->web->scrape(
    formats: ['markdown' => true],
    url: 'https://example.com',
    sharedParams: ['mainContentOnly' => true],
);

echo $page->markdown->data, PHP_EOL;
```

Methods take named arguments. Nested values are associative arrays keyed by the API's `camelCase` field names.

## Look up a brand

The generated Brand helper requires the fields of every lookup type at once, so it can't send a single lookup such as `by_domain`. Use the SDK's low-level `request` method instead. It keeps the SDK's authentication, retries, and error handling, and every PHP Brand example in these docs uses it.

Save this as `brand.php` and run `php brand.php`. It prints the company name.

```php brand.php theme={null}
<?php

require __DIR__.'/vendor/autoload.php';

use ContextDev\Client;

$client = new Client(apiKey: getenv('CONTEXT_DEV_API_KEY'));

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

Keep the path relative (`brand/retrieve`, with no leading slash) so the request keeps the `/v1` base path. The method returns the raw HTTP response, so decode the body yourself.

## Notes

* Set `timeout` in seconds and `maxRetries` on the client: `new Client(requestOptions: ['timeout' => 120, 'maxRetries' => 0])`.
* If `$client->web->scrape` doesn't accept an option you need, such as `highlightsParams`, `jsonParams`, or `productParams`, your installed version predates it. Send the request with `$client->request(method: 'post', path: 'web/scrape', body: [...])`.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.