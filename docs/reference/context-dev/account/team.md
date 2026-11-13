# Team access

> Manage organization roles, invitations, SSO, and offboarding.

Each organization has one Owner, plus Admins and Members. Manage access on the [Team page](https://context.dev/dashboard/team).

## Role capabilities

| Capability | Owner | Admin | Member |
| - | - | - | - |
| Read usage, logs, results, and team | Yes | Yes | Yes |
| Manage shared keys, monitors, batches, and webhooks | Yes | Yes | Yes |
| Manage billing, payment, Auto-Topup, and spend alerts | Yes | Yes | No |
| Redeem codes and earn credits | Yes | Yes | Yes |
| Change organization name/logo and manage Members | Yes | Yes | No |
| Assign roles and manage Admins | Yes | No | No |
| Configure SSO and domain auto-join | Yes | No | No |
| Transfer ownership or delete the organization | Yes | No | No |

Members are trusted developers with access to shared production resources. Use [restricted API keys](https://docs.context.dev/account/api-keys.md) for integration permissions.

## Invitations and SSO

Invitations expire after 14 days and must match the recipient. New invitations and SSO/domain joins default to Member; Owners can invite Admins. An invitation cannot change an existing teammate’s role.

Enterprise SSO requires a Scale or Enterprise entitlement and a verified domain. Domain auto-join is a separate Owner setting. Team controls do not allow you to change your own role or deactivate yourself.

## Deactivate or remove access

Deactivation preserves the teammate’s role in the roster while blocking access and revoking delegated credentials and invitations. Reactivation restores membership, but revoked integrations must be connected again.

Removal ends membership and revokes organization-bound agent/MCP credentials. Shared API keys remain active; rotate keys the teammate may have copied.

## Transfer ownership or delete

The Owner can transfer ownership to an active teammate; the previous Owner becomes Admin. Do this before deleting a personal account that owns a shared organization.

Organization deletion requires an ended subscription and confirmation of the organization name. It disables keys and integrations and removes organization access; teammates’ personal accounts remain.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.