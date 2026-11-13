# JavaScript and TypeScript

> Install the JavaScript and TypeScript SDK, scrape a page, look up a brand, and set timeouts and retries.

The `context.dev` package works in JavaScript and TypeScript on Node.js 20 or later. [SDKs](https://docs.context.dev/sdks) covers the API key and the defaults all SDKs share.

## Install

```bash theme={null}
npm install context.dev
```

## Scrape a page

Save this as `scrape.mjs` and run `node scrape.mjs`. It prints the page as Markdown, starting with `# Example Domain`.

```javascript scrape.mjs theme={null}
import ContextDev from "context.dev";

const client = new ContextDev({ apiKey: process.env.CONTEXT_DEV_API_KEY });

const page = await client.web.scrape({
  url: "https://example.com",
  formats: { markdown: true },
  sharedParams: { mainContentOnly: true },
});

console.log(page.markdown.data);
```

For TypeScript, save the same code as `scrape.mts`, run `npm install --save-dev tsx`, then run `npx tsx scrape.mts`.

## Look up a brand

Replace the request and the `console.log` line with this lookup. It prints the company name.

```typescript theme={null}
const response = await client.brand.retrieve({
  type: "by_domain",
  domain: "stripe.com",
});

console.log(response.brand?.title);
```

## Notes

* Methods use `camelCase`, such as `client.web.mapUrls`. Request fields keep their API names, such as `sharedParams`.
* Set `timeout` in milliseconds and `maxRetries` on the client: `new ContextDev({ timeout: 120_000, maxRetries: 0 })`.
* Each Scrape output has `success`. Check it before you read `data`.

## Handle insufficient credits

Catch `ContextDev.APIError` and inspect `error_code` to handle `402 USAGE_EXCEEDED`:

```typescript theme={null}
try {
  await client.web.scrape({ url: "https://example.com", formats: { markdown: true } });
} catch (error) {
  if (error instanceof ContextDev.APIError) {
    const payload = error.error as { error_code?: string; error_data?: unknown } | undefined;
    if (payload?.error_code === "USAGE_EXCEEDED") {
      console.error("Insufficient credits. Inspect usage and refill information:", payload.error_data);
      console.error("https://context.dev/dashboard/subscription");
    } else {
      throw error;
    }
  } else {
    throw error;
  }
}
```

Retry once the account has sufficient credits. Authentication refresh does not restore credits. See [billing error handling](https://docs.context.dev/sdks#billing-errors).


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.