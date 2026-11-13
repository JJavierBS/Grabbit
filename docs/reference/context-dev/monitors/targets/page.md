# Page monitors

> Watch the visible text of one page, focus on regions with CSS selectors, and describe which changes matter with instructions.

A `page` target watches the visible text of one URL. Without `instructions`, detection is `exact` and any text difference is a change. With `instructions`, detection is `semantic` and a judge decides whether a difference matters.

## Fields

| Field | Default | Notes |
| - | - | - |
| `url` | Required | Public `http(s)` URL. |
| `include_selectors` | Main content | CSS selectors for the regions to watch, combined in document order. Omit it or send `[]` for automatic main-content extraction. |
| `exclude_selectors` | None | CSS selectors to remove before comparing. They win over `include_selectors`. |
| `instructions` | None | 1–2,000 characters on what matters and what to ignore. Makes detection `semantic`. |
| `normalize_whitespace` | `true` | Ignore whitespace-only differences. Set `false` when spacing matters. |
| `actions` | None | Up to 5 [browser actions](https://docs.context.dev/scrape/browser-actions.md) run in order after load, before capture, on every run. Requires a paid plan and changes the [run price](https://docs.context.dev/account/credits.md). Changing actions starts a new baseline. |

Each selector list takes up to 50 selectors of 1–2,048 characters.

## How a run works

Every run fetches the page fresh and applies `exclude_selectors`, then `include_selectors`. If the filtered page has no usable text, the run fails with `fetch_failed` and the old baseline stays.

* An exact monitor reports the first fetch that differs from the baseline.
* A semantic monitor fetches the page again to confirm a difference before the judge sees it. The judge then applies `confidence_threshold`, described in [Change detection](https://docs.context.dev/monitors/targets#change-detection).

## Example

Watch only the incidents section of a status page and report new or resolved incidents.

```json theme={null}
{
  "name": "Status page incidents",
  "target": {
    "type": "page",
    "url": "https://status.example.com",
    "instructions": "Report new or resolved incidents. Ignore uptime percentages.",
    "include_selectors": ["#incidents"]
  },
  "change_detection": { "type": "semantic", "confidence_threshold": 0.8 }
}
```

Omit `instructions` and `change_detection` to get an exact monitor that reports any text change inside `#incidents`.

## Related

* [Targets](https://docs.context.dev/monitors/targets): detection rules and how to update a target.
* [Runs and changes](https://docs.context.dev/monitors/runs-and-changes.md): what a page change contains.
* [Browser actions](https://docs.context.dev/scrape/browser-actions.md): the actions a page monitor can run before capture.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.