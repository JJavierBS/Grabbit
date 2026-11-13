# Security and API stability

> Find security evidence, data controls, service status, and API compatibility guidance.

Use the [Trust Center](https://trust.context.dev) for current security reports and controls, the [status page](https://status.context.dev) for incidents, and your signed agreement for contractual commitments.

## Security and data controls

Review the [DPA](https://context.dev/dpa) and current subprocessors for your processing requirements. ZDR is an organization entitlement and must be requested and [confirmed per call](https://docs.context.dev/optimization/zero-data-retention.md#confirm-zdr-was-honored).

Keep API keys on the server. Use [restricted keys](https://docs.context.dev/account/api-keys.md), [team roles](https://docs.context.dev/account/team.md), and an established rotation process. Retained logs redact recognized credentials; this does not make arbitrary content safe to retain.

## API versioning

The public base URL is `https://api.context.dev/v1`. The [OpenAPI document](https://docs.context.dev/openapi.json) describes request methods, parameters, responses, and errors.

Clients should tolerate new optional fields and endpoints, and use a fallback for enum values described as extensible. Removing fields, changing their type or meaning, or making optional input required needs a new version or communicated migration path.

Breaking changes are announced in the [changelog](https://docs.context.dev/changelog.md). Deprecated surfaces remain available for at least 90 days after announcement, subject to contractual support windows.

## SDK compatibility and changing data

SDKs publish separately from the server contract. Pin package versions and compare serialized requests with the reference when a typed helper cannot express a supported input. See [SDK compatibility](https://docs.context.dev/sdks#use-the-low-level-request-method).

Stable response shapes do not imply stable content. Scrape returns nine output objects, each with `requested`, `success`, and `data`; source pages and extracted values can change. Test representative successes, failures, and incomplete results after upgrades.

## Support and procurement

Confirm plan allowances, support terms, SSO requirements, and any SLA in your agreement. Use [support@context.dev](mailto:support@context.dev) for integration and procurement questions, with request IDs for API failures.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.