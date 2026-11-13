# API keys

> Create restricted credentials, inspect usage, and rotate access safely.

Manage organization keys on the [API keys page](https://context.dev/dashboard/api-keys). Free organizations can have two keys; paid organizations can have 50. Keep secret keys in a server-side secret store.

## Choose permissions

New keys default to **Full access**, including future API groups. **Restricted** keys receive only their explicit grants. A restricted key with no scopes can still submit agent feedback.

| Dashboard group | Level | Scope |
| - | - | - |
| Data APIs | None / Use | `data:execute`. |
| Account logs, usage, and browser profiles | None / Read | `logs:read`. |
| Monitors | None / Read / Manage | `monitors:read` / `monitors:write`. |
| Batches | None / Read / Manage | `batches:read` / `batches:write`. |
| Access policies | None / Read / Manage | `access_policies:read` / `access_policies:write`. |

Manage includes Read. Grants apply to all resources in the organization, not individual jobs. Managed workloads do not also require `data:execute`; that scope controls direct data calls. To limit which websites a key can reach, apply an [access policy](https://docs.context.dev/optimization/access-policies.md#limit-an-api-key) to it, and don't give that key `access_policies:write`.

## Create or change a key

Choose Full access or Restricted, save the key in your application’s secret store, and send it as a Bearer token. Changes apply to subsequent requests. Already accepted work, submitted batches, and scheduled monitors continue; stop those resources separately if needed. Renaming keys requires a paid plan.

Read access includes configurations, results, history, and delivery searches. Explicit runs, mutations, delivery retries, and secret rotation require Manage. Monitor signing secrets are omitted from read-only responses. Delivery endpoints check the source’s batch or monitor permission.

A missing grant returns `403 INSUFFICIENT_PERMISSIONS` with `required_permission` when identifiable. [Team roles](https://docs.context.dev/account/team.md) control dashboard access separately; scopes are not spending caps.

## Inspect usage and retire keys

A key’s usage link opens its recent usage and request logs. The Logs API accepts `key_id` with a `logs:read` key.

To rotate, create a replacement, update the application, verify it, then disable the old key. Disable or delete retired keys from their action menu. Removing a teammate does not erase copied shared keys; rotate those keys when offboarding.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.