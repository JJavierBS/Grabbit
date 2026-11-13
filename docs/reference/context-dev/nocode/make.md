# Make

> Retrieve a company profile in Make and pass its fields to the next step.

Use Make's HTTP module to send a Context.dev request, parse the response, and map company fields into the next step.

## Before you start

1. Create a Context.dev API key in the [dashboard](https://context.dev/dashboard).
2. Create a Make scenario with a trigger that supplies a company domain.
3. Keep the API key in a Make connection or another secret field. Do not place it in scenario names, notes, logs, or output bundles.

## Retrieve a company profile

Add **HTTP > Make a request** after your trigger and configure it as follows:

| Field | Value |
| - | - |
| URL | `https://api.context.dev/v1/brand/retrieve` |
| Method | `POST` |
| `Authorization` header | `Bearer YOUR_CONTEXT_DEV_API_KEY` |
| `Content-Type` header | `application/json` |
| Parse response | Yes |

Use a raw JSON body and map the domain from your trigger:

```json theme={null}
{
  "type": "by_domain",
  "domain": "{{1.company_domain}}"
}
```

`type` selects the lookup method. For a domain lookup, send `by_domain` and the `domain` field together.

Run the scenario once so Make learns the response fields. You can then map values such as `brand.title`, `brand.domain`, and entries from `brand.logos` into later modules.

## Use another lookup method

Change the body according to the input you already have:

> [tab] Work email
>
> ```json theme={null}
> {
>   "type": "by_email",
>   "email": "{{1.work_email}}"
> }
> ```

> [tab] Company name
>
> ```json theme={null}
> {
>   "type": "by_name",
>   "name": "{{1.company_name}}",
>   "country_gl": "{{1.country_code}}"
> }
> ```

> [tab] Transaction
>
> ```json theme={null}
> {
>   "type": "by_transaction",
>   "transaction_info": "{{1.transaction_descriptor}}",
>   "high_confidence_only": true
> }
> ```

Each request must contain the fields for one lookup type. See [Retrieve brand data](https://docs.context.dev/brand/overview) for the complete decision map.

## Route expected data states

Add a router after the HTTP module:

* Continue the enriched path when the request succeeds and the field you need is present.
* Continue a fallback path when an optional array, such as `brand.logos`, is empty.
* Send unresolved identities to review instead of silently overwriting a known CRM or transaction record.

Use Make's mapping controls rather than a fixed array position when the distinction between logo types matters. The first returned asset is not a permanent promise that it will match every background or layout.

## Handle API failures

Attach an error-handler route to the HTTP module.

| Response | Make behavior |
| - | - |
| `400` with `error_code` `NOT_FOUND` | No brand matched the input. Treat it as an unresolved lookup and route the record to review, not as a broken request. |
| Other `400`, or `422` | Stop and inspect the mapped body. Retrying the same invalid input will not help. |
| `401` or `403` | Check the secret, account access, and endpoint permissions. |
| `408`, `429`, or `5xx` | Retry a limited number of times with increasing delay and jitter. |

Do not retry every error indefinitely. Record the status, Context.dev error code, request ID, operation, and a redacted input so a failed scenario can be diagnosed safely. See [Troubleshooting](https://docs.context.dev/optimization/troubleshooting.md) for the shared failure model.

## Example scenario

```text theme={null}
New CRM company
  -> Normalize the company domain
  -> HTTP: POST /v1/brand/retrieve
  -> Router
     -> Profile found: fill only blank CRM fields
     -> Missing or ambiguous: create a review task
     -> Transient failure: limited delayed retry
```

This pattern also works before Google Slides, email, database, and notification modules. Keep the Context.dev result as evidence for the next step; do not automatically turn descriptive text or images into approved marketing claims.

## Cost and scheduling

Make bills scenario operations separately from Context.dev API usage. Check the current Context.dev endpoint cost on the [pricing page](https://context.dev/pricing/) and your Make plan before enabling a high-volume schedule. Cache stable results in your own workflow only when the applicable data terms and freshness requirements allow it.

## Next steps

> [card] [Brand lookup methods](https://docs.context.dev/brand/overview)
>
> Choose the right request body for domains, emails, names, tickers, URLs, or transactions.

> [card] [Production checklist](https://docs.context.dev/optimization/best-practices.md)
>
> Add timeouts, bounded retries, observability, and cache controls.

> [card] [Make HTTP docs](https://www.make.com/en/help/modules/http)
>
> Configure requests, response parsing, mapping, and error handlers in Make.

> [card] [Zapier](https://docs.context.dev/nocode/zapier.md)
>
> Build equivalent workflows with the Context.dev Zapier app.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.