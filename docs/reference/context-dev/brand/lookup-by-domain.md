# Lookup by domain

> Retrieve a profile for a known website domain.

Use `type: "by_domain"` when you know the company’s website. A URL such as `https://www.stripe.com/pricing` is normalized to `stripe.com`.

## Request

Send this body to `POST /brand/retrieve`. See the [Quickstart](https://docs.context.dev/quickstart.md) for authentication and SDK setup.

```json theme={null}
{
  "type": "by_domain",
  "domain": "stripe.com"
}
```

Read the profile as shown in [Brand overview](https://docs.context.dev/brand/overview#read-the-profile).

## Freshness and cold domains

`maxAgeMs` defaults to three months. Set `0` to refresh or accept a larger window for infrequently changing profiles.

An uncached domain with `timeoutOpts.behavior: "fail"` and a deadline below 10,000 ms returns `422 COLD_DOMAIN_TIMEOUT_TOO_LOW`. Use a 60,000 ms budget, allow partial results, or [prefetch](https://docs.context.dev/brand/prefetching.md) before the lookup. Keep your client timeout longer than the API deadline.

A background refresh can use:

```json theme={null}
{
  "type": "by_domain",
  "domain": "stripe.com",
  "maxAgeMs": 0,
  "timeoutOpts": {
    "milliseconds": 60000,
    "behavior": "return-partial"
  }
}
```

Inspect `partial` and handle website-access errors without retrying indefinitely. See [troubleshooting](https://docs.context.dev/optimization/troubleshooting.md).


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.