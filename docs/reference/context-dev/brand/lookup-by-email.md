# Lookup by email

> Resolve a work email’s domain to a company profile.

Use `type: "by_email"` to retrieve the company associated with a work email. This resolves the email’s domain; it does not identify the person.

## Request

Send this body to `POST /brand/retrieve`. See the [Quickstart](https://docs.context.dev/quickstart.md) for authentication and SDK setup.

```json theme={null}
{
  "type": "by_email",
  "email": "alex@stripe.com"
}
```

For a signup form, debounce until the email is valid, fill suggestions from the returned profile, and preserve the user’s corrections. Use [People](https://docs.context.dev/people/enrich.md) if you need a person profile.

## Handle personal email addresses

| Response | Action |
| - | - |
| `422 FREE_EMAIL_DETECTED` | Skip company enrichment or ask for a website. |
| `422 DISPOSABLE_EMAIL_DETECTED` | Skip the address. |
| `422 COLD_DOMAIN_TIMEOUT_TOO_LOW` | Allow more time or [prefetch](https://docs.context.dev/brand/prefetching.md). |
| `400 NOT_FOUND` | Keep an unresolved company state. |

An uncached domain needs at least 10,000 ms with `behavior: "fail"`; use a longer deadline for cold lookups. See [lookup by domain](https://docs.context.dev/brand/lookup-by-domain.md#freshness-and-cold-domains).


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.