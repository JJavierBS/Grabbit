# Search monitors

> Search the web on every run and report results you haven't seen before, judged against your instructions or reported one by one.

A `search` target runs a web search on every check and reports results not seen before. Detection defaults to `semantic`: a judge keeps only results that describe a new development matching `instructions`. Set `exact` to report every new result instead.

## Fields

| Field | Default | Notes |
| - | - | - |
| `query` | Required | 1–500 characters. Supports operators such as `site:`, `-site:`, and quoted phrases. |
| `instructions` | The query | 1–2,000 characters on which new results matter and which to ignore. |

Unlike page targets, adding or omitting `instructions` doesn't change the detection type. Send `"change_detection": {"type": "exact"}` to turn the judge off.

## How a run works

Each run fetches up to 20 results for `query`, restricted to a freshness window that covers at least two schedule intervals: the last 24 hours, week, month, or year, whichever is the smallest that fits. The baseline run records those results and reports nothing. Later runs keep only results whose URL hasn't been seen within the window, then drop results published before the monitor was created. Results with no publish date are kept.

* An exact monitor reports every remaining result. The title is `New results for "<query>"`, and the summary lists up to three result titles.
* A semantic monitor asks the judge about each remaining result. A result is reported when it describes a concrete development rather than an evergreen page, opinion piece, or listicle, the development happened after monitoring began, it matches `instructions`, it isn't one of the monitor's last 10 reported changes, and confidence is at or above `confidence_threshold`. The judge writes the change's `title`, `summary`, and `importance`. If the judge doesn't return verdicts, the run fails with `judge_failed`.

Every reported result appears in the change's `matched_urls` and as an `evidence` entry whose `url` is the result and whose `after` holds the title and snippet. The change's `url` is the first new result. See [Runs and changes](https://docs.context.dev/monitors/runs-and-changes.md) for the full shape.

The monitor's baseline on [Retrieve a monitor](https://docs.context.dev/api-reference/monitors/retrieve.md) holds the `results` as last observed, each with `url`, `title`, `description`, and `published_at`, plus `captured_at`.

## Example

Watch for acquisition or product news about a company and skip commentary.

```json theme={null}
{
  "name": "Acme news",
  "target": {
    "type": "search",
    "query": "\"Acme Corp\" -site:acme.com",
    "instructions": "Alert me when Acme announces an acquisition or a new product. Ignore opinion pieces."
  },
  "change_detection": { "type": "semantic", "confidence_threshold": 0.8 },
  "schedule": { "type": "interval", "frequency": 1, "unit": "days" }
}
```

Omit `instructions` and set `"change_detection": {"type": "exact"}` to get every new result for the query.

## Related

* [Targets](https://docs.context.dev/monitors/targets): detection rules and how to update a target.
* [Runs and changes](https://docs.context.dev/monitors/runs-and-changes.md): what a search change contains.
* [Web search](https://docs.context.dev/search/overview): the search behind each run and its query operators.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.