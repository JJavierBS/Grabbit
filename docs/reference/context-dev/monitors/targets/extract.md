# Extract monitors

> Watch the pages of a site that matter for your instructions, with an optional JSON Schema that shapes the baseline data.

An `extract` target watches the pages of a site that fit your `instructions`. Detection is always `semantic`: a judge decides whether a confirmed text difference on a tracked page matters.

## Fields

| Field | Default | Notes |
| - | - | - |
| `url` | Required | Root URL to start from. |
| `instructions` | Required | 1–2,000 characters on which pages and facts to track and which changes to report. |
| `schema` | Summary and key points | Optional JSON Schema, up to 20,000 characters serialized and 12 levels deep. |
| `max_pages` | `10` | 1–50 pages to track. |
| `max_depth` | None | 0–10 link levels from `url`. `0` tracks only `url`. |
| `follow_subdomains` | `false` | Also consider pages on subdomains. |

## How a run works

A discovery crawl picks up to `max_pages` pages that fit `instructions` and `schema`, and it refreshes that set periodically. Each run fetches the tracked pages again, confirms text differences, and asks the judge whether they matter, using `confidence_threshold` as described in [Change detection](https://docs.context.dev/monitors/targets#change-detection).

Extract monitors never compare extracted data. `schema` gives the judge extra context and shapes the baseline `data` on [Retrieve a monitor](https://docs.context.dev/api-reference/monitors/retrieve.md), which refreshes about once a day. Changes contain diffs, summaries, and evidence, not data in your schema's shape.

## Example

Track a competitor's product lineup across up to 20 pages, two link levels deep.

```json theme={null}
{
  "name": "Competitor product lineup",
  "target": {
    "type": "extract",
    "url": "https://example.com",
    "instructions": "Track product names, plan tiers, and feature limits. Ignore blog posts and job listings.",
    "max_pages": 20,
    "max_depth": 2
  }
}
```

## Related

* [Targets](https://docs.context.dev/monitors/targets): detection rules and how to update a target.
* [Runs and changes](https://docs.context.dev/monitors/runs-and-changes.md): what an extract change contains.
* [Retrieve a monitor](https://docs.context.dev/api-reference/monitors/retrieve.md): where the baseline `data` appears.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.