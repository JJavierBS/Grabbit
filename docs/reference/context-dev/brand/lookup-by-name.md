# Lookup by name

> Resolve a company name to its website and profile.

Use `type: "by_name"` when the company’s domain is unknown. Send a name of 3–30 characters and an optional country hint.

## Request

Send this body to `POST /brand/retrieve`. See the [Quickstart](https://docs.context.dev/quickstart.md) for authentication and SDK setup.

```json theme={null}
{
  "type": "by_name",
  "name": "Stripe",
  "country_gl": "us"
}
```

`country_gl` is a supported ISO 3166-1 alpha-2 code. Omit it when you have no reliable location hint.

## Verify the match

Compare `brand.title` and `brand.domain` with the intended company before merging the result into your records. Common names can be ambiguous. For user selection, [Auto-complete Brand](https://docs.context.dev/brand/search.md) returns a short list of candidates.

An unresolved name can return `400 NOT_FOUND`. Preserve the original input and let the user provide a domain. See [Brand options](https://docs.context.dev/brand/overview#options) for freshness, speed, and language controls.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.