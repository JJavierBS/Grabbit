# Access policies

> Control which websites your requests can visit and return.

An access policy is a list of domains your requests can or can't access. Requests to blocked websites are refused, and content from them is never returned or charged.

> [!NOTE]
>
> Access policies are enabled per organization. [Contact us](mailto:support@context.dev) to turn them on. Until then, the access policy endpoints and requests that list `policies` return `403 ACCESS_POLICIES_NOT_ENABLED`.

## Create a policy

Send this body to [`POST /v1/access-policies`](https://docs.context.dev/api-reference/access-policies/create). See the [Quickstart](https://docs.context.dev/quickstart.md) for authentication.

```json theme={null}
{
  "name": "Research sources",
  "allowed_domains": ["arxiv.org", "*.gov"]
}
```

Use `allowed_domains` to allow only those domains, or `blocked_domains` to block them. Send one, not both. Each domain includes its subdomains, and `*.gov` covers every `.gov` site.

The response includes the policy `id`, such as `pol_3f9c2a7e5b8d4c1f9a6e0b2d7c4f8a1e`, plus `created_at` and `updated_at`. `allowed_domains` is `null` for a blocklist and `blocked_domains` is `null` for an allowlist.

## Apply policies to a request

Add policy IDs to `policies`. This scrape only runs if every listed policy allows the URL:

```json theme={null}
{
  "url": "https://arxiv.org/abs/2410.01234",
  "policies": ["pol_3f9c2a7e5b8d4c1f9a6e0b2d7c4f8a1e"]
}
```

On endpoints that take query parameters, send a comma-separated list, such as `policies=pol_3f9c2a7e5b8d4c1f9a6e0b2d7c4f8a1e,pol_81ab4d6e2f9c0a7b5e3d1c8f6a4b2e9d`.

List several policies to combine them. For example, one policy that allows `github.com` and another that blocks `gist.github.com` together allow GitHub without gists.

Batches apply `policies` to every page, and monitors apply them to every run.

## Apply a policy automatically

Use `applies_to` to choose where a policy applies without listing it:

| `applies_to` | The policy applies to |
| - | - |
| `request` (default) | Requests that list it in `policies`. |
| `api_keys` | Every request made with the keys in `api_key_ids`. |
| `organization` | Every request from your account. |

Requests can add more policies but can't skip API key or organization policies.

### Limit an API key

Give an agent or integration a key that can only reach the websites you choose:

```json theme={null}
{
  "name": "Agent sandbox",
  "allowed_domains": ["arxiv.org", "*.gov"],
  "applies_to": "api_keys",
  "api_key_ids": ["ctxt_keyid_4b7e2f9a1c8d4e6fa3b5c7d9e1f20a4b"]
}
```

A key's ID appears as `key_id` in your [request logs](https://docs.context.dev/optimization/usage-and-logs.md).

### Apply to your whole account

```json theme={null}
{
  "name": "No social media",
  "blocked_domains": ["facebook.com", "tiktok.com"],
  "applies_to": "organization"
}
```

## What gets checked

| Endpoint | When a website is blocked |
| - | - |
| Scrape, Crawl, Map, Styleguide, Fonts, Brand, Prefetch | The request returns `403 ACCESS_POLICY_DENIED`. Crawl skips blocked links it finds. |
| Search, Answers, News | Blocked results are removed. Answers never uses them as sources. |
| Batches | Blocked URLs are listed in `invalid_urls` and never run. Pages that redirect to a blocked website fail with `ACCESS_POLICY_DENIED`. |
| Monitors | A blocked target is rejected when you save the monitor. If a policy blocks it later, runs fail with `access_policy_denied`. |

Redirects and embedded frames are checked too. Company and people data aren't affected.

## Handle a blocked request

```json theme={null}
{
  "error_code": "ACCESS_POLICY_DENIED",
  "message": "An access policy blocks gist.github.com.",
  "error_data": {
    "url": "https://gist.github.com/example",
    "denied_by": ["pol_81ab4d6e2f9c0a7b5e3d1c8f6a4b2e9d"]
  }
}
```

`denied_by` lists every policy that blocked the URL, including API key and organization policies.

## Manage policies

| Action | Endpoint |
| - | - |
| [Create](https://docs.context.dev/api-reference/access-policies/create.md) | `POST /v1/access-policies` |
| [List](https://docs.context.dev/api-reference/access-policies/list.md) | `GET /v1/access-policies` |
| [Retrieve](https://docs.context.dev/api-reference/access-policies/retrieve.md) | `GET /v1/access-policies/{policy_id}` |
| [Update](https://docs.context.dev/api-reference/access-policies/update.md) | `PATCH /v1/access-policies/{policy_id}` |
| [Delete](https://docs.context.dev/api-reference/access-policies/delete.md) | `DELETE /v1/access-policies/{policy_id}` |

List returns policies newest first, 25 per page and up to 100 with `limit`; page with `cursor` set to the previous response's `next_cursor`. Every policy carries `created_at` and `updated_at`, when it was last changed.

Creating, updating, and deleting policies requires the `access_policies:write` [permission](https://docs.context.dev/account/api-keys.md); listing and retrieving them requires `access_policies:read`. Any key can use them in `policies`. Don't grant `access_policies:write` to a key you limit with a policy, since it could change its own limits. Changes apply right away, including to running batches and monitors. A request that lists a deleted or unknown policy fails with `400`.

> [!TIP]
>
> Allowlists are the strictest option. A blocklist only covers the domains you list, so the same content on another website can still be reached.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.