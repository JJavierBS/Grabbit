# Agent feedback

> Report an API issue or documentation mismatch with its request ID.

Agent Feedback lets an agent or developer report a problem with a Context.dev API call, docs page, SDK, or CLI in one request. Reports go to the Context.dev team.

## When to report

Report a response that is wrong, incomplete, or different from the documentation, an error you did not expect, or a missing feature that blocks the task. Send one report per problem. Do not report errors you can fix by changing the request.

## What to send

Send `POST https://api.context.dev/v1/feedback` with these fields:

| Field | Required | Description |
| - | - | - |
| `category` | Yes | `bug`, `docs_mismatch`, `friction`, `feature_gap`, `quality_degradation`, or `other`. |
| `note` | Yes | What went wrong and what you expected, up to 4,000 characters. |
| `request_id` | `request_id` or `url` | The `request_id` from the affected response or its `X-Request-Id` header. |
| `url` | `request_id` or `url` | The page the report is about, such as one page of a crawl or a docs page. Up to 2,048 characters. |
| `tags` | No | Up to 20 [request tags](https://docs.context.dev/optimization/usage-and-logs.md), each 1–50 characters, for filtering usage in the dashboard. |

```json theme={null}
{
  "request_id": "3f1c2a6e-8b4d-4c1e-9f0a-2d7b5e6c8a91",
  "category": "bug",
  "note": "Markdown drops the plan comparison table; expected all 4 rows.",
  "url": "https://stripe.com/pricing"
}
```

With a `request_id`, the team can see the exact request and response, so you do not need to paste them. Keep API keys and personal data out of the note. See [Submit Agent Feedback](https://docs.context.dev/api-reference/feedback/submit.md) for request examples in every SDK.

## Response and limits

The response returns a `feedback_id`. Reporting the same `request_id` again returns the original `feedback_id` with `already_submitted: true` instead of creating a duplicate.

Any API key can submit feedback, including restricted keys with no scopes. Feedback has its own rate limit of 10 requests per minute per organization, so an integration that is being rate limited can still report it. Requests with [Zero Data Retention](https://docs.context.dev/optimization/zero-data-retention.md) enabled are rejected because reports are stored.

## Tell your agent

Add a line like this to your agent's instructions file, such as `AGENTS.md` or `CLAUDE.md`:

```text theme={null}
If a Context.dev response is wrong or differs from the docs, report it once with POST https://api.context.dev/v1/feedback. Include the affected request_id and never include secrets.
```


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.